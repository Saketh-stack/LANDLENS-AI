from firebase_functions import https_fn
from firebase_admin import initialize_app
from app.main import app as fastapi_app

initialize_app()

api = https_fn.on_request(fastapi_app, memory=1024, timeout_sec=120, max_instances=10)
