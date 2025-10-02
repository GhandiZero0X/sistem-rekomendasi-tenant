# controllers/dashboardController.py
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
USER_DATA_FILE = os.path.join(DATA_DIR, "users.csv")
TENANT_DATA_FILE = os.path.join(DATA_DIR, "tenant_preprocessed.csv")

# Get analytics untuk superadmin (tenant dan users)
def get_superadmin_dashboard():
    result = {}

    # --- Tenant Analytics ---
    if os.path.exists(TENANT_DATA_FILE):
        tenants = pd.read_csv(TENANT_DATA_FILE)
        result["tenant"] = {
            "total_tenants": len(tenants),
            "by_jenis_usaha": tenants["jenis_usaha"].value_counts().to_dict(),
            "by_terminal": tenants["lokasi"].value_counts().to_dict(),
            "by_rentang_harga": tenants["rentang_harga"].value_counts().to_dict(),
            "avg_rating": round(tenants["rating"].mean(), 2),
            "total_review": int(tenants["total_review"].sum())
        }
    else:
        result["tenant"] = {"error": "Tenant dataset not found"}

    # --- User Analytics ---
    if os.path.exists(USER_DATA_FILE):
        users = pd.read_csv(USER_DATA_FILE)
        result["user"] = {
            "total_users": len(users),
            "approved": int((users["status_approval"] == 1).sum()),
            "pending": int((users["status_approval"] == 0).sum()),
            "by_role": users["role"].value_counts().to_dict()
        }
    else:
        result["user"] = {"error": "User dataset not found"}

    return result


# Get analytics untuk admin (tenant only)
def get_admin_dashboard():
    result = {}

    if os.path.exists(TENANT_DATA_FILE):
        tenants = pd.read_csv(TENANT_DATA_FILE)
        result["tenant"] = {
            "total_tenants": len(tenants),
            "by_jenis_usaha": tenants["jenis_usaha"].value_counts().to_dict(),
            "by_terminal": tenants["lokasi"].value_counts().to_dict(),
            "by_rentang_harga": tenants["rentang_harga"].value_counts().to_dict(),
            "avg_rating": round(tenants["rating"].mean(), 2),
            "total_review": int(tenants["total_review"].sum())
        }
    else:
        result["tenant"] = {"error": "Tenant dataset not found"}

    return result
