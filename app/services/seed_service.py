# app/services/seed_service.py
from extensions import db
from app.models import PermissionTable, RoleTable, UserTable
from app.models.expert_system import Category, Symptom, Disease, Rule


def _get_or_create(model, defaults=None, **kwargs):
    instance = db.session.scalar(db.select(model).filter_by(**kwargs))
    if instance:
        return instance
    params = dict(defaults or {})
    params.update(kwargs)
    instance = model(**params)
    db.session.add(instance)
    return instance


def seed_permissions_and_roles():
    permissions = [
        ("USER_CREATE", "Create Users", "Users"),
        ("USER_EDIT", "Edit Users", "Users"),
        ("USER_DELETE", "Delete Users", "Users"),
        ("ROLE_MANAGE", "Manage Roles", "Roles"),
        ("PERMISSION_MANAGE", "Manage Permissions", "Permissions"),
        ("author_rules", "Author Expert Rules", "Expert System"),
        ("manage_symptoms", "Manage Symptoms", "Expert System"),
        ("manage_diseases", "Manage Diseases", "Expert System"),
        ("manage_rules", "Manage Rules", "Expert System"),
        ("manage_categories", "Manage Categories", "Expert System"),
        ("run_diagnosis", "Run Diagnosis", "Expert System"),
        ("view_cases", "View Case History", "Expert System"),
    ]

    perm_objs = []
    for code, name, module in permissions:
        perm = _get_or_create(
            PermissionTable,
            code=code,
            defaults={"name": name, "module": module},
        )
        perm.name = name
        perm.module = module
        perm_objs.append(perm)

    admin_role = _get_or_create(RoleTable, name="Admin", defaults={"description": "System administrator"})
    doctor_role = _get_or_create(RoleTable, name="Doctor", defaults={"description": "Knowledge author"})
    user_role = _get_or_create(RoleTable, name="User", defaults={"description": "Diagnosis user"})

    db.session.flush()

    admin_role.permissions = perm_objs
    doctor_role.permissions = [
        p for p in perm_objs
        if p.code in {
            "author_rules",
            "manage_symptoms",
            "manage_diseases",
            "manage_rules",
            "manage_categories",
            "view_cases",
        }
    ]
    user_role.permissions = [p for p in perm_objs if p.code == "run_diagnosis"]

    db.session.commit()


def seed_admin_user():
    admin = db.session.scalar(db.select(UserTable).filter_by(username="admin"))
    if admin:
        return
    admin_role = db.session.scalar(db.select(RoleTable).filter_by(name="Admin"))
    if not admin_role:
        return
    admin = UserTable(
        username="admin",
        email="admin@example.com",
        full_name="System Administrator",
        is_active=True,
    )
    admin.set_password("Admin@123")
    admin.roles = [admin_role]
    db.session.add(admin)
    db.session.commit()


def seed_expert_data():
    if db.session.scalar(db.select(Symptom).limit(1)):
        return

    cat_resp = _get_or_create(Category, name="Respiratory", defaults={"description": "Breathing-related illnesses"})
    cat_digest = _get_or_create(Category, name="Digestive", defaults={"description": "Gastrointestinal illnesses"})
    cat_neuro = _get_or_create(Category, name="Neurological", defaults={"description": "Nervous system illnesses"})
    cat_bact = _get_or_create(Category, name="Bacterial", defaults={"description": "Bacterial infections"})

    symptoms = {
        "coughing": Symptom(name="Coughing", description="Persistent cough or respiratory distress"),
        "sneezing": Symptom(name="Sneezing", description="Frequent sneezing"),
        "nasal_discharge": Symptom(name="Nasal discharge", description="Mucus from nostrils"),
        "drop_egg": Symptom(name="Drop in egg production", description="Reduced egg output"),
        "diarrhea": Symptom(name="Diarrhea", description="Loose or watery droppings"),
        "bloody_diarrhea": Symptom(name="Bloody diarrhea", description="Blood in droppings"),
        "lethargy": Symptom(name="Lethargy", description="Low energy or inactivity"),
        "ruffled": Symptom(name="Ruffled feathers", description="Unkempt feathers"),
        "swollen_face": Symptom(name="Swollen face", description="Facial swelling"),
        "lameness": Symptom(name="Lameness", description="Difficulty walking"),
    }
    db.session.add_all(symptoms.values())

    diseases = {
        "infectious_bronchitis": Disease(
            name="Infectious Bronchitis",
            description="Highly contagious respiratory disease affecting chickens.",
            treatment="Isolate affected birds, provide supportive care, consult a vet about vaccination strategy.",
            category=cat_resp,
        ),
        "newcastle": Disease(
            name="Newcastle Disease",
            description="Viral disease causing respiratory and neurological signs.",
            treatment="Isolate, notify vet, and follow vaccination protocols.",
            category=cat_neuro,
        ),
        "coccidiosis": Disease(
            name="Coccidiosis",
            description="Parasitic disease affecting the intestinal tract.",
            treatment="Administer anticoccidial medication and improve litter hygiene.",
            category=cat_digest,
        ),
        "fowl_cholera": Disease(
            name="Fowl Cholera",
            description="Bacterial infection causing sudden illness and death.",
            treatment="Treat with antibiotics under veterinary guidance and improve sanitation.",
            category=cat_bact,
        ),
        "marek": Disease(
            name="Marek's Disease",
            description="Viral disease causing paralysis and tumors.",
            treatment="No cure; vaccinate chicks and isolate affected birds.",
            category=cat_neuro,
        ),
    }
    db.session.add_all(diseases.values())
    db.session.flush()

    rules = [
        Rule(
            title="Respiratory infection pattern",
            description="Coughing + sneezing + nasal discharge",
            priority=1,
            confidence=85.0,
            disease=diseases["infectious_bronchitis"],
            symptoms=[
                symptoms["coughing"],
                symptoms["sneezing"],
                symptoms["nasal_discharge"],
            ],
        ),
        Rule(
            title="Neurological respiratory combo",
            description="Coughing + nasal discharge + lethargy",
            priority=2,
            confidence=80.0,
            disease=diseases["newcastle"],
            symptoms=[
                symptoms["coughing"],
                symptoms["nasal_discharge"],
                symptoms["lethargy"],
            ],
        ),
        Rule(
            title="Coccidiosis signature",
            description="Bloody diarrhea + lethargy",
            priority=1,
            confidence=90.0,
            disease=diseases["coccidiosis"],
            symptoms=[
                symptoms["bloody_diarrhea"],
                symptoms["lethargy"],
            ],
        ),
        Rule(
            title="Fowl cholera indicators",
            description="Swollen face + lethargy + ruffled feathers",
            priority=2,
            confidence=78.0,
            disease=diseases["fowl_cholera"],
            symptoms=[
                symptoms["swollen_face"],
                symptoms["lethargy"],
                symptoms["ruffled"],
            ],
        ),
        Rule(
            title="Marek's disease pattern",
            description="Lameness + lethargy",
            priority=3,
            confidence=75.0,
            disease=diseases["marek"],
            symptoms=[
                symptoms["lameness"],
                symptoms["lethargy"],
            ],
        ),
    ]
    db.session.add_all(rules)
    db.session.commit()


def seed_all():
    seed_permissions_and_roles()
    seed_admin_user()
    seed_expert_data()
