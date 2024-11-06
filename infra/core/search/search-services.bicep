metadata description = 'Creates an Azure AI Search instance.'
param name string
param location string = resourceGroup().location
param tags object = {}

param sku object = {
  name: 'standard'
}

param authOptions object = {}
param disableLocalAuth bool = false
param disabledDataExfiltrationOptions array = []
param encryptionWithCmk object = {
  enforcement: 'Unspecified'
}
@allowed([
  'default'
  'highDensity'
])
param hostingMode string = 'default'
param networkRuleSet object = {
  bypass: 'None'
  ipRules: []
}
param partitionCount int = 1
@allowed([
  'enabled'
  'disabled'
])
param publicNetworkAccess string = 'enabled'
param replicaCount int = 1
@allowed([
  'disabled'
  'free'
  'standard'
])
param semanticSearch string = 'disabled'
param managedIdentityPrincipalId string = ''
param managedIdentityClientId string = ''

param indexName string
param openAIEndpointURI string
param openAIAdaModelName string
param dataSourceStorageResourceID string
param managedIdentityResourceID string

resource search 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: name
  location: location
  tags: tags
  // The free tier does not support managed identity
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityResourceID}': {}
    }
  }
  properties: {
    authOptions: disableLocalAuth ? null : authOptions
    disableLocalAuth: disableLocalAuth
    disabledDataExfiltrationOptions: disabledDataExfiltrationOptions
    encryptionWithCmk: encryptionWithCmk
    hostingMode: hostingMode
    networkRuleSet: networkRuleSet
    partitionCount: partitionCount
    publicNetworkAccess: publicNetworkAccess
    replicaCount: replicaCount
    semanticSearch: semanticSearch
  }
  sku: sku
}

module aiSearchRole '../security/role.bicep' = {
  name: 'ai-search-index-data-contributor'
  params: {
    principalId: managedIdentityPrincipalId
    roleDefinitionId: '8ebe5a00-799e-43f5-93ac-243d3dce84a7' //Search Index Data Contributor
    principalType: 'ServicePrincipal'
  }
}

module aiSearchRoleServiceContributor '../security/role.bicep' = {
  name: 'ai-search-index-service-contributor'
  params: {
    principalId: managedIdentityPrincipalId
    roleDefinitionId: '7ca78c08-252a-4471-8644-bb5ff32d4ba0' //Search Service Contributor
    principalType: 'ServicePrincipal'
  }
}

resource setupSearchService 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  name: '${search.name}-setup'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityResourceID}': {}
    }
  }
  kind: 'AzurePowerShell'
  properties: {
    azPowerShellVersion: '8.3'
    timeout: 'PT30M'
    arguments: '-searchServiceName \\"${search.name}\\" -indexName \\"${indexName}\\" -OpenAIEndpointURI \\"${openAIEndpointURI}\\" -OpenAIAdaModelName \\"${openAIAdaModelName}\\" -dataSourceStorageResourceID \\"${dataSourceStorageResourceID}\\" -managedIdentityResourceID \\"${managedIdentityResourceID}\\" -managedIdentityClientID \\"${managedIdentityClientId}\\"'
    scriptContent: loadTextContent('../../hooks/SetupSearchService.ps1')
    cleanupPreference: 'OnSuccess'
    retentionInterval: 'P1D'
  }
}

output id string = search.id
output endpoint string = 'https://${name}.search.windows.net/'
output name string = search.name
//output principalId string = search.identity.principalId

