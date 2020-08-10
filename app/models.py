"""

AUTOR: jarquinsandra


"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from app import db
import datetime


#fields in this class are aligned with the pd dataframe created from files imported 
class Files(db.Model):
		__tablename__ = 'files'
		id = db.Column(db.Integer, primary_key=True)
		filename = db.Column(db.String(100), unique=False, nullable=False)
		intensity = db.Column(db.Float, unique=False, nullable=False)
		mz = db.Column(db.Float, unique=False, nullable=False)
		origin = db.Column(db.String(100), unique=False, nullable=False)
		species = db.Column(db.String(60), unique=False, nullable=False)
		wd = db.Column(db.String(60), unique=False, nullable=False)
		time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
		time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
		
		
		@staticmethod
		def get_by_species(species):
			return Files.query.filter_by(species=species).all()
		
		@staticmethod
		def get_by_wd(wd):
			return Files.query.filter_by(wd=wd).all()
		def delete(self):
			db.session.delete(self)
			db.session.commit()


class ReferenceSpectra(db.Model):
	__tablename__= 'reference_spectra'
	id = db.Column(db.Integer, primary_key = True)
	species = db.Column(db.String(60), unique=False, nullable=False)
	mz = db.Column(db.Float, unique=False, nullable=False)
	int_rel = db.Column(db.Float, unique=False, nullable=False)
	time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
	
class TempSpectra(db.Model):
	__tablename__= 'temp_spectra'
	id = db.Column(db.Integer, primary_key = True)
	mz = db.Column(db.Float, unique=False, nullable=False)
	int_rel = db.Column(db.Float, unique=False, nullable=False)


class TempSpectra2(db.Model):
	__tablename__= 'temp_all_spectra'
	id = db.Column(db.Integer, primary_key = True)
	mz = db.Column(db.Float, unique=False, nullable=False)
	intensity = db.Column(db.Float, unique=False, nullable=False)
