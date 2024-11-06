param(
    [string] [Parameter(Mandatory=$true)] $AppId,
    [string] [Parameter(Mandatory=$true)] $ACAFrontEndUrl
)

#$sp = az ad sp create-for-rbac --name $AppName
#$spJson = $sp | convertfrom-json -Depth 100
$spFullJsonApp = az ad app show --id $AppId | convertfrom-json

#$ACAFrontEndUrl = "https://yak-f5tal2iqu5dcc-ca.orangetree-ba843724.eastus.azurecontainerapps.io"

$bodyPatch = @{
	identifierUris = @("api://$($spFullJsonApp.appId)")
	appRoles = @(
		@{
			allowedMemberTypes = @("User")
			description = "Allow Developer access features"
			displayName = "Developer"
			id = "17b4118b-8e4e-42e7-9017-e1865f0d9662"
			isEnabled = $true
			origin = "Application"
			value = "Developer"
		}
	)
	requiredResourceAccess = @(
		@{
			resourceAppId = "00000003-0000-0000-c000-000000000000"
			resourceAccess = @(
				@{
					id = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"
					type = "Scope"
				}
			)
		}
	)
	web = @{
		homePageUrl = "$acaFrontEndUrl"
		redirectUris = @(
			"$acaFrontEndUrl/.auth/login/aad/callback"
		)
		implicitGrantSettings = @{
			enableAccessTokenIssuance = $false
			enableIdTokenIssuance = $true
		}
	}
	spa = @{
		redirectUris = @(
			"$acaFrontEndUrl"
		)
	}
}

az rest `
    --method PATCH `
    --uri "https://graph.microsoft.com/v1.0/applications/$($spFullJsonApp.Id)" `
    --headers 'Content-Type=application/json' `
    --body ($bodyPatch | ConvertTo-Json -Depth 100 -Compress)