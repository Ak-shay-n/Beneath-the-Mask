from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user
from . import db
from datetime import datetime

auth = Blueprint("auth", __name__)


def get_elapsed_time():
    """Calculate elapsed time since user started (in seconds)"""
    if current_user.start_time:
        elapsed = datetime.utcnow() - current_user.start_time
        return round(elapsed.total_seconds(), 2)
    return 0


@auth.route("/login/", methods=["POST", "GET"])
@login_required
def login_page():
    if request.method == "POST":
        if (
            request.form.get("username").upper() in ["SANJAY KALPANA", "SANJAYKALPANA"]
            and request.form.get("password") == "143kalpana"
        ):
            flash(
                "Suspicious Activity! please answer security questions to continue",
                "doubt",
            )
            current_user.ispassword = True
            current_user.passwordtime = f"{get_elapsed_time()}s"
            db.session.commit()
            return redirect(url_for("auth.security"))
        else:
            flash("Authentication failed!", "error")
            return redirect(url_for("auth.login_page"))
    return render_template("login.html")


@auth.route("/security/", methods=["POST", "GET"])
@login_required
def security():
    wrongans = []
    if request.method == "POST":
        creds = {"Catname": "30/12/2004", "Hometown": "DIYA", "Food": "SANJAY@111122"}
        Catname = request.form.get("Catname")
        Hometown = request.form.get("Hometown")
        Food = request.form.get("Food")
        if (
            Catname.upper() == creds["Catname"]
            and Hometown.upper() == creds["Hometown"]
            and Food.upper() == creds["Food"]
        ):
            current_user.issecurityquestion = True
            current_user.securitytime = f"{get_elapsed_time()}s"
            db.session.commit()
            # Show terminal animation before redirecting
            return render_template("login_security.html", show_terminal=True)
        else:
            if Catname.upper() != creds["Catname"]:
                wrongans.append("LunarDOB")
            if Hometown.upper() != creds["Hometown"]:
                wrongans.append("PetName")
            if Food.upper() != creds["Food"]:
                wrongans.append("Artist")

            flash(" ".join(wrongans) + " is wrong!", "error")
            return redirect(url_for("auth.security"))
    if current_user.ispassword == 0:
        flash("Not authorized", "danger")
        return redirect(url_for("auth.login_page"))
    return render_template("login_security.html")


@auth.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home_page"))


@auth.route("/last_page/")
@login_required
def last_page():
    if current_user.isofa == 0:
        flash("Not authorized", "danger")
        return redirect(url_for("auth.security"))
    return render_template("last_page.html")


@auth.route("/twofactor", methods=["POST", "GET"])
@login_required
def twofactor():
    if request.method == "POST":
        otp = request.form.get("otp")
        # Accept answer in format DD/MM/YYYY - correct answer is 03/02/2026
        correct_answer = "03/02/2026"
        if otp.strip() == correct_answer:
            current_user.isofa = True
            current_user.ofatime = f"{get_elapsed_time()}s"
            db.session.commit()
            # Redirect to loading screen before final riddle
            return redirect(url_for("auth.loading_screen"))
        else:
            flash("Wrong answer! Try again.", "error")
            return redirect(url_for("auth.twofactor"))
    return render_template("login_2fa.html")


@auth.route("/loading")
@login_required
def loading_screen():
    if current_user.isofa == 0:
        flash("Not authorized", "danger")
        return redirect(url_for("auth.twofactor"))
    return render_template("loading_screen.html")


@auth.route("/final-riddle", methods=["POST", "GET"])
@login_required
def final_riddle():
    if current_user.isofa == 0:
        flash("Not authorized", "danger")
        return redirect(url_for("auth.twofactor"))
    
    if request.method == "POST":
        answer = request.form.get("answer")
        # Answer: "Volodymyr Zelenskyy"
        correct_answer = "volodymyr zelenskyy"
        if answer.strip().lower() == correct_answer:
            current_user.completed = f"{get_elapsed_time()}s"
            db.session.commit()
            return redirect(url_for("auth.last_page"))
        else:
            flash("Wrong answer! Think harder...", "error")
            return redirect(url_for("auth.final_riddle"))
    
    return render_template("login_final_riddle.html")


@auth.route("/mission-complete")
@login_required
def mission_complete():
    # Only accessible if they completed the final riddle
    if not current_user.completed:
        flash("Not authorized", "danger")
        return redirect(url_for("auth.final_riddle"))
    return render_template("mission_complete.html")
