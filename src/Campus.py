# -*- coding: utf-8 -*-
import gtk

import os
from datetime import date
from random import randint

from db import db
from Timetableasy import app
from Planning import Planning

class Campus(object):
	ADD_ACTION = 1

	def init_graphics(self):
		"""init graphic interface, map dialog_campus.glade"""
		from GtkMapper import GtkMapper
		if hasattr(self, "init"):
			return
		self.init = True
		GtkMapper('graphics/dialog_campus.glade', self, app.debug)

	def add_campus(self):
		"""connect buttons and display dialog_campus """

		self.init_graphics()
		self.dialog.valid.connect("clicked", self.on_dialog_add)
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		return result

	def change_campus(self):
		"""connect buttons, set new title, fill the name field,
		 and display dialog_campus """

		self.init_graphics()
		self.dialog.name.set_text(self.name)
		self.dialog.obj.set_title("Modification du campus " + self.name)
		self.dialog.valid.connect("clicked", self.on_dialog_change)
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		return result

	def get_dialog_fields(self):
		"""get field of the dialog_campus and fill campus
		 object with that"""

		self.name = self.dialog.name.get_text()

	# dialog callback
	def on_dialog_cancel(self, widget):
		"""close dialog_campus"""

		self.dialog.obj.response(gtk.RESPONSE_CANCEL)

	def on_dialog_add(self, widget):
		"""call get_dialog_fields, add the object to the session
		 and call db.session_try_commit, response
		 gtk.RESPONSE_OK"""

		from Planning import Planning
		self.get_dialog_fields()
		self.planning = Planning()
		db.session.add(self)
		db.session_try_commit()
		self.dialog.obj.response(gtk.RESPONSE_OK)

	def on_dialog_change(self, widget):
		"""call get_dialog_fields, call db.session_try_commit,
		 response gtk.RESPONSE_OK"""

		self.get_dialog_fields()
		db.session_try_commit()
		self.dialog.obj.response(gtk.RESPONSE_OK)

	# menu callbacks
	def on_menu_add(self, widget):
		"""initialize campus, call add_campus and call replug
		for update object entries"""
		campus = Campus()
		campus.init_graphics()
		if campus.add_campus() == gtk.RESPONSE_OK:
			for id in self.row:
				self.row[id].tree.replug(self.row[id].obj_parent)

	def on_menu_edit(self, widget):
		"""call change_campus, and call replug for update object
		  entries"""

		if self.change_campus() == gtk.RESPONSE_OK:
			for id in self.row:
				self.row[id].tree.replug(self.row[id].obj_parent)

	def on_menu_delete(self, widget):
		"""call dialog for confirmation, if validate delete
		object of the session, call db.session_try_commit and
		call replug for update object entries, and destroy dialog"""

		dialog = gtk.MessageDialog(None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		    gtk.MESSAGE_QUESTION,
		    gtk.BUTTONS_OK_CANCEL,
		    "Etes vous sûr de vouloir supprimer le campus " + self.name + "?")
		if dialog.run() == gtk.RESPONSE_OK:
			db.session.delete(self)
			db.session_try_commit()
			for id in self.row:
				self.row[id].tree.replug(self.row[id].obj_parent)
		dialog.destroy()

	# TreeMgmt Callbacks
	def cb_tree_plug(self, tree, iter, id):
		"""plug object's childs in the tree"""
		from Class import Class
		from User import User
		from TreeMgmt import TreeRowMgmtSeparator

		for iclass in self.classes:
			tree.plug(iter, iclass, self)
		tree.plug_action(iter, Class(), self, Class.ADD_ACTION)
		tree.plug_group(iter, User(), self, User.CAMPUS_TEACHERS_GROUP)
		tree.plug_group(iter, User(), self, User.CAMPUS_MANAGERS_GROUP)

	def cb_tree_pixbuf(self, tree, id):
		"""return the pixbuf for the tree"""
		image = gtk.Image()
		if self.row[id].action == self.ADD_ACTION:
			image.set_from_file(os.path.normpath('graphics/images/campus_add.png'))
		else:
			image.set_from_file(os.path.normpath('graphics/images/campus.png'))
		return image.get_pixbuf()

	def cb_tree_name(self, tree, id):
		"""return the name for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "Nouveau campus"
		return self.name

	def cb_tree_tooltip_text(self, tree, id):
		"""return the tooltip text for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "double clic pour ajouter"
		else:
			return None

	def on_tree_rightclick(self, tree, event, id):
		"""call when the user do a right click on the tree row"""
		if not self.row[id].action:
			self.init_graphics()
			self.menu.show_all()
			self.menu.popup(None, None, None, event.button, event.time)

	def on_tree_selected(self, tree, id):
		"""call when the user double click on the tree row"""
		if self.row[id].action == self.ADD_ACTION:
			if self.add_campus() == gtk.RESPONSE_OK:
				for id in self.row:
					self.row[id].tree.replug(self.row[id].obj_parent)
		else:
			self.planning.display(app.contentmgr)

	# db_fill callback
	def cb_fill(self, number):
		"""callback for fill the db"""

		from User import User
		from Class import Class
		import Event
		for i in range(number):
			campus = Campus()
			campus.name = "Campus"+str(i)
			Event.fill_date = date(date.today().year + i, 1, 1)
			campus.planning = Planning()
			campus.planning.cb_fill(number * 10)
			db.session.add(campus)

			user = User()
			user.campus = [campus]
			user.cb_fill(randint(1, number), campus.name + '_manager')

			user = User()
			user.teacher_campus = [campus]
			user.cb_fill(randint(1, number), campus.name + '_teacher')

			classe = Class()
			classe.campus = campus
			classe.cb_fill(number)

def init():
	"""define table campus and mapping"""

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper
	# Dependencies
	from Planning import Planning

	t_campus = Table('campus', db.metadata,
		Column('id',					types.Integer,
			Sequence('campus_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),

		Column('name',					types.VARCHAR(255),
			nullable	= False,
			unique		= True),

		Column('id_planning',				types.Integer,
			ForeignKey('planning.id'),
			nullable	= False),
	)

	mapper(Campus, t_campus, properties = {
		'planning'	: relationship(Planning,
			backref		= backref('type_campus', uselist = False)),
	})
