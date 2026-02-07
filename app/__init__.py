# app/__init__.py
import os
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, csrf, login_manager
from app.models.user import UserTable


def create_app(config_class: type[Config] = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    #init extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    # Flask-Login settings
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    
    @login_manager.user_loader
    def load_user(user_id: str):
        return UserTable.query.get(int(user_id))
    
    # register blueprints
    from app.routes.user_routes import user_bp
    from app.routes.role_routes import role_bp
    from app.routes.permission_routes import permission_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.expert_system import expert_system_bp
    from app.routes.audit_routes import audit_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(expert_system_bp)
    app.register_blueprint(audit_bp)
    
    @app.route("/")
    def home():
        return redirect(url_for("auth.login"))
    
    # create tables
    with app.app_context():
        from app.models.user import UserTable
        from app.models.role import RoleTable
        from app.models.permission import PermissionTable
        from app.models.expert_system import Category, Symptom, Disease, Rule, Case
        from app.models.audit_log import AuditLog

        # Default RESET_DB to 0 to prevent database reset on restart
        if os.environ.get("RESET_DB", "0") == "1":
            db.drop_all()

        db.create_all()
        
        # Only seed if the database is empty (e.g. check if any users exist)
        if not UserTable.query.first():
            from app.services.seed_service import seed_all
            seed_all()
        
    return app
