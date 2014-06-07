# -*- coding: utf-8 -*-
import gtk

import os
import re
import datetime
from datetime import date
from random import randint

from db import db
from Timetableasy import app
from TreeMgmt import TreeMgmt
from Period import Period

class Cursus(object):
	ADD_ACTION = 1

	def init_graphics(self):
		from GtkMapper import GtkMapper
		if hasattr(self, "init"):
			return
		self.init = True
		mapper = GtkMapper('graphics/dialog_cursus.glade', self, app.debug)

	def add_cursus(self):
		"""connect buttons and display dialog_cursus """

		self.init_graphics()
		self.dialog.valid.connect("clicked", self.on_dialog_add)
		result = self.dialog.obj.run()
		print "result : " + str(result)
		self.dialog.obj.hide()
		return result

	def change_cursus(self):
		"""connect buttons, set new title, fill dialog fields with,
		 object fields and display dialog_cursus """

		self.init_graphics()
		res = re.split("[-]", str(self.start))
		year, month, day = res
		date = datetime.date(int(year), int(month), int(day))

		self.dialog.name.set_text(self.name)
		self.dialog.start.set_text(date.strftime('%A %d %B %Y').title())
		self.calendar.select_day(int(day))
		self.calendar.select_month(int(month)-1, int(year))

		self.dialog.obj.set_title("Modification du cursus " + self.name)
		self.dialog.valid.connect("clicked", self.on_dialog_change)
		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		return result

	def get_dialog_fields(self):
		"""get field of the dialog_cursus and fill cursus
		 object with that"""

		self.name = self.dialog.name.get_text()
		year, month, day = self.calendar.get_date()
		self.start = datetime.date(year, month+1, day)
		self.id_period = 1

	def place_popup(self):
		dialog_alloc = self.dialog.obj.get_position()
		entry_alloc = self.dialog.start.get_allocation()
		# XXX : offset tout moche a fix
		popup_x = dialog_alloc[0] + entry_alloc.x + 5
		popup_y = dialog_alloc[1] + entry_alloc.y + 50
		self.popup_calendar.move(popup_x, popup_y)
		self.popup_calendar.set_keep_above(True)

	# dialog callback
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
		self.dialog.start.set_text(date.strftime('%A %d %B %Y').title())
		self.popup_calendar.hide()

	def on_dialog_cancel(self, widget):
		"""close dialog_cursus"""

		self.dialog.obj.response(gtk.RESPONSE_CANCEL)

	def on_dialog_add(self, widget):
		"""call get_dialog_fields, add the object to the session
		 and call db.session_try_commit, response
		 gtk.RESPONSE_OK"""

		self.get_dialog_fields()
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
		"""initialize cursus, call add_cursus and call replug
		for update object entries"""

		cursus = Cursus()
		cursus.init_graphics()
		if cursus.add_cursus() == gtk.RESPONSE_OK:
			TreeMgmt.replug_parents(self)

	def on_menu_edit(self, widget):
		"""call change_cursus, and call replug for update object
		  entries"""

		if self.change_cursus() == gtk.RESPONSE_OK:
			TreeMgmt.replug_parents(self)

	def on_menu_delete(self, widget):
		"""call dialog for confirmation, if validate delete
		object of the session, call db.session_try_commit and
		call replug for update object entries, and destroy dialog"""

		dialog = gtk.MessageDialog(None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		    gtk.MESSAGE_QUESTION,
		    gtk.BUTTONS_OK_CANCEL,
		    "Etes vous sûr de vouloir supprimer le cursus " + self.name + "?")
		if dialog.run() == gtk.RESPONSE_OK:
			db.session.delete(self)
			db.session_try_commit()
			TreeMgmt.replug_parents(self)
		dialog.destroy()

	# TreeMgmt Callbacks
	def cb_tree_plug(self, tree, iter, id):
		"""plug object's childs in the tree"""
		from Period import Period
		from User import User
		from TreeMgmt import TreeRowMgmtSeparator

		period = None
		for period in self.periods:
			tree.plug(iter, period, self)
		self.last_period = period

		add_period = Period()
		tree.plug_action(iter, add_period, self,
		    Period.ADD_ACTION)

		tree.plug_group(iter, User(), self, User.CURSUS_MANAGERS_GROUP)

	def cb_tree_pixbuf(self, tree, id):
		"""return the pixbuf for the tree"""
		image = gtk.Image()
		if self.row[id].action == self.ADD_ACTION:
			image.set_from_file(os.path.normpath('graphics/images/cursus_add.png'))
		else:
			image.set_from_file(os.path.normpath('graphics/images/cursus.png'))
		return image.get_pixbuf()

	def cb_tree_name(self, tree, id):
		"""return the name for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "Nouveau cursus"
		return self.name

	def cb_tree_tooltip_text(self, tree, id):
		"""return the tooltip text for the tree"""
		if self.row[id].action == self.ADD_ACTION:
			return "double clic pour ajouter"
		else:
			if hasattr(self, "last_period") and self.last_period:
				return 'Début: ' + str(self.start) + ' Fin: ' + str(self.last_period.end)
			return 'Début: ' + str(self.start)

	def on_tree_rightclick(self, tree, event, id):
		"""call when the user do a right click on the tree row"""
		if not self.row[id].action:
			self.init_graphics()
			self.menu.show_all()
			self.menu.popup(None, None, None, event.button, event.time)

	def on_tree_selected(self, tree, id):
		"""call when the user double click on the tree row"""
		if self.row[id].action == self.ADD_ACTION:
			if self.add_cursus() == gtk.RESPONSE_OK:
				TreeMgmt.replug_parents(self)

	# db_fill callback
	def cb_fill(self, number):
		"""callback for fill the db"""

		from User import User
		import Event
		for i in range(number):
			cursus = Cursus()
			cursus.name = "Cursus-"+str(date.today().year + i)
			cursus.start = date(date.today().year + i, 1, 1)
			db.session.add(cursus)

			period = Period()
			period.cursus = cursus
			period.cb_fill(number, cursus.name)

			user = User()
			user.cursus = [cursus]
			user.cb_fill(randint(1, number), 'cursus_user'+str(i))

def init():
	"""define table cursus and mapping"""

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper
	# Dependencies
	from Period import Period

	t_cursus = Table('cursus', db.metadata,
		Column('id',					types.Integer,
			Sequence('cursus_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),

		Column('name',					types.VARCHAR(255),
			nullable	= False,
			unique		= True),

		Column('start',					types.Date(),
			nullable	= False),
	)

	mapper(Cursus, t_cursus)
