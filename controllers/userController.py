# controllers/userController.py
from flask import send_file, Response
import os
import pandas as pd
import bcrypt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
USERPATH = os.path.join(DATA_DIR, "users.csv")

# get all users
def get_all_users():
    """"Menampilkan semua users"""
    if not os.path.exists(USERPATH):
        return []
    df = pd.read_csv(USERPATH)
    return df.to_dict(orient="records")

# get satuan users
def get_user_by_id(user_id: int):
    """Menampilkan satu user berdasarkan ID"""
    if not os.path.exists(USERPATH):
        return {"error": "Dataset tidak ditemukan."}
    df = pd.read_csv(USERPATH)
    user = df[df["id"].astype(int) == user_id]
    if user.empty:
        return {"error": f"User dengan id {user_id} tidak ditemukan."}
    return user.to_dict(orient="records")[0]

def add_user(user_data: dict):
    """Tambah satu user (hanya superadmin)"""
    df = pd.read_csv(USERPATH) if os.path.exists(USERPATH) else pd.DataFrame()
    # Auto-assign ID
    next_id = 1 if df.empty else int(df["id"].max() + 1)
    user_data["id"] = next_id
    # Hash password sebelum disimpan
    if "password" in user_data and user_data["password"]:
        user_data["password"] = bcrypt.hashpw(
            user_data["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
    else:
        return {"error": "Password tidak boleh kosong."}
    # Default value status approval
    user_data["status_approval"] = int(user_data.get("status_approval", 1))
    # Default role
    user_data["role"] = user_data.get("role", "admin")
    # Simpan data baru
    df = pd.concat([df, pd.DataFrame([user_data])], ignore_index=True)
    df.to_csv(USERPATH, index=False)

    return {"success": f"User baru dengan ID {next_id} berhasil ditambahkan."}


# add batch user hanya untuk superadmin
def add_batch_users(users_data: list):
    """Tambah banyak user sekaligus (hanya superadmin)"""
    if not users_data or not isinstance(users_data, list):
        return {"error": "Input harus berupa list of user data."}

    df = pd.read_csv(USERPATH) if os.path.exists(USERPATH) else pd.DataFrame()

    # Cari ID terakhir
    next_id = 1 if df.empty else df["id"].max() + 1

    # Tambahkan ID, hash password, dan pastikan status_approval int
    for i, user in enumerate(users_data):
        user["id"] = int(next_id + i)

        if "password" in user:
            user["password"] = bcrypt.hashpw(
                user["password"].encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

        if "status_approval" in user:
            user["status_approval"] = int(user["status_approval"])
        else:
            user["status_approval"] = 0  # default

    # Gabungkan ke dataset
    new_df = pd.DataFrame(users_data)
    df = pd.concat([df, new_df], ignore_index=True)

    # Simpan ulang
    df.to_csv(USERPATH, index=False)
    return {"success": f"{len(users_data)} user baru berhasil ditambahkan."}


def update_user(user_id: int, user_data: dict):
    """Merubah data user berdasarkan ID"""
    if not os.path.exists(USERPATH):
        return {"error": "Dataset tidak ditemukan."}

    df = pd.read_csv(USERPATH)

    if user_id not in df["id"].astype(int).values:
        return {"error": f"User dengan id {user_id} tidak ditemukan."}

    for key, value in user_data.items():
        if key not in df.columns or value in [None, "", " "]:
            continue  # lewati field kosong

        if key == "password":
            # Hash ulang password hanya jika diubah
            hashed_pw = bcrypt.hashpw(
                value.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            df.loc[df["id"].astype(int) == user_id, key] = hashed_pw

        elif key == "status_approval":
            # Pastikan integer
            df.loc[df["id"].astype(int) == user_id, key] = int(value)

        else:
            df.loc[df["id"].astype(int) == user_id, key] = value

    df.to_csv(USERPATH, index=False)
    return {"success": f"Data user dengan ID {user_id} berhasil diperbarui."}


# delete user dengan menonaktifkan akun pada status_approval menjadi 0
def delete_user(user_id: int):
    """Menghapus user berdasarkan ID (menonaktifkan akun)"""
    if not os.path.exists(USERPATH):
        return {"error": "Dataset tidak ditemukan."}
    df = pd.read_csv(USERPATH)
    if user_id not in df["id"].astype(int).values:
        return {"error": f"User dengan id {user_id} tidak ditemukan."}
    
    df.loc[df["id"].astype(int) == user_id, "status_approval"] = 0
    df.to_csv(USERPATH, index=False)
    return {"success": f"User dengan id {user_id} telah dinonaktifkan."}

# delete batch user dengan menonaktifkan akun pada status_approval menjadi 0
def delete_batch_users(user_ids: list):
    """Menonaktifkan banyak user sekaligus berdasarkan list ID"""
    if not os.path.exists(USERPATH):
        return {"error": "Dataset tidak ditemukan."}

    if not isinstance(user_ids, list) or len(user_ids) == 0:
        return {"error": "Input harus berupa list id user yang valid."}

    df = pd.read_csv(USERPATH)
    id_values = df["id"].astype(int).values

    not_found = []
    updated_count = 0

    for user_id in user_ids:
        if user_id in id_values:
            df.loc[df["id"].astype(int) == user_id, "status_approval"] = 0
            updated_count += 1
        else:
            not_found.append(user_id)

    df.to_csv(USERPATH, index=False)

    if len(not_found) == len(user_ids):
        return {"error": "Tidak ada user yang ditemukan untuk dihapus."}

    msg = f"{updated_count} user berhasil dinonaktifkan."
    if not_found:
        msg += f" (ID tidak ditemukan: {not_found})"
    return {"success": msg}

# download users dataset bentuk CSV
def download_users_csv():
    """Download dataset users dalam format CSV"""
    if not os.path.exists(USERPATH):
        return {"error": "Dataset tidak ditemukan."}
    
    return send_file(
        USERPATH,
        mimetype="text/csv",
        as_attachment=True,
        download_name="users_dataset.csv"
    )

# download users dataset bentuk excel
def download_users_excel():
    """Download dataset users dalam format Excel"""
    if not os.path.exists(USERPATH):
        return {"error": "Dataset tidak ditemukan."}

    df = pd.read_csv(USERPATH)

    # Buat buffer file Excel di memori
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Users")
        writer.save()
    excel_buffer.seek(0)

    return Response(
        excel_buffer.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=users_dataset.xlsx"
        }
    )
