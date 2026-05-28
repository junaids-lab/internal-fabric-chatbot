# Azure Container Apps Deployment

Build and push the container image to Azure Container Registry, then deploy to Azure Container Apps with the environment variables from `.env.example`.

Runtime requirements:

- public or private ingress for the API, depending on your frontend
- managed identity if Search or Foundry calls use keyless auth
- Application Insights for traces and failed semantic model calls
- CORS restricted to your actual frontend origin

The backend is stateless. Session history can be added later with Cosmos DB, Redis, or the Foundry thread store.

If `AZURE_AI_FOUNDRY_API_KEY` is blank, assign the Container App managed identity the required Foundry project/application role so `DefaultAzureCredential` can request a `https://ai.azure.com/.default` token.
