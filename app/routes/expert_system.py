# app/routes/expert_system.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from utils.decorators import require_permission
from app.forms.expert_system_forms import (
    CategoryForm,
    SymptomForm,
    DiseaseForm,
    RuleForm,
)
from app.services.diagnosis_service import DiagnosisService
from app.services.expert_system_service import (
    CategoryService,
    SymptomService,
    DiseaseService,
    RuleService,
    CaseService,
)
from app.services.audit_service import AuditService

expert_system_bp = Blueprint("expert_system", __name__, url_prefix="/expert-system")


@expert_system_bp.route("/author-rules")
@login_required
@require_permission("author_rules")
def author_rules():
    return redirect(url_for("expert_system.rules_index"))


@expert_system_bp.route("/diagnose", methods=["GET", "POST"])
@login_required
@require_permission("run_diagnosis")
def diagnose():
    symptoms = DiagnosisService.get_all_symptoms()
    diagnosis_results = None
    selected_ids = []

    if request.method == "POST":
        selected_ids = [int(id) for id in request.form.getlist("symptoms")]
        if selected_ids:
            diagnosis_results = DiagnosisService.run_inference(selected_ids)
            if diagnosis_results:
                case = DiagnosisService.record_case(
                    current_user.id,
                    selected_ids,
                    diagnosis_results[0],
                )
                AuditService.log("DIAGNOSE", "Case", case.id, f"User ran diagnosis, result: {case.disease.name}")
        else:
            flash("Please select at least one symptom.", "warning")

    return render_template(
        "expert_system/diagnose.html",
        symptoms=symptoms,
        results=diagnosis_results,
        selected_ids=set(selected_ids),
    )


@expert_system_bp.route("/cases")
@login_required
@require_permission("view_cases")
def cases_index():
    # If user is Admin or Doctor, show all cases
    if current_user.has_role("Admin") or current_user.has_role("Doctor"):
        cases = CaseService.get_all()
    else:
        # Otherwise, show only their own cases
        cases = CaseService.get_by_user(current_user.id)
        
    return render_template("expert_system/cases/index.html", cases=cases)


@expert_system_bp.route("/cases/<int:case_id>")
@login_required
@require_permission("view_cases")
def cases_detail(case_id: int):
    case = CaseService.get_by_id(case_id)
    if case is None:
        abort(404)
        
    # Security check: User can only view their own case unless they are Admin/Doctor
    if not (current_user.has_role("Admin") or current_user.has_role("Doctor")):
        if case.user_id != current_user.id:
            abort(403)
            
    return render_template("expert_system/cases/detail.html", case=case)


@expert_system_bp.route("/categories")
@login_required
@require_permission("manage_categories")
def categories_index():
    categories = CategoryService.get_all()
    return render_template("expert_system/categories/index.html", categories=categories)


@expert_system_bp.route("/categories/create", methods=["GET", "POST"])
@login_required
@require_permission("manage_categories")
def categories_create():
    form = CategoryForm()
    if form.validate_on_submit():
        category = CategoryService.create(
            {"name": form.name.data, "description": form.description.data}
        )
        AuditService.log("CREATE", "Category", category.id, f"Created category: {category.name}")
        flash(f"Category '{category.name}' created successfully.", "success")
        return redirect(url_for("expert_system.categories_index"))
    return render_template("expert_system/categories/create.html", form=form)


@expert_system_bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("manage_categories")
def categories_edit(category_id: int):
    category = CategoryService.get_by_id(category_id)
    if category is None:
        abort(404)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        CategoryService.update(
            category,
            {"name": form.name.data, "description": form.description.data},
        )
        AuditService.log("UPDATE", "Category", category.id, f"Updated category: {category.name}")
        flash("Category updated successfully.", "success")
        return redirect(url_for("expert_system.categories_index"))
    return render_template(
        "expert_system/categories/edit.html",
        form=form,
        category=category,
    )


@expert_system_bp.route("/categories/<int:category_id>/delete", methods=["GET", "POST"])
@login_required
@require_permission("manage_categories")
def categories_delete(category_id: int):
    category = CategoryService.get_by_id(category_id)
    if category is None:
        abort(404)
    if request.method == "POST":
        category_name = category.name
        CategoryService.delete(category)
        AuditService.log("DELETE", "Category", category_id, f"Deleted category: {category_name}")
        flash("Category deleted successfully.", "success")
        return redirect(url_for("expert_system.categories_index"))
    return render_template(
        "expert_system/categories/delete_confirm.html",
        category=category,
    )


@expert_system_bp.route("/symptoms")
@login_required
@require_permission("manage_symptoms")
def symptoms_index():
    symptoms = SymptomService.get_all()
    return render_template("expert_system/symptoms/index.html", symptoms=symptoms)


@expert_system_bp.route("/symptoms/create", methods=["GET", "POST"])
@login_required
@require_permission("manage_symptoms")
def symptoms_create():
    form = SymptomForm()
    if form.validate_on_submit():
        symptom = SymptomService.create(
            {"name": form.name.data, "description": form.description.data}
        )
        AuditService.log("CREATE", "Symptom", symptom.id, f"Created symptom: {symptom.name}")
        flash(f"Symptom '{symptom.name}' created successfully.", "success")
        return redirect(url_for("expert_system.symptoms_index"))
    return render_template("expert_system/symptoms/create.html", form=form)


@expert_system_bp.route("/symptoms/<int:symptom_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("manage_symptoms")
def symptoms_edit(symptom_id: int):
    symptom = SymptomService.get_by_id(symptom_id)
    if symptom is None:
        abort(404)
    form = SymptomForm(obj=symptom)
    if form.validate_on_submit():
        SymptomService.update(
            symptom,
            {"name": form.name.data, "description": form.description.data},
        )
        AuditService.log("UPDATE", "Symptom", symptom.id, f"Updated symptom: {symptom.name}")
        flash("Symptom updated successfully.", "success")
        return redirect(url_for("expert_system.symptoms_index"))
    return render_template(
        "expert_system/symptoms/edit.html",
        form=form,
        symptom=symptom,
    )


@expert_system_bp.route("/symptoms/<int:symptom_id>/delete", methods=["GET", "POST"])
@login_required
@require_permission("manage_symptoms")
def symptoms_delete(symptom_id: int):
    symptom = SymptomService.get_by_id(symptom_id)
    if symptom is None:
        abort(404)
    if request.method == "POST":
        symptom_name = symptom.name
        SymptomService.delete(symptom)
        AuditService.log("DELETE", "Symptom", symptom_id, f"Deleted symptom: {symptom_name}")
        flash("Symptom deleted successfully.", "success")
        return redirect(url_for("expert_system.symptoms_index"))
    return render_template(
        "expert_system/symptoms/delete_confirm.html",
        symptom=symptom,
    )


@expert_system_bp.route("/diseases")
@login_required
@require_permission("manage_diseases")
def diseases_index():
    diseases = DiseaseService.get_all()
    return render_template("expert_system/diseases/index.html", diseases=diseases)


@expert_system_bp.route("/diseases/create", methods=["GET", "POST"])
@login_required
@require_permission("manage_diseases")
def diseases_create():
    form = DiseaseForm()
    if form.validate_on_submit():
        disease = DiseaseService.create(
            {
                "name": form.name.data,
                "description": form.description.data,
                "treatment": form.treatment.data,
                "category_id": form.category_id.data,
            }
        )
        AuditService.log("CREATE", "Disease", disease.id, f"Created disease: {disease.name}")
        flash(f"Disease '{disease.name}' created successfully.", "success")
        return redirect(url_for("expert_system.diseases_index"))
    return render_template("expert_system/diseases/create.html", form=form)


@expert_system_bp.route("/diseases/<int:disease_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("manage_diseases")
def diseases_edit(disease_id: int):
    disease = DiseaseService.get_by_id(disease_id)
    if disease is None:
        abort(404)
    form = DiseaseForm(obj=disease)
    if form.validate_on_submit():
        DiseaseService.update(
            disease,
            {
                "name": form.name.data,
                "description": form.description.data,
                "treatment": form.treatment.data,
                "category_id": form.category_id.data,
            },
        )
        AuditService.log("UPDATE", "Disease", disease.id, f"Updated disease: {disease.name}")
        flash("Disease updated successfully.", "success")
        return redirect(url_for("expert_system.diseases_index"))
    return render_template(
        "expert_system/diseases/edit.html",
        form=form,
        disease=disease,
    )


@expert_system_bp.route("/diseases/<int:disease_id>/delete", methods=["GET", "POST"])
@login_required
@require_permission("manage_diseases")
def diseases_delete(disease_id: int):
    disease = DiseaseService.get_by_id(disease_id)
    if disease is None:
        abort(404)
    if request.method == "POST":
        disease_name = disease.name
        DiseaseService.delete(disease)
        AuditService.log("DELETE", "Disease", disease_id, f"Deleted disease: {disease_name}")
        flash("Disease deleted successfully.", "success")
        return redirect(url_for("expert_system.diseases_index"))
    return render_template(
        "expert_system/diseases/delete_confirm.html",
        disease=disease,
    )


@expert_system_bp.route("/rules")
@login_required
@require_permission("manage_rules")
def rules_index():
    rules = RuleService.get_all()
    return render_template("expert_system/rules/index.html", rules=rules)


@expert_system_bp.route("/rules/create", methods=["GET", "POST"])
@login_required
@require_permission("manage_rules")
def rules_create():
    form = RuleForm()
    if form.validate_on_submit():
        rule = RuleService.create(
            {
                "title": form.title.data,
                "description": form.description.data,
                "priority": form.priority.data,
                "confidence": form.confidence.data,
                "disease_id": form.disease_id.data,
            },
            symptom_ids=form.symptom_ids.data or [],
        )
        AuditService.log("CREATE", "Rule", rule.id, f"Created rule: {rule.title}")
        flash(f"Rule '{rule.title}' created successfully.", "success")
        return redirect(url_for("expert_system.rules_index"))
    return render_template("expert_system/rules/create.html", form=form)


@expert_system_bp.route("/rules/<int:rule_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("manage_rules")
def rules_edit(rule_id: int):
    rule = RuleService.get_by_id(rule_id)
    if rule is None:
        abort(404)
    form = RuleForm(original_rule=rule, obj=rule)
    if form.validate_on_submit():
        RuleService.update(
            rule,
            {
                "title": form.title.data,
                "description": form.description.data,
                "priority": form.priority.data,
                "confidence": form.confidence.data,
                "disease_id": form.disease_id.data,
            },
            symptom_ids=form.symptom_ids.data or [],
        )
        AuditService.log("UPDATE", "Rule", rule.id, f"Updated rule: {rule.title}")
        flash("Rule updated successfully.", "success")
        return redirect(url_for("expert_system.rules_index"))
    return render_template(
        "expert_system/rules/edit.html",
        form=form,
        rule=rule,
    )


@expert_system_bp.route("/rules/<int:rule_id>/delete", methods=["GET", "POST"])
@login_required
@require_permission("manage_rules")
def rules_delete(rule_id: int):
    rule = RuleService.get_by_id(rule_id)
    if rule is None:
        abort(404)
    if request.method == "POST":
        rule_title = rule.title
        RuleService.delete(rule)
        AuditService.log("DELETE", "Rule", rule_id, f"Deleted rule: {rule_title}")
        flash("Rule deleted successfully.", "success")
        return redirect(url_for("expert_system.rules_index"))
    return render_template(
        "expert_system/rules/delete_confirm.html",
        rule=rule,
    )
