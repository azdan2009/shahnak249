import os
from flask import Flask, jsonify, render_template
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User, AdminUser, Wallet


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "لازم تسجل دخول الأول عشان توصل للصفحة دي"
    login_manager.login_message_category = "error"

    @login_manager.user_loader
    def load_user(user_id):
        # user_id بالشكل "user-3" أو "admin-1"
        kind, _id = user_id.split("-")
        if kind == "admin":
            return AdminUser.query.get(int(_id))
        return User.query.get(int(_id))

    # تسجيل مسارات الدخول والتسجيل
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/api")
    def api_status():
        return jsonify({
            "project": "شحنك",
            "status": "الخادم شغال ✅",
            "tagline": "كل شحناتك في مكان واحد"
        })

    @app.route("/")
    @login_required
    def home():
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        balance = float(wallet.balance) if wallet else 0
        return render_template("home.html", wallet_balance=balance)

    @app.route("/health")
    def health():
        # يتأكد إن قاعدة البيانات متصلة فعلاً
        try:
            db.session.execute(db.text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {e}"
        return jsonify({"database": db_status})

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
