import random
from email.mime.text import MIMEText
import smtplib
from functools import wraps
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask import jsonify
from extensions import db

def generate_otp():
    return str(random.randint(100000, 999999))  # Generates a 6-digit OTP as a string

def send_email(recipient_email, otp, sender_email, sender_password, smtp_server, smtp_port):
    try:
        # Create the email content with the OTP
        msg = MIMEText(f"Your OTP is {otp}. It expires in 2 minutes.")
        msg['Subject'] = "Your OTP Code"  
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")  
        return False
user_collection=db['users']
def send_file(recipient_email, file_name, sender_email, sender_password, smtp_server, smtp_port):
    try:
        # Create the email content with the file sharing details
        msg = MIMEText(f"You have a new file shared with you: {file_name}. Please log in to access it.")
        msg['Subject'] = "New File Shared with You"
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def role_required(allowed_roles):
    def wrapper(func):
        @wraps(func)
        @jwt_required()
        def decorated_view(*args,**kwargs):
            current_user=get_jwt_identity()
            user=user_collection.find_one({"email":current_user})
            if not user or user["role"] not in allowed_roles:
                return jsonify({"error": "Access forbidden: insufficient privileges"}), 403

            return func(*args, **kwargs)
        return decorated_view
    return wrapper