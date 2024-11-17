param(
    [string] [Parameter(Mandatory=$true)] $functionAppName,
    [string] [Parameter(Mandatory=$true)] $RG
)

function zipdeploy(){
    param(
        [string]$deployfilepath,
        #[string]$deploymentUrl,
        [string]$RG,
        [string]$functionAppName
    )
    #PowerShell
    $filePath = $deployfilepath
    # $apiUrl = $deploymentUrl
    # $userAgent = "powershell/1.0"
    Connect-AzAccount -Identity -AccountId $managedIdentityClientID
    # $token = ConvertFrom-SecureString (Get-AzAccessToken -AsSecureString).Token -AsPlainText
    # $headers = @{
    #     'Authorization' = "Bearer $token"
    # }
    #Invoke-RestMethod -Uri $apiUrl -Headers $headers -UserAgent $userAgent -Method POST -InFile $filePath -ContentType "multipart/form-data" -Proxy "http://localhost:8080" -SkipCertificateCheck
    #curl -X POST -H "Authorization: Bearer $token" --data-binary $filePath $apiUrl
    az functionapp deployment source config-zip -g $RG -n $functionAppName --src $filePath --build-remote true
}

$filePath = (Get-Location).path+'/deploy.zip'
#$appSvcDeploymentUrl = "https://$functionAppName.scm.azurewebsites.net/api/zipdeploy"

#Read the base64 encoded zip file from the injected environment variable from bicep
$base64file=$env:CONTENT
$zipfile=[System.Convert]::FromBase64String($base64file)
[System.IO.File]::WriteAllBytes($filePath, $zipfile)

zipdeploy -deployfilepath $filePath -RG $RG -functionAppName $functionAppName #-deploymentUrl $appSvcDeploymentUrl