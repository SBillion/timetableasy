# -*- coding: utf-8 -*-
import gtk

import os
from random import randint

from db import db
from Timetableasy import app
from Planning import Planning

class Class(object):
	ADD_ACTION = 1

	def init_graphics(self):
		from GtkMapper import GtkMapper
		if hasattr(self, "init"):
			return
		self.init = True
		mapper = GtkMapper('graphics/dialog_class.glade', self, app.debug)
		self.action_add = mapper.glade.menu.add

	def add_class(self, campus):
		"""connect buttons and display dialog_class """

		self.init_graphics()
		self.dialog.valid.connect("clicked", self.on_dialog_add)
		self.campus = campus
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		if not result == gtk.RESPONSE_OK:
			self.campus = None
		return result

	def change_class(self):
		"""connect buttons, set new title, fill the name field,
		 and display dialog_class """

		self.init_graphics()
		self.dialog.name.set_text(self.name)
		self.dialog.obj.set_title("Modification de la classe " + self.name)
		self.dialog.valid.connect("clicked", self.on_dialog_change)
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		return result

	def get_dialog_fields(self):
		"""get field of the dialog_class and fill class
		 object with that"""

		self.name = self.dialog.name.get_text()

	# dialog callback
	def on_dialog_cancel(self, widget):
		"""close dialog_class"""

		self.dialog.obj.response(gtk.RESPONSE_CANCEL)

	def on_dialog_add(self, widget):
		"""call get_dialog_fields, add the object to the session
		 and call db.session_try_commit, response
		 gtk.RESPONSE_OK"""

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
	def on_menu_add(self, widget, id):
		"""initialize class, call add_class and call replug
		for update object entries"""

		classe = Class()
		classe.init_graphics()
		if classe.add_class(self.row[id].obj_parent) == gtk.RESPONSE_OK:
			for id in self.row:
				self.row[id].tree.replug(self.row[id].obj_parent)

	def on_menu_edit(self, widget):
		"""call change_class, and call replug for update object
		  entries"""

		if self.change_class() == gtk.RESPONSE_OK:
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
		    "Etes vous sûr de vouloir supprimer la classe " + self.name + "?")
		if dialog.run() == gtk.RESPONSE_OK:
			db.session.delete(self)
			db.session_try_commit()
			for id in self.row:
				self.row[id].tree.replug(self.row[id].obj_parent)
		dialog.destroy()

	# TreeMgmt Callbacks
	def cb_tree_plug(self, tree, iter, id):
		"""plug object's childs in the tree"""
		from User import User
		from TreeMgmt import TreeRowMgmtSeparator
		from Period import Period

		def plug_period(obj, tree, iter, parent):
			for period in obj.periods:
				tree.plug(iter, period, parent)
			link_period = Period()
			tree.plug_action(iter, link_period, parent,
			    Period.LINK_CLASS_ACTION)
		image = gtk.Image()
		image.set_from_file(os.path.normpath('graphics/images/period_group.png'))
		period_group = TreeRowMgmtSeparator(plug_period, self,
		    "Périodes", image.get_pixbuf(),
		    "Périodes de la classe " + self.name)
		tree.plug(iter, period_group, self)

		tree.plug_group(iter, User(), self, User.CLASS_STUDENTS_GROUP)
		tree.plug_group(iter, User(), self, User.CLASS_TEACHERS_GROUP)
		tree.plug_group(iter, User(), self, User.CLASS_MANAGERS_GROUP)

	def cb_tree_pixbuf(self, tree, id):
		"""return the pixbuf for the tree"""
		image = gtk.Image()
		if self.row[id].action == self.ADD_ACTION:
			image.set_from_file(os.path.normpath('graphics/images/class_add.png'))
		else:
			image.set_from_file(os.path.normpath('graphics/images/class.png'))
		return image.get_pixbuf()

	def cb_tree_name(self, tree, id):
		"""return the name for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "Nouvelle classe"
		return self.name

	def cb_tree_tooltip_text(self, tree, id):
		"""return the tooltip text for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "double clic pour ajouter"

	def on_tree_rightclick(self, tree, event, id):
		"""call when the user do a right click on the tree row"""
		if not self.row[id].action:
			self.init_graphics()
			self.action_add.connect("activate", self.on_menu_add, id)
			self.menu.show_all()
			self.menu.popup(None, None, None, event.button, event.time)

	def on_tree_selected(self, tree, id):
		"""call when the user double click on the tree row"""
		if self.row[id].action == self.ADD_ACTION:
			if self.add_class(self.row[id].obj_parent) == gtk.RESPONSE_OK:
				for id in self.row:
					self.row[id].tree.replug(self.row[id].obj_parent)
		else:
			self.planning.display(app.contentmgr)

	# db_fill callback
	def cb_fill(self, number):
		"""callback for fill the db"""

		from User import User
		from Planning import Planning
		from Cursus import Cursus
		def fill_insert(classe, i):
			classe.name = "C"+str(i)

			classe.planning = Planning()
			# XXX fill planning with normal events ?
			#classe.planning.cb_fill(number)
			# XXX fill planning with course events
			cursus = db.session.query(Cursus).get(i+1)
			if cursus:
				periods = cursus.periods
				import Event
				Event.fill_date = cursus.start
			else:
				periods = []
			for period in periods:
				for course in period.courses:
					from Event import Event
					# XXX move fill event in class
					event = Event()
					event.planning = classe.planning
					event.course = course
					course.c_elearning_rest = course.c_elearning
					course.c_classroom_rest = course.c_classroom
					course.c_practice_rest = course.c_practice
					course.e_oral_rest = course.e_oral
					course.e_practice_rest = course.e_practice
					hours = course.c_elearning
					hours += course.c_classroom
					hours += course.c_practice
					hours += course.e_oral
					hours += course.e_practice
					event.cb_fill(hours / 2)

				if len(period.classes) == 0:
					for course in period.courses:
						event = Event()
						event.planning = period.planning
						event.course = course
						event.cb_fill(event.course.e_exam / 2 + 1)

				import Event
				Event.fill_date = period.end

			classe.periods = periods

			user = User()
			user.manager_class = [classe]
			user.cb_fill(randint(1, number),
			    classe.campus.name + '_' + classe.name +
			    '_manager_user' + str(i))

			user = User()
			user.student_class = classe
			user.cb_fill(randint(10, 30), classe.campus.name+'_'+classe.name+'_student_user'+str(i))

			db.session.add(classe)

		for i in range(number - 1):
			classe = Class()
			classe.campus = self.campus
			fill_insert(classe, i)
		i = number - 1
		fill_insert(self, i)


def init():
	"""define table class and mapping"""

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper
	# Dependencies
	from Planning import Planning
	from Campus import Campus
	from Period import Period

	t_class = Table('class', db.metadata,
		Column('id',					types.Integer,
			Sequence('class_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),

		Column('name',					types.VARCHAR(255),
			nullable	= False),

		Column('id_planning',				types.Integer,
			ForeignKey('planning.id'),
			nullable	= False),

		Column('id_campus',				types.Integer,
			ForeignKey('campus.id'),
			nullable	= False),
	)

	t_class_period = Table('class_period', db.metadata,
		Column('id_class',				types.Integer,
			ForeignKey('class.id'),
			nullable	= False),

		Column('id_period',				types.Integer,
			ForeignKey('period.id'),
			nullable	= False),
	)

	mapper(Class, t_class, properties = {
		'planning'	: relationship(Planning,
			backref		= backref('type_class', uselist = False)),

		'campus'	: relationship(Campus,
			backref		= backref('classes',
				cascade		= "all, delete-orphan",
				order_by	= t_class.c.name.desc())),

		'periods'	: relationship(Period,
			secondary	= t_class_period,
			backref		= 'classes'),
	})
