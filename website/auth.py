from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
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
        username = request.form.get("username", "").strip().upper()
        password = request.form.get("password", "")
        
        # Get credentials from config (environment variables)
        valid_username = current_app.config.get('GAME_USERNAME', '')
        valid_password = current_app.config.get('GAME_PASSWORD', '')
        
        # Check both variations of username (with/without space)
        valid_usernames = [valid_username, valid_username.replace(" ", "")]
        
        if username in valid_usernames and password == valid_password:
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
        # Get security answers from config (environment variables)
        creds = {
            "Catname": current_app.config.get('SECURITY_ANSWER_1', ''),
            "Hometown": current_app.config.get('SECURITY_ANSWER_2', ''),
            "Food": current_app.config.get('SECURITY_ANSWER_3', '')
        }
        Catname = request.form.get("Catname", "").strip()
        Hometown = request.form.get("Hometown", "").strip()
        Food = request.form.get("Food", "").strip()
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
        otp = request.form.get("otp", "").strip()
        # Get 2FA answer from config (environment variables)
        correct_answer = current_app.config.get('TWO_FA_ANSWER', '')
        if otp == correct_answer:
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
        answer = request.form.get("answer", "").strip()
        # Get final riddle answer from config (environment variables)
        correct_answer = current_app.config.get('FINAL_RIDDLE_ANSWER', '')
        if answer.lower() == correct_answer:
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
