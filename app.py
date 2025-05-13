from flask import Flask, render_template, request,session
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

app = Flask(__name__)

#para llevar  el secreto de la app desde las variables de entorno (recomendado para seguridad)
app.secret_key = os.environ.get('secret_key')
if not app.secret_key:
    app.secret_key = 'secret_key'


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
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        mensaje = request.form.get('mensaje')
        #aqui agregar la lógica para enviar el mensaje a la base de datos de mongoDbAtlas(administracion)
        #colección "contactos tarea para hacer internamente"
        return  render_template('contacto.html', nombre=nombre, email=email, mensaje=mensaje)
    return render_template('contacto.html')


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
                return redirect(url_for('gestion_mongoDb'))
            else:
                error_message = "Usuario o contraseña incorrectos."
                return render_template('login.html', error_message=error_message)    

        else:
            error_message = "No se tiene conectividad con la base de datos."
            return render_template('login.html', error_message=error_message)        

    return render_template('login.html')   

    





@app.route('/', methods=['GET', 'POST'])
def gestion_mongoDb():
    client = connect_mongo()
    databases=[]
    error_message = None
    if client:
        try:
            databases = client.list_database_names()
        except Exception as e:
            error_message = "No es posible listar las bases de datos."
            print(f"Error listing databases: {e}")
        finally:
            client.close()       

    if request.method == 'POST':
        selected_db = request.form.get('database')
        collection_data = get_collection_data(selected_db) # type: ignore
        return render_template('index.html', databases=databases, selected_db=selected_db, collection_data=collection_data, error_message=error_message)
   
    return render_template('index.html', databases=databases, error_message=error_message)
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
    
                
            
    

    

        
        
        


    
    


      

    
    
    
