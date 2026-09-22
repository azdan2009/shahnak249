import os
from flask import Flask, jsonify
from flask_login import LoginManager
from config import Config
from models import db, User, AdminUser


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # user_id بالشكل "user-3" أو "admin-1"
        kind, _id = user_id.split("-")
        if kind == "admin":
            return AdminUser.query.get(int(_id))
        return User.query.get(int(_id))

    @app.route("/")
    def home():
        return jsonify({
            "project": "شحنك",
            "status": "الخادم شغال ✅",
            "tagline": "كل شحناتك في مكان واحد"
        })

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
