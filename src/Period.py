# -*- coding: utf-8 -*-
import gtk

import os
import re
import datetime
from datetime import date

from db import db
from Timetableasy import app
from Planning import Planning

global interface_period

class PeriodInterface(object):

	def __init__(self):
		from GtkMapper import GtkMapper
		mapper = GtkMapper('graphics/dialog_period.glade', self, app.debug)
		self.action_add = mapper.glade.menu.add
		self.dialog_confirmation = gtk.MessageDialog(None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		    gtk.MESSAGE_QUESTION,
		    gtk.BUTTONS_OK_CANCEL,
		    None)

	def add(self, obj):
		"""connect buttons, set title and display dialog_period """

		self.current_obj = obj
		year, month, day = self.calendar.get_date()
		date = datetime.date(year, month+1, day)
		self.dialog.end.set_text(date.strftime('%A %d %B %Y').title())
		self.dialog.obj.set_title("Création d'une période")
		self.dialog.valid.connect("clicked", self.on_dialog_add)
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		self.current_obj = None
		return result

	def change(self, obj):
		"""connect buttons, set new title, fill dialog fields with
		 object fields and display dialog_period """

		self.current_obj = obj
		res = re.split("[-]", str(obj.end))
		year, month, day = res
		date = datetime.date(int(year), int(month), int(day))

		self.dialog.name.set_text(obj.name)
		self.dialog.end.set_text(date.strftime('%A %d %B %Y').title())
		self.calendar.select_day(int(day))
		self.calendar.select_month(int(month)-1, int(year))

		self.dialog.obj.set_title("Modification de la periode " + obj.name)
		self.dialog.valid.connect("clicked", self.on_dialog_change)
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		self.current_obj = None
		return result

	def menu_display(self, obj, event):
		self.current_obj = obj
		self.menu.show_all()
		self.menu.popup(None, None, None, event.button, event.time)

	def insert(self, obj):
		from ComboMgmt import ComboMgmt
		self.current_obj = obj
		def query(db, cursus):
			from copy import deepcopy
			if cursus:
				result = []
				for period in cursus.periods:
					result.append(period)
				return result
			return db.session.query(Period).all()
		if len(obj.classe.periods):
			cursus = obj.classe.periods[0].cursus
		else:
			cursus = None
		periodstore = db.session_query(query, cursus,
		    "period_insert : query(Period).all()")
		if len(obj.classe.periods):
			for period in obj.classe.periods:
				periodstore.remove(period)
		self.period_combo = ComboMgmt(self.periods, periodstore)
		if cursus:
			self.dialog_link.obj.set_title("Insertion d'une période du cursus " + cursus.name)
		else:
			self.dialog_link.obj.set_title("Insertion d'une période")
		result = self.dialog_link.obj.run()
		self.dialog_link.obj.hide()
		self.period_combo = None
		return result

	def menu_link_display(self, obj, event):
		self.current_obj = obj
		self.menu_link.show_all()
		self.menu_link.popup(None, None, None, event.button, event.time)

	def get_dialog_fields(self):
		"""get field of the dialog_period and fill cursus
		 object with that"""

		obj = self.current_obj
		obj.name = self.dialog.name.get_text()
		year, month, day = self.calendar.get_date()
		obj.end = datetime.date(year, month+1, day)

	def place_popup(self):
		dialog_alloc = self.dialog.obj.get_position()
		entry_alloc = self.dialog.end.get_allocation()
		# XXX : offset tout moche a fix
		popup_x = dialog_alloc[0] + entry_alloc.x + 5
		popup_y = dialog_alloc[1] + entry_alloc.y + 50
		self.popup_calendar.move(popup_x, popup_y)
		self.popup_calendar.set_keep_above(True)

	# dialog callbacks
	def on_date_focus(self, widget, direction=None, data=None):
		"""on fields date focus, show the calendar widget"""

		self.place_popup()
		self.popup_calendar.show()

	def on_popup_calendar_unfocus(self, widget, direction=None, data=None):
		"""on calendar unfocus, hide the calendar"""

		self.popup_calendar.hide()

	def on_calendar_icon_press(self, widget, direction=None, data=None):
		"""on date icon click, show the calendar widget"""

		self.place_popup()
		self.popup_calendar.show()

	def on_calendar_day_selected_double_click(self, calendar):
		"""on day double click on calendar, fill the field date
		 with selected date parse in strftime format, hide
		 calendar"""

		year, month, day = calendar.get_date()
		date = datetime.date(year, month+1, day)
		self.dialog.end.set_text(date.strftime('%A %d %B %Y').title())
		self.popup_calendar.hide()

	def on_dialog_cancel(self, widget):
		"""close dialog_period"""

		self.dialog.obj.response(gtk.RESPONSE_CANCEL)

	def on_dialog_add(self, widget):
		"""call get_dialog_fields, and call db.session_query,
		 response gtk.RESPONSE_OK"""

		def query(db, obj):
			"""callback for db.session_query, this query
			 add obj to session and call db.session_try_commit"""

			from Planning import Planning
			obj.planning = Planning()
			db.session.add(obj)
			db.session_try_commit()
		obj = self.current_obj
		self.get_dialog_fields()
		db.session_query(query, obj,
		    str("insert period " + obj.name +
		    " (end:" + str(obj.end) + ") in db"))
		self.dialog.obj.response(gtk.RESPONSE_OK)

	def on_dialog_change(self, widget):
		"""call get_dialog_fields, call db.session_try_commit,
		 response gtk.RESPONSE_OK"""

		self.get_dialog_fields()
		db.session_try_commit()
		self.dialog.obj.response(gtk.RESPONSE_OK)

	def on_dialog_link_cancel(self, widget):
		self.dialog_link.obj.response(gtk.RESPONSE_CANCEL)

	def on_dialog_link_insert(self, widget):
		obj = self.current_obj
		period = self.period_combo.get_selected_object()
		period.classes.append(obj.classe)
		db.session_try_commit()
		self.dialog_link.obj.response(gtk.RESPONSE_OK)

	# menu callbacks
	def on_menu_add(self, widget):
		"""initialize period, call add_period and call replug
		for update object entries"""

		obj = self.current_obj
		period = Period()
		period.cursus = obj.cursus
		if self.add(period) == gtk.RESPONSE_OK:
			for id in obj.row:
				obj.row[id].tree.replug(obj.row[id].obj_parent)
		else:
			period.cursus = None
		self.current_obj = None

	def on_menu_edit(self, widget):
		"""call change_period, and call replug for update object
		  entries"""

		obj = self.current_obj
		if self.change(obj) == gtk.RESPONSE_OK:
			for id in obj.row:
				obj.row[id].tree.replug(obj.row[id].obj_parent)
		self.current_obj = None

	def on_menu_delete(self, widget):
		"""call dialog for confirmation, if validate delete
		object of the session, call db.session_try_commit and
		call replug for update object entries, and destroy dialog"""

		obj = self.current_obj
		self.dialog_confirmation.set_markup(
		    "Etes vous sûr de vouloir supprimer la période " + obj.name + " ?")
		if self.dialog_confirmation.run() == gtk.RESPONSE_OK:
			db.session.delete(obj)
			db.session_try_commit()
			for id in obj.row:
				obj.row[id].tree.replug(obj.row[id].obj_parent)
		self.dialog_confirmation.hide()
		self.current_obj = None

	def on_menu_insert(self, widget):
		obj = self.current_obj
		if self.insert(obj) == gtk.RESPONSE_OK:
			for id in obj.row:
				obj.row[id].tree.replug(obj.row[id].obj_parent)
		self.current_obj = None

	def on_menu_remove(self, widget):
		obj = self.current_obj
		self.dialog_confirmation.set_markup(
		    "Etes vous sûr de vouloir retirer la période " + obj.name + " ?")
		if self.dialog_confirmation.run() == gtk.RESPONSE_OK:
			obj.classes.remove(obj.classe)
			db.session_try_commit()
			for id in obj.row:
				obj.row[id].tree.replug(obj.row[id].obj_parent)
		self.dialog_confirmation.hide()
		self.current_obj = None

class Period(object):
	ADD_ACTION = 1
	LINK_CLASS_ACTION = 2

	# TreeMgmt Callbacks
	def cb_tree_isplugable(self, tree, id):
		if id == "campus":
			return False
		return True

	def cb_tree_plug(self, tree, iter, id):
		"""plug object's childs in the tree"""
		from Course import Course

		for course in self.courses:
			tree.plug(iter, course, self)

		add_course = Course()
		tree.plug_action(iter, add_course, self,
		    Course.ADD_ACTION)

	def cb_tree_pixbuf(self, tree, id):
		"""return the pixbuf for the tree"""
		image = gtk.Image()
		if (self.row[id].action == self.ADD_ACTION or
		    self.row[id].action == self.LINK_CLASS_ACTION):
			image.set_from_file(os.path.normpath('graphics/images/period_add.png'))
		else:
			image.set_from_file(os.path.normpath('graphics/images/period.png'))
		return image.get_pixbuf()

	def cb_tree_name(self, tree, id):
		"""return the name for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "Nouvelle période"
		elif self.row[id].action == self.LINK_CLASS_ACTION:
			return "Insérer une période"
		if id == "campus":
			return self.cursus.name + " - " + self.name
		return self.name

	def cb_tree_tooltip_text(self, tree, id):
		"""return the tooltip text for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "double clic pour ajouter"
		elif self.row[id].action == self.LINK_CLASS_ACTION:
			return "double clic pour insérer"
		if self.row[id].id and id == "cursus":
			parent_childs = self.row[id].row_parent.childs
			i = self.row[id].id - 1
			return str(parent_childs[i].end) + " : " + str(self.end)
		elif self.row[id].id and id == "campus":
			parent_childs = self.row[id].row_parent.childs
			i = self.row[id].id - 1
			return str(parent_childs[i].end) + " : " + str(self.end)
		return str(self.cursus.start) + " : " + str(self.end)

	def on_tree_rightclick(self, tree, event, id):
		"""call when the user do a right click on the tree row"""
		if not self.row[id].action:
			if id == "cursus":
				interface_period.menu_display(self, event)
			elif id == "campus":
				self.classe = self.row[id].obj_parent.obj
				interface_period.menu_link_display(self, event)

	def on_tree_selected(self, tree, id):
		"""call when the user double click on the tree row"""
		if self.row[id].action == self.ADD_ACTION:
			self.cursus = self.row[id].obj_parent
			if interface_period.add(self) == gtk.RESPONSE_OK:
				for id in self.row:
					self.row[id].tree.replug(self.row[id].obj_parent)
			else:
				self.cursus = None
		elif self.row[id].action == self.LINK_CLASS_ACTION:
			self.classe = self.row[id].obj_parent.obj
			if interface_period.insert(self) == gtk.RESPONSE_OK:
				for id in self.row:
					self.row[id].tree.replug(self.row[id].obj_parent)
		else:
			self.planning.display(app.contentmgr)

	# db_fill callback
	def cb_fill(self, number, prefix):
		"""callback for fill the db"""

		from Course import Course
		import Event
		def fill_insert(period, i):
			period.name = "Period"+str(i)
			d = date(period.cursus.start.year, i * 6, 1)
			period.end = d
			period.planning = Planning()
			period.planning.cb_fill(number)

			db.session.add(period)

		period = Period()
		period.cursus = self.cursus
		fill_insert(period, 1)
		course = Course()
		course.period = period
		course.cb_fill(prefix + period.name + "Course")

		if Event.fill_date < period.end:
			Event.fill_date = period.end

		fill_insert(self, 2)
		course = Course()
		course.period = self
		course.cb_fill(prefix + self.name + "Course")


	# combobox display
	def cb_combobox(self):
		return self.cursus.name + " - " + self.name

def init():
	""" initialize graphics interface_period define table period
	 and mapping"""

	# Graphics initialisation
	global interface_period
	interface_period = PeriodInterface()

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper
	# dependencies
	from Planning import Planning
	from Cursus import Cursus

	t_period = Table('period', db.metadata,
		Column('id',					types.Integer,
			Sequence('period_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),

		Column('name',					types.VARCHAR(255),
			nullable	= False),

		Column('end',					types.Date(),
			nullable	= False),

		Column('id_planning',				types.Integer,
			ForeignKey('planning.id'),
			nullable	= False),

		Column('id_cursus',				types.Integer,
			ForeignKey('cursus.id'),
			nullable	= False),
	)

	mapper(Period, t_period,  properties = {
		'planning'	: relationship(Planning,
			backref		= backref('type_period', uselist = False)),

		'cursus'	: relationship(Cursus,
			backref		= backref('periods',
				cascade		= "all, delete-orphan",
				order_by	= t_period.c.end.asc())),
	})
