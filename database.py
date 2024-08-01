from pymongo import MongoClient
import certifi

MONGO_URI = 'mongodb+srv://anajassov:admin@clusterpythonbd.fx3n9x8.mongodb.net/?retryWrites=true&w=majority&appName=ClusterPythonBD'
ca = certifi.where()

def dbConnection():
    try: 
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db = client["signosBD"]
    except ConnectionError:
        print("Error de conexión con la BD")
    return db