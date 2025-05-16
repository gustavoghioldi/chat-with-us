CookBook
=====
Descargar e intalar:
Docker
Ollama
git
dbeaver
en caso de utilizar windows instalar un ambiente de wsl2  
python 3.12.3

en terminal de ubuntu
============

 docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  agnohq/pgvector:16

docker run -d \
  -e POSTGRES_PASSWORD=barba \
  -p 5531:5432 \
  -v appvolume:/var/lib/postgresql/data \
  -p 5432:5432 \
  --name pgapp \
  postgres:latest


desde dbeaver crear una base de datos con el nombre barbadb

crear un ambiente de python: python3 -m venv .venv

activar el source: source .venv/bin/activate 

instalar dependencias: pip install -r requirements.txt

pedir el archivo .env y copiarlo en la carpeta principal

desde el ide correr MIGRATE

correr python manage.py runserver
