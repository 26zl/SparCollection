# Lokal kjøring

1. Start Azure Functions-APIet:
   ```sh
   cd azure_functions
   func start
   ```

2. Klargjør frontend-variabler. Kopier `.env.example` til f.eks. `frontend/.env.local` og sett
   ```
   VITE_API_URL=http://localhost:7071/api
   ```
   (Hvis du lar den stå tom, brukes `/api` og Vite-proxyen sender trafikk til Functions på port 7071.)

3. Kjør Vite-devserver:
   ```sh
   npm --prefix frontend ci
   npm --prefix frontend run dev
   ```

# Produksjonsbygg

- Kjør `npm run build` i repo-roten. Scriptet kjører `npm ci` og `npm run build` inne i `frontend/` og resultatet havner i `frontend/dist/`.
- Arbeidsflyten `webapp-deploy.yml` gjør det samme i GitHub Actions og pakker innholdet i `frontend/dist/` til `release.zip`.

# Deploy

- App Service publish profile legges i secret `APPLICATION_PUBLISH_PROFILE`.
- `webapp-deploy.yml` bygger med `VITE_API_URL=https://sparcollection-azfunc.azurewebsites.net/api` og ZipDeployer pakker `frontend/dist/` direkte til App Service.
- Husk å aktivere CORS på Functions-app-en for hostnavnet til App Service.

Backend (Azure Functions) deployes fortsatt via `main_sparcollection-azfunc.yml`.
