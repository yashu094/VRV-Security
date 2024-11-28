# Secure File Management and Sharing System  

A robust backend system built with Flask, providing secure user authentication, file upload, sharing, and role-based access control. This project ensures data security and user management for a modern file management platform.  

---

## Features  

### Authentication and Authorization  
- **User Signup and Login**: Users can register and log in securely with hashed passwords.  
- **OTP Verification**: Enhances security during login with time-sensitive OTP.  
- **JWT Token-Based Authentication**: Manages sessions with JSON Web Tokens (JWT).  
- **Role-Based Access Control (RBAC)**: Differentiates permissions for Admin and Users.  

### File Management  
- **File Upload**: Authenticated users can upload files with type restrictions.  
- **File Retrieval**: Users can download their uploaded files.  
- **File Sharing**: Share files securely with other users, including admin-initiated sharing.  
- **File Deletion**: Users can delete their own files; admins can delete any file.  

### Admin Capabilities  
- **Full File Control**: Admins can upload, download, share, edit, and delete any file.  
- **Dashboard**: View and manage all users and files.  

### Security Features  
- **Password Hashing**: Securely stores passwords using Flask-Bcrypt.  
- **JWT Revocation**: Ensures logout functionality by revoking JWT tokens.  
- **Access Control**: Restricts unauthorized file access and sharing.  

---

## API Endpoints  

### Authentication  
| Endpoint             | Method | Description                       | Protected |  
|----------------------|--------|-----------------------------------|-----------|  
| `/auth/signup`       | POST   | Register a new user               | No        |  
| `/auth/login`        | POST   | Login with email and password     | No        |  
| `/auth/verify-otp`   | POST   | Verify OTP                        | No        |  
| `/auth/logout`       | POST   | Logout and revoke JWT             | Yes       |  

### File Management  
| Endpoint              | Method | Description                          | Protected |  
|-----------------------|--------|--------------------------------------|-----------|  
| `/file/upload`        | POST   | Upload a file                       | Yes       |  
| `/file/<filename>`    | GET    | Retrieve a file                     | Yes       |  
| `/file/delete/<filename>` | DELETE | Delete a file                      | Yes       |  
| `/file/share/<filename>` | POST | Share a file with another user      | Yes       |  

### Admin Dashboard  
| Endpoint             | Method | Description                       | Protected |  
|----------------------|--------|-----------------------------------|-----------|  
| `/admin/admin-dashboard`   | GET    | View all users and files          | Yes       |  

### User Dashboard  
| Endpoint             | Method | Description                       | Protected |  
|----------------------|--------|-----------------------------------|-----------|  
| `/user/user-dashboard`    | GET    | View user-specific files and info | Yes       |  

---

## Folder Structure  

```plaintext
secure-file-management/
│
├── app.py                # Main application entry point
├── extensions.py         # Flask extensions (JWT, DB, Bcrypt)
├── routes/               # Application routes
│   ├── auth.py           # Authentication and authorization routes
│   ├── admin.py          # Admin-specific routes
│   ├── user.py           # User-specific routes
│   └── file.py           # File upload, sharing, and management routes
│
├── utils/                # Utility functions
│   ├── helpers.py        # OTP generation, email sending
│
├── uploads/              # Directory for uploaded files
│
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation


## Prerequisites  
- Python 3.8+  
- MongoDB installed and running locally or on a server.  
