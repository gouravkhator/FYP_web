from firebase_admin import auth, initialize_app
import os
import pathlib

fb_admin_config_path = os.path.join(pathlib.Path(__file__).parent, 'key/fb_admin_config.json')

if not os.path.exists(fb_admin_config_path):
    print(f"Please provide firebase admin config file in the path: {fb_admin_config_path}")
    exit(1)

# we have to set this field before any admin stuff, as it will set firebase admin
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = fb_admin_config_path

app = initialize_app() # initialize firebase admin app

def create_user(email, user_id):
    try:
        # if user is there, return that
        return auth.get_user_by_email(email=email)
    except:
        # else create the user
        return auth.create_user(email=email, uid=user_id) if user_id else auth.create_user(email=email)
