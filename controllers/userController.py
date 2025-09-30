import os
import pandas as pd

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

# add user hanya untuk superadmin
def add_user(user_data: dict):
    """"Tambah satu user"""
    df = pd.read_csv(USERPATH) if os.path.exists(USERPATH) else pd.DataFrame()
    
    # auto-assign ID
    next_id = 1 if df.empty else df["id"].max() + 1
    user_data["id"] = int(next_id)

    df = pd.concat([df, pd.DataFrame([user_data])], ignore_index=True)
    df.to_csv(USERPATH, index=False)
    return {"success": f"User baru dengan id {next_id} berhasil ditambahkan."}

# add batch user hanya untuk superadmin
def add_batch_users(users_data: list):
    """Tambah banyak user sekaligus"""
    if not users_data or not isinstance(users_data, list):
        return {"error": "Input harus berupa list of user data."}

    df = pd.read_csv(USERPATH) if os.path.exists(USERPATH) else pd.DataFrame()

    # Cari ID terakhir
    next_id = 1 if df.empty else df["id"].max() + 1

    # Tambahkan ID ke setiap user baru
    for i, user in enumerate(users_data):
        user["id"] = int(next_id + i)

    # Gabungkan ke dataset
    new_df = pd.DataFrame(users_data)
    df = pd.concat([df, new_df], ignore_index=True)

    # Simpan ulang
    df.to_csv(USERPATH, index=False)
    return {"success": f"{len(users_data)} user baru berhasil ditambahkan."}

# update user
def update_user(user_id: int, user_data: dict):
    """Merubah data user berdasarkan ID"""
    if not os.path.exists(USERPATH):
        return {"error": "Dataset tidak ditemukan."}
    df = pd.read_csv(USERPATH)
    if user_id not in df["id"].astype(int).values:
        return {"error": f"User dengan id {user_id} tidak ditemukan."}
    
    for key, value in user_data.items():
        if key in df.columns:
            df.loc[df["id"].astype(int) == user_id, key] = value

    df.to_csv(USERPATH, index=False)
    return {"success": f"Data user dengan id {user_id} berhasil diperbarui."}

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