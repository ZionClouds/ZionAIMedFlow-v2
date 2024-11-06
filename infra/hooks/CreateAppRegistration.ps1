param(
    [string] [Parameter(Mandatory=$true)] $AppName
)

Write-Warning "Don't forget to save the output of this command. It contains the secret for the app registration and the AppId."
az ad sp create-for-rbac --name $AppName
