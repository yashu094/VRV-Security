from flask import Blueprint,jsonify,make_response
from utils.helpers import role_required
from flask_jwt_extended import get_jwt_identity,jwt_required
from extensions import db
users_collection=db['users']
user_bp=Blueprint('user',__name__)

@user_bp.route('/user-dashboard',methods=['GET'])
@role_required(["admin","user"])
@jwt_required()  # Only authenticated users can access
def user_dashboard():
    current_user = get_jwt_identity()
    
    # Get the user data
    user = users_collection.find_one({"email": current_user})
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get files uploaded by the user
    uploaded_files = user.get("files", [])
    
    # Get shared files for the user
    shared_files = [file for file in uploaded_files if "shared_with" in file]  
    
    dashboard_data = {
        "email": user["email"],
        "name": f"{user['first_name']} {user['last_name']}",
        "uploaded_files": uploaded_files,
        "shared_files": shared_files  
    }
    
    return jsonify({"message": "User Dashboard", "data": dashboard_data}), 200
