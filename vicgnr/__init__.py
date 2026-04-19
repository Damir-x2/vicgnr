import os

from flask import Flask

from .extensions import db, login


def make_app(test_cfg=None):
    a = Flask(__name__, instance_relative_config=True)
    p = os.path.join(a.instance_path, "vicgnr.db")

    a.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", f"sqlite:///{p}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_cfg:
        a.config.update(test_cfg)

    os.makedirs(a.instance_path, exist_ok=True)

    db.init_app(a)
    login.init_app(a)

    from .models import User

    @login.user_loader
    def load_user(uid):
        return db.session.get(User, int(uid))

    from .auth import bp as auth_bp
    from .main import bp as main_bp

    a.register_blueprint(auth_bp)
    a.register_blueprint(main_bp)

    with a.app_context():
        db.create_all()

    return a
