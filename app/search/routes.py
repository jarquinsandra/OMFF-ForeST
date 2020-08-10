"""

AUTOR: jarquinsandra


"""
import pandas as pd
from flask import render_template, url_for, redirect, make_response, request, abort, flash
from . import search
from .forms import ConsensusSearchForm
from .forms import SpecieSearchForm
from .forms import WDSearchForm
from .forms import DownloadForm
from .forms import DownloadForm2
from .forms import DownloadFile
from app.models import Files
from app.models import ReferenceSpectra
from app import db
from sqlalchemy import create_engine
from bokeh.plotting import figure
from bokeh.embed import components
from app import url
engine = create_engine(url)


@search.route('/consensus_search', methods= ['GET','POST'])
def consensus_form():
    form = ConsensusSearchForm()
    if form.validate_on_submit():
        species = form.species.data
        species_validate = ReferenceSpectra.query.filter_by(species=species).all()
        if species_validate:
            return redirect(url_for('search.show_dashboard',species=species)) 
        else:
            flash('Your specie is not in the DB please try with another specie')
        
    return render_template('consensus_search.html', form=form)

@search.route('/consensus_search/<species>', methods=['GET','POST'])
def show_dashboard(species):
    species=species
    form = DownloadFile() 
    plots = []
    plots.append(make_plot(species))
    all_ref_spectra=pd.read_sql_table('reference_spectra', con= db.engine)
    species_search = all_ref_spectra.species.str.contains(species)
    species_display=all_ref_spectra[species_search]
    species_display = species_display[['mz','int_rel']]
    if request.method == 'POST':
        resp = make_response(species_display.to_csv(sep="\t", index=False))
        resp.headers["Content-Disposition"] = 'attachment; filename= "consensus_spectra.txt"'
        resp.headers["Content-Type"] = "text/csv"
        return resp
    return render_template('dashboard_search.html', plots=plots, form=form, species=species)

def make_plot(species):
    all_ref_spectra=pd.read_sql_table('reference_spectra', con= db.engine)
    species_search = all_ref_spectra.species.str.contains(species)
    species_display=all_ref_spectra[species_search]
    x=species_display['mz']
    y=species_display['int_rel']
    TOOLTIPS = [("mass", "$x"), ("intensity", "$y")]
    plot = figure(plot_height=300, sizing_mode='scale_width', x_axis_label= 'm/z',
    y_axis_label= 'int %[BP]', tooltips = TOOLTIPS)
    plot.segment(x, y, x, 0 , color="red", line_width=1)
    plot.segment(0,0,1000,0,color='black',line_width=1)
    #plot.circle(x2,y2, color = 'red', line_width=0.5)
    script, div = components(plot)
    return script, div


@search.route('/specie_search', methods=['GET','POST'])
def specie_search():
    form = SpecieSearchForm()
    if form.validate_on_submit():
        species = form.species.data
        species_validate = Files.query.filter(Files.species.ilike(species+'%'))
        if species_validate:
            return redirect(url_for('search.specie_results',species=species)) 
        else:
            flash('Your specie is not in the DB please try with another specie')
        
    return render_template('specie_search.html', form=form)


@search.route('/specie_search/<species>', methods=['GET','POST'])
def specie_results(species):
    species_q =species.lower()
    files=pd.read_sql_table('files', con= db.engine)
    species_unique = files.drop_duplicates(['species','wd'])	
    species_unique = species_unique[['filename','species','wd','origin', 'time_created']]
    species_unique['species']=species_unique['species'].str.lower()
    species_search = species_unique.species.str.contains(species_q)
    species_display=species_unique[species_search]
    return render_template('specie_results.html',  tables=[species_display.to_html(classes= "table-hover")], titles=species_unique.columns.values, species=species)
    
@search.route('/wd_search', methods=['GET','POST'])
def wd_search():
    form= WDSearchForm()
    if form.validate_on_submit():
        wd = form.wd.data
        wd_validate = Files.query.filter_by(wd=wd).all()
        if wd_validate:
            return redirect(url_for('search.wd_results',wd=wd)) 
        else:
            flash('Your WD number is not in the DB please try with another WD number')
    return render_template('wd_search.html', form=form)


@search.route('/wd_search/<wd>', methods=['GET','POST'])
def wd_results(wd):
    wd = wd.lower()
    files=pd.read_sql_table('files', con= db.engine)
    wd_unique = files.drop_duplicates(['species','wd'])	
    wd_unique = wd_unique[['filename','species','wd','origin', 'time_created']]
    wd_unique['wd']=wd_unique['wd'].str.lower()
    wd_search = wd_unique.wd.str.contains(wd)
    wd_display=wd_unique[wd_search]
    return render_template('wd_results.html',  tables=[wd_display.to_html(classes="table-hover")], titles=wd_unique.columns.values, wd=wd.upper())

@search.route('/wd_all', methods=['GET','POST'])
def wd_all():
    form = DownloadForm()
    files=pd.read_sql_table('files', con= db.engine)
    wd_unique = files.drop_duplicates(['species','wd'])	
    wd_unique = wd_unique[['species','wd']]
    if request.method == 'POST':
        resp = make_response(wd_unique.to_csv(index=False))
        resp.headers["Content-Disposition"] = 'attachment; filename= "wd_ForeST.csv"'
        resp.headers["Content-Type"] = "text/csv"
        return resp
    return render_template('wd_all.html',  tables=[wd_unique.to_html(classes="table-hover")], titles=wd_unique.columns.values, form=form)

@search.route('/species_all', methods=['GET','POST'])
def species_all():
    form=DownloadForm2()
    files=pd.read_sql_table('files', con= db.engine)
    wd_unique = files.drop_duplicates(['species','wd'])	
    wd_unique = wd_unique[['species','wd']]
    spectra = wd_unique.groupby('species').count()
    spectra = spectra.rename(columns = {'wd':'spectra_number'})
    spectra.reset_index(level=0, inplace=True)
    if request.method == 'POST':
        resp = make_response(spectra.to_csv(index=False))
        resp.headers["Content-Disposition"] = 'attachment; filename= "spectra_ForeST.csv"'
        resp.headers["Content-Type"] = "text/csv"
        return resp

    return render_template('species_all.html',  tables=[spectra.to_html(classes="table-hover")], titles=spectra.columns.values, form=form)

@search.route('/all_db/<int:page>', methods=['GET'])
def all_db(page=1):
    per_page = 40
    posts = Files.query.order_by(Files.wd.desc()).paginate(page,per_page,error_out=False)
    #all_in_db = Files.all_paginated(page, per_page)
    return render_template('all_db.html',
                           posts=posts) 

