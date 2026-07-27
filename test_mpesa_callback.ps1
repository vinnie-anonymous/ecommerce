# test_mpesa_callback.ps1

param(
    [string]$NgrokUrl = "https://YOUR-NGROK.ngrok.io"  # Change this to your actual URL
)

Write-Host "Testing M-PESA Callback at: $NgrokUrl" -ForegroundColor Cyan

# Create the callback payload
$body = @{
    Body = @{
        stkCallback = @{
            MerchantRequestID = "MERCHANT-$(Get-Date -Format 'yyyyMMddHHmmss')"
            CheckoutRequestID = "ws_CO_$(Get-Date -Format 'yyyyMMddHHmmss')"
            ResultCode = 0
            ResultDesc = "The service request is processed successfully."
            CallbackMetadata = @{
                Item = @(
                    @{ Name = "Amount"; Value = 1500 },
                    @{ Name = "MpesaReceiptNumber"; Value = "QGH7$(Get-Random -Minimum 10000 -Maximum 99999)" },
                    @{ Name = "TransactionDate"; Value = (Get-Date -Format 'yyyyMMddHHmmss') },
                    @{ Name = "PhoneNumber"; Value = "254708374149" }
                )
            }
        }
    }
} | ConvertTo-Json -Depth 10

Write-Host "Sending callback with payload:" -ForegroundColor Yellow
Write-Host $body -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "$NgrokUrl/payments/mpesa/callback/" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "Response received:" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "Error occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    }
}