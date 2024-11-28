from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
MONGO_URI='mongodb+srv://21pa1a05b6:vOKAtPrxbODmQ87W@cluster0.mwzqsiz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client=MongoClient(MONGO_URI)
db = client['VRS']  

bcrypt = Bcrypt()
jwt=JWTManager()
