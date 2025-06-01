from flask import Flask, render_template, request,session,redirect,url_for
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

app = Flask(__name__)

#para llevar  el secreto de la app desde las variables de entorno (recomendado para seguridad)
app.secret_key = os.environ.get('secret_key')
if not app.secret_key:
    app.secret_key = 'secret_key'


# Versión de la aplicación
VERSION_APP = "Versión 2.2 del Mayo 22 del 2025"
CREATOR_APP = "Juan Carlos Rodriguez/https://github.com/juancarloswill/BigDataApp"
mongo_uri = os.environ.get("MONGODB_URI")

if not mongo_uri:
    uri = 'mongodb+srv://jrodriguezg42:ca54sa69@dbcentral.kbsaqft.mongodb.net/?retryWrites=true&w=majority&appName=DbCentral'
    mongo_uri = uri

def connect_mongo():
    try:
        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        print("Conexión exitosa a MongoDB")
        return client 
    except Exception as e:
        print(f"Error connecting to MondoDB: {e}")
        return None
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('name')
        email = request.form.get('email')
        mensaje = request.form.get('message')

        client = connect_mongo()
        if client:
            db = client['BaseCentral']
            contactos_collection = db['contacto']

            contacto_data = {
                'nombreContacto': nombre,
                'email': email,
                'mensaje': mensaje
            }
            contactos_collection.insert_one(contacto_data)
            client.close()

        # Pasamos "enviado=True" al HTML
        return render_template('contacto.html', nombre=nombre, email=email, mensaje=mensaje, enviado=True)

    return render_template('contacto.html', enviado=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        client = connect_mongo()
        if client:   
            db= client['administracion']   
            seguridad_colection= db['seguridad']
            
            username = request.form.get('username')
            password = request.form.get('password')

            #verificar las credenciales
            user = seguridad_colection.find_one({'usuario': username, 'pass': password})
            if user:
                session['usuario'] = username
                return redirect(url_for('gestion_proyecto'))
            else:
                error_message = "Usuario o contraseña incorrectos."
                return render_template('login.html', error_message=error_message, version=VERSION_APP,creador=CREATOR_APP)    

        else:
            error_message = "No se tiene conectividad con la base de datos."
            return render_template('login.html', error_message=error_message, version=VERSION_APP,creador=CREATOR_APP)        

    return render_template('login.html', version=VERSION_APP,creador=CREATOR_APP)   

@app.route('/gestion_proyecto', methods=['GET', 'POST'])
def gestion_proyecto():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    try:
        client = connect_mongo()
        # Obtener lista de bases de datos
        databases = client.list_database_names()
        # Eliminar bases de datos del sistema
        system_dbs = ['admin', 'local', 'config']
        databases = [db for db in databases if db not in system_dbs]
        
        selected_db = request.form.get('database') if request.method == 'POST' else request.args.get('database')
        collections_data = []
        
        if selected_db:
            db = client[selected_db]
            collections = db.list_collection_names()
            for index, collection_name in enumerate(collections, 1):
                collection = db[collection_name]
                count = collection.count_documents({})
                collections_data.append({
                    'index': index,
                    'name': collection_name,
                    'count': count
                })
        
        return render_template('gestion/index.html',
                            databases=databases,
                            selected_db=selected_db,
                            collections_data=collections_data,
                            version=VERSION_APP,
                            creador=CREATOR_APP,
                            usuario=session['usuario'])
    except Exception as e:
        return render_template('gestion/index.html',
                            error_message=f'Error al conectar con MongoDB: {str(e)}',
                            version=VERSION_APP,
                            creador=CREATOR_APP,
                            usuario=session['usuario'])

       
def get_collection_data(selected_db):
    client = connect_mongo()
    collections_data=[]
    if client and selected_db:
        db = client[selected_db]
        try:
            collections = db.list_collection_names()
            for index, collection_name in enumerate(collections):
                count = db[collection_name].count_documents({})
                collections_data.append({
                    'index': index+1,
                    'name': collection_name,
                    'count': count
                })

                                                
            
        except Exception as e:
            print(f"Error al obtener las colecciones de la {selected_db}: {e}")
        finally:
            client.close()
    return collections_data
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))
    
                
            
    

    

        
        
        


    
    


      

    
    
    
