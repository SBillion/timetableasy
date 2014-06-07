# -*- coding: utf-8 -*-
import gtk

import os
from random import randint

from db import db
from Timetableasy import app

global interface_course

class CourseInterface(object):

	def __init__(self):
		from GtkMapper import GtkMapper
		mapper = GtkMapper('graphics/dialog_course.glade', self, app.debug)
		self.action_add = mapper.glade.menu.add
		self.dialog_confirmation = gtk.MessageDialog(None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		    gtk.MESSAGE_QUESTION,
		    gtk.BUTTONS_OK_CANCEL,
		    None)

	def add(self, obj):
		"""connect buttons, set_title and display dialog_course"""

		self.current_obj = obj
		self.dialog.name.set_text("")
		self.dialog.c_elearning.set_value(0)
		self.dialog.c_classroom.set_value(0)
		self.dialog.c_practice.set_value(0)
		self.dialog.e_practice.set_value(0)
		self.dialog.e_exam.set_value(0)
		self.dialog.e_oral.set_value(0)
		self.dialog.obj.set_title("Création d'un cours")
		self.dialog.valid.connect("clicked", self.on_dialog_add)
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		self.current_obj = None
		return result

	def change(self, obj):
		"""connect buttons, set new title, fill fields with
		 object fields, and display dialog_course"""

		self.current_obj = obj
		self.dialog.name.set_text(obj.name)
		self.dialog.c_elearning.set_value(obj.c_elearning)
		self.dialog.c_classroom.set_value(obj.c_classroom)
		self.dialog.c_practice.set_value(obj.c_practice)
		self.dialog.e_practice.set_value(obj.e_practice)
		self.dialog.e_exam.set_value(obj.e_exam)
		self.dialog.e_oral.set_value(obj.e_oral)
		self.dialog.obj.set_title("Modification du cours " + obj.name)
		self.dialog.valid.connect("clicked", self.on_dialog_change)
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		self.current_obj = None
		return result

	def duplicate(self, obj):
		"""fill all dialog fields with obj fields, set new title
		 and display dialog_course """

		self.current_obj = obj
		self.dialog.name.set_text("")
		self.dialog.c_elearning.set_value(obj.c_elearning)
		self.dialog.c_classroom.set_value(obj.c_classroom)
		self.dialog.c_practice.set_value(obj.c_practice)
		self.dialog.e_practice.set_value(obj.e_practice)
		self.dialog.e_exam.set_value(obj.e_exam)
		self.dialog.e_oral.set_value(obj.e_oral)
		self.dialog.obj.set_title("Duplication du cours " + obj.name)
		self.dialog.valid.connect("clicked", self.on_dialog_add)
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		self.current_obj = None
		return result

	def menu_display(self, obj, event):
		self.current_obj = obj
		self.menu.show_all()
		self.menu.popup(None, None, None, event.button, event.time)

	def get_dialog_fields(self):
		"""get field of the dialog_course and fill course
		 object with that"""

		obj = self.current_obj
		obj.name = self.dialog.name.get_text()
		obj.c_elearning = int(self.dialog.c_elearning.get_value())
		obj.c_classroom = int(self.dialog.c_classroom.get_value())
		obj.c_practice = int(self.dialog.c_practice.get_value())
		obj.e_practice = int(self.dialog.e_practice.get_value())
		obj.e_exam = int(self.dialog.e_exam.get_value())
		obj.e_oral = int(self.dialog.e_oral.get_value())

	# dialog callbacks
	def on_dialog_cancel(self, widget):
		"""close dialog_course"""

		self.dialog.obj.response(gtk.RESPONSE_CANCEL)

	def on_dialog_add(self, widget):
		"""call get_dialog_fields, and call db.session_query,
		 response gtk.RESPONSE_OK"""

		def query(db, obj):
			"""callback for db.session_query, this query
			 add obj to session and call db.session_try_commit"""

			db.session.add(obj)
			db.session_try_commit()
		obj = self.current_obj
		self.get_dialog_fields()
		db.session_query(query, obj,
		    str("insert course " + obj.name +
		    " (e-learning:" + str(obj.c_elearning) +
		    " ,classroom:" + str(obj.c_classroom) +
		    " ,practice:" + str(obj.c_practice) +
		    " ,eval practice:" + str(obj.e_practice) +
		    " ,exam:" + str(obj.e_exam) +
		    " ,oral:" + str(obj.e_oral) + ") in db"))
		self.dialog.obj.response(gtk.RESPONSE_OK)

	def on_dialog_change(self, widget):
		"""call get_dialog_fields, call db.session_try_commit,
		 response gtk.RESPONSE_OK"""

		self.get_dialog_fields()
		db.session_try_commit()
		self.dialog.obj.response(gtk.RESPONSE_OK)

	# menu callbacks
	def on_menu_add(self, widget):
		"""initialize course, call keep all links, call duplicate
		and call replug for update object entries"""

		obj = self.current_obj
		course = Course()
		course.period = obj.period
		course.teachers = obj.teachers
		course.name = obj.name
		course.c_elearning = obj.c_elearning
		course.c_classroom = obj.c_classroom
		course.c_practice = obj.c_practice
		course.e_practice = obj.e_practice
		course.e_exam = obj.e_exam
		course.e_oral = obj.e_oral
		if self.duplicate(course) == gtk.RESPONSE_OK:
			for id in obj.row:
				obj.row[id].tree.replug(obj.row[id].obj_parent)
		else:
			course.period = None
			course.teachers = []
		self.current_obj = None

	def on_menu_edit(self, widget):
		"""call self.change, and call replug for update object
		  entries"""

		obj = self.current_obj
		if self.change(obj) == gtk.RESPONSE_OK:
			for id in obj.row:
				obj.row[id].tree.replug(obj.row[id].obj_parent)
		self.current_obj = None

	def on_menu_delete(self, widget):
		"""call dialog_confirmation for confirmation, if validate delete
		object of the session, call db.session_try_commit and
		call replug for update object entries, and destroy
		dialog_confirmation"""

		obj = self.current_obj
		self.dialog_confirmation.set_markup("Etes vous sûre de vouloir supprimer le cours " + obj.name + " ?")
		if self.dialog_confirmation.run() == gtk.RESPONSE_OK:
			db.session.delete(obj)
			db.session_try_commit()
			for id in obj.row:
				obj.row[id].tree.replug(obj.row[id].obj_parent)
		self.dialog_confirmation.hide()
		self.current_obj = None

class Course(object):
	ADD_ACTION = 1

	# TreeMgmt Callbacks
	def cb_tree_pixbuf(self, tree, id):
		"""return the pixbuf for the tree"""
		image = gtk.Image()
		if self.row[id].action == self.ADD_ACTION:
			image.set_from_file(os.path.normpath('graphics/images/course_add.png'))
		else:
			image.set_from_file(os.path.normpath('graphics/images/course.png'))
		return image.get_pixbuf()

	def cb_tree_name(self, tree, id):
		"""return the name for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "Nouveau cours"
		return self.name

	def cb_tree_tooltip_text(self, tree, id):
		"""return the tooltip text for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "double clic pour ajouter un cours"
		c = self.c_elearning + self.c_classroom + self.c_practice
		e = self.e_practice + self.e_exam + self.e_practice
		event_c = 0
		event_e = 0
		for event in self.events:
			if (event.modality == 'lesson_elearning' or
			    event.modality == 'lesson_classroom' or
			    event.modality == 'lesson_practice'):
				event_c += event.time_length
			elif (event.modality == 'evaluation_practice' or
			    event.modality == 'evaluation_exam' or
			    event.modality == 'evaluation_oral'):
				event_e += event.time_length
		# XXX color based on quota (ex: red if over event_c > c )
		return str("Cours: " + str(event_c) + "h/" + str(c) + "h, " +
		    "Evaluations: " + str(event_e) + "h/" + str(e) + "h")

	def on_tree_rightclick(self, tree, event, id):
		"""call when the user do a right click on the tree row"""
		if not self.row[id].action:
			interface_course.menu_display(self, event)

	def on_tree_selected(self, tree, id):
		"""call when the user double click on the tree row"""
		if self.row[id].action == self.ADD_ACTION:
			self.period = self.row[id].obj_parent
			if interface_course.add(self) == gtk.RESPONSE_OK:
				for id in self.row:
					self.row[id].tree.replug(self.row[id].obj_parent)
			else:
				self.period = None

	# db_fill callback
	def cb_fill(self, prefix):
		"""callback for fill the db"""

		def fill_insert(course, i, hours):
			from Event import Event
			hours_free = hours
			course.name = prefix+str(i)
			course.e_practice = randint(2, 6)
			course.e_exam = randint(2, 4)
			course.e_exam -= course.e_exam % 2
			course.e_oral = randint(2, 4)
			hours_free -= (course.e_practice + course.e_exam +
			    course.e_oral)

			course.c_elearning = randint(1, max([6, hours_free]))
			hours_free -= course.c_elearning

			course.c_classroom = hours_free / 2
			hours_free -= course.c_classroom

			course.c_practice = hours_free

			db.session.add(course)
		hours_free = 700
		i = 0
		while hours_free >= 60:
			course = Course()
			course.period = self.period
			hours = randint(24, 60)
			fill_insert(course, i, hours)
			hours_free -= hours
			i += 1
		fill_insert(self, i, hours_free)

def init():
	""" initialize graphics interface_course define table course
	 and mapping"""

	global interface_course
	interface_course = CourseInterface()

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper
	# Dependencies
	from Period import Period
	from User import User
	from Class import Class

	t_course = Table('course', db.metadata,
		Column('id',					types.Integer,
			Sequence('course_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),

		Column('name',					types.VARCHAR(255),
			nullable	= False,
			unique		= True),

		Column('c_elearning',				types.Integer,
			nullable	= False),

		Column('c_classroom',				types.Integer,
			nullable	= False),

		Column('c_practice',				types.Integer,
			nullable	= False),

		Column('e_practice',				types.Integer,
			nullable	= False),

		Column('e_exam',				types.Integer,
			nullable	= False),

		Column('e_oral',				types.Integer,
			nullable	= False),

		Column('id_period',				types.Integer,
			ForeignKey('period.id'),
			nullable	= False),
	)

	t_user_class_course = Table('user_class_course', db.metadata,
		Column('id_user',				types.Integer,
			ForeignKey('user.id'),
			nullable	= False),

		Column('id_class',				types.Integer,
			ForeignKey('class.id'),
			nullable	= False),

		Column('id_course',				types.Integer,
			ForeignKey('course.id'),
			nullable	= False),
	)

	mapper(Course, t_course, properties = {
		'period'	: relationship(Period,
			backref		= backref('courses',
				cascade		= "all, delete-orphan",
				order_by	= t_course.c.name.desc())),

		'teachers'	: relationship(User,
			secondary	= t_user_class_course,
			backref		= 'courses'),

		'classes'	: relationship(Class,
			secondary	= t_user_class_course,
			backref		= 'courses'),
	})

