# -*- coding: utf-8 -*-
import gtk
import webkit
from dateutil.relativedelta import *

import sys
import os
import re
import datetime
import json
import urllib
from time import mktime

from db import db
from Timetableasy import app

# view mode: enum like
VIEW_MODE_DAY, VIEW_MODE_WEEK, VIEW_MODE_MONTH = range(3)

# view mode 2 fullcalendar mode
planning_view_mod = {
    VIEW_MODE_DAY	: 'agendaDay',
    VIEW_MODE_WEEK	: 'agendaWeek',
    VIEW_MODE_MONTH	: 'month',
}

class Planning(object):

	def clean(self, gui):
		self.browser = None
		self.view.destroy()
		self.menu.destroy()

	def display(self, gui):
		"""display the planning and set is title with the name
		 of the owner (class X, campus X, user X, manager X ...)
		 get gtk object, initialize button..."""

		from GtkMapper import GtkMapper

		if gui.tabs_is_displayed(self):
			gui.tabs_go_to(self)
			return

		# - set up internal var
		self.refresh = True
		self.finish = False
		file = os.path.abspath('graphics/fullcalendar/view.html')
		self.uri = 'file:' + urllib.pathname2url(file)
		self.display_univ = False
		self.display_campus = False
		self.display_class = False
		self.display_period = False
		self.view_mode = VIEW_MODE_WEEK
		self.date = datetime.date.today()
		self.planning_stack = [self.id]

		# - generate description and title
		if self.type_user:
			if self.type_user.login == app.user.login:
				# current user planning
				self.title = "Mon planning"
			elif self.type_user.type == 'student':
				self.title = str("Etudiant " +
				    self.type_user.login)
			elif self.type_user.type == 'manager':
				self.title = str("Manager " +
				    self.type_user.login)
			elif self.type_user.type == 'admin':
				self.title = str("Administrateur " +
				    self.type_user.login)
			elif self.type_user.type == 'teacher':
				self.title = str("Enseignant " +
				    self.type_user.login)
			self.description = str("Planning de " +
			    self.type_user.firstname + " " +
			    self.type_user.name)
			if self.type_user.student_class:
				student_class = self.type_user.student_class
				campus = student_class.campus
				self.description += str("\nClasse " +
				    student_class.name)
				self.description += str("\nCampus " +
				    campus.name)

		elif self.type_class:
			self.title = "Classe " + self.type_class.name
			self.description = str("Planning de la classe " +
			    self.type_class.name)
			self.description += str("\nCampus " +
			    self.type_class.campus.name)
		elif self.type_campus:
			self.title = "Campus " + self.type_campus.name
			self.description = str("Planning du campus " +
			    self.type_campus.name)
		elif self.type_period:
			self.title = "Période " + self.type_period.name
			self.description = str("Planning de la période " +
			    self.type_period.name)
		elif self.type_univ:
			self.title = "Université " + self.type_univ.name
			self.description = str("Planning de l'université " +
			    self.type_univ.name)
		else:
			# should never happen
			print 'unknow planning'
			self.title = "Planning"
			self.description = str("Planning inconnu")

		# - set up gui component
		mapper = GtkMapper('graphics/view_planning.glade', self, app.debug)
		# - set up view gui
		self.toolbar.description.set_text(self.description)
		self.update_date()
		# - set up menu_top gui
		self.calendar.select_month(self.date.month - 1, self.date.year)
		self.calendar.select_day(self.date.day)
		self.calendar.mark_day(self.date.day)
		# - set up html browser with fullcalendar
		self.browser = webkit.WebView()
		self.fullcalendar.add(self.browser)
		self.browser.connect('resource-request-starting', \
		    self.resource_request_starting, self)
		self.browser.connect('load-finished', self.load_finished)
		self.browser.connect('title-changed', self.title_changed)
		self.browser.connect('button_press_event', self.button_click)
		self.browser.open(self.uri)
		# - call gui to add widgets,
		gui.tabs_create(self.title, self)
		# - init planning merge
		self.planning_parent = {}
		self.get_planning(self.planning_parent, False)
		self.cb_check_opt_availability()

	def execute(self, script):
		"""execute a js script in planning view"""

		# XXX status version : bug in python-webkit on enum type
		#status = self.browser.get_property('load-status')
		#if status == webkit.LOAD_FIRST_VISUALLY_NON_EMPTY_LAYOUT or \
		#    status == webkit.LOAD_FINISHED:
		#	self.browser.execute_script(script)
		if self.finish:
			print "execute script : \n\n" + str(script)
			self.browser.execute_script(script)
		else:
			print "cannot execute : load not finished"
			print "script : \n\n" + str(script)

	def menu_context_popup(self, event, duplicate_event = False):
		"""call the right click menu on planning, hide duplicate
		 and delete if not rights"""

		self.popmenu.obj.show_all()
		if duplicate_event == False:
			self.popmenu.duplicate.hide()
			self.popmenu.delete.hide()
		self.popmenu.obj.popup(None, None, None, event.button,
		    event.time)

	def cb_check_opt_availability(self):
		"""check the user's rights for disable event's add if
		 not rights and hide the opt buttons(class, campus...)
		 for disable merge depending on planning's type"""

		self.opt_class.show()
		self.opt_period.show()
		self.opt_campus.show()
		self.opt_univ.show()

		if self.type_class:
			if self.check_rights("class", (self.type_class.campus.id, self.type_class.id)) == False:
				self.add_event.hide()
			self.opt_class.hide()
		elif self.type_campus:
			if self.check_rights("campus", self.type_campus.id) == False:
				self.add_event.hide()
			self.opt_class.hide()
			self.opt_campus.hide()
			self.opt_period.hide()
		elif self.type_univ:
			if self.check_rights("univ") == False:
				self.add_event.hide()
			self.opt_class.hide()
			self.opt_campus.hide()
			self.opt_univ.hide()
			self.opt_period.hide()
		elif self.type_period:
			if self.check_rights("period") == False:
				self.add_event.hide()
			self.opt_class.hide()
			self.opt_campus.hide()
			self.opt_period.hide()
		elif self.type_user:
			if self.check_rights("user", self.id) == False:
				self.add_event.hide()
			if self.type_user.is_admin():
				if len(self.type_user.campus) == 0:
					self.opt_campus.hide()
				if len(self.type_user.manager_class) == 0 and self.type_user.student_class:
					self.opt_class.hide()
			if self.type_user.is_manager():
				if len(self.type_user.campus) == 0:
					self.opt_campus.hide()
				if len(self.type_user.manager_class) == 0 and self.type_user.student_class:
					self.opt_class.hide()
			elif self.type_user.is_student():
				if self.type_user.student_class == None:
					self.opt_class.hide()
				if (self.type_user.student_class != None and self.type_user.student_class.id_campus == None):
					self.opt_campus.hide()
			if len(self.type_user.cursus) == 0:
				self.opt_period.hide()

	def refresh_events(self):
		"""Refresh planning's view"""

		print "REFRESH"
		# XXX hack for FullCalendar eventsrefetch bug
		#self.refresh = True
		#self.browser.reload()
		script = "$('#calendar').fullCalendar('refetchEvents')"
		self.execute(script)

	def events2json(self, start, end):
		"""get all events attached to this planning, return events
		 in json format"""

		from Event import Event

		start = datetime.datetime.fromtimestamp(float(start))
		end = datetime.datetime.fromtimestamp(float(end))

		events = self.get_event(start, end)

		fullcalendar_events = []
		if events:
			for list in events:
				if list != None:
					for event in list :
						delta = relativedelta(hours = event.time_length)
						event.end = event.datetime + delta
						editable = False
						classname = ""
						if event.planning.type_user:
							event.txt_type = "Utilisateur"
							classname = "fc-user"
							if self.check_rights("user", event.id_planning) == True:
								editable = True
						elif event.planning.type_class:
							event.txt_type = "Classe"
							classname = "fc-class"
							if self.check_rights("class", (event.planning.type_class.campus.id, event.planning.type_class.id)) == True:
								editable = True
						elif event.planning.type_campus:
							event.txt_type = "Campus"
							classname = "fc-campus"
							if self.check_rights("campus", event.planning.type_campus.id) == True:
								editable = True
						elif event.planning.type_period:
							event.txt_type = "Période"
							classname = "fc-period"
							if self.check_rights("period") == True:
								editable = True
						elif event.planning.id == app.university.id_planning:
							event.txt_type = "Université"
							classname = "fc-univ"
							if self.check_rights("univ") == True:
								editable = True
						else:
							event.txt_type = "Autre"
						if event.required_event:
							classname = classname + " fc-mandatory"

						fullcalendar_event = {
						    'title'	: event.name,
						    'start'	: int(mktime(event.datetime.timetuple())),
						    'end'	: int(mktime(event.end.timetuple())),
						    'allDay'	: False,
						    'id'	: event.id,
						    'className'	: classname,
						    'editable' : editable,
						    'tipsy' : event.cb_tooltip(),
						    'fdate' : event.datetime.strftime('%A %d %B %Y,<br />%H:%M:%S').title()
						}

						fullcalendar_events.append(fullcalendar_event)
		# XXX print (json.dumps(fullcalendar_events))
		return json.dumps(fullcalendar_events)

	def update_date(self):
		"""change date's display depending on view_mode (month,
		 week, day) on the planning"""

		if self.view_mode == VIEW_MODE_DAY:
			self.toolbar.date.set_text(self.date.strftime('%A %d %B %Y'))
		if self.view_mode == VIEW_MODE_WEEK:
			delta = relativedelta(days=6-self.date.weekday())
			end = self.date + delta
			delta = relativedelta(days=-self.date.weekday())
			start = self.date + delta
			text = start.strftime('%d ')
			if start.month != end.month:
				text += start.strftime('%b ')
			if start.year != end.year:
				text += start.strftime('%Y ')
			text += '- '
			text += end.strftime('%d %b %Y')
			self.toolbar.date.set_text(text)
		if self.view_mode == VIEW_MODE_MONTH:
			self.toolbar.date.set_text(self.date.strftime('%B %Y'))

	# browser callback:
	def title_changed(self, view, frame, title):
		"""manage action on planning view, resize event, right
		click, drop and click event... """

		from Event import Event

		def query(db, id):
			"""callback for db.session_query, this query
			 event in terms of this id"""

			return db.session.query(Event).get(id)

		print "title change : %s" % title
		if title == "none":
			return
		# list event
		data = re.search('/signal/events/.*\?.*start=(.*)&end=(.*).*', title)
		if data:
			start = data.group(1)
			end = data.group(2)
			events = "$('#events').text('%s')" % \
			    self.events2json(start, end).replace("'", "\\'")
			self.browser.execute_script(events)
		# create event
		data = re.search('/signal/events-create/.*\?.*start=(.*)&end=(.*).*', title)
		if data:
			start = data.group(1)
			end = data.group(2)
			# XXX create event
			self.refresh_events()
		# resize event
		data = re.search('/signal/event-resize/.*\?.*minutedelta=(.*)&id=(.*)', title)
		if data:
			minutedelta = data.group(1)
			id = data.group(2)
			event = db.session_query(query, id,
			    "planning : query(Event).get(" + str(id) + ")")
			event.time_length += int(minutedelta)/60
			db.session_try_commit()
		# drop event
		data = re.search('/signal/event-drop/.*\?.*daydelta=(.*)&minutedelta=(.*)&id=(.*)', title)
		if data:
			daydelta = data.group(1)
			minutedelta = data.group(2)
			id = data.group(3)
			event = db.session_query(query, id,
			    "planning : query(Event).get(" + str(id) + ")")
			delta = relativedelta(days=int(daydelta), minutes=int(minutedelta))
			event.datetime += delta
			db.session_try_commit()
		# click event
		data = re.search('/signal/event-click/.*\?.*id=(.*)', title)
		if data:
			id = data.group(1)
			event = db.session_query(query, id,
			    "planning : query(Event).get(" + str(id) + ")")
			editable_event = False
			if event.planning.type_user and self.check_rights("user", event.id_planning) == True:
				editable_event = True
			elif event.planning.type_class and self.check_rights("class", (event.planning.type_class.campus.id, event.planning.type_class.id)) == True:
				editable_event = True
			elif event.planning.type_campus and self.check_rights("campus", event.planning.type_campus.id) == True:
				editable_event = True
			elif event.planning.type_period and self.check_rights("period") == True:
				editable_event = True
			elif self.check_rights("univ") == True:
				editable_event = True
			if editable_event:
				if event.change_event() == gtk.RESPONSE_OK:
					self.refresh_events()
		# right click event
		data = re.search('/signal/event-right-click/.*\?.*id=(.*)', title)
		if data:
			id = data.group(1)
			self.clicked_event = db.session_query(query, id,
			    "planning : query(Event).get(" + str(id) + ")")
			duplicate_event = False
			if self.clicked_event.planning.type_user and self.check_rights("user", self.clicked_event.id_planning) == True:
				duplicate_event = True
			elif self.clicked_event.planning.type_class and self.check_rights("class", (self.clicked_event.planning.type_class.campus.id, self.clicked_event.planning.type_class.id)) == True:
				duplicate_event = True
			elif self.clicked_event.planning.type_campus and self.check_rights("campus", self.clicked_event.planning.type_campus.id) == True:
				duplicate_event = True
			elif self.clicked_event.planning.type_period and self.check_rights("period") == True:
				duplicate_event = True
			elif self.check_rights("univ") == True:
				duplicate_event = True
			print 'right clic event'
			self.menu_context_popup(self.last_event, duplicate_event)
		# right click day
		data = re.search('/signal/day-right-click/.*\?.*date=(.*)', title)
		if data:
			date = data.group(1)
			print 'right clic day' + date
			self.menu_context_popup(self.last_event)

	def resource_request_starting(self, view, frame, resource, request, response, planning):
		"""Check if requested resource matches allowed : file:// """

		url = request.get_uri()
		message = request.get_property("message")
		if not message:
			return
		method = message.get_property("method")
		e = re.search('(.*):/{2,}.*', url)
		# block external request
		if not e or not e.group(1) == 'file':
			print "%s not support: != 'file'" % e.group(1)
			request.set_uri("about:blank")
			return

	def load_finished(self, web_view, web_frame):
		"""change the theme and unlock js script in execut()"""

		self.finish = True
		self.change_theme(app.settings.planning_theme)

	def button_click(self, widget, event):
		#XXX what to do with this ?
		"""comment none implemented"""

		if event.button == 3:
			self.last_event = event

	# view callbacks :
	def cb_duplicate(self, button):
		"""create a new event with the selected event's model,
		 for more rapidity with similar events"""

		event = db.copy(self.clicked_event)
		event.planning = self.clicked_event.planning
		event.classroom = self.clicked_event.classroom
		event.course = self.clicked_event.course
		event.teacher = self.clicked_event.teacher
		db.session.expunge(self.clicked_event)
		if event.duplicate_event() == gtk.RESPONSE_OK:
			self.refresh_events()
		self.clicked_event = None

	def cb_delete(self, button):
		"""shortcut for delete event on righ_click on this"""

		event = self.clicked_event
		self.dialog_confirmation = gtk.MessageDialog(None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		    gtk.MESSAGE_QUESTION,
		    gtk.BUTTONS_OK_CANCEL,
		    None)
		self.dialog_confirmation.set_markup("Etes vous sûre de vouloir supprimer l'événement " + event.name + " ?")
		if self.dialog_confirmation.run() == gtk.RESPONSE_OK:
			db.session.delete(event)
			db.session_try_commit()
			self.refresh_events()
		self.dialog_confirmation.destroy()
		self.clicked_event = None

	def cb_refresh(self, button):
		"""force refresh of the view (in righ_click menu)"""

		self.refresh_events()

	def cb_print(self, button):
		"""call an impression of the current view"""

		script = """

		var view = $('#calendar').fullCalendar('getView');
		var subclass = '.fc-view-' + view.name + ' ';

		if(view.name != 'month' && $(subclass + '.fc-agenda-body tr').height() <= 50) {
			agenda_head_height = $(subclass + '.fc-agenda-head').height();
			agenda_body_overflow = $(subclass + '.fc-agenda-body').css('overflow');
			agenda_body_height = $(subclass + '.fc-agenda-body').height();
			calendar_height = $('#calendar').fullCalendar('option', 'height');

			$(subclass + '.fc-agenda-body').css('overflow', 'inherit').css('height', 'auto');
			target_height = $(subclass + '.fc-agenda-body').height() + agenda_head_height;
			$(subclass + '.fc-agenda-body').css('overflow', agenda_body_overflow).css('height', agenda_body_height);
			$('#calendar').fullCalendar('option', 'height', target_height);
		}

		window.print();

		if(view.name != 'month' && $(subclass + '.fc-agenda-body tr').height() <= 50)
			$('#calendar').fullCalendar('option', 'height', calendar_height);
		"""
		self.execute(script)

	def go_next(self, button):
		"""go to the next day/week/month (in toolbar and
		 righ_click menu)"""

		delta = {
		VIEW_MODE_DAY: lambda x: relativedelta(days=x),
		VIEW_MODE_WEEK: lambda x: relativedelta(weeks=x),
		VIEW_MODE_MONTH: lambda x: relativedelta(months=x),
		}[self.view_mode](+1)
		self.date += delta
		self.update_date()
		script = "$('#calendar').fullCalendar('next')";
		self.execute(script)
		self.calendar.select_month(self.date.month - 1, self.date.year)
		self.calendar.select_day(self.date.day)

	def go_prev(self, button):
		"""go to the previous day/week/month (in toolbar and
		 righ_click menu)"""

		delta = {
		VIEW_MODE_DAY: lambda x: relativedelta(days=x),
		VIEW_MODE_WEEK: lambda x: relativedelta(weeks=x),
		VIEW_MODE_MONTH: lambda x: relativedelta(months=x),
		}[self.view_mode](+1)
		self.date -= delta
		self.update_date()
		script = "$('#calendar').fullCalendar('prev')";
		self.execute(script)
		self.calendar.select_month(self.date.month - 1, self.date.year)
		self.calendar.select_day(self.date.day)

	def go_today(self, button):
		"""go to today (in toolbar and righ_click menu)"""

		self.date = datetime.date.today()
		self.update_date()
		script = "$('#calendar').fullCalendar('today')";
		self.execute(script)
		self.calendar.select_month(self.date.month - 1, self.date.year)
		self.calendar.select_day(self.date.day)

	def view_month(self, widget):
		"""change view display in month view"""

		if widget.get_active():
			if widget == self.toolbar.month:
				self.popmenu.month.set_active(True)
				self.view_mode = VIEW_MODE_MONTH
				script = "$('#calendar').fullCalendar('changeView', 'month')"
				self.execute(script)
				self.update_date()
			else:
				self.toolbar.month.set_active(True)

	def view_week(self, widget):
		"""change view display in week view"""

		if widget.get_active():
			if widget == self.toolbar.week:
				self.popmenu.week.set_active(True)
				self.view_mode = VIEW_MODE_WEEK
				script = "$('#calendar').fullCalendar('changeView', 'agendaWeek')"
				self.execute(script)
				self.update_date()
			else:
				self.toolbar.week.set_active(True)

	def view_day(self, widget):
		"""change view display in day view"""

		if widget.get_active():
			if widget == self.toolbar.day:
				self.popmenu.day.set_active(True)
				self.view_mode = VIEW_MODE_DAY
				script = "$('#calendar').fullCalendar('changeView', 'agendaDay')"
				self.execute(script)
				self.update_date()
			else:
				self.toolbar.day.set_active(True)

	# menu_top callbacks :
	def view_univ(self, button):
		"""display optional univ events also"""

		self.display_univ = not self.display_univ
		if (self.display_univ):
			self.planning_parent['univ'][1] = True
		else:
			self.planning_parent['univ'][1] = False
		script = "$('#calendar').fullCalendar('refetchEvents')"
		self.execute(script)

	def view_campus(self, button):
		"""display optional campus events also"""

		self.display_campus = not self.display_campus
		if (self.display_campus):
			self.planning_parent['campus'][1] = True
		else:
			self.planning_parent['campus'][1] = False
		script = "$('#calendar').fullCalendar('refetchEvents')"
		self.execute(script)

	def view_class(self, button):
		"""display optional class events also"""

		self.display_class = not self.display_class
		if (self.display_class):
			self.planning_parent['class'][1] = True
		else:
			self.planning_parent['class'][1] = False
		script = "$('#calendar').fullCalendar('refetchEvents')"
		self.execute(script)

	def view_period(self, button):
		"""display optional period events also"""

		self.display_period = not self.display_period
		if (self.display_period):
			self.planning_parent['period'][1] = True
		else:
			self.planning_parent['period'][1] = False
		script = "$('#calendar').fullCalendar('refetchEvents')"
		self.execute(script)

	def go_selected_day(self, calendar):
		"""go to the selected day in calendar (not change the
		 type of view, if month view, stay month view)"""

		year, month, day = calendar.get_date()
		self.date = datetime.date(year, month + 1, day)
		self.update_date()
		script = "$('#calendar').fullCalendar('gotoDate', %d, %d, %d)" \
		    % (self.date.year, self.date.month - 1, self.date.day)
		self.execute(script)

	def go_next_month(self, calendar):
		"""go to the next month in calendar (not change the
		 type of view, if month view, stay month view)"""

		self.date += relativedelta(months=+1)
		self.update_date()
		script = "$('#calendar').fullCalendar('incrementDate', 0, 1)";
		self.execute(script)

	def go_next_year(self, calendar):
		"""go to the next year in calendar (not change the
		 type of view, if month view, stay month view)"""

		self.date += relativedelta(years=+1)
		self.update_date()
		script = "$('#calendar').fullCalendar('nextYear')";
		self.execute(script)

	def go_previous_month(self, calendar):
		"""go to the previous month in calendar (not change the
		 type of view, if month view, stay month view)"""

		self.date += relativedelta(months=-1)
		self.update_date()
		script = "$('#calendar').fullCalendar('incrementDate', 0, -1)";
		self.execute(script)

	def go_previous_year(self, calendar):
		"""go to the previous month in calendar (not change the
		 type of view, if month view, stay month view)"""

		self.date += relativedelta(years=-1)
		self.update_date()
		script = "$('#calendar').fullCalendar('prevYear')";
		self.execute(script)

	def add_event(self, button):
		"""button for open add event dialog"""

		from Event import Event

		event = Event()
		event.planning = self
		if event.add_event() == gtk.RESPONSE_OK:
			self.refresh_events()
		else:
			event.planning = None

	def get_event(self, start  = None, end = None, all = False):
		"""use for get all events link to this planning and
		 the linked planning for merge"""

		from Event import Event
		from Timetableasy import app
		def query(db, id):
			"""callback for db.session_query, this query
			 event in plannings unless private = True"""

			if type(id) is tuple:
				return db.session.query(Event).filter(Event.id_planning.in_(id[0])).filter(Event.private_event==0).filter(Event.datetime>=id[1]).filter(Event.datetime<=id[2]).all()
			else:
				return db.session.query(Event).filter(Event.id_planning.in_(id)).filter(Event.private_event==0).all()
		def query_planning_user(db, id):
			"""callback for db.session_query, this query
			 event in user's planning"""

			if type(id) is tuple:
				return db.session.query(Event).filter(Event.id_planning == id[0]).filter(Event.datetime>=id[1]).filter(Event.datetime<=id[2]).all()
			else:
				return db.session.query(Event).filter(Event.id_planning==id).all()
		def query_required(db, id):
			"""callback for db.session_query, this query
			 event in plannings  where required  = True
			 unless private = True"""

			if type(id) is tuple:
				return db.session.query(Event).filter(Event.id_planning.in_(id[0])).filter(Event.private_event==0).filter(Event.required_event==1).filter(Event.datetime>=id[1]).filter(Event.datetime<=id[2]).all()
			else:
				return db.session.query(Event).filter(Event.id_planning.in_(id)).filter(Event.private_event==0).filter(Event.required_event==1).all()
		events = []
		for i in self.planning_parent:
			change_list = []
			if type(self.planning_parent[i][0]) is list:
				change_list = self.planning_parent[i][0]
			else:
				change_list.append(self.planning_parent[i][0])
			if self.planning_parent[i][0] and self.planning_parent[i][0] == app.user.id_planning:
				if start != None and end != None:
					events.append(db.session_query(query_planning_user, (self.planning_parent[i][0], start, end),
					    str("execute query to get Event "
					    "filter on Event.id_planning== "
				            + str(self.planning_parent[i][0]) + ").filter(Event.datetime>=id[1]).filter(Event.datetime<=id[2]).all()")))
				else:
					events.append(db.session_query(query_planning_user, self.planning_parent[i][0],
					    str("execute query to get Event "
					    "filter on Event.id_planning== "
				            + str(self.planning_parent[i][0]) + ").all()")))
			elif self.planning_parent[i][0] and (self.planning_parent[i][1] or all == True):
				if start != None and end != None:
					events.append(db.session_query(query, (change_list, start, end),
					    str("execute query to get Event filter "+
				            "on Event.id_planning.in_" + str(self.planning_parent[i][0]) + ").filter(Event.private_event==0).filter(Event.datetime>=id[1]).filter(Event.datetime<=id[2]).all()")))
				else:
					events.append(db.session_query(query, change_list,
					    str("execute query to get Event filter "+
				            "on Event.id_planning.in_" + str(self.planning_parent[i][0]) + ").filter(Event.private_event==0).all()")))
			elif self.planning_parent[i][0]:
				if start != None and end != None:
					events.append(db.session_query(query_required, (change_list, start, end),
					    str("execute query to get Event filter "+
				            "on Event.id_planning.in_" + str(self.planning_parent[i][0]) + ").filter(Event.private_event==0).filter(Event.required_event==1).filter(Event.datetime>=id[1]).filter(Event.datetime<=id[2]).all()")))
				else:
					events.append(db.session_query(query_required, change_list,
					    str("execute query to get Event filter "+
				            "on Event.id_planning.in_(" + str(self.planning_parent[i][0]) + ").filter(Event.private_event==0).filter(Event.required_event==1).all()")))
		return events

	def get_planning(self, liste, required):
		"""get all necessary plannings for display required event
		 and events to merge, depending on planning's type"""

		liste['self'] = [self.id, True]
		if app.university:
			liste['univ'] = [app.university.id_planning, required]
		else:
			liste['univ'] = [None, required]
		id = False
		if self.type_user:
			if self.type_user.is_manager() or self.type_user.is_admin():
				list_id = []
				if self.type_user.campus:
					for elem in self.type_user.campus:
						list_id.append(elem.id_planning)
				if self.type_user.manager_class:
					for elem in self.type_user.manager_class:
						list_id.append(elem.campus.id_planning)
				if self.type_user.student_class and self.type_user.student_class.campus:
					list_id.append(self.type_user.student_class.campus.id_planning)
				id = list_id
			elif (self.type_user.is_student() and self.type_user.student_class and self.type_user.student_class.campus):
				id = self.type_user.student_class.campus.id_planning
		elif (self.type_class and self.type_class.campus):
			id = self.type_class.campus.id_planning
		if (id):
			liste['campus'] = [id, required]
		else:
			liste['campus'] = [None, required]
		id = False
		if self.type_user:
			if self.type_user.is_manager() or self.type_user.is_admin():
				list_id = []
				if self.type_user.manager_class:
					for elem in self.type_user.manager_class:
						list_id.append(elem.id_planning)
				if self.type_user.campus:
					for elem in self.type_user.campus:
						if elem.classes:
							for classe in elem.classes:
								list_id.append(classe.id_planning)
				if self.type_user.student_class:
					list_id.append(self.type_user.student_class.id_planning)
				id = list_id #liste['class'] = [list_id, required]
			elif (self.type_user.is_student() and self.type_user.student_class):
				id = self.type_user.student_class.id_planning
		if (id):
			liste['class'] = [id, required]
		else:
			liste['class'] = [None, required]
		ids = []
		if self.type_user:
			if self.type_user.is_manager() or self.type_user.is_admin():
				list_id = []
				for elem in self.type_user.campus:
					for classe in elem.classes:
						for period in classe.periods:
							list_id.append(period.id_planning)
				if self.type_user.manager_class:
					for elem in self.type_user.manager_class:
						if elem.periods:
							for period in elem.periods:
								list_id.append(period.id_planning)
				if self.type_user.student_class and self.type_user.student_class.periods:
					for period in self.type_user.student_class.periods:
						list_id.append(period.id_planning)
				ids = list_id
			elif (self.type_user.is_student() and self.type_user.student_class and self.type_user.student_class.periods):
				for period in self.type_user.student_class.periods:
					ids.append(period.id_planning)
		elif (self.type_class and self.type_class.periods):
			for period in self.type_class.periods:
				ids.append(period.id_planning)
		elif (self.type_campus and self.type_campus.classes):
			for classe in self.type_campus.classes:
				for period in classe.periods:
					ids.append(period.id_planning)
		if (len(ids) > 0):
			list_id = []
			for id in ids:
				list_id.append(id)
			liste['period'] = [list_id, required]
		else:
			liste['period'] = [None, required]

	def check_rights(self, type, var = None):
		"""use for all rights_check, for modify events right,
		 displaying private event or not, etc... """

		if type == "class":
			if not app.user.is_admin():
				if not app.user.is_manager():
					return False
				else:
					for elem in app.user.campus:
						if elem.id == var[0]:
							return True
					for elem in app.user.manager_class:
						if elem.id == var[1]:
							return True
					return False
			else:
				return True
		elif type == "campus":
			if not app.user.is_admin():
				if not app.user.is_manager():
					return False
				else:
					for elem in app.user.campus:
						if elem.id == var:
							return True
					return False
			else:
				return True
		#elif type == "univ":
		#	if not (app.user.is_admin()):
		#		return False
		#	else:
		#		return True
		elif type == "period":
			if not (app.user.is_admin()):
				return False
			else:
				return True
		elif type == "user":
			if not (var == app.user.id_planning):
				return False
			else:
				return True

	def export(self):
		"""parse events for ical export"""

		ical_data = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//TIMETABLEASY Calendar 0.1//EN\n"
		events = self.get_event(None, None, True)
		for list in events:
			for event in list:
				delta = relativedelta(hours=event.time_length)
				event.end = event.datetime + delta

				ical_data += "BEGIN:VEVENT\n"
				ical_data += "DTSTART:"+str(event.datetime.strftime("%Y%m%dT%H%M01Z"))+"\n"
				ical_data += "DTEND:"+str(event.end.strftime("%Y%m%dT%H%M00Z"))+"\n"
				ical_data += "UID:"+str(event.id)+"\n"
				ical_data += "CREATED:"+str(event.added)+"\n"
				ical_data += "LAST-MODIFIED:"+str(event.modified)+"\n"
				ical_data += "SUMMARY:"+str(event.name)+"\n"
				ical_data += "DESCRIPTION:"+str(event.description)+"\n"
				ical_data += "LOCATION:"+str(event.classroom)+"\n"
				ical_data += "STATUS:CONFIRMED\n"
				ical_data += "END:VEVENT\n"

		ical_data += "END:VCALENDAR\n"
		return ical_data

	def export_ical(self, button):
		"""export all events attached to this planning and the
		 linked planning"""

		self.filechooser = gtk.FileChooserDialog("Export du planning...", None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		self.filechooser.set_icon_from_file(os.path.normpath("./graphics/images/icon_planning.png"))
		filter = gtk.FileFilter()
		filter.set_name("Calendrier VCS/ICS")
		filter.add_mime_type("text/calendar")
		filter.add_pattern("*.ics")
		self.filechooser.add_filter(filter)
		self.filechooser.set_do_overwrite_confirmation(True)
		self.filechooser.set_current_folder(os.path.expanduser("~"))
		self.filechooser.set_current_name("Planning.ics")
		self.filechooser.show()
		response = self.filechooser.run()
		if (response == gtk.RESPONSE_OK):
			name = self.filechooser.get_filename()
			split = os.path.splitext(name)
			if (split[1] != 'ics'):
				name = split[0] + '.ics'
			data = self.export()
			f = open(name, "w")
			f.write(data)
			f.close()
		elif (response == gtk.RESPONSE_CANCEL):
			pass
		self.filechooser.destroy()

	def change_theme(self, theme="pepper"):
		"""change the planning theme"""

		script = "change_theme('"+theme+"')";
		self.execute(script)

	# db_fill callback
	def cb_fill(self, number):
		"""callback for fill the db"""

		from Event import Event

		event = Event()
		event.planning = self
		event.cb_fill(number)

		db.session.add(self)

def init():
	"""define table planning and mapping"""

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper

	t_planning = Table('planning', db.metadata,
		Column('id',					types.Integer,
			Sequence('planning_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),
	)

	mapper(Planning, t_planning)
