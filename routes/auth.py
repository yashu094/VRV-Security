from flask import Blueprint, request, jsonify, make_response
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token,decode_token,jwt_required,get_jwt_identity
from datetime import timedelta
from extensions import db, jwt
import time,jwt
from utils.helpers import generate_otp, send_email

bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__)
SECRET_KEY = "123456ancd"  
JWT_ALGORITHM = "HS256"   
SENDER_EMAIL = "zoro39023@gmail.com"  
SENDER_PASSWORD = "uurc oxja gwmo enaf"       
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

users_collection = db['users']


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    password = data.get('password')
    role = data.get('role', '').lower()

    if not all([email, first_name, last_name, password, role]):
        return make_response(jsonify({"error": "All fields are required"}), 400)

    if users_collection.find_one({"email": email}):
        return make_response(jsonify({"error": "Email already registered"}), 400)

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": hashed_password,
        "role": role
    }
    users_collection.insert_one(user)    
    
    return make_response(jsonify({"message": "User registered successfully"}), 201)



otp_store = {}


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return make_response(jsonify({"error": "Both email and password are required"}), 400)

    user = users_collection.find_one({"email": email})
    if not user:
        return make_response(jsonify({"error": "User does not exist"}), 400)

    if not bcrypt.check_password_hash(user["password"], password):
        return make_response(jsonify({"error": "Invalid password"}), 400)

    
    otp = generate_otp()
    otp_store[email] = {"otp": otp, "timestamp": time.time()}

    
    if send_email(email, otp, SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT):
        
        temp_token = create_access_token(
            identity=email,
            additional_claims={"otp_stage": True},
            expires_delta=timedelta(minutes=3)  
        )
        return jsonify({"message": "OTP sent to your email", "temp_token": temp_token}), 200
    else:
        return jsonify({"error": "Failed to send OTP"}), 500


@auth_bp.route('/verify-otp', methods=['POST'])
def verify():
    data = request.json
    temp_token = data.get("temp_token")
    input_otp = data.get("otp")

    if not all([temp_token, input_otp]):
        return make_response(jsonify({"error": "Both token and OTP are required"}), 400)

    try:
        
        decoded_token=decode_token(temp_token)  
        email = decoded_token.get('sub')
        print(decoded_token)
        print(decoded_token.get('otp_stage'))
        if not email or not decoded_token.get('otp_stage'):  
            return make_response(jsonify({"error": "Invalid token used. Please try again."}), 400)

        stored_otp_data = otp_store.get(email)
        if not stored_otp_data:
            return jsonify({"error": "Session expired. Please login again."}), 400

        OTP_EXPIRY = 180
        if time.time() - stored_otp_data['timestamp'] > OTP_EXPIRY:
            otp_store.pop(email, None)  
            return make_response(jsonify({"error": "OTP expired. Please try again."}), 400)

        
        if stored_otp_data['otp'] != input_otp:
            return make_response(jsonify({"error": "Incorrect OTP"}), 400)

        
        auth_token = create_access_token(identity=email, additional_claims={"authenticated": True})

        
        otp_store.pop(email, None)

        return jsonify({"message": "Verification successful!", "auth_token": auth_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Session expired. Please login again."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token. Please login again."}), 401
revoked_tokens = set()  

def token_revoked(jwt_token):
    return jwt_token in revoked_tokens


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jwt_token = request.headers['Authorization'].split()[1]  
    revoked_tokens.add(jwt_token)  
    return make_response(jsonify({"message": "Logged out successfully"}), 200)