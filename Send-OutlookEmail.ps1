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
        [string]                          $Cc  = "",
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

    $mail.To      = $To
    $mail.Subject = $Subject
    $mail.Cc      = $Cc
    $mail.Bcc     = $Bcc

    if ($IsHtml) {
        $mail.HTMLBody = $Body
    } else {
        $mail.Body = $Body
    }

    # ── Attachments ───────────────────────────────────────────────────────────
    foreach ($path in $Attachments) {
        if (Test-Path $path) {
            $mail.Attachments.Add($path) | Out-Null
        } else {
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

Send-OutlookEmail `
    -To      "er.shiva.sunar@gmail.com" `
    -Subject "VFS France Visa Slot Found" `
    -Body    "VFS France Visa Slot Found"

# ─────────────────────────────────────────────────────────────────────────────
# USAGE EXAMPLES  (remove the <# ... #> block comment markers to run them)
# ─────────────────────────────────────────────────────────────────────────────
<#

# Basic plain-text email
# Send-OutlookEmail `
#     -To      "someone@example.com" `
#     -Subject "Test email" `
#     -Body    "This is a plain text test email."

# HTML email with CC
Send-OutlookEmail `
    -To      "someone@example.com" `
    -Cc      "manager@example.com" `
    -Subject "Weekly Report" `
    -Body    "<h2>Report</h2><p>Please find this week's summary below.</p>" `
    -IsHtml

# Email with attachments
Send-OutlookEmail `
    -To          "someone@example.com" `
    -Subject     "Files attached" `
    -Body        "See attached files." `
    -Attachments "C:\Docs\report.pdf", "C:\Docs\data.xlsx"

#>
