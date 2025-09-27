# Kjøring lokalt

API (Azure Functions lokalt)

cd azure_functions && func start

Frontend dev

cd frontend && npm ci && npm run dev

Prod-lignende server (lokalt)

npm ci && npm run build && npm start

Tips ved konflikt på port:

- Standardport er 8080. Hvis opptatt, kan du starte med tilfeldig port:

```sh
PORT=0 npm start
```

I lokalmodus proxies /api automatisk til <http://localhost:7071> hvis FUNCTIONS_BASE_URL ikke er satt.

Bygg & deploy:
– Sett GitHub Secret: AZUREAPPSERVICE_PUBLISHPROFILE (publish profile XML innhold)
– Push til main. Workflow bygger Vite, pakker server + node_modules og ZipDeploy’er.

Ruting og proxy:
– Klient kaller alltid /api/.
– Express proxy sender til FUNCTIONS_BASE_URL/api/.
– Ingen CORS-hode nødvendig fra browser → server same-origin.
