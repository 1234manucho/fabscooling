import os
import secrets
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import or_

from models import Inquiry, NewsletterSubscriber, db


load_dotenv()
csrf = CSRFProtect()

SOLUTIONS = [
    {
        "slug": "modular-cold-rooms",
        "number": "01",
        "title": "Modular Cold Rooms",
        "summary": "Flexible chiller and freezer rooms engineered around capacity, temperature and available footprint.",
        "spec": "+8°C to −40°C",
        "icon": "box",
    },
    {
        "slug": "insulated-panel-systems",
        "number": "02",
        "title": "Insulated Panel Systems",
        "summary": "Hygienic wall, ceiling and floor panels with dependable thermal performance and sealed joints.",
        "spec": "PUR / PIR systems",
        "icon": "panels",
    },
    {
        "slug": "industrial-refrigeration",
        "number": "03",
        "title": "Industrial Refrigeration",
        "summary": "Condensing units, evaporators and controls selected for reliable, efficient daily operation.",
        "spec": "Application-sized",
        "icon": "fan",
    },
    {
        "slug": "cold-room-doors",
        "number": "04",
        "title": "Cold Room Doors",
        "summary": "Hinged, sliding and service doors designed for airtight performance, durability and safe access.",
        "spec": "Chiller / freezer",
        "icon": "door",
    },
    {
        "slug": "hvac-ventilation",
        "number": "05",
        "title": "HVAC & Ventilation",
        "summary": "Comfort cooling, extraction and controlled-air solutions for commercial and industrial spaces.",
        "spec": "Balanced airflows",
        "icon": "gauge",
    },
    {
        "slug": "service-maintenance",
        "number": "06",
        "title": "Service & Maintenance",
        "summary": "Preventive care, diagnostics and system optimization that protect uptime and product integrity.",
        "spec": "Lifecycle support",
        "icon": "wrench",
    },
]

INDUSTRIES = [
    {"number": "01", "title": "Food Processing", "copy": "Hygienic cooling for production, preparation and storage."},
    {"number": "02", "title": "Agriculture", "copy": "Post-harvest temperature control for better product life."},
    {"number": "03", "title": "Pharmaceuticals", "copy": "Stable environments for temperature-sensitive products."},
    {"number": "04", "title": "Retail & Hospitality", "copy": "Dependable back-of-house refrigeration and comfort cooling."},
    {"number": "05", "title": "Warehousing", "copy": "Scalable cold storage for distribution and logistics."},
]

EQUIPMENT = [
    {
        "number": "01",
        "family": "Comfort cooling",
        "title": "Split & Multi-Split AC",
        "copy": "Wall-mounted and multi-zone air conditioning for offices, retail, hospitality and residential spaces.",
        "image": "https://www.infobae.com/resizer/v2/IUBWSNQEORAB5EZOEFIBQ6D6UQ.jpg?auth=94a81d47d317d5ab173da7fd644a1542e76ec2557f7c07fe28448a804cab2f67&height=800&quality=88&smart=true&width=1400",
    },
    {
        "number": "02",
        "family": "Commercial HVAC",
        "title": "Packaged & Rooftop Units",
        "copy": "High-capacity packaged systems for open commercial areas, production spaces and large facilities.",
        "image": "https://media.licdn.com/dms/image/v2/C561BAQGx5eJcEQpJXQ/company-background_10000/company-background_10000/0/1626351026138/mitsubishi_electric_ireland_living_environmental_systems_cover?e=2147483647&t=9U8P_W3KSCIV8f3hLrtDuRb3FbFEgzC_OdkGOcbz4qw&v=beta",
    },
    {
        "number": "03",
        "family": "Central plants",
        "title": "Chillers & Chilled Water",
        "copy": "Central cooling plants, pumps and hydronic distribution for high-load commercial and industrial sites.",
        "image": "https://aquilacommercial.com/wp-content/uploads/2024/01/IMG_8394.png",
    },
    {
        "number": "04",
        "family": "Air movement",
        "title": "Ventilation & Ductwork",
        "copy": "Fresh-air, extraction and heat-recovery systems designed for balanced airflow and indoor air quality.",
        "image": "https://www.allaround-hvac-construction.com/wp-content/uploads/2024/07/Heat-Recovery-Ventilation.webp",
    },
    {
        "number": "05",
        "family": "Cold storage",
        "title": "Cold Room Evaporators",
        "copy": "High-airflow unit coolers configured for chillers, freezers, produce rooms and large cold stores.",
        "image": "https://image.made-in-china.com/2f0j00duroVBUEEFcn/Refrigeration-Unit-Cooling-System-Cold-Room-Vegetable-Cold-Storage-Room.jpg",
    },
    {
        "number": "06",
        "family": "Industrial refrigeration",
        "title": "Compressor Rack Systems",
        "copy": "Multi-compressor systems, receivers, controls and pipework for dependable high-capacity operation.",
        "image": "https://amal-bio.com/uploads/post/content/8fce640852b12a82a8eb91134c4600ac.jpg",
    },
    {
        "number": "07",
        "family": "Rapid cooling",
        "title": "Blast Freezer Systems",
        "copy": "Fast-pull-down refrigeration and evaporator arrays for food production and temperature-critical processing.",
        "image": "https://holodprom.com.ua/sites/default/files/viber_image_2021-01-17_11-31-10.jpg",
    },
    {
        "number": "08",
        "family": "Service lifecycle",
        "title": "Controls, Repair & Maintenance",
        "copy": "Diagnostics, planned care, component replacement and system optimization across cooling technologies.",
        "image": "https://www.carlislerefrigeration.co.uk/wp-content/uploads/2017/11/1.jpg",
    },
]

PARTNERS = [
    {"name": "IE Cooling", "domain": "iecooling.com", "role": "Cold rooms & cooling units", "url": "https://www.iecooling.com/"},
    {"name": "Korkmaz Panel", "domain": "korkmazpanel.com", "role": "Insulated panel systems", "url": "https://www.korkmazpanel.com/en"},
    {"name": "Daikin", "domain": "daikin.com", "role": "Air conditioning & VRF", "url": "https://www.daikin.com/"},
    {"name": "Carrier", "domain": "carrier.com", "role": "Commercial HVAC", "url": "https://www.carrier.com/"},
    {"name": "Trane", "domain": "trane.com", "role": "Chillers & air systems", "url": "https://www.trane.com/"},
    {"name": "Mitsubishi Electric", "domain": "mitsubishielectric.com", "role": "VRF & comfort cooling", "url": "https://www.mitsubishielectric.com/"},
    {"name": "Danfoss", "domain": "danfoss.com", "role": "Refrigeration controls", "url": "https://www.danfoss.com/"},
    {"name": "BITZER", "domain": "bitzer.de", "role": "Refrigeration compressors", "url": "https://www.bitzer.de/"},
    {"name": "Copeland", "domain": "copeland.com", "role": "Compression technology", "url": "https://www.copeland.com/"},
    {"name": "CAREL", "domain": "carel.com", "role": "Controls & monitoring", "url": "https://www.carel.com/"},
    {"name": "Güntner", "domain": "guntner.com", "role": "Heat exchange systems", "url": "https://guntner.com/"},
    {"name": "Mayekawa", "domain": "mayekawa.com", "role": "Industrial refrigeration", "url": "https://mayekawa.com/"},
    {"name": "ebm-papst", "domain": "ebmpapst.com", "role": "Fans & air movement", "url": "https://www.ebmpapst.com/"},
    {"name": "Alfa Laval", "domain": "alfalaval.com", "role": "Heat transfer equipment", "url": "https://www.alfalaval.com/"},
    {"name": "Panasonic", "domain": "panasonic.com", "role": "Commercial air conditioning", "url": "https://www.panasonic.com/"},
    {"name": "LG", "domain": "lg.com", "role": "Multi-zone HVAC systems", "url": "https://www.lg.com/"},
]

DOCUMENTATION = [
    {"number": "01", "title": "Site Survey & Design Brief", "copy": "Room dimensions, ambient conditions, product profile, workflow, utilities and future capacity recorded before system selection.", "icon": "ruler"},
    {"number": "02", "title": "Cooling-Load Basis", "copy": "A traceable engineering basis covering product load, transmission, infiltration, occupancy, pull-down and operating assumptions.", "icon": "gauge"},
    {"number": "03", "title": "Technical Proposal & BOQ", "copy": "Clear scope, equipment capacity, panel and door specifications, controls, exclusions, pricing structure and delivery responsibilities.", "icon": "file-check-2"},
    {"number": "04", "title": "Equipment Submittals", "copy": "Model schedules, technical data sheets, power requirements, refrigerant information and approved component selections.", "icon": "package-check"},
    {"number": "05", "title": "Installation & Commissioning", "copy": "Installation method, pressure tests, evacuation, control setup, temperature testing, snag closure and commissioning results.", "icon": "test-tube-2"},
    {"number": "06", "title": "Handover & Maintenance File", "copy": "Operating guidance, warranty information, preventive-maintenance plan, service contacts and system records for lifecycle care.", "icon": "clipboard-check"},
]

PROJECTS = [
    {
        "type": "Cold chain",
        "title": "High-capacity cold storage",
        "copy": "A scalable environment planned around product flow, hygiene and energy use.",
        "image": "https://mayekawa.com/applications/cold_storage/images/img_sec02.jpg",
    },
    {
        "type": "Industrial",
        "title": "Precision plant cooling",
        "copy": "Integrated refrigeration and controls designed for stable, dependable operation.",
        "image": "https://thecoldroomkahuna.com/wp-content/uploads/2024/12/Cold-Room-refrigeration-system.jpeg",
    },
    {
        "type": "Air systems",
        "title": "Turnkey HVAC delivery",
        "copy": "From site assessment and sizing through ducting, installation, testing and handover.",
        "image": "https://www.allaround-hvac-construction.com/wp-content/uploads/2024/07/Heat-Recovery-Ventilation.webp",
    },
]


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    database_url = os.getenv("DATABASE_URL") or "sqlite:///fabs_cooling.db"
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", secrets.token_hex(32)),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=4 * 1024 * 1024,
        COMPANY_EMAIL=os.getenv("COMPANY_EMAIL", "info@fabscooling.com"),
        COMPANY_PHONE=os.getenv("COMPANY_PHONE", "+254 700 000 000"),
        COMPANY_ADDRESS=os.getenv("COMPANY_ADDRESS", "Nairobi, Kenya"),
    )

    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_globals():
        return {
            "solutions": SOLUTIONS,
            "industries": INDUSTRIES,
            "equipment": EQUIPMENT,
            "partners": PARTNERS,
            "documentation": DOCUMENTATION,
            "projects": PROJECTS,
            "company_email": app.config["COMPANY_EMAIL"],
            "company_phone": app.config["COMPANY_PHONE"],
            "company_address": app.config["COMPANY_ADDRESS"],
            "current_year": datetime.utcnow().year,
        }

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/company")
    def company():
        return render_template("company.html")

    @app.get("/solutions")
    def solutions_page():
        return render_template("solutions.html")

    @app.get("/industries")
    def industries_page():
        return render_template("industries.html")

    @app.get("/projects")
    def projects_page():
        return render_template("projects.html")

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            required = {
                "full_name": "Name",
                "email": "Email",
                "solution": "Solution",
                "message": "Project brief",
            }
            missing = [label for field, label in required.items() if not request.form.get(field, "").strip()]
            if missing:
                flash(f"Please complete: {', '.join(missing)}.", "error")
                return render_template("contact.html"), 400

            reference = f"FCL-{datetime.utcnow():%y%m%d}-{secrets.token_hex(2).upper()}"
            inquiry = Inquiry(
                reference=reference,
                full_name=request.form["full_name"].strip(),
                company=request.form.get("company", "").strip(),
                email=request.form["email"].strip().lower(),
                phone=request.form.get("phone", "").strip(),
                solution=request.form["solution"].strip(),
                location=request.form.get("location", "").strip(),
                target_temperature=request.form.get("target_temperature", "").strip(),
                message=request.form["message"].strip(),
            )
            db.session.add(inquiry)
            db.session.commit()
            return redirect(url_for("inquiry_success", reference=reference))
        return render_template("contact.html")

    @app.get("/enquiry/success/<reference>")
    def inquiry_success(reference):
        inquiry = db.session.execute(db.select(Inquiry).filter_by(reference=reference)).scalar_one_or_none()
        if not inquiry:
            abort(404)
        return render_template("inquiry_success.html", inquiry=inquiry)

    @app.post("/newsletter")
    def newsletter():
        email = request.form.get("email", "").strip().lower()
        if not email or "@" not in email:
            flash("Please enter a valid email address.", "error")
            return redirect(request.referrer or url_for("index"))
        existing = db.session.execute(db.select(NewsletterSubscriber).filter_by(email=email)).scalar_one_or_none()
        if not existing:
            db.session.add(NewsletterSubscriber(email=email))
            db.session.commit()
        flash("Thank you. You are now on the FABS Cooling updates list.", "success")
        return redirect(request.referrer or url_for("index"))

    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("admin_authenticated"):
                return redirect(url_for("admin_login", next=request.path))
            return view(*args, **kwargs)
        return wrapped

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            email_ok = secrets.compare_digest(request.form.get("email", ""), os.getenv("ADMIN_EMAIL", "admin@fabscooling.com"))
            configured_password = os.getenv("ADMIN_PASSWORD", "")
            password_ok = bool(configured_password) and secrets.compare_digest(
                request.form.get("password", ""), configured_password
            )
            if email_ok and password_ok:
                session.clear()
                session["admin_authenticated"] = True
                return redirect(url_for("admin_inquiries"))
            flash("Invalid administrator credentials.", "error")
        return render_template("admin/login.html")

    @app.get("/admin/inquiries")
    @admin_required
    def admin_inquiries():
        query = request.args.get("q", "").strip()
        status = request.args.get("status", "").strip()
        statement = db.select(Inquiry)
        if status:
            statement = statement.where(Inquiry.status == status)
        if query:
            like = f"%{query}%"
            statement = statement.where(or_(Inquiry.reference.ilike(like), Inquiry.full_name.ilike(like), Inquiry.company.ilike(like), Inquiry.email.ilike(like)))
        inquiries = db.session.execute(statement.order_by(Inquiry.created_at.desc())).scalars().all()
        counts = {name: db.session.scalar(db.select(db.func.count()).select_from(Inquiry).where(Inquiry.status == name)) for name in ("new", "reviewing", "quoted", "closed")}
        return render_template("admin/inquiries.html", inquiries=inquiries, counts=counts, query=query, active_status=status)

    @app.post("/admin/inquiries/<int:inquiry_id>/status")
    @admin_required
    def admin_update_status(inquiry_id):
        inquiry = db.get_or_404(Inquiry, inquiry_id)
        status = request.form.get("status", "")
        if status not in {"new", "reviewing", "quoted", "closed"}:
            abort(400)
        inquiry.status = status
        db.session.commit()
        flash(f"{inquiry.reference} updated.", "success")
        return redirect(url_for("admin_inquiries"))

    @app.post("/admin/logout")
    @admin_required
    def admin_logout():
        session.clear()
        return redirect(url_for("admin_login"))

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "fabs-cooling"}

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("FABS Cooling database initialized.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
