# __init__.py
# Agar Flask kenali semua folder ini sebagai package

from controllers import algoritmaController
from controllers import dataController
from controllers import datasetController
from controllers import authController
from controllers import userController
from middlewares import auth_middleware
from routes import routes
from services import preprocessing
from services import watcher
from services import init_admin
from utils import jwt_utils
