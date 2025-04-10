from flask import Flask, render_template, request
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

app = Flask(__name__)
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
@app.route('/', methods=['GET', 'POST'])
def index():
    client = conect_mongo()
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
    
                
            
    

    

        
        
        


    
    


      

    
    
    
