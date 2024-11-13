param functionname string
param userManagedIdentity string
param userManagedIdentityClientId string
param userManagedIdentityPrincipalId string
param storageAccountName string
param lawresourceid string
param location string = resourceGroup().location
param Tags object = {}
param filename string = 'mymdnotes.zip'
param functionStorageContainerName string
param serviceBusEndpoint string = ''
param serviceBusQueue string = ''

var tempfilename = '${filename}.tmp'

module functionStorageAccess '../security/role.bicep' = {
  //scope: resourceGroup
  name: 'azFunction-storage-blob-data-contributor'
  params: {
    principalId: userManagedIdentityPrincipalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' //Storage Blob Data Contributor
    principalType: 'ServicePrincipal'
  }
}

resource deploymentScript 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  name: 'deployscript-Function-${functionname}'
  dependsOn: [
    azfunctionsiteconfig
    functionStorageAccess
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
    timeout: 'PT5M'
    retentionInterval: 'PT1H'
    environmentVariables: [
      {
        name: 'CONTENT'
        value: loadFileAsBase64('../../../src/azurefunctions/mymdnotes.zip')
      }
    ]
    scriptContent: 'echo "$CONTENT" > ${tempfilename} && cat ${tempfilename} | base64 -d > ${filename} && az login --identity --username ${userManagedIdentityClientId} && az storage blob upload -f ${filename} -c ${functionStorageContainerName} -n ${filename} --overwrite true'
  }
}

resource serverfarm 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: '${functionname}-farm'
  location: location
  tags: Tags
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
    size: 'Y1'
    family: 'Y'
    capacity: 0
  }
  kind: 'functioapp'
  properties: {
    perSiteScaling: false
    elasticScaleEnabled: false
    maximumElasticWorkerCount: 1
    isSpot: false
    reserved: false
    isXenon: false
    hyperV: false
    targetWorkerCount: 0
    targetWorkerSizeId: 0
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
          acrUseManagedIdentityCreds: false
          alwaysOn: false
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
    WEBSITE_RUN_FROM_PACKAGE_BLOB_MI_RESOURCE_ID: userManagedIdentity
    WEBSITE_RUN_FROM_PACKAGE: 'https://${storageAccountName}.blob.core.windows.net/${functionStorageContainerName}/${filename}'
    FUNCTIONS_WORKER_RUNTIME:'python'
    FUNCTIONS_EXTENSION_VERSION:'~4'
    APPLICATIONINSIGHTS_CONNECTION_STRING: 'InstrumentationKey=${reference(appinsights.id, '2020-02-02-preview').InstrumentationKey}'
    ApplicationInsightsAgent_EXTENSION_VERSION: '~2'
    MSI_CLIENT_ID: userManagedIdentityClientId
    AZURE_CLIENT_ID: userManagedIdentityClientId
    APPLICATIONINSIGHTS_AUTHENTICATION_STRING: 'Authorization=AAD;ClientId=${userManagedIdentityClientId}'
    SB_ENDPOINT: serviceBusEndpoint
    SB_QUEUE: serviceBusQueue
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
