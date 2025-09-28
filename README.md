# Spar Collection - Shopping List Management System

A modern web application for managing shopping lists, built with React frontend and Azure Functions backend. This system allows employees to manage shopping lists with offline support and real-time updates.

## 🏗️ Architecture

### Frontend
- **Technology**: React + TypeScript + Vite
- **Deployment**: Azure Web App
- **URL**: https://sparcollection-web-faa4hqd6hxbhaqgm.northeurope-01.azurewebsites.net
- **Features**: Offline support, PWA, responsive design

### Backend
- **Technology**: Azure Functions (Python)
- **Database**: Azure SQL Database
- **URL**: https://sparcollection-azfunc-fffjcpb5cphnfhac.northeurope-01.azurewebsites.net
- **Features**: RESTful API, event publishing, payment processing

## 📁 Project Structure

```
SparCollection/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   │   ├── ItemCard.tsx
│   │   │   └── CreateListForm.tsx
│   │   ├── pages/          # Page components
│   │   │   ├── Home.tsx
│   │   │   └── ListDetail.tsx
│   │   ├── api.ts          # API client functions
│   │   └── offline.ts      # Offline support
│   └── package.json
├── azure_functions/         # Azure Functions backend
│   ├── shared_code/        # Shared utilities
│   │   ├── data.py         # Database operations
│   │   └── servicebus.py   # Event publishing
│   ├── lists_get/          # Get all lists endpoint
│   ├── list_get/           # Get single list endpoint
│   ├── item_update/        # Update item status endpoint
│   ├── list_complete/      # Complete list endpoint
│   ├── list_create/        # Create new list endpoint
│   ├── list_delete/        # Delete list endpoint
│   └── payment_engine/     # Payment processing
└── .github/workflows/      # CI/CD pipelines
```

## 🚀 Local Development

### Standard Ports
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:7071

### Start Commands
```bash
# Backend (Terminal 1)
cd azure_functions
source .venv/bin/activate
func start --port 7071

# Frontend (Terminal 2)  
cd frontend
npm run dev
```

## 🚀 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lists_get?shopId=NO-TR-001` | Get all shopping lists |
| GET | `/api/list_get?listId=abc123&shopId=NO-TR-001` | Get specific list |
| POST | `/api/item_update/{listId}/{itemId}` | Update item status |
| POST | `/api/list_complete/{listId}?shopId=NO-TR-001&employeeId=emp123` | Mark list as completed |
| POST | `/api/list_create` | Create new list |
| DELETE | `/api/list_delete/{listId}?shopId=NO-TR-001` | Delete list |

### Service Bus Events
- `list-created` - When a new list is created
- `list-completed` - When a list is marked as completed
- `item-updated` - When an item status is updated
- `list-deleted` - When a list is deleted

## 🗄️ Database Schema

### spar.lists Table
- `id` (NVARCHAR) - Primary key
- `shop_id` (NVARCHAR) - Shop identifier
- `status` (NVARCHAR) - active/completed
- `created_at` (DATETIME2) - Creation timestamp
- `completed_at` (DATETIME2) - Completion timestamp
- `completed_by` (NVARCHAR) - Employee ID who completed

### spar.list_items Table
- `id` (NVARCHAR) - Primary key
- `list_id` (NVARCHAR) - Foreign key to lists
- `name` (NVARCHAR) - Item name
- `qty_requested` (INT) - Requested quantity
- `qty_collected` (INT) - Collected quantity
- `status` (NVARCHAR) - pending/collected/unavailable
- `version` (INT) - Version for optimistic locking

## 🛠️ Development

### Prerequisites
- Node.js 22.12.0
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
    "SQL_CONNECTION_STRING": "Server=tcp:sparcollection-web-server.database.windows.net,1433;Database=sparcollection-web-database;User Id=sparcollection-web-server-admin;Password=QZ4$cNUS4$0weaBP;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;",
    "SERVICEBUS_CONNECTION": "Endpoint=sb://sparcollectionbus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=aPBjWbFZuIL6NI4yQ4hxjWa2+umGWtSdV+ASbNhCJ/c=",
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
- `http://localhost:5173` (Vite dev server)
- `https://sparcollection-web-faa4hqd6hxbhaqgm.northeurope-01.azurewebsites.net` (production)

### Database Connection
- Uses Azure SQL Database with SQL Server authentication
- Connection string is set automatically during deployment
- Database tables are created manually in Azure Portal

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
- ✅ Delete lists
- ✅ Real-time updates
- ✅ Responsive design
- ✅ Offline support (PWA)
- ✅ Event publishing for integrations
- ✅ Payment processing simulation
- ✅ Dynamic shop ID determination
- ✅ Optimistic locking for concurrent updates

## 🎯 Case Study Requirements

This project fulfills the requirements for the Spar Collection case study:

### Functional Requirements
- ✅ Web-based application
- ✅ Tablets receive lists to be collected
- ✅ Employees can mark items as collected or unavailable
- ✅ Lists are transferred to payment engine when completed
- ✅ Offline support is implemented

### Non-Functional Requirements
- ✅ Handles 200 concurrent users
- ✅ Processes 10,000 lists per day
- ✅ Average list size: 500kb
- ✅ Offline support with PWA
- ✅ High SLA with Azure infrastructure
- ✅ Queue-based list delivery via Service Bus

## 🔮 Future Enhancements

- User authentication and authorization
- Multiple shops support
- Item categories and search
- Shopping list templates
- Mobile app
- Real-time collaboration
- Analytics and reporting