from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user
from . import db
from .modals import User
from datetime import datetime

views = Blueprint("views", __name__)
key = "$lapassion$"
home = "views.home_page"

# Admin credentials
ADMIN_USERNAME = "akshay_17"
ADMIN_PASSWORD = "legendaryak26"


@views.route("/", methods=["POST", "GET"])
def home_page():
    if request.method == "POST":
        name = request.form.get("username")
        collegename = request.form.get("teamname")
        if User.query.filter_by(username=name).first():
            flash("Username already exits!", "error")
        else:
            flash("Successfully created!", "success")
            new_user = User(
                username=name,
                teamname=collegename,
                start_time=datetime.utcnow(),  # Record start time
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
def dev_login(user_id, password):
    if password != key:
        return redirect(url_for(home))
    user = User.query.filter_by(username=user_id).first()
    login_user(user)
    return redirect(url_for("auth.login_page"))


@views.route("/dev-delete/<user_id>/<password>")
def dev_delete(user_id, password):
    if password != key:
        return redirect(url_for(home))
    User.query.filter_by(username=user_id).delete()
    db.session.commit()
    return redirect(url_for(home))


@views.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for("views.dev_dashboard"))
        else:
            flash("Invalid credentials!", "error")
    return render_template("admin_login.html")


@views.route("/admin-logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for(home))


@views.route("/dev-dashboard")
def dev_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for("views.admin_login"))
    lst = User.query.all()
    return render_template("dashboard.html", users=lst)
