import pyrebase
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

firebase_config={
    'apiKey': os.getenv("API_KEY"),
    'authDomain': os.getenv("AUTH_DOMAIN"),
    'projectId': os.getenv("PROJECT_ID"),
    'storageBucket': os.getenv("STORAGE_BUCKET"),
    'messagingSenderId': os.getenv("MESSAGING_SENDER_ID"),
    'appId': os.getenv("APP_ID"),
    'databaseURL': os.getenv("DATABASE_URL")
    }

#Inicializando
firebase=pyrebase.initialize_app(firebase_config)
bd=firebase.database()


clientes={}

lista_precios={}

notas=pd.DataFrame()

