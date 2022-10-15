from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class ScrapForm(FlaskForm):
    term = StringField('Articulo a analizar', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('Scrapear')
