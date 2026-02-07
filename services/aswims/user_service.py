from models.aswims.users import AswimsUsers
from db import db
from werkzeug.security import generate_password_hash,check_password_hash
from services.base_service import BaseService
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

class UserService:
    @staticmethod
    def register_user(data):
        # # 1. Check if email already exists
        # if AswimsUsers.query.filter_by(email_id=data.get('email_id')).first():
        #     raise ValueError("Email already registered")

        # 2. Check if mobile number already exists
        if AswimsUsers.query.filter_by(mob_no=data.get('mob_no')).first():
            raise ValueError("Mobile number already registered")

        # 3. Hash the password
        hashed_pw = generate_password_hash(data.get('password'))

        # 4. Create new User instance
        new_user = AswimsUsers(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email_id=data.get('email_id'),
            mob_no=data.get('mob_no'),
            password_hash=hashed_pw,
            designation_id=data.get('designation_id'),
            speciality_id=data.get('speciality_id'),
            super_speciality_id=data.get('super_speciality_id') # Can be None
        )

        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def login_user(identifier, password):
        user = AswimsUsers.query.filter(
            (AswimsUsers.email_id == identifier) | 
            (AswimsUsers.mob_no == identifier)
        ).first()

        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid credentials")
        
        if user.account_status == 'Pending':
            # This triggers the 401/403 error in Angular
            raise ValueError("Your account is currently 'Pending' admin approval. Please contact the Admin.")
        
        if user.account_status == 'Inactive':
            raise ValueError("This account has been deactivated. Access denied.")

        # FIX: Check which name you used in the model backref
        # If you followed the previous fix, it is 'appointment_ref'
        user_type = "User"
        if hasattr(user, 'appointment_ref') and user.appointment_ref:
            user_type = user.appointment_ref.designation_name
        elif hasattr(user, 'appointment') and user.appointment:
            user_type = user.appointment.designation_name

        h_level = user.appointment.hierarchy_level if user.appointment else 99

        # Generate tokens MANUALLY to include h_level without changing BaseService
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "user_type": user_type,
                "h_level": h_level  # Custom claim added here
            },
            expires_delta=timedelta(minutes=15)
        )
        
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "full_name": f"{user.first_name} {user.last_name}",
                "role": user_type,
                "h_level": user.appointment.hierarchy_level
            }
        }
    
    @staticmethod
    def get_all_users():
        """Fetches all users with their appointment details serialized."""
        try:
            users = AswimsUsers.query.all()
            
            # We process the list comprehension inside the try block 
            # because this is where the relationship mapping attributes 
            # (like .speciality) are actually accessed.
            return [
                {
                    "id": u.id,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "email_id": u.email_id,
                    "mob_no": u.mob_no,
                    "account_status": u.account_status,
                    "designation": u.appointment.designation_name if u.appointment else "N/A",
                    "speciality": u.speciality.speciality_name if u.speciality else "N/A",
                    "super_speciality": u.super_speciality.speciality_name if u.super_speciality else "None"
                } for u in users
            ]
        except AttributeError as ae:
            # Catch specific mapping/relationship errors
            print(f"Relationship Mapping Error: {str(ae)}")
            raise Exception(f"Configuration Error: User relationship mapping is missing ({str(ae)})")
        except Exception as e:
            # Catch general database or connection errors
            print(f"Database Error: {str(e)}")
            raise Exception("Unable to fetch users from database. Please try again later.")

    @staticmethod
    def update_user_status(user_id, new_status):
        user = AswimsUsers.query.get(user_id)
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Valid statuses: 'Active', 'Inactive', 'Pending'
        user.account_status = new_status
        db.session.commit()
        return {"success": True, "message": f"User status updated to {new_status}"}