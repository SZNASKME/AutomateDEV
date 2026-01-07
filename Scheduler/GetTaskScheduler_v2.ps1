<#
.SYNOPSIS
    Export Windows Task Scheduler to XML and Excel with all possible fields

.DESCRIPTION
    This script exports all scheduled tasks to XML files preserving folder structure,
    then converts them to Excel with comprehensive field extraction.

.PARAMETER xmlPath
    Path where XML files will be exported (default: D:\Task_Scheduler_Export\)

.PARAMETER outputExcel
    Path for output Excel file (default: D:\Task_Scheduler_Export\TaskScheduler_Report.xlsx)

.PARAMETER outputCsv
    Path for output CSV file (default: D:\Task_Scheduler_Export\TaskScheduler_Report.csv)

.PARAMETER targetPath
    Root path of tasks to export (default: "\" for all tasks)

.PARAMETER reSub
    Include subfolders recursively (Y/N, default: Y)

.PARAMETER exportFormat
    Output format: CSV, XLSX, or BOTH (default: BOTH)

.EXAMPLE
    .\GetTaskScheduler_v2.ps1 -xmlPath "C:\Exports" -targetPath "\Microsoft\" -reSub "N"

.NOTES
    Author: AutomateDEV
    Date: January 6, 2026
    Version: 2.0
    
    Update History:
    - 06/01/2026: Complete rewrite with all fields extraction and Excel support
    - 30/04/2025: Add field task status
#>

param( 
    [string]$xmlPath = "D:\Task_Scheduler_Export_v2\",   
    [string]$outputExcel = "D:\Task_Scheduler_Export_v2\TaskScheduler_Report.xlsx",
    [string]$outputCsv = "D:\Task_Scheduler_Export_v2\TaskScheduler_Report.csv", 
    [string]$targetPath = "\",                 
    [string]$reSub = "Y",
    [ValidateSet("CSV", "XLSX", "BOTH")]
    [string]$exportFormat = "BOTH"
)

# Check if ImportExcel module is available for XLSX export
$importExcelAvailable = $false
if ($exportFormat -eq "XLSX" -or $exportFormat -eq "BOTH") {
    if (Get-Module -ListAvailable -Name ImportExcel) {
        Import-Module ImportExcel
        $importExcelAvailable = $true
        Write-Host "ImportExcel module loaded successfully" -ForegroundColor Green
    } else {
        Write-Warning "ImportExcel module not found. Install it with: Install-Module -Name ImportExcel"
        if ($exportFormat -eq "XLSX") {
            Write-Host "Switching to CSV export instead" -ForegroundColor Yellow
            $exportFormat = "CSV"
        } else {
            Write-Host "Will export to CSV only" -ForegroundColor Yellow
            $exportFormat = "CSV"
        }
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Task Scheduler Export Tool v2.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

#region Helper Functions
function Convert-TaskResult {
    param([string]$resultCode)
    
    if ($resultCode -eq "" -or $resultCode -eq "Not Available") { return $resultCode }
    
    $errorCodes = @{
        "0" = "Success (0x0)"
        "0x0" = "Success (0x0)"
        "1" = "Incorrect function called (0x1)"
        "2" = "File not found (0x2)"
        "10" = "Environment incorrect (0xA)"
        "267008" = "Task has not yet run (0x41300)"
        "267009" = "Task is currently running (0x41301)"
        "267010" = "Task is disabled (0x41302)"
        "267011" = "Task has not been run yet (0x41303)"
        "267012" = "No valid triggers (0x41304)"
        "267014" = "Event trigger with no subscription (0x41306)"
        "2147750687" = "Task not scheduled (0x8004131F)"
        "2147943645" = "Access denied (0x80070005)"
        "2147942402" = "File not found (0x80070002)"
        "2147943711" = "Element not found (0x80070490)"
        "2147942667" = "Logon failure (0x8007052E)"
        "2147942512" = "Task canceled by user (0x800704C7)"
        "2147943623" = "Instance not found (0x80070439)"
        "2147944313" = "Service unavailable (0x80072EE7)"
        "2147549183" = "Object not found (0x8004021F)"
        "3221225786" = "Application terminated (0xC000013A)"
        "-2147024891" = "Access denied (0x80070005)"
    }
    
    if ($errorCodes.ContainsKey($resultCode)) {
        return $errorCodes[$resultCode]
    } elseif ($errorCodes.ContainsKey($resultCode.ToUpper())) {
        return $errorCodes[$resultCode.ToUpper()]
    } else {
        return "Unknown Result ($resultCode)"
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

function Convert-Priority {
    param([string]$priority)
    
    if ([string]::IsNullOrWhiteSpace($priority)) { return "" }
    
    switch ($priority) {
        "0" { return "Critical (0)" }
        "1" { return "Highest (1)" }
        "2" { return "Above Normal (2)" }
        "3" { return "Above Normal (3)" }
        "4" { return "Normal (4)" }
        "5" { return "Normal (5)" }
        "6" { return "Normal (6)" }
        "7" { return "Below Normal (7)" }
        "8" { return "Below Normal (8)" }
        "9" { return "Lowest (9)" }
        "10" { return "Idle (10)" }
        default { return "Priority $priority" }
    }
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

function Convert-LogonType {
    param([string]$logonType)
    
    if ([string]::IsNullOrWhiteSpace($logonType)) { return "" }
    
    switch ($logonType) {
        "InteractiveToken" { return "Interactive" }
        "Password" { return "Password" }
        "S4U" { return "Run whether user is logged on or not" }
        "InteractiveTokenOrPassword" { return "Interactive or Password" }
        "ServiceAccount" { return "Service Account" }
        default { return $logonType }
    }
}

function Convert-RunLevel {
    param([string]$runLevel)
    
    if ([string]::IsNullOrWhiteSpace($runLevel)) { return "" }
    
    switch ($runLevel) {
        "LeastPrivilege" { return "Normal (Least Privilege)" }
        "HighestAvailable" { return "Run with highest privileges" }
        default { return $runLevel }
    }
}

function Convert-MultipleInstancesPolicy {
    param([string]$policy)
    
    if ([string]::IsNullOrWhiteSpace($policy)) { return "" }
    
    switch ($policy) {
        "IgnoreNew" { return "Do not start a new instance" }
        "Parallel" { return "Run a new instance in parallel" }
        "Queue" { return "Queue a new instance" }
        "StopExisting" { return "Stop the existing instance" }
        default { return $policy }
    }
}
#endregion

#region Step 1: Export Task Scheduler to XML
Write-Host "[Step 1/2] Exporting tasks to XML..." -ForegroundColor Yellow

if (-not (Test-Path -Path $xmlPath)) {
    New-Item -ItemType Directory -Path $xmlPath | Out-Null
    Write-Host "  Created export folder: $xmlPath" -ForegroundColor Green
}

# Retrieve tasks based on recursion setting
if ($reSub -eq "N") {
    $tasks = Get-ScheduledTask | Where-Object { $_.TaskPath -eq $targetPath }
} else {
    $tasks = Get-ScheduledTask | Where-Object { $_.TaskPath -like "$targetPath*" }
}
Write-Host "  Found $($tasks.Count) tasks under $targetPath" -ForegroundColor Cyan

$exportedCount = 0
$failedCount = 0

foreach ($task in $tasks) {
    $taskName = $task.TaskName
    $taskFullPath = $task.TaskPath
    $relativePath = $taskFullPath.TrimStart("\").TrimEnd("\")  
    $taskStatus = $task.State
    
    if ($relativePath -eq "") { $relativePath = "Root" }

    $exportFolder = Join-Path $xmlPath $relativePath
    if (-not (Test-Path -Path $exportFolder)) {
        New-Item -ItemType Directory -Path $exportFolder | Out-Null
    }

    try {
        $taskXML = Export-ScheduledTask -TaskName $taskName -TaskPath $taskFullPath
        $xmlFile = Join-Path $exportFolder "$taskName.xml"
        $taskXML | Out-File $xmlFile -Encoding UTF8
        
        # Load the saved XML and add custom fields
        [xml]$xmlDoc = Get-Content $xmlFile

        # Add TaskStatus node
        $statusNode = $xmlDoc.CreateElement("TaskStatus", $xmlDoc.DocumentElement.NamespaceURI)
        $statusNode.InnerText = $taskStatus.ToString()
        $importedNode = $xmlDoc.ImportNode($statusNode, $true)
        $xmlDoc.DocumentElement.AppendChild($importedNode) | Out-Null

        # Add LastRunTime if available
        if ($task.LastRunTime) {
            $lastRunNode = $xmlDoc.CreateElement("LastRunTime", $xmlDoc.DocumentElement.NamespaceURI)
            $lastRunNode.InnerText = $task.LastRunTime.ToString("yyyy-MM-ddTHH:mm:ss")
            $importedLastRun = $xmlDoc.ImportNode($lastRunNode, $true)
            $xmlDoc.DocumentElement.AppendChild($importedLastRun) | Out-Null
        }

        # Add NextRunTime if available
        if ($task.NextRunTime) {
            $nextRunNode = $xmlDoc.CreateElement("NextRunTime", $xmlDoc.DocumentElement.NamespaceURI)
            $nextRunNode.InnerText = $task.NextRunTime.ToString("yyyy-MM-ddTHH:mm:ss")
            $importedNextRun = $xmlDoc.ImportNode($nextRunNode, $true)
            $xmlDoc.DocumentElement.AppendChild($importedNextRun) | Out-Null
        }

        # Add LastTaskResult if available
        if ($null -ne $task.LastTaskResult) {
            $lastResultNode = $xmlDoc.CreateElement("LastTaskResult", $xmlDoc.DocumentElement.NamespaceURI)
            $lastResultNode.InnerText = $task.LastTaskResult.ToString()
            $importedLastResult = $xmlDoc.ImportNode($lastResultNode, $true)
            $xmlDoc.DocumentElement.AppendChild($importedLastResult) | Out-Null
        }

        # Add NumberOfMissedRuns if available
        if ($null -ne $task.NumberOfMissedRuns) {
            $missedRunsNode = $xmlDoc.CreateElement("NumberOfMissedRuns", $xmlDoc.DocumentElement.NamespaceURI)
            $missedRunsNode.InnerText = $task.NumberOfMissedRuns.ToString()
            $importedMissedRuns = $xmlDoc.ImportNode($missedRunsNode, $true)
            $xmlDoc.DocumentElement.AppendChild($importedMissedRuns) | Out-Null
        }

        $xmlDoc.Save($xmlFile)
        $exportedCount++
        
        if ($exportedCount % 50 -eq 0) {
            Write-Host "  Exported $exportedCount tasks..." -ForegroundColor Gray
        }
    }
    catch {
        Write-Warning "  Failed to export task: $taskName from path $taskFullPath - $($_.Exception.Message)"
        $failedCount++
    }
}

Write-Host "  Exported $exportedCount tasks successfully" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "  Failed to export $failedCount tasks" -ForegroundColor Red
}
Write-Host ""
#endregion

#region Step 2: Extract XML to Excel/CSV
Write-Host "[Step 2/2] Converting XML to Excel/CSV format..." -ForegroundColor Yellow

$xmlFiles = Get-ChildItem -Path $xmlPath -Filter "*.xml" -Recurse
$results = @()
$allActionKeys = @()

# Get system information
$ipv4 = (Get-NetIPAddress | Where-Object { 
    $_.AddressFamily -eq "IPv4" -and 
    $_.InterfaceAlias -notlike "*Loopback*" -and 
    $_.IPAddress -notmatch "^169\.254\."
}).IPAddress -join ", "

$hostname = $env:COMPUTERNAME
$computerInfo = Get-ComputerInfo -Property CsName, OsName, OsVersion -ErrorAction SilentlyContinue

Write-Host "  Processing $($xmlFiles.Count) XML files..." -ForegroundColor Cyan

# First pass: Determine max actions
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

# Second pass: Extract all task data
$processedCount = 0
foreach ($xmlFile in $xmlFiles) {
    [xml]$xml = Get-Content $xmlFile.FullName -ErrorAction SilentlyContinue
    $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
    $ns.AddNamespace("t", "http://schemas.microsoft.com/windows/2004/02/mit/task")

    # Basic Task Information
    $uriNode = $xml.SelectSingleNode("//t:RegistrationInfo/t:URI", $ns)
    $uri = if ($uriNode) { $uriNode.InnerText.Trim() } else { "Unknown" }
    $taskName = ($uri -split '\\')[-1]  
    $taskPath = ($uri -replace "\\$taskName$", "") 
    
    if ($taskPath -ne "") { $taskPath += "\" }  

    # Task Status and Runtime Information
    $taskStatus = if ($xml.Task.TaskStatus) { $xml.Task.TaskStatus } else { "Unknown" }
    $lastRunTime = if ($xml.Task.LastRunTime) { $xml.Task.LastRunTime } else { "Never" }
    $nextRunTime = if ($xml.Task.NextRunTime) { $xml.Task.NextRunTime } else { "Not Scheduled" }
    $lastTaskResult = if ($null -ne $xml.Task.LastTaskResult) { Convert-TaskResult $xml.Task.LastTaskResult } else { "Not Available" }
    $numberOfMissedRuns = if ($null -ne $xml.Task.NumberOfMissedRuns) { $xml.Task.NumberOfMissedRuns } else { "0" }

    # Registration Information
    $author = $xml.SelectSingleNode("//t:RegistrationInfo/t:Author", $ns)
    $authorValue = if ($author) { $author.InnerText.Trim() } else { "" }
    
    $description = $xml.SelectSingleNode("//t:RegistrationInfo/t:Description", $ns)
    $descriptionValue = if ($description) { $description.InnerText.Trim() } else { "" }
    
    $date = $xml.SelectSingleNode("//t:RegistrationInfo/t:Date", $ns)
    $dateValue = if ($date) { 
        try { [DateTime]::Parse($date.InnerText).ToString("dd/MM/yyyy HH:mm:ss") } 
        catch { $date.InnerText } 
    } else { "" }
    
    $version = $xml.SelectSingleNode("//t:RegistrationInfo/t:Version", $ns)
    $versionValue = if ($version) { $version.InnerText.Trim() } else { "" }

    # Principal (Security) Information
    $principal = $xml.SelectSingleNode("//t:Principals/t:Principal", $ns)
    $userId = if ($principal -and $principal.UserId) { $principal.UserId } else { "" }
    $logonType = if ($principal -and $principal.LogonType) { Convert-LogonType $principal.LogonType } else { "" }
    $runLevel = if ($principal -and $principal.RunLevel) { Convert-RunLevel $principal.RunLevel } else { "" }

    # Settings
    $settings = $xml.SelectSingleNode("//t:Settings", $ns)
    $multipleInstancesPolicy = if ($settings -and $settings.MultipleInstancesPolicy) { Convert-MultipleInstancesPolicy $settings.MultipleInstancesPolicy } else { "" }
    $disallowStartIfOnBatteries = if ($settings -and $settings.DisallowStartIfOnBatteries) { Convert-Boolean $settings.DisallowStartIfOnBatteries } else { "" }
    $stopIfGoingOnBatteries = if ($settings -and $settings.StopIfGoingOnBatteries) { Convert-Boolean $settings.StopIfGoingOnBatteries } else { "" }
    $allowHardTerminate = if ($settings -and $settings.AllowHardTerminate) { Convert-Boolean $settings.AllowHardTerminate } else { "" }
    $startWhenAvailable = if ($settings -and $settings.StartWhenAvailable) { Convert-Boolean $settings.StartWhenAvailable } else { "" }
    $runOnlyIfNetworkAvailable = if ($settings -and $settings.RunOnlyIfNetworkAvailable) { Convert-Boolean $settings.RunOnlyIfNetworkAvailable } else { "" }
    $allowStartOnDemand = if ($settings -and $settings.AllowStartOnDemand) { Convert-Boolean $settings.AllowStartOnDemand } else { "" }
    $enabled = if ($settings -and $settings.Enabled) { Convert-Boolean $settings.Enabled } else { "" }
    $hidden = if ($settings -and $settings.Hidden) { Convert-Boolean $settings.Hidden } else { "" }
    $runOnlyIfIdle = if ($settings -and $settings.RunOnlyIfIdle) { Convert-Boolean $settings.RunOnlyIfIdle } else { "" }
    $wakeToRun = if ($settings -and $settings.WakeToRun) { Convert-Boolean $settings.WakeToRun } else { "" }
    $executionTimeLimit = if ($settings -and $settings.ExecutionTimeLimit) { Convert-Duration $settings.ExecutionTimeLimit } else { "" }
    $priority = if ($settings -and $settings.Priority) { Convert-Priority $settings.Priority } else { "" }

    # Idle Settings
    $idleSettings = $xml.SelectSingleNode("//t:Settings/t:IdleSettings", $ns)
    $idleDuration = if ($idleSettings -and $idleSettings.Duration) { Convert-Duration $idleSettings.Duration } else { "" }
    $idleWaitTimeout = if ($idleSettings -and $idleSettings.WaitTimeout) { Convert-Duration $idleSettings.WaitTimeout } else { "" }

    # Extract Actions
    $actions = $xml.Task.Actions.Exec
    $actionColumns = @{}
    $actionIndex = 1
    foreach ($action in $actions) {
        $command = if ($action.Command) { $action.Command.Trim() } else { "" }
        $arguments = if ($action.Arguments -and $action.Arguments.Trim() -ne "") { $action.Arguments.Trim() } else { "" }
        $workingDirectory = if ($action.WorkingDirectory) { $action.WorkingDirectory.Trim() } else { "" }
        
        $actionColumns["Command_$actionIndex"] = $command
        $actionColumns["Arguments_$actionIndex"] = $arguments
        $actionColumns["WorkingDirectory_$actionIndex"] = $workingDirectory
        $actionIndex++
    }

    # Extract Triggers (Create one row per trigger)
    $triggers = $xml.SelectNodes("//t:Triggers/*", $ns)

    if (-not $triggers -or $triggers.Count -eq 0) {
        # No triggers - create single row
        $result = [ordered]@{
            # System Information
            HostName                      = $hostname
            IPv4                          = $ipv4
            OSName                        = if ($computerInfo) { $computerInfo.OsName } else { "" }
            OSVersion                     = if ($computerInfo) { $computerInfo.OsVersion } else { "" }
            
            # Task Basic Information
            TaskName                      = $taskName
            TaskPath                      = $taskPath
            TaskFullPath                  = $uri
            TaskStatus                    = $taskStatus
            
            # Runtime Information
            LastRunTime                   = $lastRunTime
            NextRunTime                   = $nextRunTime
            LastTaskResult                = $lastTaskResult
            NumberOfMissedRuns            = $numberOfMissedRuns
            
            # Registration Information
            Author                        = $authorValue
            Description                   = $descriptionValue
            RegistrationDate              = $dateValue
            Version                       = $versionValue
            
            # Security Information
            UserId                        = $userId
            LogonType                     = $logonType
            RunLevel                      = $runLevel
            
            # Trigger Information
            TriggerType                   = ""
            TriggerStartBoundary          = ""
            TriggerEndBoundary            = ""
            TriggerEnabled                = ""
            TriggerDetail                 = ""
            TriggerRepetitionInterval     = ""
            TriggerRepetitionDuration     = ""
            TriggerDelay                  = ""
            TriggerRandomDelay            = ""
            
            # Settings
            MultipleInstancesPolicy       = $multipleInstancesPolicy
            DisallowStartIfOnBatteries    = $disallowStartIfOnBatteries
            StopIfGoingOnBatteries        = $stopIfGoingOnBatteries
            AllowHardTerminate            = $allowHardTerminate
            StartWhenAvailable            = $startWhenAvailable
            RunOnlyIfNetworkAvailable     = $runOnlyIfNetworkAvailable
            AllowStartOnDemand            = $allowStartOnDemand
            Enabled                       = $enabled
            Hidden                        = $hidden
            RunOnlyIfIdle                 = $runOnlyIfIdle
            WakeToRun                     = $wakeToRun
            ExecutionTimeLimit            = $executionTimeLimit
            Priority                      = $priority
            
            # Idle Settings
            IdleDuration                  = $idleDuration
            IdleWaitTimeout               = $idleWaitTimeout
            
            # Source
            SourceXMLFile                 = $xmlFile.FullName
        }

        # Add action columns
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
        # Multiple triggers - create one row per trigger
        foreach ($trigger in $triggers) {
            $triggerType = $trigger.LocalName
            $triggerEnabled = if ($trigger.Enabled) { Convert-Boolean $trigger.Enabled } else { "Yes" }
            $triggerExecutionTimeLimit = if ($trigger.ExecutionTimeLimit) { Convert-Duration $trigger.ExecutionTimeLimit } else { "" }
            
            $startBoundaryNode = $trigger.SelectSingleNode("t:StartBoundary", $ns)
            $formattedStartBoundary = if ($startBoundaryNode) { 
                try { [DateTime]::Parse($startBoundaryNode.InnerText).ToString("dd/MM/yyyy HH:mm:ss") } 
                catch { $startBoundaryNode.InnerText }
            } else { "" }

            $endBoundaryNode = $trigger.SelectSingleNode("t:EndBoundary", $ns)
            $formattedEndBoundary = if ($endBoundaryNode) { 
                try { [DateTime]::Parse($endBoundaryNode.InnerText).ToString("dd/MM/yyyy HH:mm:ss") } 
                catch { $endBoundaryNode.InnerText }
            } else { "" }

            # Repetition
            $repetitionNode = $trigger.SelectSingleNode("t:Repetition", $ns)
            $repetitionInterval = if ($repetitionNode -and $repetitionNode.Interval) { Convert-Duration $repetitionNode.Interval } else { "" }
            $repetitionDuration = if ($repetitionNode -and $repetitionNode.Duration) { Convert-Duration $repetitionNode.Duration } else { "" }
            $repetitionStopAtDurationEnd = if ($repetitionNode -and $repetitionNode.StopAtDurationEnd) { Convert-Boolean $repetitionNode.StopAtDurationEnd } else { "" }

            # Delays
            $delayNode = $trigger.SelectSingleNode("t:Delay", $ns)
            $delay = if ($delayNode) { Convert-Duration $delayNode.InnerText } else { "" }

            $randomDelayNode = $trigger.SelectSingleNode("t:RandomDelay", $ns)
            $randomDelay = if ($randomDelayNode) { Convert-Duration $randomDelayNode.InnerText } else { "" }

            $detail = ""

            # Parse trigger details based on type
            if ($triggerType -eq "CalendarTrigger") {
                if ($trigger.SelectSingleNode("t:ScheduleByDay", $ns)) {
                    $daysInterval = $trigger.ScheduleByDay.DaysInterval
                    $detail = "Daily - Every $daysInterval day(s) at $formattedStartBoundary"
                }
                elseif ($trigger.SelectSingleNode("t:ScheduleByWeek", $ns)) {
                    $daysString = ($trigger.SelectSingleNode("t:ScheduleByWeek/t:DaysOfWeek", $ns).ChildNodes | ForEach-Object { $_.Name }) -join ','
                    $weeksIntervalNode = $trigger.SelectSingleNode("t:ScheduleByWeek/t:WeeksInterval", $ns)
                    $weeksInterval = if ($weeksIntervalNode) { $weeksIntervalNode.InnerText } else { "1" }
                    $detail = "Weekly - Every $daysString of every $weeksInterval week(s) at $formattedStartBoundary"
                }
                elseif ($trigger.SelectSingleNode("t:ScheduleByMonth", $ns)) {
                    $monthsString = ($trigger.SelectSingleNode("t:ScheduleByMonth/t:Months", $ns).ChildNodes | ForEach-Object { $_.Name }) -join ','
                    $daysOfMonth = $trigger.SelectSingleNode("t:ScheduleByMonth/t:DaysOfMonth", $ns)
                    if ($daysOfMonth) {
                        $daysString = ($daysOfMonth.ChildNodes | ForEach-Object { $_.InnerText }) -join ','
                        $detail = "Monthly - On day(s) $daysString of $monthsString at $formattedStartBoundary"
                    } else {
                        $detail = "Monthly - $monthsString at $formattedStartBoundary"
                    }
                }
                elseif ($trigger.SelectSingleNode("t:ScheduleByMonthDayOfWeek", $ns)) {
                    $weeksOfMonth = ($trigger.SelectSingleNode("t:ScheduleByMonthDayOfWeek/t:Weeks", $ns).ChildNodes | ForEach-Object { $_.Name }) -join ','
                    $daysOfWeek = ($trigger.SelectSingleNode("t:ScheduleByMonthDayOfWeek/t:DaysOfWeek", $ns).ChildNodes | ForEach-Object { $_.Name }) -join ','
                    $monthsString = ($trigger.SelectSingleNode("t:ScheduleByMonthDayOfWeek/t:Months", $ns).ChildNodes | ForEach-Object { $_.Name }) -join ','
                    $detail = "Monthly - On $weeksOfMonth $daysOfWeek of $monthsString at $formattedStartBoundary"
                }
                else {
                    $detail = "One time at $formattedStartBoundary"
                }
            }
            elseif ($triggerType -eq "BootTrigger") {
                $detail = "At system startup"
                if ($delay) { $detail += " (Delay: $delay)" }
            }
            elseif ($triggerType -eq "LogonTrigger") {
                $userIdNode = $trigger.SelectSingleNode("t:UserId", $ns)
                $triggerUserId = if ($userIdNode) { $userIdNode.InnerText } else { "Any user" }
                $detail = "At logon of $triggerUserId"
                if ($delay) { $detail += " (Delay: $delay)" }
            }
            elseif ($triggerType -eq "EventTrigger") {
                $subscriptionNode = $trigger.SelectSingleNode("t:Subscription", $ns)
                $subscription = if ($subscriptionNode) { $subscriptionNode.InnerText } else { "" }
                $detail = "On event: $subscription"
                if ($delay) { $detail += " (Delay: $delay)" }
            }
            elseif ($triggerType -eq "TimeTrigger") {
                $detail = "One time at $formattedStartBoundary"
            }
            elseif ($triggerType -eq "IdleTrigger") {
                $detail = "On idle"
            }
            elseif ($triggerType -eq "RegistrationTrigger") {
                $detail = "On registration"
                if ($delay) { $detail += " (Delay: $delay)" }
            }
            elseif ($triggerType -eq "SessionStateChangeTrigger") {
                $stateChangeNode = $trigger.SelectSingleNode("t:StateChange", $ns)
                $stateChange = if ($stateChangeNode) { $stateChangeNode.InnerText } else { "" }
                $userIdNode = $trigger.SelectSingleNode("t:UserId", $ns)
                $triggerUserId = if ($userIdNode) { $userIdNode.InnerText } else { "Any user" }
                $detail = "On session state change: $stateChange for $triggerUserId"
                if ($delay) { $detail += " (Delay: $delay)" }
            }
            else {
                $detail = "Unknown trigger type: $triggerType"
            }

            $result = [ordered]@{
                # System Information
                HostName                      = $hostname
                IPv4                          = $ipv4
                OSName                        = if ($computerInfo) { $computerInfo.OsName } else { "" }
                OSVersion                     = if ($computerInfo) { $computerInfo.OsVersion } else { "" }
                
                # Task Basic Information
                TaskName                      = $taskName
                TaskPath                      = $taskPath
                TaskFullPath                  = $uri
                TaskStatus                    = $taskStatus
                
                # Runtime Information
                LastRunTime                   = $lastRunTime
                NextRunTime                   = $nextRunTime
                LastTaskResult                = $lastTaskResult
                NumberOfMissedRuns            = $numberOfMissedRuns
                
                # Registration Information
                Author                        = $authorValue
                Description                   = $descriptionValue
                RegistrationDate              = $dateValue
                Version                       = $versionValue
                
                # Security Information
                UserId                        = $userId
                LogonType                     = $logonType
                RunLevel                      = $runLevel
                
                # Trigger Information
                TriggerType                   = $triggerType
                TriggerStartBoundary          = $formattedStartBoundary
                TriggerEndBoundary            = $formattedEndBoundary
                TriggerEnabled                = $triggerEnabled
                TriggerDetail                 = $detail
                TriggerRepetitionInterval     = $repetitionInterval
                TriggerRepetitionDuration     = $repetitionDuration
                TriggerDelay                  = $delay
                TriggerRandomDelay            = $randomDelay
                
                # Settings
                MultipleInstancesPolicy       = $multipleInstancesPolicy
                DisallowStartIfOnBatteries    = $disallowStartIfOnBatteries
                StopIfGoingOnBatteries        = $stopIfGoingOnBatteries
                AllowHardTerminate            = $allowHardTerminate
                StartWhenAvailable            = $startWhenAvailable
                RunOnlyIfNetworkAvailable     = $runOnlyIfNetworkAvailable
                AllowStartOnDemand            = $allowStartOnDemand
                Enabled                       = $enabled
                Hidden                        = $hidden
                RunOnlyIfIdle                 = $runOnlyIfIdle
                WakeToRun                     = $wakeToRun
                ExecutionTimeLimit            = $executionTimeLimit
                Priority                      = $priority
                
                # Idle Settings
                IdleDuration                  = $idleDuration
                IdleWaitTimeout               = $idleWaitTimeout
                
                # Source
                SourceXMLFile                 = $xmlFile.FullName
            }

            # Add action columns
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

    $processedCount++
    if ($processedCount % 50 -eq 0) {
        Write-Host "  Processed $processedCount files..." -ForegroundColor Gray
    }
}

Write-Host "  Processed $processedCount XML files" -ForegroundColor Green
Write-Host ""
#endregion

#region Step 3: Export Results
Write-Host "[Step 3/3] Exporting results..." -ForegroundColor Yellow

if ($results.Count -eq 0) {
    Write-Warning "No data to export!"
    exit
}

# Export to CSV
if ($exportFormat -eq "CSV" -or $exportFormat -eq "BOTH") {
    try {
        $results | Export-Csv -Path $outputCsv -NoTypeInformation -Encoding UTF8
        Write-Host "  ✓ CSV exported successfully" -ForegroundColor Green
        Write-Host "    File: $outputCsv" -ForegroundColor Gray
        Write-Host "    Records: $($results.Count)" -ForegroundColor Gray
    }
    catch {
        Write-Error "Failed to export CSV: $($_.Exception.Message)"
    }
}

# Export to Excel
if (($exportFormat -eq "XLSX" -or $exportFormat -eq "BOTH") -and $importExcelAvailable) {
    try {
        # Create Excel with formatting
        $excelParams = @{
            Path          = $outputExcel
            WorksheetName = "TaskScheduler"
            AutoSize      = $true
            FreezeTopRow  = $true
            BoldTopRow    = $true
            TableStyle    = "Medium2"
        }
        
        $results | Export-Excel @excelParams
        
        Write-Host "  ✓ Excel exported successfully" -ForegroundColor Green
        Write-Host "    File: $outputExcel" -ForegroundColor Gray
        Write-Host "    Records: $($results.Count)" -ForegroundColor Gray
    }
    catch {
        Write-Error "Failed to export Excel: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Export completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  - XML files: $xmlPath" -ForegroundColor White
Write-Host "  - Tasks exported: $exportedCount" -ForegroundColor White
Write-Host "  - Records in report: $($results.Count)" -ForegroundColor White
if ($exportFormat -eq "CSV" -or $exportFormat -eq "BOTH") {
    Write-Host "  - CSV file: $outputCsv" -ForegroundColor White
}
if (($exportFormat -eq "XLSX" -or $exportFormat -eq "BOTH") -and $importExcelAvailable) {
    Write-Host "  - Excel file: $outputExcel" -ForegroundColor White
}
Write-Host ""
#endregion
