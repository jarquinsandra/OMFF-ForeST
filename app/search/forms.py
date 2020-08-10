"""

AUTOR: jarquinsandra


"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length
class SpecieSearchForm(FlaskForm):
    species = StringField('GenusSpecie', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('species search')
class WDSearchForm(FlaskForm):
    wd = StringField('wd', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('WD search')
class ConsensusSearchForm(FlaskForm):
    genus = StringField('genus')
    species = StringField('species', validators=[DataRequired()])
    submit = SubmitField('search')
class DownloadForm(FlaskForm):
    submit = SubmitField('Download csv')
class DownloadForm2(FlaskForm):
    submit = SubmitField('Download csv')
class DownloadFile(FlaskForm):
    submit = SubmitField('Download spectrum')



