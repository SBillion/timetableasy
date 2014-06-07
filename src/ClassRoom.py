import gtk

import os
import re
import datetime



class ClassRoom(object):
	pass

def init():
	"""define table classroom and mapping"""

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper
	# Dependencies
	from db import db
	from Campus import Campus

	classroom_table = Table('classroom', db.metadata,
		Column('id', types.Integer,
			Sequence('classroom_seq_id', optional=True), nullable=False, primary_key=True),
		Column('name', types.VARCHAR(255), nullable=False),
		Column('id_campus', types.Integer, ForeignKey('campus.id'), nullable=False),
	)

	mapper(ClassRoom, classroom_table, properties={
		'campus'		:relationship(Campus, backref='classrooms'),
	})
