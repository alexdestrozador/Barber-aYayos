# Usa una imagen oficial de Python como base
FROM python:3.11

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos al contenedor
COPY . /app

# Instala dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto 8000 para acceder a Django
EXPOSE 8000

# Comando por defecto para correr el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
