from flask import Flask
from extensions import bcrypt,jwt
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from routes.file import file_bp


app=Flask(__name__)

app.config['JWT_SECRET_KEY']='abcdef123456'



bcrypt.init_app(app)
jwt.init_app(app)


app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(file_bp, url_prefix='/file')

if __name__=='__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)