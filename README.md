# Integración Clave Única
---
## Requisitos  
Para poder levantar el aplicativo es necesario tener instalado docker y docker-compose, en caso de no tenerlos instalados puede revisar la documentacion oficial de [Docker](https://docs.docker.com/install/) donde se explica como instalar ambas herramientas.
## Configuración inicial
Antes de levantar el aplicativo es necesario configurar algunos parametros dentro del archivo docker-compose.yml
```yml
ports:
    - "8000:8000" #El puerto debe ser de acuerdo al informado a Clave Única en la URL callback redirect  
volumes:
    - .:/app
environment:
    - ENV=development #ambiente de trabajo
    - PORT=8000 #puerto del aplicativo
    - DB=mongodb://mongodb:27017/logClaveUnica # Base de datos 
    - CLIENTID= # client_id entregado por Clave única 
    - CLIENTSECRET=  # client_secret entregado por Clave única 
    - TOKENCSRF=  # Token_csrf necesario para la validación de los datos 
```
Una vez realizada esta configuración, ya se puede levantar el sistema.
## Contruir aplicativo
Para construir el aplicativo, debe situarse en el directorio modules y desde ahi ejecutar el siguiente comando:
```bash 
docker-compose up -d
```

Una vez que finalice la construcción, el aplicativo estara listo para utilizarse.
## Bajar aplicativo
Para bajar el aplicativo, debe situarse en el directorio modules y ejecutar el comando 
```bash 
docker-compose down
```
##Acceder a la base de datos 
Para acceder a la base de datos a revisar el log de la aplicación, debe acceder al contenedor con el siguiente comando:
```bash 
docker exec -it [nombre] bash
```
Una vez dentro, ejecutar:
```bash 
mongo
```
De esta manera accedera a la base de datos. Para revisar el log ejecutar los siguientes comandos:
```bash 
use logClaveUnica
db.users.find().pretty()
```
La función **pretty()** es opcional, esto solo es para que los datos se muestren de manera mas legíble.
