"""

AUTOR: jarquinsandra


"""
from . import db_manager
from .forms import UploadForm
from io import BytesIO, StringIO
import os
import io
import urllib.request
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from flask import url_for, redirect, render_template, request, url_for, make_response, flash, Response, send_file, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from werkzeug import secure_filename
from .forms import UpdateConsensusForm
from .forms import NormalizationForm
from .forms import CalculateConsensusForm
from .forms import WDDeleteForm
from .forms import DownloadFile
from .forms import CheckForm
from .forms import FileFilterForm
from app.models import Files
from app.models import TempSpectra
from app.models import TempSpectra2
from app.models import ReferenceSpectra
from flask import render_template
from bokeh.plotting import figure
from bokeh.embed import components
import sqlalchemy
import zipfile
from zipfile import ZipFile
from app import db
from app import url
engine = create_engine(url)

#General function for binning
def slidefunc (data,window,step):
    "This function do a binning sliding window using window and step parameters, data must contain the first two colums as mz and relative intensity. The first column name has to be mz and data must be previously ordered by mz"
    minmz = data['mz'].min()
    maxmz = data['mz'].max()
    bins = []
    minbin = minmz+window
    maxbin = maxmz-window
    bins= np.arange(minbin,maxbin,step)
        
        #minus 1 correction for python index
    m = len(bins)-2
    i = 0
    j = 0
    first = 0
    n = 0
    accum = 0
    mzbins = pd.DataFrame(bins, columns= ['bins'])
    mzbins['int_rel'] = np.nan
    mzbins['samples'] = np.nan
    data = data.sort_values(by=['mz'])
    while (j<=m):
        lower = bins[j]- window
        upper = bins[j]+ window
        while data.iat[i,0]<= lower:
            i = i + 1
        first = i
        while data.iat[i,0]< upper:            
            accum = accum + data.iat[i,1]
            n = n + 1
            i = i + 1
        if (n):
            mzbins.iat[j,1] = accum/n
            mzbins.iat[j,2] = n
            #a = accum/n
            #b = n
            accum = 0 
            n = 0
        j = j + 1
        i = first
            # Jump empty regions
       # empty =   mzbins.iat[j,0]+window
       # while j<m and data.iat[i,0] > empty :
        #    j = j + 1
    mzbins = mzbins.fillna(0)   
    return mzbins
     
#Function for calculation of mean intensity and mass
def peak_search(dataframe, noise_level): 
    peaks = pd.DataFrame(columns=['mz','int_rel'])
    peak_search_active = 0
    top = len(dataframe)
    for s in range (1, top):
        mzbin_int = dataframe.iloc[s]['int_rel']
        if mzbin_int>0 and peak_search_active==0 :
            peak_start=s
            peak_search_active=1
        if mzbin_int==0 and peak_search_active ==1:
            peak_stop =s-1
            peak_mz = dataframe[['bins']].iloc[[peak_start,peak_stop]].mean()
            peak_int = dataframe[['int_rel']].iloc[[peak_start,peak_stop]].mean()
            peak_means = pd.DataFrame([[peak_mz.iloc[0],peak_int.iloc[0]]], columns=['mz','int_rel'])
            if peak_int.iloc[0] > noise_level:
                peaks = peaks.append(peak_means, ignore_index=True)
            peak_search_active = 0
    return peaks



@db_manager.route('/add_spectra', methods = ['GET','POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f =form.file.data
        mylist = []
        content = pd.DataFrame()
        for file in f:
            filename = secure_filename(file.filename)
            content_loop = pd.read_csv(file, sep="\t", header=None, skip_blank_lines=True, skiprows=4)
            mylist.append(filename)
            content_loop = content_loop.iloc [:,0:2]
            content_loop=content_loop.rename(columns = {0:'mz',1:'intensity'})
            content_loop['filename'] = filename
            content_loop =content_loop.dropna(axis=1, how='all')
            content = content.append(content_loop, ignore_index=True)
            content['species'] = content['filename'].str.split('_').str[0]
            content['wd'] = content['filename'].str.split('_').str[1]
            content['origin'] = content['filename'].str.split('_').str[2]
            content = content.dropna()
            content['origin'] = content.origin.replace({'.txt':''}, regex=True)
            
        content.to_sql('files', con = db.engine, if_exists='append', index=False)
        flash('Your files were succesfully loaded')
        return render_template('add_spectra.html', form=form)
        
    
    return render_template('add_spectra.html', form=form)
#Remove header   
@db_manager.route('/remove_header', methods = ['GET','POST'])
def remove_header():
    form = CheckForm()
    if form.validate_on_submit():
        f =form.file.data
        mylist = []
        content = pd.DataFrame()
        bad_words =['WD','wd','LRP','RT','Mass','Intensity','Scan','File','Mass','Absolute'] 
        for file in f:
            filename = secure_filename(file.filename)
            content_loop = pd.read_csv(file, sep="\t", header=None, skip_blank_lines=True, skiprows=4)
            mylist.append(filename)

    return render_template('remove_header.html', form=form)

#Define normalization of files when needed
@db_manager.route('/normalization', methods=['GET','POST'])
def normalize():
    form = NormalizationForm()
    if form.validate_on_submit():
        f =form.file.data
        
        content = pd.DataFrame()
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as csv_zip:
            for file in f:
                filename = secure_filename(file.filename)
                content_loop = pd.read_csv(file, sep="\t", header=None, skip_blank_lines=True, skiprows=3)
                content_loop = content_loop.iloc [:,0:2]
                content_loop=content_loop.rename(columns = {0:'mz',1:'intensity'})
                content_loop =content_loop.dropna(axis=1, how='all')
                max_100 = content_loop['intensity'].max()
                content_loop['intensity2'] = (content_loop['intensity']*100)/max_100
                del content_loop['intensity']
                content_loop=content_loop.rename(columns= {'intensity2':'intensity'})
                data = zipfile.ZipInfo(filename)
                data.compress_type = zipfile.ZIP_DEFLATED
                csv_zip.writestr(data, content_loop.to_csv(sep="\t", index=False))
        memory_file.seek(0)    
        
        return send_file(memory_file, attachment_filename='normalized.zip', as_attachment=True)
         
           #download file """
            #resp = make_response(content.to_csv(sep="\t", index=False))
            #resp.headers["Content-Disposition"] = 'attachment; filename= "{}"'.format(filename)
            #resp.headers["Content-Type"] = "text/csv"
            #return resp
     
            

        
    return render_template('normalization.html', form=form)
        
    
#Define calculation of average spectra
@db_manager.route('/consensus_update', methods = ['GET','POST'])
def consensus_update():
    form = UpdateConsensusForm()
    sliding_window_width =0.01
    sliding_window_step = 0.003
    mz_tolerance = 0.02
    noise_level = 1
    peak_presence = 0.5
    if request.method == 'POST':
        files=pd.read_sql_table('files', con= db.engine)
        raw = files[['mz','intensity','species','wd']]
        wd = raw.drop_duplicates(['species','wd'])	
        wd = wd[['species','wd']]
        spectra = wd.groupby('species').count()
        spectra = spectra.rename(columns = {'wd':'spectra_number'})
        spectra.reset_index(level=0, inplace=True) 
        species = spectra['species']
        multi_raw= raw.set_index(['species','wd'])

        #applies the binning function to all the species peaks
        slidexy = raw.groupby('species').apply(lambda x: slidefunc(x,sliding_window_width, sliding_window_step))
        #drop numerical index generated by the function
        slidexy.index = slidexy.index.droplevel(1)
        #calculate number of samples per species
        count2=multi_raw.reset_index().groupby('species')['wd'].nunique()
        count2 = pd.DataFrame(count2)
        #add column with cutoff calculation 
        count2['cutoff']= count2['wd']*peak_presence
        #merge both dataframes based on species
        df3 = pd.merge(slidexy,count2, left_index=True, right_index=True)
        #set intensity of the bins lower than cutoff to 0
        df3.loc[df3['samples'] < df3['cutoff'], 'int_rel'] = 0
        df3=df3.drop(['samples','wd','cutoff'], axis=1)
        df3=df3.reset_index()
        peaks = df3.groupby('species').apply(lambda x: peak_search(x, noise_level))
        peaks.reset_index(level=0, inplace=True)
        db.session.query(ReferenceSpectra).delete()
        db.session.commit()
        peaks.to_sql('reference_spectra', con=db.engine, if_exists='append', index=False)
        flash('Consensus spectra are updated')

        return render_template('consensus_update.html', form=form)
    return render_template('consensus_update.html', form=form)




@db_manager.route('/delete_wd', methods =['GET','POST'])
def delete_wd():
    form = WDDeleteForm()
    wd = form.wd.data
    if form.validate_on_submit():
        wd_to_delete = Files.query.filter_by(wd=wd).all()
        if wd_to_delete:
            Files.query.filter(Files.wd==wd).delete()
            db.session.commit()
            flash ('your wd spectra was correctly deleted from the database')
        else:
            flash('WD number is not in the Database')
            
    return render_template ("wd_delete.html", form=form)


@db_manager.route('/custome_consensus', methods = ['GET','POST'])
def calculate_consensus():
    form = CalculateConsensusForm()
    window = form.window.data
    step = form.step.data
    noise_level = form.noise_level.data
    peak_presence = form.peak_presence.data
     
    if form.validate_on_submit():
        f =form.file.data
        mylist = []
        content = pd.DataFrame()
        i = 0 
        for file in f:
            filename = secure_filename(file.filename)
            content_loop = pd.read_csv(file, sep="\t", header=None, skip_blank_lines=True, skiprows=4)
            mylist.append(filename)
            content_loop = content_loop.iloc [:,0:2]
            content_loop=content_loop.rename(columns = {0:'mz',1:'intensity'})
            content_loop['filename'] = filename
            content_loop =content_loop.dropna(axis=1, how='all')
            content = content.append(content_loop, ignore_index=True)
            i+=1 
        content['species'] = content['filename'].str.split('_').str[0]
        content['wd'] = content['filename'].str.split('_').str[1]
        content['origin'] = content['filename'].str.split('_').str[2]
        content = content.dropna()
        content['origin'] = content.origin.replace({'.txt':''}, regex=True)
        content = content.drop(['filename','origin','wd','species'], axis=1)
        content = content.sort_values(by=['mz'])
        content = content.reset_index(drop=True)       
        cut = i*peak_presence
        
        slidexy=slidefunc(content,window,step)
        slidexy.loc[slidexy['samples'] < cut, 'int_rel'] = 0
        peaks = pd.DataFrame(columns=['mz','int_rel'])
        peak_search_active = 0
        top = len(slidexy)
        for s in range (1, top):
            mzbin_int = slidexy.iloc[s]['int_rel']
            if mzbin_int>0 and peak_search_active==0 :
                peak_start=s
                peak_search_active=1
            if mzbin_int==0 and peak_search_active ==1:
                peak_stop =s-1
                peak_mz = slidexy[['bins']].iloc[[peak_start,peak_stop]].mean()
                peak_int = slidexy[['int_rel']].iloc[[peak_start,peak_stop]].mean()
                peak_means = pd.DataFrame([[peak_mz.iloc[0],peak_int.iloc[0]]], columns=['mz','int_rel'])                
                if peak_int.iloc[0] > noise_level:
                    peaks = peaks.append(peak_means, ignore_index=True) 
                
                peak_search_active = 0
        db.session.query(TempSpectra).delete()
        db.session.commit()
        db.session.query(TempSpectra2).delete()
        db.session.commit()
        peaks.to_sql('temp_spectra', con = db.engine,  if_exists='append', index=False)
        content.to_sql('temp_all_spectra', con = db.engine, if_exists='append', index=False)       
        return redirect(url_for('db_manager.show_dashboard'))
     
    return render_template('custome_consensus.html', form=form)

@db_manager.route('/dashboard/', methods = ['GET','POST'])
def show_dashboard():
    form = DownloadFile() 
    plots = []
    plots.append(make_plot())
    ref_spectra=pd.read_sql_table('temp_spectra', con= db.engine)
    
    if request.method == 'POST':
        resp = make_response(ref_spectra.to_csv(sep="\t", index=False))
        resp.headers["Content-Disposition"] = 'attachment; filename= "consensus_spectra.txt"'
        resp.headers["Content-Type"] = "text/csv"
        return resp
    return render_template('dashboard.html', plots=plots, form=form)

def make_plot():
    
    ref_spectra=pd.read_sql_table('temp_spectra', con= db.engine)
    all_spectra= pd.read_sql_table('temp_all_spectra', con= db.engine)
    
    x2=ref_spectra['mz']
    y2=ref_spectra['int_rel']
    x = all_spectra['mz']
    y = all_spectra['intensity']
    TOOLTIPS = [("mass", "$x"), ("intensity", "$y")]
    plot = figure(plot_height=300, sizing_mode='scale_width', x_axis_label= 'm/z',
    y_axis_label= 'int %[BP]', tooltips=TOOLTIPS)
    plot.circle(x, y, line_width=1, alpha=0.4)
    plot.segment(x2, y2, x2, 0 , color="red", line_width=1)
    plot.segment(0,0,1000,0,color='black',line_width=1)
    #plot.circle(x2,y2, color = 'red', line_width=0.5)
    script, div = components(plot)
    return script, div

#File filter
@db_manager.route('/file_filter', methods = ['GET','POST'])
def file_filter():
    form = FileFilterForm()
    if form.validate_on_submit():
        f =form.file.data
        mylist = []
        content = pd.DataFrame()
        countsp=list()
        countus=list()
        file_nor = list()
        for file in f:
            filename = secure_filename(file.filename)
            count = filename.count('_')
            count_spaces=filename.count(' ')
            if count > 2:
                countus.append(file)
            if count_spaces > 0:
                countsp.append(file)
        
            df = pd.read_csv(file, sep="\t", header=None, skip_blank_lines=True, skiprows=4)
            df['filename'] = filename
            highest = df[1].max()
            if highest > 100:
                file_nor.append(file)
        
        return render_template('file_filter_results.html', form=form, countus=countus, countsp=countsp, file_nor=file_nor)
        
    
    return render_template('file_filter.html', form=form)