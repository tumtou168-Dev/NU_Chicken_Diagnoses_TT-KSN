# app/forms/expert_system_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
from app.forms.multi_checkbox_field import MultiCheckboxField
from app.models.expert_system import Category, Disease, Symptom, Rule
from extensions import db


def _category_choices():
    items = db.session.scalars(
        db.select(Category).order_by(Category.name)
    ).all()
    return [(0, "Uncategorized")] + [(c.id, c.name) for c in items]


def _disease_choices():
    items = db.session.scalars(
        db.select(Disease).order_by(Disease.name)
    ).all()
    return [(d.id, d.name) for d in items]


def _symptom_choices():
    items = db.session.scalars(
        db.select(Symptom).order_by(Symptom.name)
    ).all()
    return [(s.id, s.name) for s in items]


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField("Description")
    submit = SubmitField("Save")


class SymptomForm(FlaskForm):
    name = StringField("Symptom Name", validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField("Description")
    submit = SubmitField("Save")


class DiseaseForm(FlaskForm):
    name = StringField("Disease Name", validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=5, max=255)])
    treatment = TextAreaField("Recommended Treatment", validators=[DataRequired(), Length(min=5, max=255)])
    category_id = SelectField("Category", coerce=int)
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id.choices = _category_choices()


class RuleForm(FlaskForm):
    title = StringField("Rule Title", validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField("Rule Description", validators=[DataRequired(), Length(min=5, max=255)])
    priority = IntegerField("Priority", validators=[DataRequired(), NumberRange(min=1, max=100)])
    confidence = FloatField("Base Confidence (%)", validators=[DataRequired(), NumberRange(min=1, max=100)])
    disease_id = SelectField("Disease", coerce=int, validators=[DataRequired()])
    symptom_ids = MultiCheckboxField("Symptoms", coerce=int)
    submit = SubmitField("Save")

    def __init__(self, original_rule: Rule | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disease_id.choices = _disease_choices()
        self.symptom_ids.choices = _symptom_choices()
        if original_rule and not self.is_submitted():
            self.symptom_ids.data = [s.id for s in original_rule.symptoms]
