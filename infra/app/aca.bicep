param name string
param location string = resourceGroup().location
param tags object = {}

param identityName string = ''
param identityId string = ''
param containerAppsEnvironmentName string
param imageName string
param imageTargetPort string = '80'
param acaBackEndUri string = ''
param serviceName string = 'aca'
param openAiDeploymentName string
param openAiEndpoint string
param openAiApiVersion string
param openAiType string
param aiSearchEndpoint string = ''
param aiSearchIndexName string = ''
param aiSearchSemanticConfig string = ''
param appinsights_Connectionstring string
param storageEndpoint string = ''
param appRegistrationClientId string = ''

@description('The secrets required for the container')
@secure()
param secrets object = {}

#disable-next-line secure-secrets-in-params
param clientSecretSettingName string = ''

param tokenStoreSASUrlSettingName string = ''

module app '../core/host/container-app-upsert.bicep' = {
  name: '${serviceName}-container-app-module'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName })
    identityName: !empty(identityName) ? identityName : null
    identityType: 'UserAssigned'
    containerAppsEnvironmentName: containerAppsEnvironmentName
    imageName: imageName
    appRegistrationClientId: appRegistrationClientId
    clientSecretSettingName: clientSecretSettingName
    env: [
      {
        name: 'AZURE_CLIENT_ID'
        value: !empty(identityId) ? identityId : ''
      }
      {
        name: 'AI_SEARCH_ENDPOINT'
        value: aiSearchEndpoint
      }
      {
        name: 'AI_SEARCH_INDEX_NAME'
        value: aiSearchIndexName
      }
      {
        name: 'AI_SEARCH_SEMANTIC_CONFIG'
        value: aiSearchSemanticConfig
      }
      {
        name: 'backendUri'
        value: '${acaBackEndUri}/api/'
      }
      {
        name: 'OPENAI__TYPE'
        value: openAiType
      }
      {
        name: 'GPT_OPENAI_API_VERSION'
        value: openAiApiVersion
      }
      {
        name: 'GPT_OPENAI_ENDPOINT'
        value: openAiEndpoint
      }
      {
        name: 'GPT_OPENAI_DEPLOYMENT_NAME'
        value: openAiDeploymentName
      }
      {
        name: 'APPLICATIONINSIGHTS__CONNECTIONSTRING'
        value: appinsights_Connectionstring
      }
      {
        name: 'PORT'
        value: imageTargetPort
      }
      {
        name: 'AZURE_TABLES_ENDPOINT'
        value: storageEndpoint
      }
      {
        name: 'AppDebug'
        value: 'false'
      }
    ]
    //secrets: secrets
    secrets: secrets
    targetPort: int(imageTargetPort)
    tokenStoreSASUrlSettingName: tokenStoreSASUrlSettingName
  }
}

output SERVICE_ACA_NAME string = app.outputs.name
output SERVICE_ACA_URI string = app.outputs.uri
output SERVICE_ACA_IMAGE_NAME string = app.outputs.imageName
