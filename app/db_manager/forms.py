"""

AUTOR: jarquinsandra


"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, MultipleFileField, FileField,FloatField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length

class UploadForm(FlaskForm):
    file = MultipleFileField('Input Files')
    submit_file = SubmitField('upload to db')

class CheckForm(FlaskForm):
    file = MultipleFileField('Input Files')
    submit_file = SubmitField('upload to db')
    
class NormalizationForm(FlaskForm):
    file = MultipleFileField('Input Files')
    submit_file = SubmitField('Normalize')

class UpdateConsensusForm(FlaskForm):
    submit_signal = SubmitField('Calculate consensus')
    comments = StringField('Anotations', widget=TextArea())

class CalculateConsensusForm(FlaskForm):
    file = MultipleFileField('txt files')
    submit_file = SubmitField('calculate consensus')
    step = FloatField('bin', default=0.003)
    window = FloatField('window', default= 0.01)
    noise_level = FloatField('noise level', default = 1.0)
    peak_presence = FloatField('peak presence', default = 0.5)

class WDDeleteForm(FlaskForm):
    wd = StringField('wd', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('DELETE')

class DownloadFile(FlaskForm):
    submit = SubmitField('Download spectrum')


class FileFilterForm(FlaskForm):
    file = MultipleFileField('Input Files')
    submit_file = SubmitField('check files')