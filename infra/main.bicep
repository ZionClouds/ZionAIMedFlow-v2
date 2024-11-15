//targetScope = 'subscription'
targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
@allowed([
  'canadaeast'
  'eastus'
  'eastus2'
  'switzerlandnorth'
  'uksouth'
  'northcentralus'
  'australiaeast'
  'swedencentral'
])
@metadata({
  azd: {
    type: 'location'
  }
})
param location string

@description('The name of the OpenAI resource')
param openAiResourceName string = ''

@description('The SKU name of the OpenAI resource')
param openAiSkuName string = ''

@description('The API version of the OpenAI resource')
param openAiApiVersion string = '2024-02-15-preview'

@description('The type of the OpenAI resource')
param openAiType string = 'azure'

@description('The name of the OpenAI deployment')
param openAiDeploymentName string = 'gpt-4o'

@description('The name of the OpenAI deployment')
param openAiDeploymentCapacity string = '30'

@description('Deployment Model Version')
param openAiDeploymentVersion string = '2024-08-06'

@description('The name of the OpenAI embedding deployment')
param openAiEmbeddingDeploymentName string = 'text-embedding-ada-002'

@description('The name of the OpenAI embedding deployment')
param openAiEmbeddingDeploymentCapacity string = '120'

@description('Deployment Embedding Model Version')
param openAiEmbeddingDeploymentVersion string = '2'

@description('The name of the search service')
param searchServiceName string = ''

@description('The name of the AI search index')
param aiSearchIndexName string = 'vector-health'

@description('Container Image Name FrontEnd')
param imageNameFrontEnd string = 'welasco/dips-frontend:latest'

@description('Container Image TargetPort FrontEnd')
param imageTargetPortFrontEnd string = '80'

@description('Container Image Name BackEnd')
param imageNameBackEnd string = 'welasco/dips-backend:latest'

@description('Container Image Name DIPs')
param imageNameDIPs string = 'welasco/dips:latest'

@description('Container Image TargetPort BackEnd')
param imageTargetPortBackEnd string = '80'

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Whether the deployment is running on GitHub Actions')
param runningOnGh string = ''

@description('Whether the deployment is running on Azure DevOps Pipeline')
param runningOnAdo string = ''

@description('App Registration ClientId')
param appRegistrationClientId string

@description('App Registration Secret')
@secure()
param appRegistrationSecret string

param storageAccountContainerName string = 'docs'
param storageAccountContainerTokenStore string = 'tokenstore'
param storageAccountContainerFunction string = 'function'

//var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var resourceToken = toLower(uniqueString(resourceGroup().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

var serviceBusQueueName = 'dips-messages'

// resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
//   name: 'rg-${environmentName}'
//   location: location
//   tags: tags
// }

var prefix = toLower('${environmentName}-${resourceToken}')
var aiSearchSemanticConfig = '${aiSearchIndexName}-semantic-configuration'

var clientSecretSettingName = 'microsoftproviderauthenticationsecret'

// USER ROLES
var principalType = empty(runningOnGh) && empty(runningOnAdo) ? 'User' : 'ServicePrincipal'
module managedIdentity 'core/security/managed-identity.bicep' = {
  name: 'managed-identity'
  //scope: resourceGroup
  params: {
    name: 'id-${resourceToken}'
    location: location
    tags: tags
  }
}

module openAi 'core/ai/cognitiveservices.bicep' = {
  name: 'openai'
  //scope: resourceGroup
  params: {
    name: !empty(openAiResourceName) ? openAiResourceName : '${resourceToken}-openai'
    location: location
    tags: tags
    sku: {
      name: !empty(openAiSkuName) ? openAiSkuName : 'S0'
    }
    deployments: [
      {
        name: openAiDeploymentName
        model: {
          format: 'OpenAI'
          name: openAiDeploymentName
          version: openAiDeploymentVersion
        }
        sku: {
          name: 'GlobalStandard'
          capacity: openAiDeploymentCapacity
        }
      }
      {
        name: openAiEmbeddingDeploymentName
        model: {
          format: 'OpenAI'
          name: openAiEmbeddingDeploymentName
          version: openAiEmbeddingDeploymentVersion
        }
        sku: {
          name: 'Standard'
          capacity: openAiEmbeddingDeploymentCapacity
        }
      }
    ]
  }
}

module speechService 'core/ai/cognitiveservices.bicep' = {
  name: replace('${take(prefix, 12)}aispeechService', '-', '')
  //scope: resourceGroup
  params: {
    name: replace('${take(prefix, 12)}aispeechService', '-', '')
    location: location
    tags: tags
    kind: 'SpeechServices'
    sku: {
      name: 'S0'
      tier: 'Standard'
    }
  }
}

module cosmosMongoDB 'core/database/cosmos/cosmos-account.bicep' = {
  name: replace('${take(prefix, 12)}cosmosmongodb', '-', '')
  params: {
    name: replace('${take(prefix, 12)}cosmosmongodb', '-', '')
    location: location
    tags: tags
    kind: 'MongoDB'
  }
}

module storage 'core/storage/storage.bicep' = {
  //scope: resourceGroup
  name: replace('${take(prefix, 12)}mednotesin', '-', '')
  params: {
    location: location
    storageAccountName: replace('${take(prefix, 12)}mednotesin', '-', '')
    storageAccountType: 'Standard_LRS'
    storageAccountContainerName: storageAccountContainerName
    storageAccountContainerTokenStore: storageAccountContainerTokenStore
    functionStorageContainerName: storageAccountContainerFunction
  }
}

module logAnalyticsWorkspace 'core/monitor/loganalytics.bicep' = {
  name: 'loganalytics'
  //scope: resourceGroup
  params: {
    name: '${prefix}-loganalytics'
    location: location
    tags: tags
  }
}

module servicebus 'core/message/servicebus.bicep' = {
  name: replace('${take(prefix, 12)}-servicebus', '-', '')
  //scope: resourceGroup
  params: {
    serviceBusNamespaceName: replace('${take(prefix, 12)}-servicebus', '-', '')
    location: location
    Tags: tags
    serviceBusQueueName: serviceBusQueueName
  }
}

module functionApp 'core/host/function-app.bicep' = {
  name: 'function-app-mymdnotes'
  //scope: resourceGroup
  params: {
    functionname: replace('${take(prefix, 12)}-mymdnotes', '-', '')
    location: location
    Tags: tags
    userManagedIdentityClientId: managedIdentity.outputs.managedIdentityClientId
    userManagedIdentityPrincipalId: managedIdentity.outputs.managedIdentityPrincipalId
    storageAccountName: storage.outputs.storageAccountName
    lawresourceid: logAnalyticsWorkspace.outputs.id
    functionStorageContainerName: storage.outputs.storageAccountContainerFunction
    userManagedIdentity: managedIdentity.outputs.managedIdentityResourceId
    serviceBusEndpoint: '${servicebus.name}.servicebus.windows.net'
    serviceBusQueue: serviceBusQueueName
  }
}

module monitoring 'core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  //scope: resourceGroup
  params: {
    location: location
    tags: tags
    logAnalyticsName: logAnalyticsWorkspace.name
    applicationInsightsName: '${prefix}-appinsights'
    applicationInsightsDashboardName: '${prefix}-dashboard'
  }
}

// Container apps host (including container registry)
module containerApps 'core/host/container-apps.bicep' = {
  name: 'container-apps'
  //scope: resourceGroup
  params: {
    name: 'app'
    location: location
    tags: tags
    containerAppsEnvironmentName: '${prefix}-containerapps-env'
    logAnalyticsWorkspaceName: logAnalyticsWorkspace.outputs.name
  }
}

module dips 'app/aca.bicep' = {
  name: 'dips'
  //scope: resourceGroup
  params: {
    name: toLower(replace('${take(prefix, 19)}-caDIPs', '--', '-'))
    location: location
    tags: tags
    identityName: managedIdentity.outputs.managedIdentityName
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    imageName: imageNameDIPs
    imageTargetPort: imageTargetPortBackEnd
    ingressEnabled: false
    acaEnviromentVariables: [
      {
        name: 'AZURE_CLIENT_ID'
        value: managedIdentity.outputs.managedIdentityClientId
      }
      {
        name: 'TYPE'
        value: openAiType
      }
      {
        name: 'CHAT_MODEL'
        value: openAiDeploymentName
      }
      {
        name: 'ENDPOINT'
        value: openAi.outputs.endpoint
      }
      {
        name: 'VERSION'
        value: openAiApiVersion
      }
      {
        name: 'SPEECH_REGION'
        value: location
      }
      {
        name: 'SPEECH_RESOURCE_ID'
        value: speechService.outputs.id
      }
      {
        name: 'AZURE_COSMOS_LISTCONNECTIONSTRINGURL'
        value: 'https://management.azure.com/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosMongoDB.name}/listConnectionStrings?api-version=2024-08-15'
      }
      {
        name: 'STORAGE_URL'
        value: storage.outputs.storageEndpointBlob
      }
      {
        name: 'SB_CONNECTION_STRING'
        value: '${servicebus.name}.servicebus.windows.net'
      }
      {
        name: 'SB_QUEUE'
        value: 'dips-messages'
      }
      {
        name: 'APPLICATIONINSIGHTS__CONNECTIONSTRING'
        value: monitoring.outputs.applicationInsightsConnectionString
      }
      {
        name: 'PORT'
        value: '80'
      }
    ]
  }
}

module aca 'app/aca.bicep' = {
  name: 'acaFrontEnd'
  //scope: resourceGroup
  params: {
    name: toLower(replace('${take(prefix, 19)}-acaFrontEnd', '--', '-'))
    location: location
    tags: tags
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    imageName: imageNameFrontEnd
    imageTargetPort: imageTargetPortFrontEnd
    appRegistrationClientId: appRegistrationClientId
    clientSecretSettingName: clientSecretSettingName
    tokenStoreSASUrlSettingName: storageAccountContainerTokenStore
    secrets: {
      tokenstore: '${storage.outputs.storageEndpointBlob}${storageAccountContainerTokenStore}?${storage.outputs.storageToken}'
      microsoftproviderauthenticationsecret: appRegistrationSecret
    }
    acaEnviromentVariables: [
      {
        name: 'AZURE_CLIENT_ID'
        value: managedIdentity.outputs.managedIdentityClientId
      }
      {
        name: 'backendUri'
        value: '${acaBackEnd.outputs.SERVICE_ACA_URI}/'
      }
      {
        name: 'APPLICATIONINSIGHTS__CONNECTIONSTRING'
        value: monitoring.outputs.applicationInsightsConnectionString
      }
      {
        name: 'PORT'
        value: '80'
      }
    ]
  }
}

module acaBackEnd 'app/aca.bicep' = {
  name: 'acaBackEnd'
  //scope: resourceGroup
  params: {
    name: toLower(replace('${take(prefix, 19)}-caBackEnd', '--', '-'))
    location: location
    tags: tags
    identityName: managedIdentity.outputs.managedIdentityName
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    imageName: imageNameBackEnd
    imageTargetPort: imageTargetPortBackEnd
    appRegistrationClientId: appRegistrationClientId
    clientSecretSettingName: clientSecretSettingName
    secrets: {
      microsoftproviderauthenticationsecret: appRegistrationSecret
    }
    acaEnviromentVariables: [
      {
        name: 'AZURE_CLIENT_ID'
        value: managedIdentity.outputs.managedIdentityClientId
      }
      {
        name: 'STORAGE_CONNECTION_STRING'
        value: storage.outputs.storageEndpointBlob
      }
      {
        name: 'AZURE_COSMOS_LISTCONNECTIONSTRINGURL'
        value: 'https://management.azure.com/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosMongoDB.name}/listConnectionStrings?api-version=2024-08-15'
      }
      {
        name: 'APPLICATIONINSIGHTS__CONNECTIONSTRING'
        value: monitoring.outputs.applicationInsightsConnectionString
      }
      {
        name: 'PORT'
        value: '80'
      }
    ]
  }
}

// module aiSearchRole 'core/security/role.bicep' = {
//   //scope: resourceGroup
//   name: 'ai-search-index-data-contributor'
//   params: {
//     principalId: managedIdentity.outputs.managedIdentityPrincipalId
//     roleDefinitionId: '8ebe5a00-799e-43f5-93ac-243d3dce84a7' //Search Index Data Contributor
//     principalType: 'ServicePrincipal'
//   }
// }

module cosmosRoleAssignment 'core/security/role.bicep' = {
  //scope: resourceGroup
  name: 'cosmos-account-role'
  params: {
    principalId: managedIdentity.outputs.managedIdentityPrincipalId
    roleDefinitionId: '5bd9cd88-fe45-4216-938b-f97437e15450' // DocumentDB Account Contributor
    principalType: 'ServicePrincipal'
  }
}

module cognitiveServicesSpeechRoleAssignment 'core/security/role.bicep' = {
  //scope: resourceGroup
  name: 'speech-account-role'
  params: {
    principalId: managedIdentity.outputs.managedIdentityPrincipalId
    roleDefinitionId: '0e75ca1e-0464-4b4d-8b93-68208a576181' // Cognitive Services Speech Contributor
    principalType: 'ServicePrincipal'
  }
}

module serviceBusAccountRole 'core/security/role.bicep' = {
  //scope: resourceGroup
  name: 'serviceBus-account-role'
  params: {
    principalId: managedIdentity.outputs.managedIdentityPrincipalId
    roleDefinitionId: '090c5cfd-751d-490a-894a-3ce6f1109419' // Azure Service Bus Data Owner
    principalType: 'ServicePrincipal'
  }
}

module appinsightsAccountRole 'core/security/role.bicep' = {
  //scope: resourceGroup
  name: 'appinsights-account-role'
  params: {
    principalId: managedIdentity.outputs.managedIdentityPrincipalId
    roleDefinitionId: '3913510d-42f4-4e42-8a64-420c390055eb' // Monitoring Metrics Publisher
    principalType: 'ServicePrincipal'
  }
}

// module aiSearchStorageAccess 'core/security/role.bicep' = {
//   //scope: resourceGroup
//   name: 'storage-blob-data-contributor'
//   params: {
//     principalId: managedIdentity.outputs.managedIdentityPrincipalId
//     roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' //Storage Blob Data Contributor
//     principalType: 'ServicePrincipal'
//   }
// }

module acaBackEndStorageTableAccess 'core/security/role.bicep' = {
  //scope: resourceGroup
  name: 'storage-table-data-contributor'
  params: {
    principalId: managedIdentity.outputs.managedIdentityPrincipalId
    roleDefinitionId: '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3' //Storage Table Data Contributor
    principalType: 'ServicePrincipal'
  }
}

module userCosmosRoleAssignment 'core/security/role.bicep' = if (!empty(principalId)){
  //scope: resourceGroup
  name: 'user-cosmos-account-role'
  params: {
    principalId: principalId
    roleDefinitionId: '5bd9cd88-fe45-4216-938b-f97437e15450' // DocumentDB Account Contributor
    principalType: principalType
  }
}

module userCognitiveServicesSpeechRoleAssignment 'core/security/role.bicep' = if (!empty(principalId)){
  //scope: resourceGroup
  name: 'user-speech-account-role'
  params: {
    principalId: principalId
    roleDefinitionId: '0e75ca1e-0464-4b4d-8b93-68208a576181' // Cognitive Services Speech Contributor
    principalType: principalType
  }
}

module userServiceBusAccountRole 'core/security/role.bicep' = if (!empty(principalId)){
  //scope: resourceGroup
  name: 'user-serviceBus-account-role'
  params: {
    principalId: principalId
    roleDefinitionId: '090c5cfd-751d-490a-894a-3ce6f1109419' // Azure Service Bus Data Owner
    principalType: principalType
  }
}

module userAiSearchRole 'core/security/role.bicep' = if (!empty(principalId)) {
  //scope: resourceGroup
  name: 'user-ai-search-index-data-contributor'
  params: {
    principalId: principalId
    roleDefinitionId: '8ebe5a00-799e-43f5-93ac-243d3dce84a7' //Search Index Data Contributor
    principalType: principalType
  }
}

module openaiRoleUser 'core/security/role.bicep' = if (!empty(principalId)) {
  //scope: resourceGroup
  name: 'user-openai-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' //Cognitive Services OpenAI User
    principalType: principalType
  }
}

module userStorageAccess 'core/security/role.bicep' = if (!empty(principalId)) {
  //scope: resourceGroup
  name: 'user-storage-blob-data-contributor'
  params: {
    principalId: principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' //Storage Blob Data Contributor
    principalType: principalType
  }
}

module useracaBackEndStorageAccess 'core/security/role.bicep' = if (!empty(principalId)) {
  //scope: resourceGroup
  name: 'user-storage-table-data-contributor'
  params: {
    principalId: principalId
    roleDefinitionId: '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3' //Storage Table Data Contributor
    principalType: principalType
  }
}

output AZURE_LOCATION string = location
//output RESOURCE_GROUP_NAME string = resourceGroup.name

output AZURE_OPENAI_CHATGPT_DEPLOYMENT string = openAiDeploymentName
output AZURE_OPENAI_API_VERSION string = openAiApiVersion
output AZURE_OPENAI_ENDPOINT string = openAi.outputs.endpoint
output AZURE_OPENAI_RESOURCE string = openAi.outputs.name
output AZURE_OPENAI_SKU_NAME string = openAi.outputs.skuName

// output SERVICE_ACA_NAME string = aca.outputs.SERVICE_ACA_NAME
// output SERVICE_ACA_URI string = aca.outputs.SERVICE_ACA_URI
// output SERVICE_ACA_IMAGE_NAME string = aca.outputs.SERVICE_ACA_IMAGE_NAME

output AZURE_CONTAINER_ENVIRONMENT_NAME string = containerApps.outputs.environmentName
output APPINSIGHTS_CONNECTIONSTRING string = monitoring.outputs.applicationInsightsConnectionString

output OpenAI__Type string = 'azure'
output OpenAI__API_Version string = openAiApiVersion
output OpenAI__Endpoint string = openAi.outputs.endpoint
output OpenAI__Deployment string = openAiDeploymentName
output OpenAI__Embedding_Deployment string = openAiEmbeddingDeploymentName

output ApplicationInsights__ConnectionString string = monitoring.outputs.applicationInsightsConnectionString
//output ACAFrontEndUrl string = aca.outputs.SERVICE_ACA_URI
