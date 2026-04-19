from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from .extensions import db
from .models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        u = request.form.get("username", "").strip()
        e = request.form.get("email", "").strip().lower()
        p = request.form.get("password", "")
        p2 = request.form.get("confirm_password", "")

        if not u or not e or not p:
            flash("Fill all required fields.", "error")
        elif p != p2:
            flash("Passwords are different.", "error")
        elif User.query.filter_by(username=u).first():
            flash("Username already exists.", "error")
        elif User.query.filter_by(email=e).first():
            flash("Email already exists.", "error")
        else:
            x = User(username=u, email=e)
            x.set_pass(p)
            db.session.add(x)
            db.session.commit()
            login_user(x)
            flash("Account created.", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")

        x = User.query.filter_by(username=u).first()
        if x is None or not x.check_pass(p):
            flash("Invalid credentials.", "error")
        else:
            login_user(x)
            flash("Welcome back.", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@bp.route("/logout")
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("main.index"))
