# Frontend Authentication

Use MSAL in the included browser frontend. The backend does not use a hardcoded group or service principal for semantic model execution.

Flow:

1. User signs in with Entra ID.
2. Frontend acquires a delegated token for the Power BI/Fabric API.
3. Frontend sends that token to `POST /chat`.
4. Backend calls Power BI Execute Queries API using the same user token.
5. Fabric semantic model permissions and RLS decide what the user can see.

Request example:

```http
POST /chat
Authorization: Bearer <user-powerbi-access-token>
Content-Type: application/json

{
  "question": "كم عدد الإشتراكات الجديدة هذا الشهر؟",
  "locale": "ar",
  "filters": {
    "start_date": "2026-05-01",
    "end_date": "2026-05-24"
  }
}
```

The user should normally have Read and Build permissions on the semantic model.

## App Registration

Create an Entra ID app registration for the browser UI:

- Platform: Single-page application
- Redirect URI local: `http://localhost:8000`
- Redirect URI local fallback: `http://127.0.0.1:8000`
- Redirect URI deployed: `https://<container-app-url>`
- API permissions: Power BI Service delegated permission `Dataset.Read.All`
- Admin consent: grant if your tenant requires it

If sign-in fails with `AADSTS900971: No reply address provided`, the app registration is missing the SPA redirect URI. Add `http://localhost:8000` under **Authentication > Single-page application redirect URIs** and retry sign-in from the same URL.

Then set:

```text
ENTRA_TENANT_ID=0a0efc93-807d-479a-818e-db0372a19c6a
ENTRA_FRONTEND_CLIENT_ID=<spa-app-client-id>
POWERBI_DELEGATED_SCOPES=https://analysis.windows.net/powerbi/api/Dataset.Read.All
```

When the user presses Sign in, the frontend acquires the Power BI token and sends it to the backend as:

```http
Authorization: Bearer <access-token>
```
