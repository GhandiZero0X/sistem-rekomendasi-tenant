# routes/routes.py
import pandas as pd
import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from controllers.datasetController import (
    get_all_tenants, get_tenant_by_id,
    add_tenant, add_batch_tenants, update_tenant, 
    delete_tenant, delete_batch_tenants, download_dataset_csv, download_dataset_excel
)
from controllers.algoritmaController import get_recommendations_by_filters, run_clustering, get_top_recommendation
from controllers.authController import register, login, approve_user
from controllers.userController import (
    get_all_users, get_user_by_id, add_user, add_batch_users, update_user, delete_user, delete_batch_users, download_users_csv, download_users_excel
)
from controllers.dashboardController import get_superadmin_dashboard, get_admin_dashboard
from utils.jwt_utils import decode_token
from middlewares.auth_middleware import token_required, role_required
from werkzeug.utils import secure_filename

routes = Blueprint("routes", __name__)

UPLOAD_FOLDER = "static/images/tenant"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ===== Page Frontend =====
# Home page route
@routes.route("/")
def home():
    # Jalankan clustering
    hasil_cluster = run_clustering()

    # Ambil cluster 1 (populer) dan cluster 0 (baru)
    cluster_popular = hasil_cluster["all_kmeans"].get(1, pd.DataFrame())
    cluster_new = hasil_cluster["all_kmeans"].get(0, pd.DataFrame())

    # Ambil rekomendasi top tenant (yang sudah difilter Service & Mahal)
    top_tenant = get_top_recommendation(top_n=10)

    # Kirim semua ke template
    return render_template(
        "index.html",
        top_tenant=top_tenant.to_dict(orient="records"),
        cluster_popular=cluster_popular.to_dict(orient="records"),
        cluster_new=cluster_new.to_dict(orient="records"),
    )

@routes.route("/test")
def test(): 
    return render_template("test.html")

# login page route
@routes.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        response = login()  # langsung return Flask response

        # Flask response bisa unpack ke (obj, code)
        if isinstance(response, tuple):
            res_obj, status = response
        else:
            res_obj, status = response, 200

        # Ambil data json dari objek Flask Response
        result = res_obj.get_json()

        if "error" in result:
            return jsonify(result), status

        # Simpan token dan role ke session
        session["token"] = result["token"]
        session["role"] = result["role"]

        # Redirect sesuai role
        if result["role"] == "superadmin":
            return jsonify({"redirect": url_for("routes.dashboard")})
        else:
            return jsonify({"redirect": url_for("routes.dashboard")})

    return render_template("pages/login.html")

# logout route
@routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login_page"))

# register page route
@routes.route("/register")
def register_page():
    return render_template("pages/register.html")

# dashboard page route
@routes.route("/dashboard")
@token_required
@role_required(["admin","superadmin"])
def dashboard():
    total_users = get_all_users()
    total_tenants = len(get_all_tenants())
    
    # hitung berdasarkan role user
    total_admins = sum(1 for u in total_users if u.get("role") == "admin")
    total_superadmins = sum(1 for u in total_users if u.get("role") == "superadmin")
    
    tenant_recommendasi = get_top_recommendation(top_n=30)

    return render_template("pages/dashboard.html", total_users=total_users, total_tenants=total_tenants,
                            total_admins=total_admins, total_superadmins=total_superadmins,
                            tenant_recommendasi=tenant_recommendasi.to_dict(orient="records"))

# user dashboard page route
@routes.route("/dashboardUser")
@token_required
@role_required(["superadmin"])
def user_dashboard():
    users = get_all_users()
    return render_template("pages/dashboardUser.html", users=users)

# download users dataset dalam format CSV
@routes.route("/download/users/csv", methods=["GET"])
@token_required
@role_required(["superadmin"])
def download_userscsv():
    return download_users_csv()

# download users dataset dalam format Excel
@routes.route("/download/users/excel", methods=["GET"])
@token_required
@role_required(["superadmin"])
def download_usersexcel():
    return download_users_excel()

# tenant dashboard page route
@routes.route("/dashboardTenant")
@token_required
@role_required(["admin", "superadmin"])
def tenant_dashboard():
    tenants = get_all_tenants()
    return render_template("pages/dashboardTenant.html", tenants=tenants)

# === Download dataset dalam format CSV ===
@routes.route("/download/csv", methods=["GET"])
@token_required
@role_required(["admin", "superadmin"])
def download_csv():
    return download_dataset_csv()

# === Download dataset dalam format Excel ===
@routes.route("/download/excel", methods=["GET"])
@token_required
@role_required(["admin", "superadmin"])
def download_excel():
    return download_dataset_excel()

# edit tenant page route
@routes.route("/editTenant", methods=["GET", "POST"])
@token_required
@role_required(["admin", "superadmin"])
def editTenant():
    tenant_id = request.args.get("id", type=int)

    if request.method == "GET":
        if not tenant_id:
            return redirect(url_for("routes.tenant_dashboard"))

        # Ambil data tenant berdasarkan ID
        tenant = get_tenant_by_id(tenant_id)
        if "error" in tenant:
            return jsonify(tenant), 404

        return render_template("pages/edit-tenant.html", tenant=tenant)

    # Kalau POST (submit form edit)
    nama_brand = request.form.get("nama_brand")
    jenis_usaha = request.form.get("jenis_usaha")
    lokasi = request.form.get("lokasi")
    rating = request.form.get("rating")
    total_review = request.form.get("total_review")
    rentang_harga = request.form.get("rentang_harga")
    gambar = request.files.get("gambar")

    update_data = {
        "nama_brand": nama_brand,
        "jenis_usaha": jenis_usaha,
        "lokasi": lokasi,
        "rating": rating,
        "total_review": total_review,
        "rentang_harga": rentang_harga
    }

    if gambar and allowed_file(gambar.filename):
        filename = secure_filename(gambar.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        gambar.save(save_path)
        update_data["gambar"] = filename

    result = update_tenant(tenant_id, update_data)

    if "error" in result:
        return jsonify(result), 400

    return redirect(url_for("routes.tenant_dashboard"))

# add tenant page route
@routes.route("/addTenant", methods=["GET", "POST"])
@token_required
@role_required(["admin", "superadmin"])
def addTenant():
    if request.method == "POST":
        nama_brand = request.form.get("nama_brand")
        jenis_usaha = request.form.get("jenis_usaha")
        lokasi = request.form.get("lokasi")
        rating = request.form.get("rating")
        total_review = request.form.get("total_review")
        rentang_harga = request.form.get("rentang_harga")
        gambar = request.files.get("gambar")

        if not nama_brand or not jenis_usaha:
            return jsonify({"error": "Nama brand dan jenis usaha wajib diisi"}), 400

        filename = None
        if gambar and allowed_file(gambar.filename):
            filename = secure_filename(gambar.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            gambar.save(save_path)
        else:
            return jsonify({"error": "Format gambar tidak valid"}), 400

        tenant_data = {
            "nama_brand": nama_brand,
            "jenis_usaha": jenis_usaha,
            "lokasi": lokasi,
            "rating": rating,
            "total_review": total_review,
            "rentang_harga": rentang_harga,
            "gambar": filename  # hanya nama file
        }

        add_tenant(tenant_data)
        return redirect(url_for("routes.tenant_dashboard"))

    return render_template("pages/add-tenant.html")

@routes.route("/editUser", methods=["GET", "POST"])
@token_required
@role_required("superadmin")
def editUser():
    user_id = request.args.get("id", type=int)

    # Validasi ID
    if not user_id:
        return redirect(url_for("routes.user_dashboard"))

    if request.method == "GET":
        # Ambil data user
        user = get_user_by_id(user_id)
        if "error" in user:
            return jsonify(user), 404

        return render_template("pages/edit-user.html", user=user)

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("roleUser")
        status = request.form.get("statusApproval")

        # Mapping status ke angka
        if status == "disetujui":
            status_value = 1
        elif status == "menunggu":
            status_value = 0
        else:
            status_value = None

        update_data = {
            "username": username,
            "password": password,
            "role": role,
            "status_approval": status_value,
        }

        result = update_user(user_id, update_data)
        if "error" in result:
            return jsonify(result), 400

        # Sukses redirect ke dashboard
        return redirect(url_for("routes.user_dashboard"))

# Add User (hanya superadmin)
@routes.route("/addUser", methods=["GET", "POST"])
@token_required
@role_required("superadmin")
def addUser():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("roleUser")
        # Validasi field
        if not username or not password or not role:
            return jsonify({"error": "Semua field harus diisi"}), 400
        # Buat dictionary untuk dikirim ke controller
        user_data = {
            "username": username,
            "password": password,
            "role": role,
        }
        # Simpan lewat controller
        result = add_user(user_data)

        if "error" in result:
            return jsonify(result), 400

        return redirect(url_for("routes.user_dashboard"))
    return render_template("pages/add-user.html")

# ===== API Test Postman =====
# ===== Page Auth : admin dan superadmin =====
# Register admin baru
@routes.route("/register", methods=["POST"])
def register_route():
    return register()

# Login admin dan superadmin
@routes.route("/login", methods=["POST"])
def login_route():
    return login()

# Approve akun admin oleh superadmin
@routes.route("/approve/<int:user_id>", methods=["PUT"])
@token_required
@role_required("superadmin")
def approve_route(user_id):
    return approve_user(user_id)

# ===== Page dashboard =====
@routes.route("/admin", methods=["GET"])
@token_required
def dashboard_test():
    auth_header = request.headers.get("Authorization")
    token = auth_header.replace("Bearer ", "")
    decoded = decode_token(token)
    user_role = decoded.get("role")

    if user_role == "superadmin":
        return jsonify(get_superadmin_dashboard())
    elif user_role == "admin":
        return jsonify(get_admin_dashboard())
    else:
        return jsonify({"error": "Unauthorized access"}), 403

# ===== Page CRUD USER : dataset user =====
# Menampilkan semua user
@routes.route("/usersAll", methods=["GET"])
@token_required
@role_required("superadmin")
def users():
    return jsonify(get_all_users())

# Menampilkan satuan user by id
@routes.route("/userGet/<int:user_id>", methods=["GET"])
@token_required
@role_required("superadmin")
def user_by_id(user_id):
    return jsonify(get_user_by_id(user_id))

# menambahkan satu user
@routes.route("/userAdd", methods=["POST"])
@token_required
@role_required("superadmin")
def user_add():
    data = request.get_json()
    return jsonify(add_user(data))

# menambahkan batch user
@routes.route("/users/batch", methods=["POST"])
@token_required
@role_required("superadmin")
def user_add_batch():
    data = request.get_json()
    return jsonify(add_batch_users(data))

# merubah data user berdasarkan id
@routes.route("/userPut/<int:user_id>", methods=["PUT"])
@token_required
@role_required("superadmin")
def user_update(user_id):
    data = request.get_json()
    return jsonify(update_user(user_id, data))

# menghapus user berdasarkan id
@routes.route("/userDelete/<int:user_id>", methods=["DELETE"])
@token_required
@role_required("superadmin")
def user_delete(user_id):
    return jsonify(delete_user(user_id))

# menghapus batch user
@routes.route("/users/batch", methods=["DELETE"])
@token_required
@role_required("superadmin")
def user_delete_batch():
    data = request.get_json()
    return jsonify(delete_batch_users(data))

# ===== Page CRUD TENANT : dataset tenant =====
# Menampilkan semua tenant
@routes.route("/tenants", methods=["GET"])
@token_required
@role_required(["admin", "superadmin"])
def tenants():
    return jsonify(get_all_tenants())

# Menampilkan satu tenant berdasarkan ID
@routes.route("/tenant/<int:tenant_id>", methods=["GET"])
@token_required
@role_required(["admin", "superadmin"])
def tenant_by_id(tenant_id):
    return jsonify(get_tenant_by_id(tenant_id))

# Menambah satu tenant
@routes.route("/tenantAdd", methods=["POST"])
@token_required
@role_required(["admin", "superadmin"])
def tenant_add():
    data = request.get_json()
    return jsonify(add_tenant(data))

# Menambah banyak tenant sekaligus
@routes.route("/tenants/batch", methods=["POST"])
@token_required
@role_required(["admin", "superadmin"])
def tenant_add_batch():
    data = request.get_json()
    return jsonify(add_batch_tenants(data))

# Merubah data tenant berdasarkan ID
@routes.route("/tenantPut/<int:tenant_id>", methods=["PUT"])
@token_required
@role_required(["admin", "superadmin"])
def tenant_update(tenant_id):
    data = request.get_json()
    return jsonify(update_tenant(tenant_id, data))

# Hapus tenant berdasarkan ID
@routes.route("/tenantDelete/<int:tenant_id>", methods=["DELETE"])
@token_required
@role_required(["admin", "superadmin"])
def tenant_delete(tenant_id):
    return jsonify(delete_tenant(tenant_id))

# Hapus banyak tenant sekaligus
@routes.route("/tenants/batch", methods=["DELETE"])
@token_required
@role_required(["admin", "superadmin"])
def tenant_delete_batch():
    data = request.get_json()
    return jsonify(delete_batch_tenants(data))

# ===== Page HOME REKOMENDASI : API ENDUSER =====
# rekomendasi top 10 tenant berdasarkan rating dan jumlah rating tenant
@routes.route("/toptenants", methods=["GET"])
def top_tenants():
    from controllers.algoritmaController import get_top_recommendation
    hasil = get_top_recommendation(top_n=10)
    return jsonify(hasil.to_dict(orient="records"))

@routes.route("/recommend", methods=["GET"])
def recommend():
    lokasi = request.args.get("lokasi")
    aktivitas = request.args.get("aktivitas")
    harga = request.args.get("harga")
    hasil = get_recommendations_by_filters(lokasi, aktivitas, harga, top_n=30)

    if hasil is None:
        return jsonify({"error": "Minimal isi salah satu filter (lokasi / aktivitas / harga)."}), 400
    if isinstance(hasil, str):
        return jsonify({"error": hasil}), 400
    return jsonify(hasil.to_dict(orient="records"))

# clustering
@routes.route("/clustering", methods=["GET"])
def clustering():
    hasil = run_clustering()
    hasil["all_kmeans"] = {str(k): v.to_dict(orient="records") for k, v in hasil["all_kmeans"].items()}
    return jsonify(hasil)
