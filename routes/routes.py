from flask import Blueprint, request, jsonify, render_template
from controllers.datasetController import (
    get_all_tenants, get_tenant_by_id,
    add_tenant, add_batch_tenants, update_tenant, 
    delete_tenant, delete_batch_tenants
)
from controllers.algoritmaController import get_recommendations_by_filters, run_clustering
from controllers.authController import register, login, approve_user
from controllers.userController import (
    get_all_users, get_user_by_id, add_user, add_batch_users
)
from middlewares.auth_middleware import token_required, role_required

routes = Blueprint("routes", __name__)

@routes.route("/") 
def home(): 
    return render_template("test.html")

# ===== API ENDUSER =====
# rekomendasi
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
    # hasil["all_spectral"] = {str(k): v.to_dict(orient="records") for k, v in hasil["all_spectral"].items()}
    return jsonify(hasil)

# ===== API ADMIN =====
# Auth admin dan superadmin
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

#dataset user
# Menampilkan semua user
@routes.route("/users", methods=["GET"])
def users():
    return jsonify(get_all_users())

# Menampilkan satuan user by id
@routes.route("/user/<int:user_id>", methods=["GET"])
def user_by_id(user_id):
    return jsonify(get_user_by_id(user_id))

# menambahkan satu user
@routes.route("/user", methods=["POST"])
def user_add():
    data = request.get_json()
    return jsonify(add_user(data))

# menambahkan batch user
@routes.route("/users/batch", methods=["POST"])
def user_add_batch():
    data = request.get_json()
    return jsonify(add_batch_users(data))

# dataset tenant
# Menampilkan semua tenant
@routes.route("/tenants", methods=["GET"])
def tenants():
    return jsonify(get_all_tenants())

# Menampilkan satu tenant berdasarkan ID
@routes.route("/tenant/<int:tenant_id>", methods=["GET"])
def tenant_by_id(tenant_id):
    return jsonify(get_tenant_by_id(tenant_id))

# Menambah satu tenant
@routes.route("/tenantAdd", methods=["POST"])
def tenant_add():
    data = request.get_json()
    return jsonify(add_tenant(data))

# Menambah banyak tenant sekaligus
@routes.route("/tenants/batch", methods=["POST"])
def tenant_add_batch():
    data = request.get_json()
    return jsonify(add_batch_tenants(data))

# Merubah data tenant berdasarkan ID
@routes.route("/tenantPut/<int:tenant_id>", methods=["PUT"])
def tenant_update(tenant_id):
    data = request.get_json()
    return jsonify(update_tenant(tenant_id, data))

# Hapus tenant berdasarkan ID
@routes.route("/tenantDelete/<int:tenant_id>", methods=["DELETE"])
def tenant_delete(tenant_id):
    return jsonify(delete_tenant(tenant_id))

# Hapus banyak tenant sekaligus
@routes.route("/tenants/batch", methods=["DELETE"])
def tenant_delete_batch():
    data = request.get_json()
    return jsonify(delete_batch_tenants(data))