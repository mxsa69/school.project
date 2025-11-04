from flask import Flask, render_template, request, redirect, url_for, session, send_file
from .db import init_db, get_db
import os, uuid, io, csv
from datetime import datetime

def _short_id():
    """Erzeugt zufällige kurze Teilnehmer-ID"""
    return uuid.uuid4().hex[:8].upper()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")

    os.makedirs(app.instance_path, exist_ok=True)
    init_db(app)

    # Health Check
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Startseite
    @app.get("/")
    def index():
        return render_template("home.html")

    # Nutzer-Start
    @app.get("/start-user")
    def start_user():
        session.clear()
        session["participant_id"] = _short_id()
        session["consent_given"] = False
        return redirect(url_for("consent"))

    # Admin Landing
    @app.get("/admin")
    def admin_home():
        return render_template("admin/landing.html")

    # Einwilligung
    @app.route("/consent", methods=["GET", "POST"])
    def consent():
        if request.method == "POST":
            if request.form.get("agree") == "1":
                session["consent_given"] = True
                return redirect(url_for("pre_survey"))
            return redirect(url_for("consent"))
        return render_template("survey/consent.html",
                               participant_id=session.get("participant_id"))

    # Pre-Survey
    @app.route("/pre", methods=["GET", "POST"])
    def pre_survey():
        if request.method == "POST":
            session["who_pre"] = [
                int(request.form["who1"]),
                int(request.form["who2"]),
                int(request.form["who3"]),
                int(request.form["who4"]),
                int(request.form["who5"]),
            ]
            session["pos_pre"] = int(request.form["positive"])
            session["stress_pre"] = int(request.form["stressed"])
            return redirect(url_for("activity"))
        return render_template("survey/pre.html",
                               participant_id=session.get("participant_id"))

    # Aktivität
    @app.route("/activity", methods=["GET", "POST"])
    def activity():
        if request.method == "POST":
            session["activity"] = app.config.get("ACTIVITY_NAME", "Flow-Klassenaktivität")
            session["level"] = app.config.get("ACTIVITY_LEVEL", "mittel")
            return redirect(url_for("post_survey"))
        return render_template("survey/activity.html",
                               activity_name=app.config.get("ACTIVITY_NAME", "Flow-Klassenaktivität"),
                               activity_level=app.config.get("ACTIVITY_LEVEL", "mittel"),
                               participant_id=session.get("participant_id"))

    # Post-Survey (NUR EINMAL, korrekt eingerückt)
    @app.route("/post", methods=["GET", "POST"])
    def post_survey():
        if request.method == "POST":
            db = get_db()

            # Antworten aus Formular holen
            flow_values = [int(request.form[f"flow{i}"]) for i in range(1, 7)]
            flow_score  = round(sum(flow_values) / len(flow_values), 2)

            who5_pre  = session.get("who_pre", [])
            who5_post = [int(request.form[f"who{i}"]) for i in range(1, 6)]

            who5_pre_sum  = sum(who5_pre) if who5_pre else None
            who5_post_sum = sum(who5_post)
            who5_pre_x4   = who5_pre_sum * 4 if who5_pre else None
            who5_post_x4  = who5_post_sum * 4
            delta_who5    = who5_post_x4 - who5_pre_x4 if who5_pre else None

            pos_pre    = session.get("pos_pre")
            stress_pre = session.get("stress_pre")
            pos_post   = int(request.form["positive"])
            stress_post= int(request.form["stressed"])
            delta_pos  = pos_post   - pos_pre    if pos_pre    is not None else None
            delta_stress = stress_post - stress_pre if stress_pre is not None else None

            # ✅ Richtiger INSERT: 31 Spalten ↔ 31 Werte
            db.execute("""
                INSERT INTO responses (
                    created_at,
                    activity, level,
                    who5_pre_1, who5_pre_2, who5_pre_3, who5_pre_4, who5_pre_5, who5_pre_sum,
                    positive_pre_0_10, stressed_pre_0_10,
                    flow_1, flow_2, flow_3, flow_4, flow_5, flow_6, flow_score,
                    who5_post_1, who5_post_2, who5_post_3, who5_post_4, who5_post_5, who5_post_sum,
                    positive_post_0_10, stressed_post_0_10,
                    who5_pre_x4, who5_post_x4, delta_who5,
                    delta_positive, delta_stressed
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                session.get("activity"),
                session.get("level"),

                who5_pre[0] if len(who5_pre) > 0 else None,
                who5_pre[1] if len(who5_pre) > 1 else None,
                who5_pre[2] if len(who5_pre) > 2 else None,
                who5_pre[3] if len(who5_pre) > 3 else None,
                who5_pre[4] if len(who5_pre) > 4 else None,
                sum(who5_pre) if who5_pre else None,

                pos_pre, stress_pre,

                flow_values[0], flow_values[1], flow_values[2],
                flow_values[3], flow_values[4], flow_values[5],
                flow_score,

                who5_post[0], who5_post[1], who5_post[2],
                who5_post[3], who5_post[4], sum(who5_post),

                pos_post, stress_post,

                who5_pre_x4, who5_post_x4, delta_who5,
                delta_pos, delta_stress
            ))
            db.commit()

            session.clear()
            return redirect(url_for("index"))

        return render_template("survey/post.html",
                               participant_id=session.get("participant_id"))

    # -------- Admin (unverändert) --------
    def admin_required():
        return session.get("is_admin") is True

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if admin_required():
            return redirect(url_for("admin_dashboard"))
        error = None
        if request.method == "POST":
            user = request.form.get("username", "")
            pw   = request.form.get("password", "")
            if user == app.config.get("ADMIN_USER") and pw == app.config.get("ADMIN_PASS"):
                session["is_admin"] = True
                return redirect(url_for("admin_dashboard"))
            else:
                error = "Ungültiger Benutzername oder Passwort."
        return render_template("admin/login.html", error=error)

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("is_admin", None)
        return redirect(url_for("index"))

    @app.route("/admin/dashboard")
    def admin_dashboard():
        if not admin_required():
            return redirect(url_for("admin_login"))
        db   = get_db()
        rows = db.execute("SELECT * FROM responses ORDER BY id DESC LIMIT 500").fetchall()
        cons = db.execute("SELECT * FROM consent_logs ORDER BY id DESC LIMIT 200").fetchall()
        n = len(rows)
        avg_flow = None
        if n:
            vals = [r["flow_score"] for r in rows if r["flow_score"] is not None]
            avg_flow = round(sum(vals) / len(vals), 2) if vals else None
        return render_template("admin/dashboard.html", rows=rows, cons=cons, n=n, avg_flow=avg_flow)

    @app.route("/admin/export.csv")
    def admin_export_csv():
        if not admin_required():
            return redirect(url_for("admin_login"))
        db   = get_db()
        rows = db.execute("SELECT * FROM responses ORDER BY id DESC").fetchall()
        if not rows:
            return "No data", 204
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
        mem = io.BytesIO(buf.getvalue().encode("utf-8"))
        return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="responses_export.csv")

    @app.route("/admin/export.json")
    def admin_export_json():
        if not admin_required():
            return redirect(url_for("admin_login"))
        db   = get_db()
        rows = db.execute("SELECT * FROM responses ORDER BY id DESC").fetchall()
        from flask import jsonify
        return jsonify([dict(r) for r in rows])

    return app
