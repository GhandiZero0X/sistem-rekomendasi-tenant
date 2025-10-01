import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
USER_DATA_FILE = os.path.join(DATA_DIR, "users.csv")
TENANT_DATA_FILE = os.path.join(DATA_DIR, "tenant_preprocessed.csv")

# Get user analytics