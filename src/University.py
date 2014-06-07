import gtk

import os
from random import randint

from db import db
from Timetableasy import app
from TreeMgmt import TreeMgmt

global interface_university

class UniversityInterface(object):

	def __init__(self):
		from GtkMapper import GtkMapper
		mapper = GtkMapper('graphics/dialog_university.glade', self,
		    app.debug)

	def edit(self, obj):
		self.current_obj = obj
		self.name.set_text(obj.name)
		self.email_server.set_text(obj.email_server)
		self.password_length.set_value(obj.password_length)
		result = self.dialog.run()
		self.dialog.hide()
		print result
		self.current_obj = None
		return result

	def get_dialog_fields(self):
		"""get field of the dialog_university and fill university
		 object with that"""

		obj = self.current_obj
		obj.name = self.name.get_text()
		obj.password_length = self.password_length.get_value_as_int()
		obj.email_server = self.email_server.get_text()

	def menu_cursus_display(self, obj, event):
		self.current_obj = obj
		self.menu_cursus.show_all()
		self.menu_cursus.popup(None, None, None, event.button,
		    event.time)

	def menu_campus_display(self, obj, event):
		self.current_obj = obj
		self.menu_campus.show_all()
		self.menu_campus.popup(None, None, None, event.button,
		    event.time)

	# dialog callbacks
	def on_valid(self, widget):
		self.get_dialog_fields()
		db.session_try_commit()
		TreeMgmt.replug_parents(self.current_obj)
		self.dialog.response(gtk.RESPONSE_OK)

	def on_cancel(self, widget):
		self.dialog.response(gtk.RESPONSE_CANCEL)

	# menu callbacks
	def on_campus_add(self, widget):
		from Campus import Campus
		obj = self.current_obj
		campus = Campus()
		campus.init_graphics()
		if campus.add_campus() == gtk.RESPONSE_OK:
			TreeMgmt.replug_parents(obj)
		self.current_obj = None

	def on_cursus_add(self, widget):
		from Cursus import Cursus
		obj = self.current_obj
		cursus = Cursus()
		cursus.init_graphics()
		if cursus.add_cursus() == gtk.RESPONSE_OK:
			TreeMgmt.replug_parents(obj)
		self.current_obj = None

	def on_settings_edit(self, widget):
		obj = self.current_obj
		self.edit(obj)
		self.current_obj = None

class University(object):
	ADD_CURSUS = 1
	ADD_CAMPUS = 2

	def new(self):
		# XXX here we should put SQL installation on remote server
		# XXX then run first user creation
		pass

	def edit(self):
		return interface_university.edit(self)

	# TreeMgmt Callbacks
	def cb_tree_plug(self, tree, iter, id):
		"""plug object's childs in the tree"""
		from TreeMgmt import TreeRowMgmtSeparator
		if id == "cursus":
			from Cursus import Cursus
			from User import User
			def query(db, empty):
				q = db.session.query(Cursus)
				return q.order_by(Cursus.start.desc()).all()
			cursuslist = db.session_query(query, None,
			    'university, cursuslist : ' +
			    'query(Cursus).order_by(Cursus.start.desc()).all()')
			if cursuslist:
				for cursus in cursuslist:
					tree.plug(iter, cursus, self)
			tree.plug_action(iter, Cursus(), self,
			    Cursus.ADD_ACTION)
			tree.plug_group(iter, User(), self,
			    User.ADMINISTRATORS_GROUP)

		else:
			from Campus import Campus

			def query(db, empty):
				q = db.session.query(Campus)
				return q.order_by(Campus.name.desc()).all()

			campuslist = db.session_query(query, None,
			    'university, campuslist : ' +
			    'query(Campus).order_by(Campus.name.desc()).all()')
			for campus in campuslist:
				tree.plug(iter, campus, self)
			tree.plug_action(iter, Campus(), self,
			    Campus.ADD_ACTION)

	def cb_tree_pixbuf(self, tree, id):
		"""return the pixbuf for the tree"""
		image = gtk.Image()
		image.set_from_file(os.path.normpath('graphics/images/university.png'))
		return image.get_pixbuf()

	def cb_tree_name(self, tree, id):
		"""return the name for the tree"""
		return self.name

	def on_tree_rightclick(self, tree, event, id):
		"""call when the user do a right click on the tree row"""
		if not self.row[id].action:
			if id == "cursus":
				interface_university.menu_cursus_display(self,
				    event)
			elif id == "campus":
				interface_university.menu_campus_display(self,
				    event)

	def on_tree_selected(self, tree, id):
		"""call when the user double click on the tree row"""
		self.planning.display(app.contentmgr)

	# db_fill callback
	def cb_fill(self, number):
		"""callback for fill the db"""
		from Planning import Planning
		from User import User
		self.planning = Planning()
		self.planning.cb_fill(number * 10)
		self.name = "Timetableasy"
		db.session.add(self)
		user = User()
		user.cb_fill(randint(1, number), "db_user")

def init():
	""" initialize graphics interface_university define table university
	 and mapping"""

	global interface_university
	interface_university = UniversityInterface()

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper
	# Dependencies
	from Planning import Planning

	t_university = Table('university', db.metadata,
		Column('id',					types.Integer,
			Sequence('university_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),

		Column('name',					types.VARCHAR(255),
			nullable	= False),

		Column('password_length',			types.Integer,
			nullable	= False,
			default		= 8),

		Column('email_server',				types.VARCHAR(255),
			nullable	= False,
			default		= 'smtp.asystant.net'),

		Column('id_planning',				types.Integer,
			ForeignKey('planning.id'),
			nullable	= False),
	)

	mapper(University, t_university, properties = {
		'planning'	: relationship(Planning,
			backref		= backref('type_univ', uselist = False)),
	})
