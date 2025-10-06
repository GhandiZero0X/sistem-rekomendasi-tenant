import pandas as pd
from flask import Blueprint, request, jsonify, render_template
from controllers.datasetController import (
    get_all_tenants, get_tenant_by_id,
    add_tenant, add_batch_tenants, update_tenant, 
    delete_tenant, delete_batch_tenants
)
from controllers.algoritmaController import get_recommendations_by_filters, run_clustering, get_top_recommendation
from controllers.authController import register, login, approve_user
from controllers.userController import (
    get_all_users, get_user_by_id, add_user, add_batch_users, update_user, delete_user
)
from controllers.dashboardController import get_superadmin_dashboard, get_admin_dashboard
from utils.jwt_utils import decode_token
from middlewares.auth_middleware import token_required, role_required

routes = Blueprint("routes", __name__)

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
@routes.route("/loginPage")
def login_page():
    return render_template("login.html")

# register page route
@routes.route("/registerPage")
def register_page():
    return render_template("register.html")

# dashboard page route
@routes.route("/dashboardPage")
@token_required
def dashboard_page():
    return render_template("dashboard.html")

# tenant page route
@routes.route("/tenant")
def tenant():
    return render_template("tenant.html")

# edit tenant page route
@routes.route("/editTenant")
def editTenant():
    return render_template("editTenant.html")

# user page route
@routes.route("/user")
def user():
    return render_template("user.html")

# edit user page route
@routes.route("/editUser")
def editUser():
    return render_template("editUser.html")

# ===== API ADMIN =====
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
@routes.route("/dashboard", methods=["GET"])
@token_required
def dashboard():
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
    hasil = get_recommendations_by_filters(lokasi, aktivitas, harga, top_n=50)

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
