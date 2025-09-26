from flask import Blueprint, render_template, request, jsonify
from controllers.algoritmaController import get_recommendations_by_filters, run_clustering
from controllers.datasetController import delete_tenant, get_all_tenants, get_tenant_by_id, update_tenant, add_tenant

routes = Blueprint("routes", __name__)

@routes.route("/")
def home():
    return render_template("test.html")

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

@routes.route("/clustering", methods=["GET"])
def clustering():
    hasil = run_clustering()
    hasil["all_kmeans"] = {str(k): v.to_dict(orient="records") for k, v in hasil["all_kmeans"].items()}
    hasil["all_spectral"] = {str(k): v.to_dict(orient="records") for k, v in hasil["all_spectral"].items()}
    return jsonify(hasil)

@routes.route("/tenant/delete/<int:tenant_id>", methods=["DELETE"])
def delete_tenant_route(tenant_id):
    result = delete_tenant(tenant_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result), 200

@routes.route("/tenants", methods=["GET"])
def get_all_tenants_route():
    result = get_all_tenants()
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result), 200

@routes.route("/tenant/<int:tenant_id>", methods=["GET"])
def get_tenant_by_id_route(tenant_id):
    result = get_tenant_by_id(tenant_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result), 200

@routes.route("/tenant/update/<int:tenant_id>", methods=["PUT"])
def update_tenant_route(tenant_id):
    update_data = request.json
    result = update_tenant(tenant_id, update_data)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result), 200

@routes.route("/tenant/add", methods=["POST"])
def add_tenant_route():
    tenant_data = request.json
    result = add_tenant(tenant_data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201
