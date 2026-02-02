from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from flask_login import login_user
from . import db
from .modals import User
from datetime import datetime
from functools import wraps

views = Blueprint("views", __name__)
home = "views.home_page"


def admin_required(f):
    """Decorator to require admin login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Admin access required", "danger")
            return redirect(url_for("views.admin_login"))
        return f(*args, **kwargs)
    return decorated_function


def dev_access_required(f):
    """Decorator to require dev access key for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        password = kwargs.get('password', '')
        dev_key = current_app.config.get('DEV_ACCESS_KEY', '')
        if not dev_key or password != dev_key:
            flash("Access denied", "danger")
            return redirect(url_for(home))
        return f(*args, **kwargs)
    return decorated_function


@views.route("/", methods=["POST", "GET"])
def home_page():
    if request.method == "POST":
        name = request.form.get("username", "").strip()
        collegename = request.form.get("teamname", "").strip()
        
        # Basic input validation
        if not name or not collegename:
            flash("Please fill in all fields!", "error")
            return redirect(url_for(home))
        
        if len(name) > 100 or len(collegename) > 100:
            flash("Input too long!", "error")
            return redirect(url_for(home))
            
        if User.query.filter_by(username=name).first():
            flash("Username already exits!", "error")
        else:
            flash("Successfully created!", "success")
            new_user = User(
                username=name,
                teamname=collegename,
                start_time=datetime.utcnow(),
                ispassword=0,
                issecurityquestion=0,
                isofa=0,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("auth.login_page"))
    return render_template("home_page.html")


@views.route("/dev-login/<user_id>/<password>")
@dev_access_required
def dev_login(user_id, password):
    user = User.query.filter_by(username=user_id).first()
    if not user:
        flash("User not found", "error")
        return redirect(url_for(home))
    login_user(user)
    return redirect(url_for("auth.login_page"))


@views.route("/dev-delete/<user_id>/<password>")
@dev_access_required
def dev_delete(user_id, password):
    user = User.query.filter_by(username=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted", "success")
    else:
        flash("User not found", "error")
    return redirect(url_for(home))


@views.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        # Get admin credentials from config (environment variables)
        admin_username = current_app.config.get('ADMIN_USERNAME', '')
        admin_password = current_app.config.get('ADMIN_PASSWORD', '')
        
        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True
            session.permanent = True  # Use permanent session for security
            return redirect(url_for("views.dev_dashboard"))
        else:
            flash("Invalid credentials!", "error")
    return render_template("admin_login.html")


@views.route("/admin-logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully", "success")
    return redirect(url_for(home))


@views.route("/dev-dashboard")
@admin_required
def dev_dashboard():
    lst = User.query.all()
    return render_template("dashboard.html", users=lst)
