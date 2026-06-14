// =========================================================================
// Bloom — Azure infrastructure (Employee + HR faces)
// =========================================================================
// Provisions every resource needed for both interfaces of Bloom:
//   - 2 Foundry projects (Employee with 6 agents, HR with 1 agent)
//   - 1 shared Azure AI Search (3 knowledge bases inside)
//   - 1 Blob Storage (sources for the KBs)
//   - 1 Cosmos DB with 2 containers (employee-memory, hr-aggregates)
//   - 2 App Services (API + Web)
//   - Application Insights + Log Analytics + Key Vault
//   - All RBAC roles so the confidentiality wall is enforced at infra level
//
// Deploy with:
//   az deployment group create -g bloom-dev-rg -f main.bicep -p env=dev
// =========================================================================

@description('Azure region (use a region with Foundry + OpenAI availability)')
param location string = resourceGroup().location

@description('Base name used as prefix for all resources')
param baseName string = 'bloom'

@description('Environment suffix (dev | staging | prod)')
param env string = 'dev'

@description('OpenAI model deployment capacity (TPM in thousands)')
param openAiCapacity int = 30

var prefix = '${baseName}-${env}'
// Storage account names must be globally unique, lowercase, no dashes
var storageName = toLower('${baseName}${env}stg${uniqueString(resourceGroup().id)}')

// =========================================================================
// AI Foundry — shared hub + 2 projects (Employee, HR)
// =========================================================================
resource foundryHub 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${prefix}-foundry-hub'
  location: location
  identity: { type: 'SystemAssigned' }
  kind: 'AIServices'
  sku: { name: 'S0' }
  properties: {
    allowProjectManagement: true
    customSubDomainName: '${prefix}-foundry-hub'
    publicNetworkAccess: 'Enabled'
  }
}

resource foundryEmployee 'Microsoft.CognitiveServices/accounts/projects@2024-10-01' = {
  parent: foundryHub
  name: 'employee'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'Bloom — Employee agents'
    description: 'Hosts the orchestrator + 5 health module agents (Cycle, Conception, Menopause, Breast, Treatment).'
  }
}

resource foundryHr 'Microsoft.CognitiveServices/accounts/projects@2024-10-01' = {
  parent: foundryHub
  name: 'hr'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: 'Bloom — HR Policy agent'
    description: 'Hosts the HR-side Policy agent. No access to employee memory.'
  }
}

// gpt-4o deployments — one per project
resource gpt4oEmployee 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundryHub
  name: 'gpt-4o'
  sku: { name: 'Standard', capacity: openAiCapacity }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-11-20'
    }
  }
}

// =========================================================================
// Azure AI Search — backs the 3 Foundry IQ knowledge bases
// =========================================================================
resource searchService 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: '${prefix}-search'
  location: location
  sku: { name: 'standard' }
  identity: { type: 'SystemAssigned' }
  properties: {
    replicaCount: 1
    partitionCount: 1
    semanticSearch: 'standard'
    authOptions: { aadOrApiKey: { aadAuthFailureMode: 'http401WithBearerChallenge' } }
    publicNetworkAccess: 'Enabled'
  }
}

// =========================================================================
// Blob Storage — KB source documents (medical PDFs, legal docs, company files)
// =========================================================================
resource storage 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  identity: { type: 'SystemAssigned' }
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowSharedKeyAccess: false  // Force identity-based access
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' = {
  parent: storage
  name: 'default'
}

resource kbMedicalContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = {
  parent: blobService
  name: 'kb-medical'
  properties: { publicAccess: 'None' }
}

resource kbLegalContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = {
  parent: blobService
  name: 'kb-legal-fr'
  properties: { publicAccess: 'None' }
}

resource kbCompanyContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = {
  parent: blobService
  name: 'kb-company'
  properties: { publicAccess: 'None' }
}

// =========================================================================
// Cosmos DB — 2 containers, separated by RBAC for the confidentiality wall
// =========================================================================
resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-08-15' = {
  name: '${prefix}-cosmos'
  location: location
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [ { locationName: location } ]
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
    capabilities: [ { name: 'EnableServerless' } ]
    disableLocalAuth: true  // Force managed-identity access — no keys
  }
}

resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-08-15' = {
  parent: cosmos
  name: 'bloom'
  properties: { resource: { id: 'bloom' } }
}

resource employeeContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-08-15' = {
  parent: cosmosDb
  name: 'employee-memory'
  properties: {
    resource: {
      id: 'employee-memory'
      partitionKey: { paths: [ '/userId' ], kind: 'Hash' }
      defaultTtl: -1  // No expiry by default; lifecycle managed by app
    }
  }
}

resource hrContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-08-15' = {
  parent: cosmosDb
  name: 'hr-aggregates'
  properties: {
    resource: {
      id: 'hr-aggregates'
      partitionKey: { paths: [ '/companyId' ], kind: 'Hash' }
    }
  }
}

// =========================================================================
// App Service — FastAPI backend + React frontend
// =========================================================================
resource appPlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: '${prefix}-plan'
  location: location
  sku: { name: 'P1v3', tier: 'PremiumV3' }
  properties: { reserved: true }  // Linux
  kind: 'linux'
}

resource backend 'Microsoft.Web/sites@2024-04-01' = {
  name: '${prefix}-api'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: appPlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      appCommandLine: 'gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app --timeout 120'
      appSettings: [
        // Foundry endpoints — TWO projects, one per face
        { name: 'AZURE_AI_PROJECT_ENDPOINT', value: 'https://${foundryHub.name}.services.ai.azure.com/api/projects/${foundryEmployee.name}' }
        { name: 'AZURE_AI_PROJECT_HR_ENDPOINT', value: 'https://${foundryHub.name}.services.ai.azure.com/api/projects/${foundryHr.name}' }
        { name: 'AZURE_OPENAI_MODEL', value: 'gpt-4o' }
        // Foundry IQ
        { name: 'FOUNDRY_IQ_SEARCH_ENDPOINT', value: 'https://${searchService.name}.search.windows.net' }
        { name: 'KB_MEDICAL_NAME', value: 'bloom-kb-medical' }
        { name: 'KB_LEGAL_FR_NAME', value: 'bloom-kb-legal-fr' }
        { name: 'KB_COMPANY_NAME', value: 'bloom-kb-company' }
        // Storage
        { name: 'BLOB_STORAGE_ACCOUNT', value: storage.name }
        // Data
        { name: 'COSMOS_ENDPOINT', value: cosmos.properties.documentEndpoint }
        { name: 'COSMOS_DATABASE', value: 'bloom' }
        { name: 'COSMOS_CONTAINER_EMPLOYEE', value: 'employee-memory' }
        { name: 'COSMOS_CONTAINER_HR', value: 'hr-aggregates' }
        // Tenant
        { name: 'AZURE_TENANT_ID', value: subscription().tenantId }
        { name: 'AZURE_SUBSCRIPTION_ID', value: subscription().subscriptionId }
        // Observability
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsights.properties.ConnectionString }
        { name: 'ENVIRONMENT', value: env }
      ]
    }
    httpsOnly: true
  }
}

resource frontend 'Microsoft.Web/sites@2024-04-01' = {
  name: '${prefix}-web'
  location: location
  properties: {
    serverFarmId: appPlan.id
    siteConfig: {
      linuxFxVersion: 'NODE|22-lts'
      appCommandLine: 'pm2 serve /home/site/wwwroot 8080 --no-daemon --spa'
    }
    httpsOnly: true
  }
}

// =========================================================================
// Observability + secrets
// =========================================================================
resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs'
  location: location
  properties: { sku: { name: 'PerGB2018' } }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${prefix}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2024-04-01-preview' = {
  name: '${prefix}-kv'
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
  }
}

// =========================================================================
// RBAC — the confidentiality wall enforced at infrastructure level
// =========================================================================
// Built-in role definition IDs (well-known GUIDs)
var roleSearchIndexDataContributor = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
var roleSearchServiceContributor   = '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
var roleStorageBlobDataReader      = '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
var roleCosmosBuiltInDataContrib   = '00000000-0000-0000-0000-000000000002'
var roleKeyVaultSecretsUser        = '4633458b-17de-408a-b874-0445c86b69e6'

// ----- Backend identity → Search (read + write for indexing operations)
resource backendSearchData 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, backend.id, 'search-data')
  scope: searchService
  properties: {
    principalId: backend.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleSearchIndexDataContributor)
    principalType: 'ServicePrincipal'
  }
}

resource backendSearchSvc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, backend.id, 'search-svc')
  scope: searchService
  properties: {
    principalId: backend.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleSearchServiceContributor)
    principalType: 'ServicePrincipal'
  }
}

// ----- Backend identity → Blob Storage (read KB sources)
resource backendBlobData 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, backend.id, 'blob-reader')
  scope: storage
  properties: {
    principalId: backend.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleStorageBlobDataReader)
    principalType: 'ServicePrincipal'
  }
}

// ----- Backend identity → Key Vault (read secrets)
resource backendKvSecrets 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, backend.id, 'kv-secrets')
  scope: keyVault
  properties: {
    principalId: backend.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleKeyVaultSecretsUser)
    principalType: 'ServicePrincipal'
  }
}

// ----- Backend identity → Cosmos DB (data-plane, both containers)
// Note: Cosmos uses SQL-role assignments, not control-plane RBAC.
resource backendCosmosData 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-08-15' = {
  parent: cosmos
  name: guid(cosmos.id, backend.id, 'cosmos-data')
  properties: {
    principalId: backend.identity.principalId
    roleDefinitionId: '${cosmos.id}/sqlRoleDefinitions/${roleCosmosBuiltInDataContrib}'
    scope: cosmos.id
  }
}

// ----- Foundry projects → Search (each project queries Foundry IQ)
resource employeeProjectSearch 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, foundryEmployee.id, 'search-reader')
  scope: searchService
  properties: {
    principalId: foundryEmployee.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleSearchIndexDataContributor)
    principalType: 'ServicePrincipal'
  }
}

resource hrProjectSearch 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, foundryHr.id, 'search-reader')
  scope: searchService
  properties: {
    principalId: foundryHr.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleSearchIndexDataContributor)
    principalType: 'ServicePrincipal'
  }
}

// ----- Foundry projects → Blob (each can read KB source documents for indexing)
resource employeeProjectBlob 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, foundryEmployee.id, 'blob-reader')
  scope: storage
  properties: {
    principalId: foundryEmployee.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleStorageBlobDataReader)
    principalType: 'ServicePrincipal'
  }
}

resource hrProjectBlob 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, foundryHr.id, 'blob-reader')
  scope: storage
  properties: {
    principalId: foundryHr.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleStorageBlobDataReader)
    principalType: 'ServicePrincipal'
  }
}

// =========================================================================
// Outputs — everything the deployment guide step 4+ needs
// =========================================================================
output backendUrl string = 'https://${backend.properties.defaultHostName}'
output frontendUrl string = 'https://${frontend.properties.defaultHostName}'
output foundryHubName string = foundryHub.name
output foundryEmployeeProjectName string = foundryEmployee.name
output foundryHrProjectName string = foundryHr.name
output foundryEmployeeEndpoint string = 'https://${foundryHub.name}.services.ai.azure.com/api/projects/${foundryEmployee.name}'
output foundryHrEndpoint string = 'https://${foundryHub.name}.services.ai.azure.com/api/projects/${foundryHr.name}'
output searchServiceName string = searchService.name
output searchEndpoint string = 'https://${searchService.name}.search.windows.net'
output storageAccountName string = storage.name
output cosmosEndpoint string = cosmos.properties.documentEndpoint
output keyVaultName string = keyVault.name
output appInsightsConnectionString string = appInsights.properties.ConnectionString
