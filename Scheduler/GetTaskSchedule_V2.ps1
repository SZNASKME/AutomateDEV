#####################################Update History##############################################
################# 30/04/2025 : Add field task status by parinya.c@askme.co.th ####################
################# 19/11/2025 : Split multiple triggers to multiple rows + add TriggerStatus #####

param( 
    [string]$xmlPath = "D:\Task_Scheduler_Export\",   
    [string]$outputCsv = "D:\Task_Scheduler_Export\Output.csv", 
    [string]$targetPath = "\",                 
    [string]$reSub = "Y"                    
)


# 1. Export Task Scheduler to XML
if (-not (Test-Path -Path $xmlPath)) {
    New-Item -ItemType Directory -Path $xmlPath | Out-Null
    Write-Host "Created export folder: $xmlPath" -ForegroundColor Green
}

# Retrieve tasks based on recursion setting
if ($reSub -eq "N") {
    $tasks = Get-ScheduledTask | Where-Object { $_.TaskPath -eq $targetPath }
} else {
    $tasks = Get-ScheduledTask | Where-Object { $_.TaskPath -like "$targetPath*" }
}
Write-Host "Found $($tasks.Count) tasks under $targetPath" -ForegroundColor Cyan

foreach ($task in $tasks) {
    $taskName = $task.TaskName
    $taskFullPath = $task.TaskPath
    $relativePath = $taskFullPath.TrimStart("\").TrimEnd("\")  
    $taskStatus = $task.State
    #write-host $taskStatus
    if ($relativePath -eq "") { $relativePath = "Root" }

    $exportFolder = Join-Path $xmlPath $relativePath
    if (-not (Test-Path -Path $exportFolder)) {
        New-Item -ItemType Directory -Path $exportFolder | Out-Null
    }

    try {
        $taskXML = Export-ScheduledTask -TaskName $taskName -TaskPath $taskFullPath
        $xmlFile = Join-Path $exportFolder "$taskName.xml"
        $taskXML | Out-File $xmlFile -Encoding UTF8
        
        # Load the saved XML
        [xml]$xmlDoc = Get-Content $xmlFile

        # Create a new node without a namespace (this avoids xmlns="")
        $statusNode = $xmlDoc.CreateElement("TaskStatus", $xmlDoc.DocumentElement.NamespaceURI)
        $statusNode.InnerText = $taskStatus.ToString()

        # Import and append to the <Task> node
        $importedNode = $xmlDoc.ImportNode($statusNode, $true)
        $xmlDoc.DocumentElement.AppendChild($importedNode) | Out-Null

        # Save the modified XML
        $xmlDoc.Save($xmlFile)

    }
    catch {
        Write-Warning "Failed to export task: $taskName from path $taskFullPath"
    }
}

function Convert-Duration {
    param([string]$duration)
    
    if ([string]::IsNullOrWhiteSpace($duration)) { return "" }
    
    # Handle P/PT format (ISO 8601 Duration)
    if ($duration -match '^P') {
        $result = @()
        
        # Years
        if ($duration -match 'P(\d+)Y') {
            $result += "$($matches[1]) year(s)"
        }
        
        # Months (before D to avoid confusion)
        if ($duration -match '(\d+)M' -and $duration -notmatch 'T.*(\d+)M') {
            $result += "$($matches[1]) month(s)"
        }
        
        # Days
        if ($duration -match '(\d+)D') {
            $result += "$($matches[1]) day(s)"
        }
        
        # Hours (after T)
        if ($duration -match 'T.*?(\d+)H') {
            $result += "$($matches[1]) hour(s)"
        }
        
        # Minutes (after T)
        if ($duration -match 'T.*?(\d+)M') {
            $result += "$($matches[1]) minute(s)"
        }
        
        # Seconds (after T)
        if ($duration -match 'T.*?(\d+(?:\.\d+)?)S') {
            $result += "$($matches[1]) second(s)"
        }
        
        if ($result.Count -eq 0) {
            return $duration
        }
        
        return ($result -join ", ")
    }
    
    return $duration
}

function Convert-Boolean {
    param([string]$value)
    
    if ([string]::IsNullOrWhiteSpace($value)) { return "" }
    
    switch ($value.ToLower()) {
        "true" { return "Yes" }
        "false" { return "No" }
        default { return $value }
    }
}

Write-Host "Exporting of scheduled tasks completed." -ForegroundColor Green

# 2. Extract XML to CSV
$xmlFiles = Get-ChildItem -Path $xmlPath -Filter "*.xml" -Recurse
$results = @()
$allActionKeys = @()

$ipv4 = (Get-NetIPAddress | Where-Object { 
    $_.AddressFamily -eq "IPv4" -and 
    $_.InterfaceAlias -notlike "*Loopback*" -and 
    $_.IPAddress -notmatch "^169\.254\."
}).IPAddress -join ", "

$hostname = $env:COMPUTERNAME

# -------- First pass: find max actions and build action keys --------
foreach ($xmlFile in $xmlFiles) {
    [xml]$xml = Get-Content $xmlFile.FullName -ErrorAction SilentlyContinue
    $actions = $xml.Task.Actions.Exec

    $actionIndex = 1
    foreach ($action in $actions) {
        $allActionKeys += "Command_$actionIndex", "Arguments_$actionIndex", "WorkingDirectory_$actionIndex"
        $actionIndex++
    }
}

$allActionKeys = $allActionKeys | Sort-Object { [int]($_ -replace '\D', '') } | Get-Unique

# -------- Second pass: build rows (1 row per Trigger) --------
foreach ($xmlFile in $xmlFiles) {
    [xml]$xml = Get-Content $xmlFile.FullName -ErrorAction SilentlyContinue
    $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
    $ns.AddNamespace("t", "http://schemas.microsoft.com/windows/2004/02/mit/task")

    $uriNode = $xml.SelectSingleNode("//t:RegistrationInfo/t:URI", $ns)
    $uri = if ($uriNode) { $uriNode.InnerText.Trim() } else { "Unknown" }
    $taskName = ($uri -split '\\')[-1]  
    $taskPath = ($uri -replace "\\$taskName$", "") 
    $taskStatus = $xml.Task.TaskStatus
    
    if ($taskPath -ne "") { $taskPath += "\" }  

    # ----- Extract Actions (เหมือนเดิม ใช้หลาย column Command_x/Arguments_x/WorkingDirectory_x) -----
    $actions = $xml.Task.Actions.Exec
    $actionColumns = @{}
    $actionIndex = 1
    foreach ($action in $actions) {
        $command = if ($action.Command) { $action.Command.Trim() } else { "" }
        $arguments = if ($action.Arguments -and $action.Arguments.Trim() -ne "") { "'$($action.Arguments.Trim())'" } else { "" }
        $workingDirectory = if ($action.WorkingDirectory) { $action.WorkingDirectory.Trim() } else { "" }
        
        $actionColumns["Command_$actionIndex"] = $command
        $actionColumns["Arguments_$actionIndex"] = $arguments
        $actionColumns["WorkingDirectory_$actionIndex"] = $workingDirectory
        $actionIndex++
    }

    # ----- Extract Triggers (สร้างหลาย row ถ้ามีหลาย trigger) -----
    $triggers = $xml.SelectNodes("//t:Triggers/*", $ns)

    if (-not $triggers -or $triggers.Count -eq 0) {
        # ไม่มี trigger เลย สร้าง 1 row ว่างสำหรับ trigger
        $result = [ordered]@{
            Name          = $taskName
            Status        = $taskStatus
            IPV4          = $ipv4 
            HostName      = $hostname 
            Path          = $taskPath
            SourceFile    = $xmlFile.FullName
            TriggerType   = ""
            StartBoundary = ""
            Detail        = ""
            TriggerStatus = ""
            ExecutionTimeLimit = ""
            Repetition_Interval = ""
            Repetition_Duration = ""
            Repetition_StopAtDurationEnd = ""
            Delay = ""
            RandomDelay = ""
        }

        foreach ($key in $allActionKeys) {
            if ($actionColumns.ContainsKey($key)) {
                $result[$key] = $actionColumns[$key]
            } else {
                $result[$key] = ""
            }
        }

        $results += New-Object PSObject -Property $result
    }
    else {
        foreach ($trigger in $triggers) {
            $triggerType = ""
            $formattedStartBoundary = ""
            $detail = ""
            $triggerStatus = ""
            $executionTimeLimit = ""
            $repetitionInterval = ""
            $repetitionDuration = ""
            $repetitionStopAtDurationEnd = ""
            $delay = ""
            $randomDelay = ""

            # StartBoundary (ใช้ได้ทั้ง CalendarTrigger และ TimeTrigger)
            $startBoundaryNode = $trigger.SelectSingleNode("t:StartBoundary", $ns)
            if ($startBoundaryNode) {
                $formattedStartBoundary = [DateTime]::Parse($startBoundaryNode.InnerText).ToString("dd/MM/yyyy HH:mm:ss")
            }

            $endBoundaryNode = $trigger.SelectSingleNode("t:EndBoundary", $ns)
            $formattedEndBoundary = if ($endBoundaryNode) { 
                try { [DateTime]::Parse($endBoundaryNode.InnerText).ToString("dd/MM/yyyy HH:mm:ss") } 
                catch { $endBoundaryNode.InnerText }
            } else { "" }
            
            # ExecutionTimeLimit
            $executionTimeLimitNode = $trigger.SelectSingleNode("t:ExecutionTimeLimit", $ns)
            if ($executionTimeLimitNode) {
                $executionTimeLimit = if ($trigger.ExecutionTimeLimit) { Convert-Duration $trigger.ExecutionTimeLimit } else { "" }
            }

            # Repetition
            $repetitionNode = $trigger.SelectSingleNode("t:Repetition", $ns)
            if ($repetitionNode) {
                $intervalNode = $repetitionNode.SelectSingleNode("t:Interval", $ns)
                if ($intervalNode) { $repetitionInterval = if ($repetitionNode -and $repetitionNode.Interval) { Convert-Duration $repetitionNode.Interval } else { "" } }
                
                $durationNode = $repetitionNode.SelectSingleNode("t:Duration", $ns)
                if ($durationNode) { $repetitionDuration = if ($repetitionNode -and $repetitionNode.Duration) { Convert-Duration $repetitionNode.Duration } else { "" } }
                
                $stopAtDurationEndNode = $repetitionNode.SelectSingleNode("t:StopAtDurationEnd", $ns)
                if ($stopAtDurationEndNode) { $repetitionStopAtDurationEnd = if ($repetitionNode -and $repetitionNode.StopAtDurationEnd) { Convert-Boolean $repetitionNode.StopAtDurationEnd } else { "" } }
            }

            # Delay (for BootTrigger, LogonTrigger, etc.)
            $delayNode = $trigger.SelectSingleNode("t:Delay", $ns)
            if ($delayNode) {
                $delay = if ($delayNode) { Convert-Duration $delayNode.InnerText } else { "" }
            }

            # RandomDelay
            $randomDelayNode = $trigger.SelectSingleNode("t:RandomDelay", $ns)
            if ($randomDelayNode) {
                $randomDelay = if ($randomDelayNode) { Convert-Duration $randomDelayNode.InnerText } else { "" }
            }

         # Trigger Enabled / Disabled
$enabledNode = $trigger.SelectSingleNode("t:Enabled", $ns)

if ($enabledNode -and $enabledNode.InnerText.Trim() -ne "") {
    if ($enabledNode.InnerText.Trim().ToLower() -eq "true") {
        $triggerStatus = "Enabled"
    }
    else {
        $triggerStatus = "Disabled"
    }
}
else {
    # ถ้าไม่มี tag <Enabled> ให้ถือว่า Enabled
    $triggerStatus = "Enabled"
}

            if ($trigger.Name -eq "CalendarTrigger") {
                $formattedStartBoundary = if ($startBoundaryNode) { [DateTime]::Parse($startBoundaryNode.InnerText).ToString("HH:mm:ss") } else { "" }
                if ($trigger.SelectSingleNode("t:ScheduleByDay", $ns)) {
                    $daysInterval = $trigger.ScheduleByDay.DaysInterval
                    $triggerType = "Daily"
                    $detail = "At $formattedStartBoundary every $daysInterval day"
                }
                elseif ($trigger.SelectSingleNode("t:ScheduleByWeek", $ns)) {
                    $daysString = ($trigger.SelectSingleNode("t:ScheduleByWeek/t:DaysOfWeek", $ns).ChildNodes | ForEach-Object { $_.Name }) -join ','
                    $weeksIntervalNode = $trigger.SelectSingleNode("t:ScheduleByWeek/t:WeeksInterval", $ns)
                    $weeksInterval = if ($weeksIntervalNode) { $weeksIntervalNode.InnerText } else { "1" }
                    $triggerType = "Weekly"
                    $detail = "At $formattedStartBoundary every $daysString of every $weeksInterval week"
                }
                elseif ($trigger.SelectSingleNode("t:ScheduleByMonth", $ns)) {
                    $daysString = ($trigger.SelectNodes("t:ScheduleByMonth/t:DaysOfMonth/t:Day", $ns) | ForEach-Object { $_.InnerText.Trim() }) -join ','
                    $monthsString = ($trigger.SelectSingleNode("t:ScheduleByMonth/t:Months", $ns).ChildNodes | ForEach-Object { $_.Name }) -join ','
                    $triggerType = "Monthly"
                    $detail = "At $formattedStartBoundary on day $daysString of $monthsString"
                }
                elseif ($trigger.SelectSingleNode("t:ScheduleByMonthDayOfWeek", $ns)) {
                    $weekString = ($trigger.SelectNodes("t:ScheduleByMonthDayOfWeek/t:Weeks/t:Week", $ns) | ForEach-Object { $_.InnerText.Trim() }) -join ','
                    $dayOfWeekString = ($trigger.SelectSingleNode("t:ScheduleByMonthDayOfWeek/t:DaysOfWeek", $ns).ChildNodes | ForEach-Object { $_.Name }) -join ','
                    $monthsString = ($trigger.SelectSingleNode("t:ScheduleByMonthDayOfWeek/t:Months", $ns).ChildNodes | ForEach-Object { $_.Name }) -join ','
                    $triggerType = "Monthly"
                    $detail = "Run on $weekString $dayOfWeekString each $monthsString starting $formattedStartBoundary"
                }
            }
            elseif ($trigger.Name -eq "TimeTrigger") {
                $triggerType = "One Time"
                $detail = "At $formattedStartBoundary"
            }

            # สร้าง 1 row ต่อ 1 trigger
            $result = [ordered]@{
                Name          = $taskName
                Status        = $taskStatus
                IPV4          = $ipv4 
                HostName      = $hostname 
                Path          = $taskPath
                SourceFile    = $xmlFile.FullName
                TriggerType   = $triggerType
                StartBoundary = $formattedStartBoundary
                EndBoundary   = $formattedEndBoundary
                Detail        = $detail
                TriggerStatus = $triggerStatus
                ExecutionTimeLimit = $executionTimeLimit
                Repetition_Interval = $repetitionInterval
                Repetition_Duration = $repetitionDuration
                Repetition_StopAtDurationEnd = $repetitionStopAtDurationEnd
                Delay = $delay
                RandomDelay = $randomDelay
            }

            # ใส่ Action columns (เหมือนเดิม)
            foreach ($key in $allActionKeys) {
                if ($actionColumns.ContainsKey($key)) {
                    $result[$key] = $actionColumns[$key]
                } else {
                    $result[$key] = ""
                }
            }

            $results += New-Object PSObject -Property $result
        }
    }
}

# Ensure all results have the same columns before exporting
$allKeys = @()
foreach ($item in $results) {
    $allKeys += $item.PSObject.Properties.Name
}
$allKeys = $allKeys | Sort-Object -Unique

# Reorder columns (ไม่มี index แล้ว ใช้ TriggerType/StartBoundary/Detail/TriggerStatus ตรง ๆ)
$finalColumns = @(
    "Name", 
    "Status", 
    "IPV4", 
    "HostName", 
    "Path", 
    "SourceFile",
    "TriggerType",
    "StartBoundary",
    "Detail",
    "TriggerStatus",
    "ExecutionTimeLimit",
    "Repetition_Interval",
    "Repetition_Duration",
    "Repetition_StopAtDurationEnd"
) + 
($allKeys | Where-Object { $_ -match "^Command_\d+" }) +
($allKeys | Where-Object { $_ -match "^Arguments_\d+" }) +
($allKeys | Where-Object { $_ -match "^WorkingDirectory_\d+" })

# Export to CSV (forcing correct column order)
$results | Select-Object $finalColumns | Export-Csv $outputCsv -NoTypeInformation -Encoding UTF8
Write-Host "Extraction completed. Output saved to $outputCsv" -ForegroundColor Green
