from flask import Blueprint, render_template, request, jsonify
from controllers.algoritmaController import get_recommendations_by_filters, run_clustering

routes = Blueprint("routes", __name__)

@routes.route("/")
def home():
    return render_template("index.html")

@routes.route("/recommend", methods=["GET"])
def recommend():
    lokasi = request.args.get("lokasi")
    aktivitas = request.args.get("aktivitas")
    harga = request.args.get("harga")

    hasil = get_recommendations_by_filters(lokasi, aktivitas, harga, top_n=20)
    if hasil is None:
        return jsonify({"error": "Minimal isi salah satu filter (lokasi / aktivitas / harga)."}), 400
    if isinstance(hasil, str):
        return jsonify({"error": hasil}), 400

    return jsonify(hasil.to_dict(orient="records"))

@routes.route("/clustering", methods=["GET"])
def clustering():
    hasil = run_clustering()
    hasil["top_kmeans"] = {str(k): v.to_dict(orient="records") for k, v in hasil["top_kmeans"].items()}
    hasil["top_spectral"] = {str(k): v.to_dict(orient="records") for k, v in hasil["top_spectral"].items()}
    return jsonify(hasil)

