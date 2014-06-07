# -*- coding: utf-8 -*-
import gtk

import os
import re
from datetime import date, time, timedelta, datetime
from time import mktime
from random import randint

from db import db
from Timetableasy import app
from ClassRoom import ClassRoom

global fill_date
fill_date = date(date.today().year, 1, 1)
global fill_time
fill_time = time(7, 00)

event_moda_disp = {
    'Aucune'			: 0,
    'Cours distanciel'		: 1,
    'Cours magistral'		: 2,
    'Travaux pratiques'		: 3,
    'Evaluation pratique'	: 4,
    'Evaluation'		: 5,
    'Evaluation orale'		: 6
}

event_moda_db = {
    'none'			: 0,
    'lesson_elearning'		: 1,
    'lesson_classroom'		: 2,
    'lesson_practice'		: 3,
    'evaluation_practice'	: 4,
    'evaluation_exam'		: 5,
    'evaluation_oral'		: 6


}

event_moda_list = ['none',
		    'lesson_elearning', 'lesson_classroom', 'lesson_practice',
		    'evaluation_practice', 'evaluation_exam', 'evaluation_oral']

class Event(object):

	def init_graphics(self):
		from ComboMgmt import ComboMgmt
		from GtkMapper import GtkMapper

		from User import User
		from Course import Course

		GtkMapper('graphics/dialog_event.glade', self, app.debug)

		def query_user(db, empty_data):
			return db.session.query(User).all()

		def query_classroom(db, empty_data):
			return db.session.query(ClassRoom).all()

		def query_course(db, empty_data):
			return db.session.query(Course).all()

		self.dialog.valid_event.set_sensitive(False)

		userstore = []
		classroomstore = []
		if self.planning.type_campus:
			self.dialog.line_private_event.obj.hide()
			self.dialog.line_modality.obj.hide()
			self.dialog.line_course.obj.hide()
			classroomstore = db.session_query(query_classroom, None,
			    "events : query(ClassRoom).all()")
			self.allow_classroom = True
			userstore = db.session_query(query_user, None,
			    "events : query(User).all()")
			self.classroom_combo = ComboMgmt(self.dialog.line_classroom.classroom, classroomstore, self.classroom, None)
			self.teacher_combo = ComboMgmt(self.dialog.line_teacher_name.teacher_name, userstore, self.teacher, self.teacher_name)

		if self.planning.type_class:
			self.dialog.line_private_event.obj.hide()
			classroomstore = db.session_query(query_classroom, None,
			    "events : query(ClassRoom).all()")
			self.allow_classroom = True
			userstore = db.session_query(query_user, None,
			    "events : query(User).all()")
			courses = db.session_query(query_course, None,
			    "events : query(Course).all()")
			'''course_store = gtk.ListStore(str, object)
			for course in courses:
				course_store.append([course.name, course])
			self.dialog.line_course.course.set_model(course_store)'''
			self.course_combo = ComboMgmt(self.dialog.line_course.course, courses, self.course, None)
			self.classroom_combo = ComboMgmt(self.dialog.line_classroom.classroom, classroomstore, self.classroom, None)
			self.teacher_combo = ComboMgmt(self.dialog.line_teacher_name.teacher_name, userstore, self.teacher, self.teacher_name)

		if self.planning.type_period:
			self.dialog.line_classroom.obj.hide()
			self.dialog.line_private_event.obj.hide()
			courses = db.session_query(query_course, None,
			    "events : query(Course).all()")
			userstore = db.session_query(query_user, None,
			    "events : query(User).all()")
			self.course_combo = ComboMgmt(self.dialog.line_course.course, courses, self.course, None)
			self.teacher_combo = ComboMgmt(self.dialog.line_teacher_name.teacher_name, userstore, self.teacher, self.teacher_name)

		if self.planning.type_user:
			self.dialog.line_private_event.private_event.set_active(1)
			self.dialog.line_required_event.obj.hide()
			self.dialog.line_teacher_name.obj.hide()
			self.dialog.line_modality.obj.hide()
			self.dialog.line_classroom.obj.hide()
			self.dialog.line_course.obj.hide()

		self.dialog_confirmation = gtk.MessageDialog(None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		    gtk.MESSAGE_QUESTION,
		    gtk.BUTTONS_OK_CANCEL,
		    None)
		return

	def add_event(self):
		"""initialize fields and call dialog_event"""

		self.init_graphics()
		self.dialog.delete_event.hide()
		self.dialog.valid_event.connect("clicked", self.on_add_event_clicked)
		self.dialog.line_private_event.private_event.set_active(0)
		self.dialog.line_required_event.required_event.set_active(1)
		self.dialog.line_modality.modality.set_active(0)
		self.popup_calendar.calendar.select_day(date.today().day)
		self.popup_calendar.calendar.select_month(date.today().month-1 , date.today().year)
		self.year, self.month, self.day = self.popup_calendar.calendar.get_date()
		d = date(self.year, self.month+1, self.day)
		self.dialog.line_date.date.set_text(d.strftime('%A %d %B %Y').title())
		self.dialog.line_time.time_hour.set_value(7)
		self.dialog.line_time_length.time_length.set_value(1)

		result = self.dialog.obj.run()
		self.dialog.obj.destroy()
		return result

	def change_event(self):
		"""get fields of selected event and fills dialog fields,
		   call dialog_event"""

		self.init_graphics()

		res = re.split("[- :]", str(self.datetime))
		year, month, day, hour, minute, sec = res

		self.dialog.line_name.name.set_text(self.name)
		if(self.description != None):
			buffer = self.dialog.line_description.description.get_buffer()
			buffer.set_text(self.description)
		d = date(int(year), int(month), int(day))
		self.dialog.line_date.date.set_text(d.strftime('%A %d %B %Y').title())
		self.popup_calendar.calendar.select_day(int(day))
		self.popup_calendar.calendar.select_month(int(month)-1, int(year))
		self.dialog.line_time.time_hour.set_value(int(hour))
		self.dialog.line_time.time_minute.set_value(int(minute))
		self.dialog.line_time_length.time_length.set_value(self.time_length)

		self.dialog.line_private_event.private_event.set_active(not self.private_event)
		self.dialog.line_required_event.required_event.set_active(not self.required_event)
		if self.modality:
			self.dialog.line_modality.modality.set_active(event_moda_db[self.modality])
		else:
			self.dialog.line_modality.modality.set_active(0)

		self.dialog.obj.set_title("Modification d'évènement")
		self.dialog.valid_event.connect("clicked", self.on_change_event_clicked)
		result = self.dialog.obj.run()
		if result == 0:
			self.dialog.obj.destroy()
			self.change_event()
			return result
		else:
			self.dialog.obj.destroy()
			return result

	def duplicate_event(self):
		"""get fields of a copy of selected event (it's not the
		 same object) and fills dialog fields, call dialog_event"""

		self.init_graphics()

		res = re.split("[- :]", str(self.datetime))
		year, month, day, hour, minute, sec = res

		self.dialog.line_name.name.set_text(self.name)
		if(self.description != None):
			buffer = self.dialog.line_description.description.get_buffer()
			buffer.set_text(self.description)
		d = date(int(year), int(month), int(day))
		self.dialog.line_date.date.set_text(d.strftime('%A %d %B %Y').title())
		self.popup_calendar.calendar.select_day(int(day))
		self.popup_calendar.calendar.select_month(int(month)-1, int(year))
		self.dialog.line_time.time_hour.set_value(int(hour))
		self.dialog.line_time.time_minute.set_value(int(minute))
		self.dialog.line_time_length.time_length.set_value(self.time_length)

		self.dialog.line_private_event.private_event.set_active(not self.private_event)
		self.dialog.line_required_event.required_event.set_active(not self.required_event)
		if self.modality:
			self.dialog.line_modality.modality.set_active(event_moda_db[self.modality])
		else:
			self.dialog.line_modality.modality.set_active(0)

		self.dialog.obj.set_title("Duplication d'évènement")
		self.dialog.delete_event.hide()
		self.dialog.valid_event.connect("clicked", self.on_add_event_clicked)
		result = self.dialog.obj.run()
		self.dialog.obj.destroy()
		return result

	def get_dialog_fields(self):
		"""fills the event's fields with the dialog_event's
		   fields"""

		self.name = self.dialog.line_name.name.get_text()
		buffer = self.dialog.line_description.description.get_buffer()
		start_iter, end_iter = buffer.get_bounds()
		self.description = buffer.get_text(start_iter, end_iter)
		self.year, self.month, self.day = self.popup_calendar.calendar.get_date()
		self.hour = self.dialog.line_time.time_hour.get_value()
		self.minute = self.dialog.line_time.time_minute.get_value()

		self.datetime = datetime(self.year, self.month+1, self.day, int(self.hour), int(self.minute))

		self.time_length = self.dialog.line_time_length.time_length.get_value()
		if self.dialog.line_teacher_name.obj.get_property('visible'):
			self.teacher = self.teacher_combo.get_selected_object()
			self.teacher_name = self.dialog.line_teacher_name.teacher_name.get_active_text()
		if not self.teacher:
			self.teacher_id = 0
		if self.dialog.line_classroom.obj.get_property('visible'):
			self.classroom = self.classroom_combo.get_selected_object()
			if not self.classroom and self.allow_classroom:
				self.classroom = ClassRoom()
				if self.planning.type_campus:
					self.classroom.campus = self.planning.type_campus
					self.classroom.name = self.dialog.line_classroom.classroom.get_active_text()
					db.session.add(self.classroom)

				elif self.planning.type_class:
					self.classroom.campus = self.planning.type_class.campus
					self.classroom.name = self.dialog.line_classroom.classroom.get_active_text()
					db.session.add(self.classroom)
		if not self.classroom:
			self.id_classroom = 0

		#parcours de self.classroom.events pour verification d'aucun evenement sur la meme plage horaire

		if self.dialog.line_required_event.obj.get_property('visible'):
			required_event = self.dialog.line_required_event.required_event.get_active_text().lower()
			if required_event == "oui":
				self.required_event = True
			else:
				self.required_event = False
		else:
			self.required_event = False
		if self.dialog.line_private_event.obj.get_property('visible'):
			private_event = self.dialog.line_private_event.private_event.get_active_text().lower()
			if private_event == "oui":
				self.private_event = True
			else:
				self.private_event = False
		else:
			self.private_event = False
		if self.dialog.line_modality.obj.get_property('visible'):
			self.modality = event_moda_list[event_moda_disp[self.dialog.line_modality.modality.get_active_text()]]
		else:
			self.modality = 'none'
		if self.dialog.line_course.obj.get_property('visible'):
			self.course = self.course_combo.get_selected_object()

	def place_popup(self):
		dialog_alloc = self.dialog.obj.get_position()
		entry_alloc = self.dialog.line_date.date.get_allocation()
		# XXX : offset tout moche a fix
		popup_x = dialog_alloc[0] + entry_alloc.x + 5
		popup_y = dialog_alloc[1] + entry_alloc.y + 50
		self.popup_calendar.obj.move(popup_x, popup_y)
		self.popup_calendar.obj.set_keep_above(True)

	def cb_tooltip(self):
		title_color_class = ''
		if self.required_event:
			title_color_class = ' required_event'
		html =	str("<table class='event_tooltip' cellspacing='0'>"+
						"<tr class='tooltip_tr'>"+
							"<td colspan='2' class='title_cont"+title_color_class+"'>"+self.name+"</td>"+
						"</tr>");
		if (self.txt_type != None):
			if self.planning.type_user:
				color = "#fc0"
			elif self.planning.type_class:
				color = "#36c"
			elif self.planning.type_campus:
				color = "#0b0"
			elif self.planning.type_period:
				color = "#a08"
			elif self.planning.id == app.university.id_planning:
				color = "#d20"
			html += str("<tr class='tooltip_tr'>"+
							"<td colspan='2' class='type_cont' style='font-weight: bold; color: "+color+";'>Planning de type "+self.txt_type+"</td>"+
						"</tr>")
		html += str("<tr class='tooltip_tr'>"+
							"<td>Date</td>"+
							"<td class='date_container'><dateXXX>"+self.datetime.strftime('%A %d %B %Y,<br />%H:%M:%S').title()+"</dateXXX></td>"+
						"</tr>")
		if (self.description != None):
			html +=	str("<tr class='tooltip_tr'>"+
							"<td>Description</td>"+
							"<td>"+str(self.description.replace('\r\n', '<br />').replace('\n', '<br />'))+"</td>"+
						"</tr>")
		if (self.teacher_name != None):
			html +=	str("<tr class='tooltip_tr'>"+
							"<td>Encadrant</td>"+
							"<td>"+str(self.teacher_name)+"</td>"+
						"</tr>")
		if (self.classroom != None):
			html +=	str("<tr class='tooltip_tr'>"+
							"<td>Salle</td>"+
							"<td>"+str(self.classroom.name)+"</td>"+
						"</tr>")
			html +=	str("</table>")
		return html

	# callbacks :
	def on_modality_changed(self, widget):
		"""if a modality is define, unlock the course choice"""

		if event_moda_disp[self.dialog.line_modality.modality.get_active_text()] != 0:
			self.dialog.line_course.course.set_sensitive(True)
		else:
			self.dialog.line_course.course.set_sensitive(False)

	def on_name_changed(self,widget):
		"""if a name is define, unlock validate button"""

		if self.dialog.line_name.name.get_text()!= "":
			self.dialog.valid_event.set_sensitive(True)
		else:
			self.dialog.valid_event.set_sensitive(False)

	def on_cancel_event_clicked(self, widget):
		"""close the dialog_event"""

		self.dialog.obj.response(gtk.RESPONSE_CANCEL)

	def on_date_focus(self, widget, direction=None, data=None):
		"""on fields date focus, show the calendar widget"""

		self.place_popup()
		self.popup_calendar.obj.show()

	def on_popup_calendar_unfocus(self, widget, direction=None, data=None):
		"""on calendar unfocus, hide the calendar"""

		self.popup_calendar.obj.hide()

	def on_date_icon_press(self, widget, direction=None, data=None):
		"""on date icon click, show the calendar widget"""

		self.place_popup()
		self.popup_calendar.obj.show()

	def on_calendar_day_selected_double_click(self, widget):
		"""on day double click on calendar, fill the field date
		 with selected date parse in strftime format, hide
		 calendar"""

		year, month, day = widget.get_date()
		d = date(year, month+1, day)
		self.dialog.line_date.date.set_text(d.strftime('%A %d %B %Y').title())
		self.popup_calendar.obj.hide()

	def on_add_event_clicked(self, widget):
		"""call get_dialog_fields, add the object in session and
		 call db.session_try_commit, return gtk.RESPONSE_OK"""

		self.get_dialog_fields()
		db.session.add(self)
		db.session_try_commit()
		self.dialog.obj.response(gtk.RESPONSE_OK)

	def on_change_event_clicked(self, widget):
		"""call get_dialog_fields, call db.session_try_commit,
		return gtk.RESPONSE_OK"""

		self.get_dialog_fields()
		db.session_try_commit()
		self.dialog.obj.response(gtk.RESPONSE_OK)

	def on_delete_event_clicked(self, widget):
		"""open the dialog_confirmation, if this response is
		 gtk.RESPONSE_OK: delete object in session, call
		 db.session_try_commit else hide dialog_confirmation"""

		self.dialog_confirmation.set_markup("Etes vous sûre de vouloir supprimer l'événement " + self.name + " ?")
		if self.dialog_confirmation.run() == gtk.RESPONSE_OK:
			db.session.delete(self)
			db.session_try_commit()
			self.dialog.obj.response(gtk.RESPONSE_OK)
		self.dialog_confirmation.hide()

	def on_time_hour_value_changed(self,widget):
		if  self.dialog.line_time.time_minute.get_value() > 0:
			self.dialog.line_time_length.time_length.set_range (1, 20- self.dialog.line_time.time_hour.get_value())
			self.dialog.line_time.time_hour.set_range(7,19)
		else:
			self.dialog.line_time_length.time_length.set_range (1, 21- self.dialog.line_time.time_hour.get_value())
			self.dialog.line_time.time_hour.set_range(7,20)

	def on_time_minute_changed(self,widget):
		if  self.dialog.line_time.time_minute.get_value() > 0:
			self.dialog.line_time_length.time_length.set_range (1, 20- self.dialog.line_time.time_hour.get_value())
			self.dialog.line_time.time_hour.set_range(7,19)


		else:
			self.dialog.line_time_length.time_length.set_range (1, 21- self.dialog.line_time.time_hour.get_value())
			self.dialog.line_time.time_hour.set_range(7,20)

	# db_fill callback
	def cb_fill(self, number):
		"""callback for fill the db"""

		def fill_insert(event, i, number):
			import Event
			if Event.fill_time.hour >= 18 or i == 0:
				#print "time go out of day range : " + str(Event.fill_time.hour) + " >= 19"
				#print "fill_date actual : " + str(Event.fill_date)
				if event.planning.type_univ:
					Event.fill_date += timedelta(
					    days = randint(7, 28))
				elif event.planning.type_period and not event.course:
					Event.fill_date += timedelta(
					    days = randint(7, 28))
				elif event.planning.type_campus:
					Event.fill_date += timedelta(
					    days = randint(7, 14))
				elif event.planning.type_class and not event.course:
					Event.fill_date += timedelta(
					    days = randint(7, 28))
				elif event.planning.type_user:
					Event.fill_date += timedelta(
					    days = randint(3, 6))
				wd = Event.fill_date.weekday()
				if event.course and wd > 3:
					delta = timedelta(days = 7 - wd)
				elif wd == 5:
					delta = timedelta(days = 2)
				else:
					delta = timedelta(days = 1)
				Event.fill_date += delta
				Event.fill_time = time(7, 00)

			#print "fill_time before : " + str(Event.fill_time)
			#print "fill_date before : " + str(Event.fill_date)

			event.name = "Event"+str(i)
			event.description = "description"
			event.modality = 'none'
			if event.course:
				event_rest = number - i
				event.required_event = True
				event.time_length = 2
				if event.planning.type_period:
					event.modality = 'evaluation_exam'
				elif event.course.e_practice > (event_rest * 2):
					event.modality = 'evaluation_practice'
					if event.course.e_oral_rest == 1:
						event.time_length = 1
					event.course.e_oral_rest -= event.time_length
				elif ((event.course.e_practice +
				    event.course.e_oral) > (event_rest * 2)):
					event.modality = 'evaluation_oral'
					if event.course.e_oral_rest == 1:
						event.time_length = 1
					event.course.e_oral_rest -= event.time_length
				else:
					modalities = []
					if (event.course.c_elearning_rest > 0):
						modalities.append('lesson_elearning')
					if (event.course.c_classroom_rest > 0):
						modalities.append('lesson_classroom')
					if (event.course.c_practice_rest > 0):
						modalities.append('lesson_practice')
					l = len(modalities)
					if l:
						event.modality = modalities[
						    randint(0, l - 1)]
					else:
						event.modality = 'lesson_practice'
					if event.modality == 'lesson_elearning':
						if event.course.c_elearning_rest == 1:
							event.time_length = 1
						event.course.c_elearning_rest -= event.time_length
					elif event.modality == 'lesson_classroom':
						if event.course.c_classroom_rest == 1:
							event.time_length = 1
						event.course.c_classroom_rest -= event.time_length
					elif event.modality == 'lesson_practice':
						if event.course.c_practice_rest == 1:
							event.time_length = 1
						event.course.c_practice_rest -= event.time_length
				#print "fill beetween 9-13 and 14-20"
				h = Event.fill_time.hour
				if h < 9:
					Event.fill_time = time(9, 00)
				elif (h + event.time_length) > 13 and h < 14:
					Event.fill_time = time(14, 00)
			else:
				#print "fill an event in the rest of the space"
				h = Event.fill_time.hour
				#print "from " + str(h) + " to 19"
				Event.fill_time = time(randint(h, 19), 00)
				h = Event.fill_time.hour
				#print "find one at " + str(h)
				event.time_length = (randint(1, 20 - h) % 4) + 1
				if not i % 2:
					event.required_event = True
				else:
					event.required_event = False


			if event.planning.type_user:
				if not i % 2:
					event.private_event = True
				else:
					event.private_event = False
			else:
				event.private_event = False

			result = datetime.combine(Event.fill_date, Event.fill_time)
			event.datetime = result

			Event.fill_time = time(Event.fill_time.hour + event.time_length, 00)

			db.session.add(event)

			if app.verbose:
				print str("fill event : (" +
				    str(event.datetime) + ", " +
				    str(event.time_length) + ")")
			#print "fill_time after : " + str(Event.fill_time)
			#print "fill_date after : " + str(Event.fill_date)

		for i in range(number - 1):
			event = Event()
			event.planning = self.planning
			event.course = self.course
			fill_insert(event, i, number - 1)
		i = number - 1
		fill_insert(self, i, i)

def init():
	"""define table event and mapping"""

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper
	# Dependencies
	from User import User
	from Course import Course
	from Planning import Planning
	from ClassRoom import ClassRoom

	t_event = Table('event', db.metadata,
		Column('id',					types.Integer,
			Sequence('event_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),

		Column('name',					types.VARCHAR(255),
			nullable	= False),

		Column('description',				types.TEXT(2000)),

		Column('start',					types.DateTime(),
			nullable	= False),

		Column('time',					types.Integer,
			nullable	= False),

		Column('name_teacher',				types.VARCHAR(255)),

		Column('id_teacher',				types.Integer,
			ForeignKey('user.id')),

		Column('id_classroom',				types.Integer,
			ForeignKey('classroom.id')),

		Column('modality',				types.Enum('none',
			    'lesson_elearning', 'lesson_classroom', 'lesson_practice',
			    'evaluation_practice', 'evaluation_exam', 'evaluation_oral'),
			nullable	= False),

		Column('id_course',				types.Integer,
			ForeignKey('course.id')),

		Column('mandatory',				types.Integer,
			nullable	= False),

		Column('private',				types.Integer,
			nullable	= False),

		Column('id_planning',				types.Integer,
			ForeignKey('planning.id'),
			nullable	= False),

		Column('added',					types.DateTime(),
			default		= datetime.now,
			nullable	= False),

		Column('modified',				types.DateTime(),
			default		= datetime.now,
			onupdate	= datetime.now,
			nullable	= False),
	)

	mapper(Event, t_event, properties = {
		'datetime'		: t_event.c.start,
		'time_length'		: t_event.c.time,
		'teacher_id'		: t_event.c.id_teacher,
		'teacher_name'		: t_event.c.name_teacher,
		'required_event'	: t_event.c.mandatory,
		'private_event'		: t_event.c.private,

		'classroom'		: relationship(ClassRoom, backref='events'),

		'course'		: relationship(Course, backref = 'events'),

		'planning'		: relationship(Planning, backref = 'events'),

		'teacher'		: relationship(User, backref = 'events'),
	})
