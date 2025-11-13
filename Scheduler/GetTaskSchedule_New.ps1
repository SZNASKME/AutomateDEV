#####################################Update History##############################################
################# 30/04/2025 : Add field task status by parinya.c@askme.co.th ####################

param( 
    [string]$xmlPath = "D:\Stonebranch\Tidlor\Script\",   
    [string]$outputCsv = "D:\Stonebranch\Tidlor\Script\Output.csv", 
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

Write-Host "Exporting of scheduled tasks completed." -ForegroundColor Green

# 2. Extract XML to CSV
$xmlFiles = Get-ChildItem -Path $xmlPath -Filter "*.xml" -Recurse
$results = @()
$allTriggerKeys = @()
$allActionKeys = @()

$ipv4 = (Get-NetIPAddress | Where-Object { 
    $_.AddressFamily -eq "IPv4" -and 
    $_.InterfaceAlias -notlike "*Loopback*" -and 
    $_.IPAddress -notmatch "^169\.254\."
}).IPAddress -join ", "

$hostname = $env:COMPUTERNAME

# Extract triggers & actions keys in first pass
foreach ($xmlFile in $xmlFiles) {
    [xml]$xml = Get-Content $xmlFile.FullName -ErrorAction SilentlyContinue
    $actions = $xml.Task.Actions.Exec
    #$triggers = $xml.SelectNodes("//t:Triggers/*")

    $actionIndex = 1
    foreach ($action in $actions) {
        $allActionKeys += "Command_$actionIndex", "Arguments_$actionIndex", "WorkingDirectory_$actionIndex"
        $actionIndex++
    }
}

$allActionKeys = $allActionKeys | Sort-Object { [int]($_ -replace '\D', '') } | Get-Unique

# Second Pass: Extract Task Data
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

    # Extract Actions
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

    # Extract Triggers
    $triggers = $xml.SelectNodes("//t:Triggers/*", $ns)
    $triggerColumns = @{}
    $triggerIndex = 1

    foreach ($trigger in $triggers) {
        $triggerType = ""
        $formattedStartBoundary = ""
        $detail = ""

   if ($trigger.Name -eq "CalendarTrigger") 
		{
        $startBoundaryNode = $trigger.SelectSingleNode("t:StartBoundary", $ns)
        $formattedStartBoundary = if ($startBoundaryNode) { 
            [DateTime]::Parse($startBoundaryNode.InnerText).ToString("dd/MM/yyyy HH:mm:ss") 
        } else { "" }

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
    elseif ($trigger.Name -eq "TimeTrigger")
	{
        $startBoundaryNode = $trigger.SelectSingleNode("t:StartBoundary", $ns)
        $formattedStartBoundary = if ($startBoundaryNode) { 
            [DateTime]::Parse($startBoundaryNode.InnerText).ToString("dd/MM/yyyy HH:mm:ss") 
        } else { "" }
        $triggerType = "One Time"
        $detail = "At $formattedStartBoundary"
    }

        # Store trigger details
        $triggerColumns["TriggerType_$triggerIndex"] = $triggerType
        $triggerColumns["StartBoundary_$triggerIndex"] = $formattedStartBoundary
        $triggerColumns["Detail_$triggerIndex"] = $detail

        # Collect all trigger keys dynamically
        if (-not $allTriggerKeys.Contains("TriggerType_$triggerIndex")) {
            $allTriggerKeys += "TriggerType_$triggerIndex", "StartBoundary_$triggerIndex", "Detail_$triggerIndex"
        }

        $triggerIndex++
    }

    # Merge Data into Task Object
    $result = [ordered]@{
        Name        = $taskName
		Status      = $taskStatus
        IPV4        = $ipv4 
        HostName    = $hostname 
        Path        = $taskPath
        SourceFile  = $xmlFile.FullName
    }

    # Add all trigger columns
    foreach ($key in $allTriggerKeys) {
        if ($triggerColumns.ContainsKey($key)) {
            $result[$key] = $triggerColumns[$key]
        } else {
            $result[$key] = ""
        }
    }

    # Add all action columns
    foreach ($key in $allActionKeys) {
        if ($actionColumns.ContainsKey($key)) {
            $result[$key] = $actionColumns[$key]
        } else {
            $result[$key] = ""
        }
    }

    # Add the result to the array
    $results += New-Object PSObject -Property $result
}

# Ensure all results have the same columns before exporting
$allKeys = @()
foreach ($item in $results) {
    $allKeys += $item.PSObject.Properties.Name
}
$allKeys = $allKeys | Sort-Object -Unique

# Reorder columns
$finalColumns = @("Name", "Status", "IPV4", "HostName", "Path", "SourceFile") + 
                ($allKeys | Where-Object { $_ -match "^TriggerType_\d+" }) +
                ($allKeys | Where-Object { $_ -match "^StartBoundary_\d+" }) +
                ($allKeys | Where-Object { $_ -match "^Detail_\d+" }) +
                ($allKeys | Where-Object { $_ -match "^Command_\d+" }) +
                ($allKeys | Where-Object { $_ -match "^Arguments_\d+" }) +
                ($allKeys | Where-Object { $_ -match "^WorkingDirectory_\d+" })

# Export to CSV (forcing correct column order)
$results | Select-Object $finalColumns | Export-Csv $outputCsv -NoTypeInformation -Encoding UTF8
Write-Host "Extraction completed. Output saved to $outputCsv" -ForegroundColor Green
