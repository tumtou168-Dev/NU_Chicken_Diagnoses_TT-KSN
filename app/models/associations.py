# app/models/associations.py
from extensions import db

# user <-> role (many-to-many)
tbl_user_roles = db.Table(
    "tbl_user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("tbl_users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("tbl_roles.id"), primary_key=True),
)

# role <-> permission (many-to-many)
tbl_role_permissions = db.Table(
    "tbl_role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("tbl_roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("tbl_permissions.id"), primary_key=True),
)

# cases <-> symptoms (many-to-many)
tbl_cases_symptoms = db.Table(
    "tbl_cases_symptoms",
    db.Column("case_id", db.Integer, db.ForeignKey("tbl_cases.id"), primary_key=True),
    db.Column("symptom_id", db.Integer, db.ForeignKey("tbl_symptoms.id"), primary_key=True),
)

# rules <-> symptoms (many-to-many)
tbl_rules_symptoms = db.Table(
    "tbl_rules_symptoms",
    db.Column("rule_id", db.Integer, db.ForeignKey("tbl_rules.id"), primary_key=True),
    db.Column("symptom_id", db.Integer, db.ForeignKey("tbl_symptoms.id"), primary_key=True),
)
