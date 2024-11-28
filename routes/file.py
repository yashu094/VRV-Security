from flask import Flask, jsonify, make_response, Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import  db
from datetime import datetime  
from utils.helpers import send_file

# Directory for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


file_bp = Blueprint('file', __name__)
users_collection = db['users']  


@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()  
    
    if 'file' not in request.files:
        return make_response(jsonify({"error": "No file part"}), 400)

    file = request.files['file']

    
    if file.filename == '':
        return make_response(jsonify({"error": "No selected file"}), 400)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        file_size = os.path.getsize(filepath)  
        file_type = file.content_type  
        upload_date = datetime.utcnow()
        file_metadata = {
            "filename": filename,
            "filepath": filepath,
            "size": file_size,
            "type": file_type,
            "upload_date": upload_date
        }
        users_collection.update_one(
            {"email": current_user}, 
            {"$push": {"files": filepath}}  
        )

        return make_response(jsonify({"message": f"File uploaded successfully: {filename}"}), 200)

    return make_response(jsonify({"error": "File type not allowed"}), 400)


@file_bp.route('/<filename>', methods=['GET'])
@jwt_required()
def get_file(filename):
    current_user = get_jwt_identity()

    # Find the user in the database
    user = users_collection.find_one({"email": current_user})

    
    file_metadata = next((file for file in user.get("files", []) if file["filename"] == filename), None)
    
    
    if not file_metadata and user['role'] != 'admin':
        return make_response(jsonify({"error": "You do not have permission to access this file"}), 403)

    
    if file_metadata:
        return make_response(jsonify({
            "filename": file_metadata["filename"],
            "size": file_metadata["size"],
            "type": file_metadata["type"],
            "upload_date": file_metadata["upload_date"]
        }), 200)
    
    
    return make_response(jsonify({"error": "File not found"}), 404)


@file_bp.route('/<filename>', methods=['DELETE'])
@jwt_required()
def delete_file(filename):
    current_user = get_jwt_identity()

    
    user = users_collection.find_one({"email": current_user})


    file_metadata = next((file for file in user.get("files", []) if file["filename"] == filename), None)

    
    if not file_metadata and user['role'] != 'admin':
        return make_response(jsonify({"error": "You do not have permission to delete this file"}), 403)

    
    try:
        file_path = file_metadata["filepath"]
        os.remove(file_path)  # Remove file from filesystem

        # Remove the file from the database (users collection)
        users_collection.update_one(
            {"email": current_user},
            {"$pull": {"files": {"filename": filename}}}  # Remove file metadata from user's files
        )

        return make_response(jsonify({"message": f"File {filename} deleted successfully"}), 200)

    except Exception as e:
        return make_response(jsonify({"error": f"An error occurred: {str(e)}"}), 500)
    
@file_bp.route('/list',methods=['GET'])
@jwt_required()
def list_files():
    current_user=get_jwt_identity()
    user=users_collection.find_one({'email:',current_user})
    if user['role']=='admin':
        all_users=users_collection.find()
        all_files=[]
        for u in all_users:
            all_files.extend(u.get('files',[]))
        return make_response(jsonify({"files": all_files}), 200)
    user_files = user.get('files', [])
    return make_response(jsonify({"files": user_files}), 200)


@file_bp.route('/share/<filename>', methods=['POST'])
@jwt_required()  # Ensure only authenticated users can share files
def share_file(filename):
    current_user = get_jwt_identity()
    data = request.json
    share_with_email = data.get('email')

    if not share_with_email:
        return make_response(jsonify({"error": "Email is required to share the file"}), 400)

    # Find the user who owns the file
    user = users_collection.find_one({"email": current_user})

    
    if filename not in [os.path.basename(f) for f in user.get("files", [])]:
        return jsonify({"error": "You do not have permission to share this file"}), 403

    # Find the user to share with
    user_to_share_with = users_collection.find_one({"email": share_with_email})
    if not user_to_share_with:
        return jsonify({"error": "User to share with not found"}), 404

    # Share the file with the other user (add the file to their record)
    users_collection.update_one(
        {"email": share_with_email},
        {"$push": {"files": os.path.join(UPLOAD_FOLDER, filename)}}
    )

    
    sender_email = 'zoro39023@gmail.com'  
    sender_password = 'uurc oxja gwmo enaf'     
    smtp_server = 'smtp.gmail.com'         
    smtp_port = 587                        

    
    email_sent = send_file(
        recipient_email=share_with_email,
        otp=None,  
        sender_email=sender_email,
        sender_password=sender_password,
        smtp_server=smtp_server,
        smtp_port=smtp_port
    )

    if not email_sent:
        return make_response(jsonify({"error": "Failed to send email notification"}), 500)

    return make_response(jsonify({"message": f"File shared successfully with {share_with_email}"}), 200)