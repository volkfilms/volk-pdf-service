import io, os, tempfile
from flask import Flask, request, send_file, jsonify
import generate_weekly_report as gen
app = Flask(__name__)
TOKEN = os.environ.get("VOLK_TOKEN", "")
@app.get("/")
def health():
    return "ok", 200
@app.post("/pdf")
def pdf():
    if TOKEN and request.headers.get("X-Volk-Token", "") != TOKEN:
        return jsonify({"error": "token invalido"}), 401
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "se esperaba JSON"}), 400
    data.setdefault("titulo", "Cierre de Semana - Equipo Volk")
    data.setdefault("responsable", "Raul Lopez")
    data.setdefault("kpi", {"completadas": 0, "pendientes": 0, "cumplimiento": 0})
    nombre = data.get("output_filename") or "Reporte_Semanal_Equipo_VOLK_MEDIA.pdf"
    if not nombre.lower().endswith(".pdf"):
        nombre += ".pdf"
    try:
        with tempfile.TemporaryDirectory() as td:
            ruta = os.path.join(td, "reporte.pdf")
            gen.build(data, ruta)
            with open(ruta, "rb") as f:
                blob = f.read()
    except Exception as e:
        return jsonify({"error": "fallo generando PDF", "detalle": str(e)}), 500
    return send_file(io.BytesIO(blob), mimetype="application/pdf", as_attachment=True, download_name=nombre)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
