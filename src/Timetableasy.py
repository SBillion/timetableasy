import gtk

import pygtk
import cairo
import gio
import pango
import atk
import pangocairo
import xml

import os

global app

class Timetableasy(object):

	def __init__(self):
		self.connected = False

	def connect(self):
		from ContentMgmt import ContentMgmt
		import User
		User.init_graphics()
		from User import interface_user

		self.user = interface_user.connect()
		if self.user != None:
			from db import db
			from University import University
			print 'access granted'
			self.connected = True
			self.user.settings.load_settings()
			def query(db, empty):
				return db.session.query(University).get(1)
			self.university = db.session_query(query, None,
			    'Timetableasy init : query(University).get(1)')
			self.contentmgr = ContentMgmt()
			# XXX what to do with that ?
			#if db.status == False:
			#	self.contentmgr.status_bar.add_action('icon', 9)
			self.contentmgr.status_bar.add_action('icon', 2)
			self.contentmgr.status_bar.set_connection_status(1)
			self.contentmgr.status_bar.check_date_display()
			# XXX first load of rights
			if (not self.user.is_admin()):
				self.contentmgr.menubar.admin.hide()
			self.contentmgr.show()
		else:
			print 'access denied'

	def start(self):
		if self.connected:
			gtk.main()

app = Timetableasy()
