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
- GitHub Actions-workflowen `main_sparcollection-web.yml` gjør det samme i CI før det pakkes til `release.zip`.

# Produksjonsdrift

- Frontend (SPA): <https://sparcollection-web-faasfhqd6lxhbasgn.northeurope-01.azurewebsites.net>
- API (Azure Functions): <https://sparcollection-azfunc-fffjcpb5cphnfhac.northeurope-01.azurewebsites.net/api>
- Service Bus: queue `list-updates` (krever `SERVICEBUS_CONNECTION` og valgfritt `SERVICEBUS_QUEUE_NAME` i Function App settings).

# GitHub-secrets

- `APPLICATION_PUBLISH_PROFILE` – publish profile for App Service (frontend).
- `AZUREAPPSERVICE_PUBLISHPROFILE_FUNCTIONS` – publish profile for Function App (API).

# Deploy

- Frontend-workflowen `main_sparcollection-web.yml` bygger Vite med `VITE_API_URL` satt til API-domenet over og ZipDeployer laster opp `frontend/dist/` til App Service.
- Functions-workflowen `main_sparcollection-azfunc.yml` pakker `azure_functions/` til `azure_functions-release.zip` og deployer til Function App.
- Sett startup command på App Service til `pm2 serve /home/site/wwwroot --spa --no-daemon` (eller tilsvarende) slik at alle SPA-ruter faller tilbake til `index.html`.
- Aktiver CORS på Function App for `https://sparcollection-web-faasfhqd6lxhbasgn.northeurope-01.azurewebsites.net`.
- Legg inn `SERVICEBUS_CONNECTION` og `SERVICEBUS_QUEUE_NAME` i Function App settings (ikke i repo).
