import logging
import os
from flask_login import UserMixin
from flask import session
from datetime import datetime, timedelta
from config import Config

# Try to import Linux-specific modules
try:
    import grp
    import spwd
    import crypt
except ImportError:
    grp = None
    spwd = None
    crypt = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

    @staticmethod
    def authenticate(username, password):
        """
        Authenticate user. 
        On Linux: Validates against system /etc/shadow and 'squid-man' group.
        On Windows/Dev: Uses fallback validation (admin/admin) if modules are missing.
        """
        logging.info(f"Authenticating user: {username}")

        # Check .env Admin Credentials (First Priority)
        # This ensures the admin configured in .env can always login affecting both Windows and Linux
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            logging.info(f"Admin Auth: User {username} logged in using .env credentials.")
            session.permanent = True
            return User(username)
        
        # Fallback for Windows / Dev environment
        if spwd is None or grp is None or crypt is None:
            if Config.DEBUG or os.name == 'nt':
                logging.warning("Linux auth modules not found. Using DEV authentication.")
                # We already checked admin creds above. If we are here in Dev/Windows mode,
                # and didn't match admin, then it's an invalid login for Dev mode.
                logging.warning(f"Dev Auth Failed: User {username} not found or password incorrect.")
            else:
                logging.error("Linux auth modules missing and not in valid Dev mode.")
            return None

        try:
            # Real Linux Authentication
            shadow_entry = spwd.getspnam(username)
            
            # Verify password using crypt
            if crypt.crypt(password, shadow_entry.sp_pwdp) == shadow_entry.sp_pwdp:
                logging.info(f"Password for user {username} is correct.")
                
                # Check group membership
                group_info = grp.getgrnam('squid-man')
                if username in group_info.gr_mem:
                    logging.info(f"User {username} belongs to group 'squid-man'.")
                    
                    # Log session info
                    session.permanent = True
                    session_timeout = datetime.now() + timedelta(minutes=15)
                    logging.info(f"Session will timeout at: {session_timeout.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    return User(username)
                else:
                    logging.warning(f"User {username} via 'squid-man' group check failed.")
                    return None
            else:
                logging.warning(f"Incorrect password for user {username}.")
                return None
        except KeyError:
            logging.error(f"User {username} not found/KeyError.")
            return None
        except Exception as e:
            logging.error(f"Auth error for {username}: {e}")
            return None