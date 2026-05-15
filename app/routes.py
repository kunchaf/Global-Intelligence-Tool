from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from .api.scraper import get_religious_breakdown
from .api.un_projections import get_un_projections
from .api.world_bank import fetch_country_data
from .compare import ALLOWED_DIMENSIONS, DIM_LABELS, build_compare_payload
from .compare_store import get_compare_payload, store_compare_payload
from .excel_export import build_compare_excel

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html", dim_labels=DIM_LABELS)


@bp.post("/compare/submit")
def compare_submit():
    c1 = (request.form.get("country1") or "").strip()
    c2 = (request.form.get("country2") or "").strip()
    c3 = (request.form.get("country3") or "").strip()
    names = [x for x in (c1, c2, c3) if x]
    if not names:
        flash("Country 1 is required.", "error")
        return redirect(url_for("main.index"))

    dims_in = request.form.getlist("dim")
    dims = [d for d in dims_in if d in ALLOWED_DIMENSIONS]
    if not dims:
        dims = ["population"]

    payload = build_compare_payload(names, dims)
    cid = store_compare_payload(payload)
    return redirect(url_for("main.compare_results", cid=cid))


@bp.route("/compare/results")
def compare_results():
    cid = request.args.get("cid", type=str)
    data = get_compare_payload(cid)
    if not data:
        flash("Results expired or invalid link. Run a new comparison.", "error")
        return redirect(url_for("main.index"))
    return render_template(
        "compare_results.html",
        payload=data,
        dim_labels=DIM_LABELS,
        export_url=url_for("main.compare_export", cid=cid),
    )


@bp.route("/compare/export")
def compare_export():
    cid = request.args.get("cid", type=str)
    data = get_compare_payload(cid)
    if not data:
        flash("Results expired or invalid link. Export is no longer available.", "error")
        return redirect(url_for("main.index"))
    bio, download_name, mimetype = build_compare_excel(data)
    return send_file(
        bio,
        as_attachment=True,
        download_name=download_name,
        mimetype=mimetype,
    )


@bp.route("/api/compare", methods=["POST"])
def compare_demographics():
    body = request.get_json(silent=True) or {}
    raw_list = body.get("countries")
    if not isinstance(raw_list, list):
        raw_list = []
    names = []
    for item in raw_list[:3]:
        if isinstance(item, str) and item.strip():
            names.append(item.strip())
    if not names:
        return jsonify({"error": "Enter at least one country name."}), 400

    dims_in = body.get("dimensions")
    if not isinstance(dims_in, list):
        dims_in = []
    dims = [d for d in dims_in if d in ALLOWED_DIMENSIONS]
    if not dims:
        dims = ["population"]

    payload = build_compare_payload(names, dims)
    return jsonify(payload)


@bp.route("/api/intelligence/<country_code>")
def get_intelligence(country_code):
    code = country_code.strip().upper()
    wb = fetch_country_data(code)
    un_data = get_un_projections(code)
    location_name = un_data.get("location_name") if isinstance(un_data, dict) else None
    religion = get_religious_breakdown(code, country_name=location_name)

    payload = {
        "country": code,
        "world_bank": wb,
        "un": un_data,
        "religion": religion,
    }
    return jsonify(payload)
