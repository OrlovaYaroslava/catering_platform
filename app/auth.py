from flask import Blueprint, render_template, redirect, url_for
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Role
from app.forms import RegisterForm

auth = Blueprint("auth", __name__)

@auth.route("/login")
def login():
    return "Login page (temporary)"

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        client_role = Role.query.filter_by(name="client").first()

        user = User(
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=client_role
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)
