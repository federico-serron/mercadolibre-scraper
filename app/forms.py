from email.policy import default
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length


class ScrapForm(FlaskForm):
    term = StringField('Articulo a analizar', validators=[DataRequired(), Length(max=128)])
    country = SelectField('Ubicacion',validators=[DataRequired()],
                                                    choices=[('https://listado.mercadolibre.com.ar', 'Argentina'),
                                                   ('https://articulo.mercadolibre.cl', 'Chile'),
                                                   ('https://listado.mercadolibre.com.co', 'Colombia'),
                                                   ('https://listado.mercadolibre.com.py', 'Paraguay'),
                                                   ('https://listado.mercadolibre.com.pe', 'Peru'),
                                                   ('https://listado.mercadolibre.com.uy', 'Uruguay'),], 
                                                    default=('https://listado.mercadolibre.com.ar', 'Argentina'))
    submit = SubmitField('Scrapear')