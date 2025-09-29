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
- **Database**: PostgreSQL (Azure Database for PostgreSQL)
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
- `id` (VARCHAR) - Primary key
- `shop_id` (VARCHAR) - Shop identifier
- `status` (VARCHAR) - active/completed
- `created_at` (TIMESTAMP) - Creation timestamp
- `completed_at` (TIMESTAMP) - Completion timestamp
- `completed_by` (VARCHAR) - Employee ID who completed

### spar.list_items Table
- `id` (VARCHAR) - Primary key
- `list_id` (VARCHAR) - Foreign key to lists
- `sku` (VARCHAR) - Item SKU
- `name` (VARCHAR) - Item name
- `qty_requested` (INTEGER) - Requested quantity
- `qty_collected` (INTEGER) - Collected quantity
- `status` (VARCHAR) - pending/collected/unavailable
- `version` (INTEGER) - Version for optimistic locking

## 🛠️ Development

### Prerequisites
- Node.js 22.12.0
- Python 3.10+
- Azure Functions Core Tools
- Azure CLI
- PostgreSQL client libraries (psycopg2)

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
