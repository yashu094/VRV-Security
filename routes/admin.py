from flask import Blueprint,jsonify,make_response
from utils.helpers import role_required
from flask_jwt_extended import get_jwt_identity,jwt_required
from extensions import db
users_collection=db['users']
admin_bp = Blueprint('admin', __name__)
@admin_bp.route('/dashboard',methods=['GET'])
@role_required(["admin"])
@jwt_required()  
def admin_dashboard():
    current_user = get_jwt_identity()
    
    user = users_collection.find_one({"email": current_user})
    if user['role'] != 'admin':
        return jsonify({"error": "You do not have permission to access the admin dashboard"}), 403
    
    
    users = list(users_collection.find({}, {"password": 0}))  
    
    dashboard_data = []
    
    for u in users:
        user_data = {
            "email": u["email"],
            "name": f"{u['first_name']} {u['last_name']}",
            "role": u['role'],
            "uploaded_files": u.get("files", [])
        }
        dashboard_data.append(user_data)
    
    return jsonify({"message": "Admin Dashboard", "data": dashboard_data}), 200
