import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from models import db, User, Wallet

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SimpleForm(FlaskForm):
    """فورم فاضي بس بيوفر حماية CSRF تلقائيًا"""
    pass


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = SimpleForm()

    if form.validate_on_submit():
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # التحقق من صحة البيانات
        if not name or not email or not password:
            flash("من فضلك املأ كل الحقول", "error")
            return render_template("register.html", form=form)

        if not EMAIL_RE.match(email):
            flash("البريد الإلكتروني غير صحيح", "error")
            return render_template("register.html", form=form)

        if len(password) < 6:
            flash("كلمة المرور لازم تكون 6 حروف على الأقل", "error")
            return render_template("register.html", form=form)

        if User.query.filter_by(email=email).first():
            flash("البريد الإلكتروني ده مسجل بالفعل", "error")
            return render_template("register.html", form=form)

        # إنشاء المستخدم
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # عشان ناخد user.id قبل الـ commit

        # إنشاء محفظة فاضية له
        wallet = Wallet(user_id=user.id, balance=0)
        db.session.add(wallet)

        db.session.commit()

        login_user(user)
        flash("تم إنشاء حسابك بنجاح 🎉", "success")
        return redirect(url_for("home"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = SimpleForm()

    if form.validate_on_submit():
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.password_hash and user.check_password(password):
            login_user(user)
            return redirect(url_for("home"))

        flash("البريد الإلكتروني أو كلمة المرور غير صحيحة", "error")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("تم تسجيل الخروج", "success")
    return redirect(url_for("auth.login"))
