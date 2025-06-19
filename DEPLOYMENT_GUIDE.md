# 🚀 Guía de Despliegue - Analizador de Espectros Armónicos

Esta guía te ayudará a desplegar tu aplicación Streamlit de análisis de espectros armónicos en diferentes plataformas.

## 📋 Requisitos Previos

Antes de desplegar, asegúrate de tener:

- ✅ Python 3.8 o superior
- ✅ Todos los archivos del proyecto
- ✅ `requirements.txt` actualizado
- ✅ Aplicación funcionando localmente

## 🎯 Opciones de Despliegue

### 1. 🌐 **Streamlit Community Cloud (GRATUITO) - RECOMENDADO**

La opción más fácil y gratuita para aplicaciones Streamlit.

#### **Pasos:**

1. **Subir código a GitHub:**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tu-usuario/tu-repositorio.git
   git push -u origin main
   ```

2. **Configurar Streamlit Cloud:**
   - Visita [share.streamlit.io](https://share.streamlit.io)
   - Inicia sesión con GitHub
   - Clic en "New app"
   - Selecciona tu repositorio
   - Archivo principal: `streamlit_app.py`
   - Despliega

#### **Ventajas:**

- ✅ Completamente gratuito
- ✅ Integración directa con GitHub
- ✅ Actualizaciones automáticas
- ✅ SSL incluido
- ✅ Perfecto para demos y prototipos

#### **Limitaciones:**

- ⚠️ Recursos limitados (1GB RAM)
- ⚠️ Se apaga tras inactividad
- ⚠️ No apto para producción pesada

---

### 2. 🐳 **Docker + Servicios Cloud**

Para mayor control y escalabilidad.

#### **Crear Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos
COPY requirements.txt .
COPY . .

# Instalar dependencias Python
RUN pip3 install -r requirements.txt

# Puerto de Streamlit
EXPOSE 8501

# Configuración de Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Comando de inicio
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### **Crear .dockerignore:**

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.git
.gitignore
README.md
Dockerfile
.dockerignore
analysis_sessions.db
*.html
*.pdf
```

---

### 3. ☁️ **Google Cloud Run (PAY-AS-YOU-GO)**

Excelente para producción con escalado automático.

#### **Pasos:**

1. **Instalar Google Cloud CLI:**

   ```bash
   # Windows
   # Descargar desde: https://cloud.google.com/sdk/docs/install

   # Linux/Mac
   curl https://sdk.cloud.google.com | bash
   ```

2. **Configurar proyecto:**

   ```bash
   gcloud auth login
   gcloud config set project TU-PROYECTO-ID
   gcloud auth configure-docker
   ```

3. **Construir y desplegar:**

   ```bash
   # Construir imagen
   docker build -t gcr.io/TU-PROYECTO/armonicos-app .

   # Subir imagen
   docker push gcr.io/TU-PROYECTO/armonicos-app

   # Desplegar en Cloud Run
   gcloud run deploy armonicos-app \
     --image gcr.io/TU-PROYECTO/armonicos-app \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 1
   ```

#### **Ventajas:**

- ✅ Escalado automático (0 a N instancias)
- ✅ Solo pagas por uso
- ✅ SSL automático
- ✅ Alta disponibilidad
- ✅ Integración con otros servicios Google

#### **Costos estimados:**

- **Gratuito:** Primeras 2M requests/mes
- **Producción ligera:** $5-20/mes
- **Producción pesada:** $50-200/mes

---

### 4. 🔷 **Microsoft Azure Container Instances**

#### **Pasos:**

1. **Instalar Azure CLI:**

   ```bash
   # Windows
   # Descargar desde: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

   # Linux
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```

2. **Configurar Azure:**

   ```bash
   az login
   az group create --name armonicos-rg --location eastus
   ```

3. **Crear Container Registry:**

   ```bash
   az acr create --resource-group armonicos-rg --name armonicosregistry --sku Basic
   az acr login --name armonicosregistry
   ```

4. **Construir y desplegar:**

   ```bash
   # Tag y push
   docker tag armonicos-app armonicosregistry.azurecr.io/armonicos-app:v1
   docker push armonicosregistry.azurecr.io/armonicos-app:v1

   # Crear container instance
   az container create \
     --resource-group armonicos-rg \
     --name armonicos-app \
     --image armonicosregistry.azurecr.io/armonicos-app:v1 \
     --cpu 1 \
     --memory 2 \
     --registry-login-server armonicosregistry.azurecr.io \
     --ports 8501 \
     --dns-name-label armonicos-unique-name
   ```

---

### 5. 🟠 **AWS ECS/Fargate**

Para ecosistema completo AWS.

#### **Pasos básicos:**

1. **Crear ECR Repository:**

   ```bash
   aws ecr create-repository --repository-name armonicos-app
   ```

2. **Construir y subir:**

   ```bash
   # Login
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com

   # Tag y push
   docker tag armonicos-app:latest ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/armonicos-app:latest
   docker push ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/armonicos-app:latest
   ```

3. **Crear servicio ECS Fargate** (usar AWS Console o CLI)

---

### 6. 💻 **VPS/Servidor Dedicado (Ubuntu)**

Para máximo control.

#### **Configuración del servidor:**

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip nginx git

# Clonar repositorio
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Instalar supervisor para gestión de procesos
sudo apt install supervisor

# Crear configuración supervisor
sudo nano /etc/supervisor/conf.d/armonicos.conf
```

#### **Configuración Supervisor (/etc/supervisor/conf.d/armonicos.conf):**

```ini
[program:armonicos]
command=/ruta/a/tu/proyecto/venv/bin/streamlit run streamlit_app.py --server.port=8501
directory=/ruta/a/tu/proyecto
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/armonicos.log
environment=HOME="/home/ubuntu",USER="ubuntu"
```

#### **Configuración Nginx (/etc/nginx/sites-available/armonicos):**

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### **Activar configuraciones:**

```bash
# Habilitar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start armonicos

# Habilitar nginx
sudo ln -s /etc/nginx/sites-available/armonicos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL con Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

---

## 🔧 **Configuraciones Adicionales para Producción**

### **Variables de Entorno (.env):**

```env
# Para producción
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Base de datos
DB_PATH=./production_sessions.db

# Configuraciones de la app
MAX_UPLOAD_SIZE=200
SESSION_TIMEOUT=3600
```

### **Configuración Streamlit (config.toml):**

Crear archivo `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#3498db"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
```

---

## 📊 **Recomendaciones por Caso de Uso**

### **🧪 Desarrollo/Demo:**

- **Opción:** Streamlit Community Cloud
- **Tiempo setup:** 5 minutos
- **Costo:** Gratuito

### **🏢 Producción Pequeña (1-50 usuarios):**

- **Opción:** Google Cloud Run o Azure Container Instances
- **Tiempo setup:** 30 minutos
- **Costo:** $10-30/mes

### **🏭 Producción Empresarial (50+ usuarios):**

- **Opción:** AWS ECS/Fargate o VPS dedicado
- **Tiempo setup:** 2-4 horas
- **Costo:** $50-500/mes

### **🔒 On-premise/Seguridad alta:**

- **Opción:** VPS/Servidor dedicado
- **Tiempo setup:** 4-8 horas
- **Costo:** Según infraestructura

---

## 🚨 **Consideraciones de Seguridad**

### **Para Producción:**

1. **Variables de entorno:** Nunca hardcodear credenciales
2. **HTTPS:** Siempre usar SSL en producción
3. **Firewall:** Configurar reglas apropiadas
4. **Backups:** Base de datos de sesiones
5. **Monitoreo:** Logs y métricas de aplicación
6. **Rate limiting:** Prevenir abuso
7. **Authentication:** Considerar autenticación si es necesario

### **Ejemplo .env para producción:**

```env
# Secrets
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=tu-clave-secreta-muy-larga

# App config
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

---

## 📈 **Monitoreo y Mantenimiento**

### **Logs importantes a monitorear:**

- Errores de aplicación
- Tiempo de respuesta
- Uso de memoria/CPU
- Uploads fallidos
- Sesiones creadas/eliminadas

### **Métricas clave:**

- Usuarios activos
- Archivos procesados por día
- Tiempo promedio de procesamiento
- Uso de almacenamiento

---

## 🆘 **Solución de Problemas Comunes**

### **Error: "Address already in use"**

```bash
# Matar procesos en puerto 8501
sudo lsof -ti:8501 | xargs kill -9
```

### **Error: "Permission denied"**

```bash
# Dar permisos correctos
chmod +x streamlit_app.py
chown -R usuario:usuario ./proyecto
```

### **Error: "Module not found"**

```bash
# Verificar instalación
pip list
pip install -r requirements.txt --upgrade
```

---

## 🎯 **Próximos Pasos Recomendados**

1. **Empezar:** Streamlit Community Cloud para pruebas
2. **Escalar:** Google Cloud Run cuando necesites más recursos
3. **Empresarial:** Migrar a AWS/Azure con autenticación
4. **Optimizar:** Monitoreo y analytics avanzados

---

**¿Necesitas ayuda específica con alguna plataforma? ¡Déjame saber y te ayudo con los detalles!** 🚀
