param functionname string
param userManagedIdentity string
param userManagedIdentityClientId string
param userManagedIdentityPrincipalId string
param storageAccountName string
param lawresourceid string
param location string = resourceGroup().location
param Tags object = {}
param filename string = 'mymdnotes.zip'
param functionStorageContainerName string = ''
param serviceBusEndpoint string = ''
param serviceBusQueue string = ''
param cosmos_listconnectionstringurl string = ''

var tempfilename = '${filename}.tmp'

module functionBlobStorageAccess '../security/role.bicep' = {
  //scope: resourceGroup
  name: 'azFunction-storage-blob-data-contributor'
  params: {
    principalId: userManagedIdentityPrincipalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' //Storage Blob Data Contributor
    principalType: 'ServicePrincipal'
  }
}

module functionQueueStorageAccess '../security/role.bicep' = {
  //scope: resourceGroup
  name: 'azFunction-storage-queue-data-contributor'
  params: {
    principalId: userManagedIdentityPrincipalId
    roleDefinitionId: '974c5e8b-45b9-4653-ba55-5f855dd0fb88' //Storage Queue Data Contributor
    principalType: 'ServicePrincipal'
  }
}

module functionWebsiteContributor '../security/role.bicep' = {
  //scope: resourceGroup
  name: 'azFunction-website-contributor'
  params: {
    principalId: userManagedIdentityPrincipalId
    roleDefinitionId: 'de139f84-1756-47ae-9be6-808fbbe84772' //Website Contributor
    principalType: 'ServicePrincipal'
  }
}

module storageAccountContributor '../security/role.bicep' = {
  //scope: resourceGroup
  name: 'storage-account-contributor'
  params: {
    principalId: userManagedIdentityPrincipalId
    roleDefinitionId: '17d1049b-9a84-46fb-8f53-869881c3d3ab' //Storage Account Contributor
    principalType: 'ServicePrincipal'
  }
}

// resource deploymentScript 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
//   name: 'deployscript-Function-${functionname}'
//   dependsOn: [
//     azfunctionsiteconfig
//     functionBlobStorageAccess
//   ]
//   tags: Tags
//   location: location
//   kind: 'AzureCLI'
//   identity: {
//     type: 'UserAssigned'
//     userAssignedIdentities: {
//       '${userManagedIdentity}': {}
//     }
//   }
//   properties: {
//     azCliVersion: '2.42.0'
//     timeout: 'PT5M'
//     retentionInterval: 'PT1H'
//     environmentVariables: [
//       {
//         name: 'CONTENT'
//         value: loadFileAsBase64('../../../src/azurefunctions/mymdnotes.zip')
//       }
//     ]
//     scriptContent: 'echo "$CONTENT" > ${tempfilename} && cat ${tempfilename} | base64 -d > ${filename} && az login --identity --username ${userManagedIdentityClientId} && az storage blob upload -f ${filename} -c ${functionStorageContainerName} -n ${filename} --account-name ${storageAccountName} --auth-mode login --overwrite true'
//   }
// }

// Consumption Plan
// resource serverfarm 'Microsoft.Web/serverfarms@2021-03-01' = {
//   name: '${functionname}-farm'
//   location: location
//   tags: Tags
//   sku: {
//     name: 'Y1'
//     tier: 'Dynamic'
//     size: 'Y1'
//     family: 'Y'
//     capacity: 0
//   }
//   kind: 'functioapp'
//   properties: {
//     perSiteScaling: false
//     elasticScaleEnabled: false
//     maximumElasticWorkerCount: 1
//     isSpot: false
//     reserved: true
//     isXenon: false
//     hyperV: false
//     targetWorkerCount: 0
//     targetWorkerSizeId: 0
//     zoneRedundant: false
//   }
// }

resource serverfarm 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: '${functionname}-farm'
  location: location
  tags: Tags
  sku: {
    name: 'B1'
    tier: 'Basic'
    size: 'B1'
    family: 'B'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
    isXenon: false
    hyperV: false
    zoneRedundant: false
  }
}

resource azfunctionsite 'Microsoft.Web/sites@2023-01-01' = {
  name: functionname
  location: location
  kind: 'functionapp'
  tags: Tags
  identity: {
      type: 'UserAssigned'
      userAssignedIdentities: {
          '${userManagedIdentity}': {}
      }
  }
  properties: {
      enabled: true
      serverFarmId: serverfarm.id
      reserved: false
      isXenon: false
      hyperV: false
      siteConfig: {
          numberOfWorkers: 1
          linuxFxVersion: 'PYTHON|3.11'
          acrUseManagedIdentityCreds: false
          alwaysOn: true
          ipSecurityRestrictions: [
              {
                  ipAddress: 'Any'
                  action: 'Allow'
                  priority: 1
                  name: 'Allow all'
                  description: 'Allow all access'
              }
          ]
          scmIpSecurityRestrictions: [
              {
                  ipAddress: 'Any'
                  action: 'Allow'
                  priority: 1
                  name: 'Allow all'
                  description: 'Allow all access'
              }
          ]
          http20Enabled: false
          functionAppScaleLimit: 200
          minimumElasticInstanceCount: 0
          minTlsVersion: '1.2'
          cors: {
              allowedOrigins: [
                  'https://portal.azure.com'
              ]
              supportCredentials: true
          }
      }
      scmSiteAlsoStopped: false
      clientAffinityEnabled: false
      clientCertEnabled: false
      clientCertMode: 'Required'
      hostNamesDisabled: false
      containerSize: 1536
      dailyMemoryTimeQuota: 0
      httpsOnly: true
      redundancyMode: 'None'
      storageAccountRequired: false
  }
}

resource azfunctionsiteconfig 'Microsoft.Web/sites/config@2021-03-01' = {
  name: 'appsettings'
  parent: azfunctionsite
  // dependsOn: [
  //   roleAssignment
  // ]
  properties: {
    //WEBSITE_RUN_FROM_PACKAGE_BLOB_MI_RESOURCE_ID: userManagedIdentity
    //WEBSITE_RUN_FROM_PACKAGE: 'https://${storageAccountName}.blob.core.windows.net/${functionStorageContainerName}/${filename}'
    FUNCTIONS_WORKER_RUNTIME:'python'
    FUNCTIONS_EXTENSION_VERSION:'~4'
    APPLICATIONINSIGHTS_CONNECTION_STRING: 'InstrumentationKey=${reference(appinsights.id, '2020-02-02-preview').InstrumentationKey}'
    APPLICATIONINSIGHTS_AUTHENTICATION_STRING: 'Authorization=AAD;ClientId=${userManagedIdentityClientId}'
    SB_ENDPOINT: serviceBusEndpoint
    SB_QUEUE: serviceBusQueue
    AzureWebJobsStorage__credential: 'managedidentity'
    AzureWebJobsStorage__clientId: userManagedIdentityClientId
    AzureWebJobsStorage__blobServiceUri: 'https://${storageAccountName}.blob.core.windows.net'
    AzureWebJobsStorage__queueServiceUri: 'https://${storageAccountName}.queue.core.windows.net'
    AzureWebJobsStorage__accountName: storageAccountName
    AZURE_COSMOS_LISTCONNECTIONSTRINGURL: cosmos_listconnectionstringurl
    MSI_CLIENT_ID: userManagedIdentityClientId
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
    //ENABLE_ORYX_BUILD: 'true'
  }
}

// resource deploymentScriptPwsh 'Microsoft.Resources/deploymentScripts@2023-08-01' = {
//   name: 'deployscript-Function-${functionname}'
//   dependsOn: [
//     azfunctionsiteconfig
//     functionBlobStorageAccess
//   ]
//   tags: Tags
//   location: location
//   kind: 'AzurePowerShell'
//   identity: {
//     type: 'UserAssigned'
//     userAssignedIdentities: {
//       '${userManagedIdentity}': {}
//     }
//   }
//   properties: {
//     azPowerShellVersion: '8.3'
//     timeout: 'PT30M'
//     retentionInterval: 'P1D'
//     environmentVariables: [
//       {
//         name: 'CONTENT'
//         value: loadFileAsBase64('../../../src/azurefunctions/mymdnotes.zip')
//       }
//     ]
//     arguments: '-functionAppName \\"${functionname}\\" -RG \\"${resourceGroup().name}\\" -managedIdentityClientID \\"${userManagedIdentityClientId}\\"'
//     scriptContent: loadTextContent('../../hooks/DeployFunction.ps1')
//     cleanupPreference: 'OnSuccess'
//   }
// }

resource deploymentScript 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  name: 'deployscript-Function-${functionname}'
  dependsOn: [
    azfunctionsiteconfig
    functionBlobStorageAccess
    functionWebsiteContributor
  ]
  tags: Tags
  location: location
  kind: 'AzureCLI'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userManagedIdentity}': {}
    }
  }
  properties: {
    azCliVersion: '2.42.0'
    timeout: 'PT20M'
    retentionInterval: 'PT1H'
    environmentVariables: [
      {
        name: 'CONTENT'
        value: loadFileAsBase64('../../../src/azurefunctions/mymdnotes.zip')
      }
    ]
    //scriptContent: 'echo "$CONTENT" > ${tempfilename} && cat ${tempfilename} | base64 -d > ${filename} && az login --identity --username ${userManagedIdentityClientId} && az storage blob upload -f ${filename} -c ${functionStorageContainerName} -n ${filename} --account-name ${storageAccountName} --auth-mode login --overwrite true'
    scriptContent: 'echo "$CONTENT" > ${tempfilename} && cat ${tempfilename} | base64 -d > ${filename} && az login --identity --username ${userManagedIdentityClientId} && echo "Listing local files" && ls -ltrah && echo "Deploying Azure Function..." && az functionapp deployment source config-zip -g ${resourceGroup().name} -n ${functionname} --src ${filename} --build-remote true --verbose --debug'
  }
}

resource appinsights 'Microsoft.Insights/components@2020-02-02' = {
  name: functionname
  tags: Tags
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    //ApplicationId: guid(functionname)
    //Flow_Type: 'Redfield'
    //Request_Source: 'IbizaAIExtension'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    WorkspaceResourceId: lawresourceid
    DisableLocalAuth: true
  }
}
