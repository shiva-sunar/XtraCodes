# ─────────────────────────────────────────────────────────────────────────────
# Check-Appointment.ps1
# Polls a Schengen appointment page and stops when slots become available.
# ─────────────────────────────────────────────────────────────────────────────

$Url = "https://schengenappointments.com/in/montreal/france/tourism"
$NoSlotMsg = "No appointments available!"
$Interval = 30*60   # seconds (5 minutes)

# ─────────────────────────────────────────────────────────────────────────────
# Send-OutlookEmail.ps1
# Sends an email using the Outlook Classic desktop app via COM automation.
# Outlook must be installed and a mail account must be configured.
# ─────────────────────────────────────────────────────────────────────────────

function Send-OutlookEmail {
    <#
    .SYNOPSIS
        Sends an email through Outlook Classic using COM automation.

    .PARAMETER To
        Recipient email address. Separate multiple with a semicolon.
        Example: "alice@example.com; bob@example.com"

    .PARAMETER Subject
        Email subject line.

    .PARAMETER Body
        Email body. Plain text by default. Set -IsHtml to send HTML.

    .PARAMETER IsHtml
        Switch. When present, the Body is treated as HTML.

    .PARAMETER Attachments
        Optional array of full file paths to attach.

    .PARAMETER Cc
        Optional CC recipients. Separate multiple with a semicolon.

    .PARAMETER Bcc
        Optional BCC recipients. Separate multiple with a semicolon.

    .EXAMPLE
        Send-OutlookEmail -To "alice@example.com" -Subject "Hello" -Body "Hi there!"

    .EXAMPLE
        Send-OutlookEmail `
            -To      "alice@example.com" `
            -Cc      "manager@example.com" `
            -Subject "Report attached" `
            -Body    "<h2>Please find the report below.</h2>" `
            -IsHtml `
            -Attachments "C:\Reports\Q1.pdf", "C:\Reports\Q2.pdf"
    #>

    [CmdletBinding()]
    param (
        [Parameter(Mandatory)] [string]   $To,
        [Parameter(Mandatory)] [string]   $Subject,
        [Parameter(Mandatory)] [string]   $Body,
        [switch]                          $IsHtml,
        [string[]]                        $Attachments = @(),
        [string]                          $Cc = "",
        [string]                          $Bcc = ""
    )

    # ── Check Outlook is available ────────────────────────────────────────────
    try {
        $outlook = New-Object -ComObject Outlook.Application -ErrorAction Stop
    }
    catch {
        Write-Error "Could not start Outlook. Make sure Outlook Classic is installed and a mail account is configured.`n$_"
        return
    }

    # ── Compose the email ─────────────────────────────────────────────────────
    $mail = $outlook.CreateItem(0)   # 0 = olMailItem

    $mail.To = $To
    $mail.Subject = $Subject
    $mail.Cc = $Cc
    $mail.Bcc = $Bcc

    if ($IsHtml) {
        $mail.HTMLBody = $Body
    }
    else {
        $mail.Body = $Body
    }

    # ── Attachments ───────────────────────────────────────────────────────────
    foreach ($path in $Attachments) {
        if (Test-Path $path) {
            $mail.Attachments.Add($path) | Out-Null
        }
        else {
            Write-Warning "Attachment not found, skipping: $path"
        }
    }

    # ── Send ──────────────────────────────────────────────────────────────────
    try {
        $mail.Send()
        Write-Host "Email sent to: $To" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to send email: $_"
    }
    finally {
        # Release COM objects to avoid Outlook staying locked
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($mail)    | Out-Null
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($outlook) | Out-Null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
    }
}


function Get-TopLevelDivs([string]$html) {
    $divs = [System.Collections.Generic.List[string]]::new()
    $depth = 0
    $start = -1
    $i = 0

    while ($i -lt $html.Length) {
        $remaining = $html.Substring($i)

        if ($remaining -match '(?si)^<div(\s[^>]*)?>') {
            if ($depth -eq 0) { $start = $i }
            $depth++
            $i += $Matches[0].Length
            continue
        }

        if ($remaining -match '(?si)^</div\s*>') {
            $depth--
            if ($depth -eq 0 -and $start -ge 0) {
                $end = $i + $Matches[0].Length
                $divs.Add($html.Substring($start, $end - $start))
                $start = -1
            }
            $i += $Matches[0].Length
            continue
        }

        $i++
    }

    return $divs
}

function Get-TargetText([string]$Url) {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -UserAgent "Mozilla/5.0"
    $html = $response.Content

    # Strip scripts and styles
    $html = $html -replace '(?s)<script[^>]*>.*?</script>', ''
    $html = $html -replace '(?s)<style[^>]*>.*?</style>', ''

    # Extract body
    if ($html -match '(?si)<body[^>]*>(.*)</body>') {
        $bodyHtml = $Matches[1]
    }
    else {
        return $null
    }

    # Get 2nd top-level div inside body  (XPath div[2])
    $outerDivs = Get-TopLevelDivs $bodyHtml
    if ($outerDivs.Count -lt 2) { return $null }

    $secondDiv = $outerDivs[1]

    # Strip outer tag to get its inner HTML
    $innerHtml = $secondDiv -replace '(?si)^<div[^>]*>', '' -replace '(?si)</div\s*>$', ''

    # Get 2nd top-level div inside that  (XPath div[2]/div[2])
    $innerDivs = Get-TopLevelDivs $innerHtml
    if ($innerDivs.Count -lt 2) { return $null }

    $targetDiv = $innerDivs[1]

    # Strip tags and decode entities
    $text = $targetDiv -replace '(?s)<[^>]+>', ' '
    $text = $text -replace '&nbsp;', ' '
    $text = $text -replace '&amp;', '&'
    $text = $text -replace '&lt;', '<'
    $text = $text -replace '&gt;', '>'
    $text = $text -replace '\s+', ' '

    return $text.Trim()
}

# ── Main loop ─────────────────────────────────────────────────────────────────

$attempt = 0

while ($true) {
    $attempt++
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Write-Host ""
    Write-Host "[$timestamp] Attempt #$attempt - Checking URL..." -ForegroundColor Cyan

    try {
        $text = Get-TargetText -Url $Url

        if ($null -eq $text) {
            Write-Host "  WARNING: Target element not found. Page structure may have changed." -ForegroundColor Yellow
            Write-Host "  Retrying in 5 minutes..." -ForegroundColor Gray
            Start-Sleep -Seconds $Interval
        }
        elseif ($text -like "*$NoSlotMsg*") {
            $preview = $text.Substring(0, [Math]::Min(80, $text.Length))
            Write-Host "  No slots yet.  ($preview ...)" -ForegroundColor DarkYellow
            Write-Host "  Waiting 5 minutes before next check..." -ForegroundColor Gray

            for ($i = $Interval; $i -gt 0; $i -= 10) {
                Write-Host "    $i seconds remaining..." -ForegroundColor DarkGray
                Start-Sleep -Seconds ([Math]::Min(10, $i))
            }
        }
        else {
            Write-Host ""
            Write-Host "  SUCCESS - APPOINTMENT SLOT FOUND!" -ForegroundColor Green
            Write-Host "  Content : $text"                   -ForegroundColor Green
            Write-Host ""
            Write-Host "  Book now: $Url"                    -ForegroundColor Green
            Write-Host ""
            Send-OutlookEmail `
                -To      "er.shiva.sunar@gmail.com" `
                -Subject "VFS France Visa Slot Found" `
                -Body    "VFS France Visa Slot Found - $text`nBook now: $Url"
            break
        }
    }
    catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
        Write-Host "  Retrying in 5 minutes..." -ForegroundColor Gray
        Start-Sleep -Seconds $Interval
    }
}