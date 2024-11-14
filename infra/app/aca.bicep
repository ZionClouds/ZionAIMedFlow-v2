param name string
param location string = resourceGroup().location
param tags object = {}

param identityName string = ''
param containerAppsEnvironmentName string
param imageName string
param imageTargetPort string = '80'
param serviceName string = 'aca'
param appRegistrationClientId string = ''
param acaEnviromentVariables array = []


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
    env: acaEnviromentVariables
    //secrets: secrets
    secrets: secrets
    targetPort: int(imageTargetPort)
    tokenStoreSASUrlSettingName: tokenStoreSASUrlSettingName
  }
}

output SERVICE_ACA_NAME string = app.outputs.name
output SERVICE_ACA_URI string = app.outputs.uri
output SERVICE_ACA_IMAGE_NAME string = app.outputs.imageName
