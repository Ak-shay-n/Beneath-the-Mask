from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user
from . import db
import pyotp
from stopwatch import *

auth = Blueprint("auth", __name__)

stopwatch = Stopwatch(2)


@auth.route("/login/", methods=["POST", "GET"])
@login_required
def login_page():
    if request.method == "POST":
        if (
            request.form.get("username").upper() in ["DEVANANDAN", "DEV ANANDAN"]
            and request.form.get("password").upper() == "~"
        ):
            flash(
                "Suspicious Activity! please answer security questions to continue",
                "doubt",
            )
            current_user.ispassword = True
            current_user.passwordtime = f"{str(stopwatch)}"
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
        creds = {"Catname": "30/12/2004", "Hometown": "DIYA", "Food": "ARIJIT SINGH"}
        Catname = request.form.get("Catnamxe")
        Hometown = request.form.get("Hometown")
        Food = request.form.get("Food")
        if (
            Catname.upper() == creds["Catname"]
            and Hometown.upper() == creds["Hometown"]
            and Food.upper() == creds["Food"]
        ):
            flash("you have answered the security question correctly", "success")
            current_user.issecurityquestion = True
            current_user.securitytime = f"{str(stopwatch)}"
            db.session.commit()
            return redirect(url_for("auth.twofactor"))
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
        if not otp.isdigit():
            flash("Enter numbers!", "error")
            return redirect(url_for("auth.twofactor"))
        otp = int(otp)
        if pyotp.TOTP("qZyNdBxMoVcKLWtRHpJmCsFAGUEbhYI").verify(otp):
            current_user.isofa = True
            db.session.commit()
            current_user.completed = f"{str(stopwatch)}"
            db.session.commit()
            return redirect(url_for("auth.last_page"))
        else:
            flash("You have supplied an invalid OTP!", "error")
            return redirect(url_for("auth.twofactor"))
    if current_user.issecurityquestion == 0:
        flash("Not authorized", "danger")
        return redirect(url_for("auth.security"))
    return render_template("login_2fa.html")
