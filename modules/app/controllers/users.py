# Importo las librarías necesarias
import os
import urllib, requests, datetime
from flask import request, redirect, json, jsonify
from app import app, mongo
import logger

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(
    __name__, filename=os.path.join(ROOT_PATH, 'output.log'))


@app.route('/login') # Url para realizar la autentización en Clave única
def user():
    # Seteo los parametros requeridos por la documentación de Clave única
    params = {
        "client_id": os.environ.get('CLIENTID'), # Variables de entorno seteadas en ./docker-compose.yml
        "state": os.environ.get('TOKENCSRF'), # Variables de entorno seteadas en ./docker-compose.yml
        "response_type":"code",
        "scope":"openid run name email",
        "redirect_uri":"http://localhost:8000/redirect/clave-unica" # URI informada para callback redirect
    }
    params_db = {
        "paso_uno": {
            "client_id": os.environ.get('CLIENTID'),
            "state": os.environ.get('TOKENCSRF'),
            "response_type":"code",
            "scope":"openid run name email",
            "redirect_uri":"http://localhost:8000/redirect/clave-unica"
        },
        "created_at" : datetime.datetime.now(),
        "updated_at" : datetime.datetime.now() 
    }
    # Guardo los datos enviados para tracking de la transacción 
    mongo.db.users.insert_one(params_db).inserted_id
    # Realizo la petición para el logueo en Clave única 
    return redirect('https://accounts.claveunica.gob.cl/openid/authorize/?'+urllib.parse.urlencode(params))

@app.route('/redirect/clave-unica') # Callback redirect
def redirect_clave_unica():
    try:
        # Obtengo los parámetros 
        code = request.args.get('code')
        state = request.args.get('state')
        if (state != "" and state == os.environ.get('TOKENCSRF')) and code != '': #Valido los parámetros 
            last_insert = mongo.db.users.find().sort("_id", -1).limit(1)
            try:
                for result_object in last_insert:
                    # Registro los datos de la respuesta del paso 1
                    mongo.db.users.update_one(
                        {
                            '_id':result_object['_id']
                        }, 
                        {
                            '$set': {
                                'updated_at':datetime.datetime.now(),
                                'paso_uno_result':{
                                    'state':state,
                                    'code':code
                                }
                            }
                        }
                    )
            except:
                return 'Ha ocurrido un error, por favor intente nuevamente'
            url = "https://accounts.claveunica.gob.cl/openid/token/" # Url para obtener el access_token
            # Parámetros requeridos
            payload = {
                'client_id': os.environ.get('CLIENTID'),# Variables de entorno seteadas en ./docker-compose.yml
                'client_secret': os.environ.get('CLIENTSECRET'),# Variables de entorno seteadas en ./docker-compose.yml
                'redirect_uri': 'http://localhost:8000/redirect/clave-unica',# URI informada para callback redirect
                'grant_type': 'authorization_code',
                'code': code, # Código obtenido en la petición anterior
                'state': os.environ.get('TOKENCSRF')# Variables de entorno seteadas en ./docker-compose.yml
            }
            files = []
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            try:
                # Realizo la petición por POST para obtener el token
                response = requests.request("POST", url, headers=headers, data = payload, files = files)
                # Registro los datos del paso 2
                mongo.db.users.update_one(
                    {
                        'paso_uno_result':{
                            'state':state,
                            'code':code
                        }
                    }, 
                    {
                        '$set': {
                            'updated_at':datetime.datetime.now(),
                            'paso_dos':payload,
                            'paso_dos_result':response.text
                        }
                    }
                )
            
            except:
                return 'Ha ocurrido un problema al realizar la petición a ' + url
            data = json.loads(response.text) # Parseo la respuesta 
            if 'access_token' in data: # Válido que obtuve el token
                url = 'https://www.claveunica.gob.cl/openid/userinfo/' # Url para obtener los datos del usuario logueado
                # Seteo la cabecera requerida para la petición
                headers = {
                    "authorization": "Bearer "+ data['access_token']
                } 
                try:
                    # Realizo la peticion para obtener los datos
                    response = requests.request("POST", url, headers=headers)
                    # Registro los datos del paso 3
                    mongo.db.users.update_one(
                        {
                            'paso_uno_result':{
                                'state':state,
                                'code':code
                            }
                        }, 
                        {
                            '$set': {
                                'updated_at':datetime.datetime.now(),
                                'paso_tres':headers,
                                'paso_tres_result':response.text
                            }
                        }
                    )
                    user = json.loads(response.text)
                    if 'RolUnico' in user:
                        return response.text # Retorno los datos del usuario logueado
                    else:
                        return 'No fue posible obtener al usuario'
                except:
                    return 'Ha ocurrido un problema al realizar la petición a ' + url                    
            else:
                return 'No fue posible obtener el token'
        return 'Parámetros incorrectos.'
    except:
        return 'Ha ocurrido un error al intentar autenticar al usuario'