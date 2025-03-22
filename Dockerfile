# Imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1

# Exponer el puerto que usa Dash
EXPOSE 8050

# Comando para ejecutar la aplicación
CMD ["python", "Aplic_atm.py"]