# Docker Setup for Personal Assistant

## Quick Start

### 1. Prerequisites
- Docker installed on your system
- Docker Compose installed

### 2. Environment Setup
Create a `.env` file in the personal_assistant directory:

```env
# Required Environment Variables
GOOGLE_API_KEY=your-google-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_API_KEY=your-supabase-api-key

# Optional Environment Variables
USER_ID=default_user
JWT_SECRET=your-super-secret-jwt-key
```

### 3. Build and Run
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Services Overview

The Docker setup runs all your personal assistant services:

| Service | Port | Description |
|---------|------|-------------|
| API Server | 8000 | Main API endpoint for React frontend |
| Meeting Server | 8100 | Handles meeting management |
| Expense Server | 8200 | Handles expense tracking |
| Orchestrator Server | 8300 | Routes requests between services |

## Accessing Services

### Health Check
```bash
curl http://localhost:8000/health
```

### API Endpoints
```bash
# Expense queries
curl -X POST http://localhost:8000/expense/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show my expenses"}'

# General queries  
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are my meetings today?"}'
```

## Development

### Docker Commands
```bash
# Build only
docker-compose build

# Start specific service
docker-compose up expense-server

# View logs for specific service
docker-compose logs personal-assistant

# Execute commands in container
docker-compose exec personal-assistant bash

# Restart services
docker-compose restart
```

### File Structure
```
personal_assistant/
├── Dockerfile              # Main container definition
├── docker-compose.yml      # Service orchestration
├── .dockerignore           # Files to exclude from build
├── requirements.txt        # Python dependencies
├── servers/               # All server files
├── agents/                # AI agents
├── mcp_tools/             # MCP tools
└── utils/                 # Utility functions
```

## Customization

### Modify Ports
Edit `docker-compose.yml` to change port mappings:
```yaml
ports:
  - "3000:8000"   # Change host port to 3000
```

### Add Environment Variables
Edit `docker-compose.yml`:
```yaml
environment:
  - YOUR_CUSTOM_VAR=${YOUR_CUSTOM_VAR}
```

### Volume Mounts
Data and logs are mounted to host directories:
```yaml
volumes:
  - ./data:/app/data      # Data persistence
  - ./logs:/app/logs      # Log files
```

## Troubleshooting

### Container Won't Start
```bash
# Check build logs
docker-compose build --no-cache

# Check service logs
docker-compose logs personal-assistant
```

### Port Conflicts
```bash
# Check what's using ports
lsof -i :8000
lsof -i :8200

# Stop conflicting services or change ports
```

### Environment Variables
```bash
# Check if .env file exists
ls -la .env

# Verify environment in container
docker-compose exec personal-assistant env | grep GOOGLE_API_KEY
```

### Database Connection
```bash
# Test Supabase connection
docker-compose exec personal-assistant python -c "
from utils.supabase_config import SupabaseManager
manager = SupabaseManager()
print('Connected:', manager.is_connected())
"
```

## Production Deployment

### Security Considerations
1. **Environment Variables**: Use Docker secrets or external key management
2. **Network Security**: Use internal networks for service communication
3. **Resource Limits**: Add CPU and memory limits
4. **Health Checks**: Configure proper health check endpoints

### Example Production Config
```yaml
# docker-compose.prod.yml
services:
  personal-assistant:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        max_attempts: 3
```

### Using with Reverse Proxy
```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Benefits

✅ **Consistent Environment**: Same setup across all machines  
✅ **Easy Deployment**: One command to start everything  
✅ **Service Isolation**: Each service runs independently  
✅ **Port Management**: All ports clearly defined  
✅ **Development Ready**: Volume mounts for live development  
✅ **Production Ready**: Health checks and restart policies