import csv
import os
import bcrypt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ADMIN_PATH = os.path.join(DATA_DIR, "users.csv")

def create_admin_csv():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # if os.path.exists(ADMIN_PATH):
    #     print("⚠️ File admins.csv sudah ada.")
    #     return

    # pembuatan akun super admin
    admin_users = [
        {
            "id": 1,
            "username": "superadmin@injourney",
            "password": "super@juandaInjourney123",
            "status_approval": 1
        }
    ]

    # hash password
    for user in admin_users:
        hashed_pw = bcrypt.hashpw(user["password"].encode("utf-8"), bcrypt.gensalt())
        user["password"] = hashed_pw.decode("utf-8")

    # tulis ke CSV
    with open(ADMIN_PATH, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "username", "password", "status_approval"])
        writer.writeheader()
        writer.writerows(admin_users)

    print(f"✅ File {ADMIN_PATH} berhasil dibuat dengan admin default (status_approval=0).")

if __name__ == "__main__":
    create_admin_csv()
