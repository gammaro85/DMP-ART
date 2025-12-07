# PST to JSON Exporter using Outlook PowerShell
# Requires Microsoft Outlook to be installed

$pstPath = Resolve-Path "pzd\pzd.pst"
$outputPath = "pzd\pzd.json"

Write-Host "PST to JSON Exporter (PowerShell)" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host "Input:  $pstPath"
Write-Host "Output: $outputPath"
Write-Host "=" * 70
Write-Host ""

try {
    # Create Outlook application object
    Write-Host "Creating Outlook COM object..." -ForegroundColor Yellow
    $outlook = New-Object -ComObject Outlook.Application
    $namespace = $outlook.GetNamespace("MAPI")

    # Add PST file
    Write-Host "Adding PST file to Outlook..." -ForegroundColor Yellow
    $namespace.AddStore($pstPath)

    # Wait a moment for Outlook to process
    Start-Sleep -Seconds 2

    # Find the PST store
    $pstStore = $null
    foreach ($store in $namespace.Stores) {
        if ($store.FilePath -eq $pstPath) {
            $pstStore = $store
            break
        }
    }

    if ($null -eq $pstStore) {
        Write-Host "Error: Could not find PST store" -ForegroundColor Red
        exit 1
    }

    Write-Host "Found PST store: $($pstStore.DisplayName)" -ForegroundColor Green

    # Initialize data structure
    $data = @{
        file = Split-Path $pstPath -Leaf
        folders = @()
        messages = @()
    }

    # Recursive function to process folders
    function Process-Folder {
        param($folder, $path = "")

        $folderName = $folder.Name
        $currentPath = if ($path) { "$path/$folderName" } else { $folderName }

        Write-Host "Processing: $currentPath ($($folder.Items.Count) items)" -ForegroundColor Gray

        # Add folder info
        $data.folders += @{
            name = $folderName
            path = $currentPath
            num_items = $folder.Items.Count
        }

        # Process messages (limit to first 500 per folder)
        $maxMessages = [Math]::Min($folder.Items.Count, 500)
        for ($i = 1; $i -le $maxMessages; $i++) {
            try {
                $item = $folder.Items.Item($i)

                # Check if it's a mail item
                if ($item.Class -eq 43) {  # olMail = 43
                    $bodyPreview = if ($item.Body.Length -gt 500) {
                        $item.Body.Substring(0, 500) + "..."
                    } else {
                        $item.Body
                    }

                    $data.messages += @{
                        folder = $currentPath
                        subject = $item.Subject
                        sender = $item.SenderName
                        sent_on = $item.SentOn.ToString("yyyy-MM-dd HH:mm:ss")
                        body = $bodyPreview
                    }
                }
            } catch {
                # Skip problematic items
            }
        }

        # Process subfolders
        foreach ($subfolder in $folder.Folders) {
            Process-Folder -folder $subfolder -path $currentPath
        }
    }

    # Start processing from root
    $rootFolder = $pstStore.GetRootFolder()
    Process-Folder -folder $rootFolder

    # Remove PST from Outlook
    Write-Host "Removing PST from Outlook..." -ForegroundColor Yellow
    $namespace.RemoveStore($rootFolder)

    # Convert to JSON and save
    Write-Host "Saving JSON..." -ForegroundColor Yellow
    $jsonContent = $data | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($outputPath, $jsonContent, [System.Text.Encoding]::UTF8)

    Write-Host ""
    Write-Host "Success!" -ForegroundColor Green
    Write-Host "  Folders: $($data.folders.Count)"
    Write-Host "  Messages: $($data.messages.Count)"
    Write-Host "  Output: $outputPath"

} catch {
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red

    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "  1. Make sure Microsoft Outlook is installed"
    Write-Host "  2. Try running PowerShell as Administrator"
    Write-Host "  3. Check if the PST file is not corrupted"
    Write-Host "  4. Use alternative tools like readpst or PST Viewer"
    exit 1
} finally {
    # Cleanup
    if ($outlook) {
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
