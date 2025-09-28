# Spar Collection - Shopping List Management System

A modern web application for managing shopping lists, built with React frontend and Azure Functions backend.

## 🏗️ Architecture

### Frontend
- **Technology**: React + TypeScript + Vite
- **Deployment**: Azure Web App
- **URL**: https://sparcollection-web-faa4hqd6hxbhaqgm.northeurope-01.azurewebsites.net

### Backend
- **Technology**: Azure Functions (Python)
- **Database**: Azure SQL Database
- **URL**: https://sparcollection-azfunc-fffjcpb5cphnfhac.northeurope-01.azurewebsites.net

## 📁 Project Structure

```
SparCollection/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   └── api.ts          # API client functions
│   └── package.json
├── azure_functions/         # Azure Functions backend
│   ├── shared_code/        # Shared utilities
│   │   ├── database.py     # Database operations
│   │   └── servicebus.py   # Event publishing
│   ├── lists_get/          # Get all lists endpoint
│   ├── list_get/           # Get single list endpoint
│   ├── item_update/        # Update item status endpoint
│   └── list_complete/      # Complete list endpoint
└── .github/workflows/      # CI/CD pipelines
```

## 🚀 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lists_get?shopId=NO-TR-001` | Get all shopping lists |
| GET | `/api/list_get?listId=abc123&shopId=NO-TR-001` | Get specific list |
| POST | `/api/item_update/{listId}/{itemId}` | Update item status |
| POST | `/api/list_complete/{listId}` | Mark list as completed |

## 🗄️ Database Schema

### Lists Table
- `id` (NVARCHAR) - Primary key
- `title` (NVARCHAR) - List title
- `status` (NVARCHAR) - active/completed
- `shop_id` (NVARCHAR) - Shop identifier
- `created_at` (DATETIME2) - Creation timestamp
- `updated_at` (DATETIME2) - Last update timestamp

### Items Table
- `id` (NVARCHAR) - Primary key
- `list_id` (NVARCHAR) - Foreign key to lists
- `name` (NVARCHAR) - Item name
- `qty` (INT) - Quantity
- `status` (NVARCHAR) - pending/collected/unavailable
- `version` (INT) - Version for optimistic locking
- `created_at` (DATETIME2) - Creation timestamp
- `updated_at` (DATETIME2) - Last update timestamp

## 🛠️ Development

### Prerequisites
- Node.js 18+
- Python 3.10+
- Azure Functions Core Tools
- Azure CLI

### Local Development

1. **Start Backend (Azure Functions)**
   ```bash
   cd azure_functions
   source ../.venv/bin/activate
   func start
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access Application**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:7071

### Environment Variables

#### Frontend (.env)
```bash
# Comment out for local development (uses Vite proxy)
# VITE_API_URL=https://sparcollection-azfunc-fffjcpb5cphnfhac.northeurope-01.azurewebsites.net/api
```

#### Backend (local.settings.json)
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "SQL_CONNECTION_STRING": "Server=tcp:sparcollection-web-server.database.windows.net,1433;Database=sparcollection-web-database;Authentication=Active Directory Default;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;",
    "SERVICEBUS_CONNECTION": "Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=<policy>;SharedAccessKey=<key>",
    "SERVICEBUS_QUEUE_NAME": "list-updates"
  }
}
```

## 🚀 Deployment

The application uses GitHub Actions for automated deployment:

1. **Frontend Deployment** (`.github/workflows/main_sparcollection-web.yml`)
   - Builds React app with production API URL
   - Deploys to Azure Web App

2. **Backend Deployment** (`.github/workflows/main_sparcollection-azfunc.yml`)
   - Installs Python dependencies
   - Deploys to Azure Functions
   - Sets SQL connection string

## 🔧 Configuration

### CORS Settings
The Azure Functions are configured to allow requests from:
- `http://localhost:3000` (local development)
- `http://localhost:4173` (Vite preview)
- `http://localhost:5173` (Vite dev server)
- `http://localhost:5174` (Vite dev server fallback)
- `https://sparcollection-web-faa4hqd6hxbhaqgm.northeurope-01.azurewebsites.net` (production)

### Database Connection
- Uses Azure SQL Database with Active Directory authentication
- Connection string is set automatically during deployment
- Database tables are created automatically on first run

## 🐛 Troubleshooting

### Common Issues

1. **"Failed to fetch" error locally**
   - Ensure `VITE_API_URL` is commented out in `.env`
   - Check that Azure Functions are running on port 7071

2. **HTTP 500 errors in production**
   - Check Azure Portal logs for detailed error messages
   - Verify SQL connection string is set correctly
   - Ensure database exists and is accessible

3. **CORS errors**
   - Verify frontend URL is in `allowedOrigins` in `host.json`
   - Check that requests include proper headers

### Logs
- **Frontend**: Browser Developer Tools → Console
- **Backend**: Azure Portal → Function App → Monitor → Logs
- **Database**: Azure Portal → SQL Database → Query editor

## 📝 Features

- ✅ Create and manage shopping lists
- ✅ Add items with quantities
- ✅ Mark items as collected or unavailable
- ✅ Complete lists
- ✅ Real-time updates
- ✅ Responsive design
- ✅ Offline support (PWA)
- ✅ Event publishing for integrations

## 🔮 Future Enhancements

- User authentication and authorization
- Multiple shops support
- Item categories and search
- Shopping list templates
- Mobile app
- Real-time collaboration
- Analytics and reporting