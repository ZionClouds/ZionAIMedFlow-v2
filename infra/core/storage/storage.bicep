@description('Storage Account type')
@allowed([
  'Premium_LRS'
  'Premium_ZRS'
  'Standard_GRS'
  'Standard_GZRS'
  'Standard_LRS'
  'Standard_RAGRS'
  'Standard_RAGZRS'
  'Standard_ZRS'
])
param storageAccountType string
param location string
param storageAccountName string
param storageAccountContainerName string = ''
param storageAccountContainerTokenStore string = ''
param baseTime string = utcNow('u')

resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
  properties: {}
}

resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = if (!empty(storageAccountContainerName)) {
  name: 'default'
  parent: sa
}

resource symbolicname 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = if (!empty(storageAccountContainerName)) {
  name: storageAccountContainerName
  parent: blobServices
}

resource storageContainerTokenStore 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = if (!empty(storageAccountContainerTokenStore)) {
  name: storageAccountContainerTokenStore
  parent: blobServices
}

var add180Days = dateTimeAdd(baseTime, 'P180D')
// var storageToken = listServiceSAS(sa.name,'2024-03-01', {
//   canonicalizedResource: '/blob/${sa.name}/${storageAccountContainerTokenStore}'
//   signedResource: 'c'
//   signedProtocol: 'https'
//   signedPermission: 'rwd'
//   signedServices: 'b'
//   signedExpiry: add180Days
// }).serviceSasToken


output storageAccountName string = sa.name
output storageAccountId string = sa.id
output storageEndpointTable string = sa.properties.primaryEndpoints.table
output storageEndpointBlob string = sa.properties.primaryEndpoints.blob

output storageToken string = listServiceSAS(sa.name,'2024-01-01', {
  canonicalizedResource: '/blob/${sa.name}/${storageAccountContainerTokenStore}'
  signedResource: 'c'
  signedProtocol: 'https'
  signedPermission: 'rwd'
  signedServices: 'b'
  signedExpiry: add180Days
}).serviceSasToken
