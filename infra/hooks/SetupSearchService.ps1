param(
    [string] [Parameter(Mandatory=$true)] $searchServiceName,
    [string] [Parameter(Mandatory=$true)] $indexName,
    [string] [Parameter(Mandatory=$true)] $OpenAIEndpointURI,
    [string] [Parameter(Mandatory=$true)] $OpenAIAdaModelName,
    [string] [Parameter(Mandatory=$true)] $dataSourceStorageResourceID,
    [string] [Parameter(Mandatory=$true)] $managedIdentityResourceID,
    [string] [Parameter(Mandatory=$true)] $managedIdentityClientID
)

$ErrorActionPreference = 'Stop'
Connect-AzAccount -Identity -AccountId $managedIdentityClientID
$token = Get-AzAccessToken -ResourceUrl https://search.azure.com | select -expand Token

function InvokeAISearchChange {
    param (
        [string] [Parameter(Mandatory=$true)] $searchServiceName,
        [string] [Parameter(Mandatory=$true)] $definitiontype,
        [string] [Parameter(Mandatory=$true)] $definition,
        [string] [Parameter(Mandatory=$true)] $token
    )

    $apiversion = '2024-05-01-Preview'
    $headers = @{ 'Authorization' = "Bearer $token"; 'Content-Type' = 'application/json'; }
    #$uri = "https://$searchServiceName.search.windows.net"
    $uri = ("https://$searchServiceName.search.windows.net/" + $definitiontype + "?api-version=" +$apiversion)
    # https://vwsaisearch.search.windows.net/-version=2024-05-01-Preview
    try {
        Invoke-WebRequest `
            -Method 'POST' `
            -Uri $uri `
            -Headers  $headers `
            -Body $definition
    } catch {
        Write-Error $_
        throw
    }
}

$indexDefinition = @{
    "name" = "$indexName"
    "fields" = @(
        @{"name" = "chunk_id"; "type" = "Edm.String"; "searchable" = $true; "filterable" = $true; "retrievable" = $true; "stored" = $true; "sortable" = $true; "facetable" = $true; "key" = $true; "analyzer" = "keyword"},
        @{"name" = "parent_id"; "type" = "Edm.String"; "searchable" = $true; "filterable" = $true; "retrievable" = $true; "stored" = $true; "sortable" = $true; "facetable" = $true; "key" = $false},
        @{"name" = "chunk"; "type" = "Edm.String"; "searchable" = $true; "retrievable" = $true; "stored" = $true},
        @{"name" = "title"; "type" = "Edm.String"; "searchable" = $true; "filterable" = $true; "retrievable" = $true; "stored" = $true},
        @{"name" = "metadata_storage_path"; "type" = "Edm.String"; "searchable" = $true; "retrievable" = $true; "stored" = $true},
        @{"name" = "text_vector"; "type" = "Collection(Edm.Single)"; "searchable" = $true; "retrievable" = $true; "stored" = $true; "dimensions" = 1536; "vectorSearchProfile" = "$indexName-azureOpenAi-text-profile"}
    )
    "semantic" = @{
        "defaultConfiguration" = "$indexName-semantic-configuration"
        "configurations" = @(
        @{
            "name" = "$indexName-semantic-configuration"
            "prioritizedFields" = @{
            "titleField" = @{
                "fieldName" = "title"
            }
            "prioritizedContentFields" = @(
                @{
                "fieldName" = "chunk"
                }
            )
            }
        }
        )
    }
    "vectorSearch" = @{
        "algorithms" = @(
        @{
            "name" = "$indexName-algorithm"
            "kind" = "hnsw"
            "hnswParameters" = @{
            "metric" = "cosine"
            "m" = 4
            "efConstruction" = 400
            "efSearch" = 500
            }
        }
        )
        "profiles" = @(
        @{
            "name" = "$indexName-azureOpenAi-text-profile"
            "algorithm" = "$indexName-algorithm"
            "vectorizer" = "$indexName-azureOpenAi-text-vectorizer"
        }
        )
        "vectorizers" = @(
        @{
            "name" = "$indexName-azureOpenAi-text-vectorizer"
            "kind" = "azureOpenAI"
            "azureOpenAIParameters" = @{
              "resourceUri" = "$OpenAIEndpointURI"
              "deploymentId" = "$OpenAIAdaModelName"
              "modelName" = "$OpenAIAdaModelName"
              "authIdentity" = @{
                "@odata.type" = "#Microsoft.Azure.Search.DataUserAssignedIdentity"
                "userAssignedIdentity" = "$managedIdentityResourceID"
              }
            }
        }
        )
    }
}

$skillsetDefinition = @{
    "name" = "$indexName-skillset"
    "description" = "Skillset to chunk documents and generate embeddings"
    "skills" = @(
      @{
        "@odata.type" = "#Microsoft.Skills.Text.SplitSkill"
        "name" = "#1"
        "description" = "Split skill to chunk documents"
        "context" = "/document"
        "defaultLanguageCode" = "en"
        "textSplitMode" = "pages"
        "maximumPageLength" = 2000
        "pageOverlapLength" = 500
        "maximumPagesToTake" = 0
        "inputs" = @(
          @{
            "name" = "text"
            "source" = "/document/content"
          }
        )
        "outputs" = @(
          @{
            "name" = "textItems"
            "targetName" = "pages"
          }
        )
      },
      @{
        "@odata.type" = "#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill"
        "name" = "#2"
        "description" = $null
        "context" = "/document/pages/*"
        "resourceUri" = "$OpenAIEndpointURI"
        "deploymentId" = "$OpenAIAdaModelName"
        "dimensions" = 1536
        "modelName" = "$OpenAIAdaModelName"
        "inputs" = @(
          @{
            "name" = "text"
            "source" = "/document/pages/*"
          }
        )
        "outputs" = @(
          @{
            "name" = "embedding"
            "targetName" = "text_vector"
          }
        )
        "authIdentity" = @{
            "@odata.type" = "#Microsoft.Azure.Search.DataUserAssignedIdentity"
            "userAssignedIdentity" = "$managedIdentityResourceID"
        }
      }
    )
    "cognitiveServices" = $null
    "knowledgeStore" = $null
    "indexProjections" = @{
      "selectors" = @(
        @{
          "targetIndexName" = "$indexName"
          "parentKeyFieldName" = "parent_id"
          "sourceContext" = "/document/pages/*"
          "mappings" = @(
            @{
              "name" = "text_vector"
              "source" = "/document/pages/*/text_vector"
              "sourceContext" = $null
              "inputs" = @()
            },
            @{
              "name" = "chunk"
              "source" = "/document/pages/*"
              "sourceContext" = $null
              "inputs" = @()
            },
            @{
              "name" = "metadata_storage_path"
              "source" = "/document/metadata_storage_path"
              "sourceContext" = $null
              "inputs" = @()
            },
            @{
              "name" = "title"
              "source" = "/document/title"
              "sourceContext" = $null
              "inputs" = @()
            }
          )
        }
      )
      "parameters" = @{
        "projectionMode" = "skipIndexingParentDocuments"
      }
    }
    "encryptionKey" = $null
}

$dataSourceDefinition = @{
    "type" = "azureblob"
    "credentials" = @{
        "connectionString" = "ResourceId=$dataSourceStorageResourceID;"
    }

    "identity" = @{
        "@odata.type"= "#Microsoft.Azure.Search.DataUserAssignedIdentity"
        "userAssignedIdentity"= "$managedIdentityResourceID"
    }
    "container" = @{
        "name" = "docs"
    }
    "name" = "$indexName-datasource"
}

$indexerDefinition=@{
    "name" = "$indexName-indexer"
    "dataSourceName" = "$indexName-datasource"
    "skillsetName" = "$indexName-skillset"
    "targetIndexName" = "$indexName"
    "parameters" = @{
      "configuration" = @{
        "dataToExtract" = "contentAndMetadata"
        "parsingMode" = "default"
      }
    }
    "fieldMappings" = @(
      @{
        "sourceFieldName" = "metadata_storage_name"
        "targetFieldName" = "title"
      }
    )
}

InvokeAISearchChange `
    -searchServiceName $searchServiceName `
    -definitiontype "indexes" `
    -definition ($indexDefinition | ConvertTo-Json -Depth 100) `
    -token $token

InvokeAISearchChange `
    -searchServiceName $searchServiceName `
    -definitiontype "skillsets" `
    -definition ($skillsetDefinition | ConvertTo-Json -Depth 100) `
    -token $token

InvokeAISearchChange `
    -searchServiceName $searchServiceName `
    -definitiontype "datasources" `
    -definition ($dataSourceDefinition | ConvertTo-Json -Depth 100) `
    -token $token

InvokeAISearchChange `
    -searchServiceName $searchServiceName `
    -definitiontype "indexers" `
    -definition ($indexerDefinition | ConvertTo-Json -Depth 100) `
    -token $token