"""
ERP Modules Service Layer
Business logic for comprehensive ERP functionality
"""

from modules.shared.database import get_db_connection, get_db_type, generate_id
from datetime import datetime
import json
import logging
import bcrypt
import secrets

logger = logging.getLogger(__name__)


class ERPException(Exception):
    """Custom exception for ERP business logic errors"""
    def __init__(self, message, error_code, status_code=400, field=None, details=None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.field = field
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationService:
    """Service class for authentication operations"""
    
    @staticmethod
    def hash_password(password):
        """
        Hash password using bcrypt
        Returns bcrypt hash string
        """
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """
        Verify password against bcrypt hash
        Returns True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def generate_session_token():
        """
        Generate a secure random session token
        Returns 32-character hex string
        """
        return secrets.token_hex(32)
    
    @staticmethod
    def authenticate_user(email, password, user_type):
        """
        Authenticate user with email and password
        Supports three user types: admin, operator, business_owner
        Returns dict with success status and user data
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        try:
            # Determine which table to query based on user_type
            if user_type == 'admin':
                # Query super_admins table
                cursor.execute(f"""
                    SELECT id, email, password_hash, full_name as business_name, is_active
                    FROM super_admins
                    WHERE email = {ph}
                """, (email,))
            elif user_type == 'operator':
                # Query erp_staff table
                cursor.execute(f"""
                    SELECT id, email, password_hash, staff_name as business_name, user_id, is_active
                    FROM erp_staff
                    WHERE email = {ph}
                """, (email,))
            else:  # business_owner
                # Query users table
                cursor.execute(f"""
                    SELECT id, email, password_hash, business_name, is_active
                    FROM users
                    WHERE email = {ph}
                """, (email,))
            
            user = cursor.fetchone()
            
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Convert to dict if needed
            if not isinstance(user, dict):
                if user_type == 'operator':
                    user_dict = {
                        'id': user[0],
                        'email': user[1],
                        'password_hash': user[2],
                        'business_name': user[3],
                        'user_id': user[4],
                        'is_active': user[5]
                    }
                else:
                    user_dict = {
                        'id': user[0],
                        'email': user[1],
                        'password_hash': user[2],
                        'business_name': user[3],
                        'is_active': user[4]
                    }
            else:
                user_dict = dict(user)
            
            # Check if user is active
            if not user_dict.get('is_active'):
                return {
                    'success': False,
                    'error': 'Account is inactive. Please contact administrator.'
                }
            
            # Verify password
            if not AuthenticationService.verify_password(password, user_dict['password_hash']):
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Return success with user data (excluding password hash)
            user_data = {
                'id': user_dict['id'],
                'email': user_dict['email'],
                'business_name': user_dict.get('business_name', '')
            }
            
            # For operators, include the business owner's user_id
            if user_type == 'operator':
                user_data['business_owner_id'] = user_dict.get('user_id')
            
            return {
                'success': True,
                'user': user_data
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                'success': False,
                'error': 'Authentication failed. Please try again.'
            }
        finally:
            conn.close()
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        Change user password
        Verifies old password before updating
        Returns dict with success status
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        try:
            # Get current password hash from users table
            cursor.execute(f"""
                SELECT password_hash FROM users WHERE id = {ph}
            """, (user_id,))
            
            user = cursor.fetchone()
            
            if not user:
                # Try erp_staff table
                cursor.execute(f"""
                    SELECT password_hash FROM erp_staff WHERE id = {ph}
                """, (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    # Try super_admins table
                    cursor.execute(f"""
                        SELECT password_hash FROM super_admins WHERE id = {ph}
                    """, (user_id,))
                    user = cursor.fetchone()
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found',
                    'error_code': 'USER_NOT_FOUND'
                }
            
            # Get password hash
            if isinstance(user, dict):
                current_hash = user['password_hash']
            else:
                current_hash = user[0]
            
            # Verify old password
            if not AuthenticationService.verify_password(old_password, current_hash):
                return {
                    'success': False,
                    'error': 'Current password is incorrect',
                    'error_code': 'INCORRECT_PASSWORD'
                }
            
            # Hash new password
            new_hash = AuthenticationService.hash_password(new_password)
            
            # Update password in appropriate table
            # Try users table first
            cursor.execute(f"""
                UPDATE users SET password_hash = {ph} WHERE id = {ph}
            """, (new_hash, user_id))
            
            if cursor.rowcount == 0:
                # Try erp_staff table
                cursor.execute(f"""
                    UPDATE erp_staff SET password_hash = {ph} WHERE id = {ph}
                """, (new_hash, user_id))
                
                if cursor.rowcount == 0:
                    # Try super_admins table
                    cursor.execute(f"""
                        UPDATE super_admins SET password_hash = {ph} WHERE id = {ph}
                    """, (new_hash, user_id))
            
            conn.commit()
            
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Password change error: {e}")
            return {
                'success': False,
                'error': 'Failed to change password',
                'error_code': 'PASSWORD_CHANGE_FAILED'
            }
        finally:
            conn.close()


class ERPService:
    """Service class for ERP operations"""
    
    @staticmethod
    def validate_gst_number(gst_number):
        """
        Validate GST number format: 2 digits + 10 alphanumeric + 1 digit + Z + 1 digit
        Total: 15 characters
        """
        if not gst_number:
            return True  # GST is optional
        
        if len(gst_number) != 15:
            return False
        
        # Check format: 2 digits + 10 alphanumeric + 1 digit + Z + 1 digit
        if not gst_number[:2].isdigit():
            return False
        if not gst_number[2:12].isalnum():
            return False
        if not gst_number[12].isdigit():
            return False
        if gst_number[13].upper() != 'Z':
            return False
        if not gst_number[14].isdigit():
            return False
        
        return True
    
    @staticmethod
    def validate_ifsc_code(ifsc_code):
        """
        Validate IFSC code format: 4 letters + 7 alphanumeric
        Total: 11 characters
        """
        if not ifsc_code:
            return False
        
        if len(ifsc_code) != 11:
            return False
        
        # Check format: 4 letters + 7 alphanumeric
        if not ifsc_code[:4].isalpha():
            return False
        if not ifsc_code[4:].isalnum():
            return False
        
        return True
    
    @staticmethod
    def validate_hsn_code(hsn_code):
        """
        Validate HSN code format: 4, 6, or 8 digits
        """
        if not hsn_code:
            return True  # HSN is optional
        
        if not hsn_code.isdigit():
            return False
        
        if len(hsn_code) not in [4, 6, 8]:
            return False
        
        return True
    
    @staticmethod
    def check_credit_limit(customer_id, new_amount):
        """
        Check if customer credit limit will be exceeded
        Returns True if within limit, raises ERPException if exceeded
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        try:
            cursor.execute(f"SELECT credit_limit, outstanding_balance FROM erp_customers WHERE id={ph}", (customer_id,))
            row = cursor.fetchone()
            
            if not row:
                raise ERPException(
                    "Customer not found",
                    "CUSTOMER_NOT_FOUND",
                    404
                )
            
            credit_limit = float(row['credit_limit'] or 0)
            outstanding = float(row['outstanding_balance'] or 0)
            
            if credit_limit > 0 and (outstanding + new_amount) > credit_limit:
                raise ERPException(
                    f"Credit limit exceeded. Customer limit: ₹{credit_limit:,.2f}, Current outstanding: ₹{outstanding:,.2f}, New sale: ₹{new_amount:,.2f}",
                    "CREDIT_LIMIT_EXCEEDED",
                    422,
                    "customer_id",
                    {
                        "credit_limit": credit_limit,
                        "current_outstanding": outstanding,
                        "new_amount": new_amount
                    }
                )
            
            return True
            
        finally:
            conn.close()