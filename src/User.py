# -*- coding: utf-8 -*-
import gtk

import os
import md5

from db import db
from Timetableasy import app
from TreeMgmt import TreeMgmt

global interface_user

class UserInterface(object):

	def __init__(self):
		from GtkMapper import GtkMapper
		mapper = GtkMapper('graphics/dialog_user.glade', self, app.debug)
		self.connect_dialog.set_app_paintable(True)
		self.connect_dialog.realize()

		pixbuf = gtk.gdk.pixbuf_new_from_file("graphics/images/connect_background.jpg")
		pixbuf.scale_simple(600, 375, gtk.gdk.INTERP_NEAREST)
		self.connect_dialog.window.set_back_pixmap(pixbuf.render_pixmap_and_mask()[0], False)

		self.action_add = mapper.glade.menu.add
		self.dialog_confirmation = gtk.MessageDialog(None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		    gtk.MESSAGE_QUESTION,
		    gtk.BUTTONS_OK_CANCEL,
		    None)

	def password(self, length):
		"""generate password for user with length in arg or 8"""

		from random import Random
		rng = Random()
		righthand = '23456qwertasdfgzxcvbQWERTASDFGZXCVB'
		lefthand = '789yuiophjknmYUIPHJKLNM'
		allchars = righthand + lefthand

		#user didn't specify a length.  that's ok, just use 8
		if not length:
			length = 8

		passwd = ""
		for i in range(length):
			if i%2:
				passwd += rng.choice(lefthand)
			else:
				passwd += rng.choice(righthand)
		return passwd

	def password_edit(self):
		"""call the dialog_password, if user continue, call
		status_password for display the response"""

		self.dialog_password.set_title("Modification de mot de passe")
		result = self.dialog_password.run()
		self.dialog_password.hide()
		if result != gtk.RESPONSE_CANCEL and result != 	gtk.RESPONSE_DELETE_EVENT:
			 self.status_password()
		return result

	def status_password(self):
		"""call change_pass_status window, display error message,
		or confirmation message """

		result = self.change_pass_status.run()
		self.change_pass_status.hide()
		return result

	def on_valid_password_clicked(self, widget):
		"""check the user's password, check if both new password
		are identicals, change the change_pass_status in error case"""

		passwd = self.old_password.get_text()
		login = app.user.login
		md5passwd = md5.new(passwd)
		def query(db, login):
			return db.session.query(User).filter(User.login==login).first()
		user = db.session_query(query, login,
		    "auth : query(User).filter(User.login==login(" + str(login) + ").first()")
		if app.user.password != md5passwd.hexdigest():
			self.change_pass_status.set_markup("Erreure: ancien mot de passe invalide")
			self.dialog_password.response(gtk.RESPONSE_OK)
		else:
			passwd1 = self.new_password1.get_text()
			passwd2 = self.new_password2.get_text()
			if passwd1 == passwd2:
				md5passwd = md5.new(passwd1)
				app.user.password = md5passwd.hexdigest()
				db.session_try_commit()
				self.dialog_password.response(gtk.RESPONSE_OK)
			else:
				self.change_pass_status.set_markup("Erreure: les nouveaux mots de passe ne sont pas identiques")

	def on_cancel_password_clicked(self, widget):
		"""close the dialog_password"""

		self.dialog_password.response(gtk.RESPONSE_CANCEL)

	def on_close_message_clicked(self, widget):
		"""close the change_pass_status"""

		self.change_pass_status.response(gtk.RESPONSE_OK)

	def mail(self, dst_user):
		"""send a mail for new dst_user with login, password.
		In use app.university.email_server (SMTP). Send by admin
		email to created user email with calling server.sendmail"""

		from smtplib import SMTP

		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
		    % (app.user.email, dst_user.email, "Votre compte timetableasy"))
		msg += "Bonjour " + dst_user.name + " " + dst_user.firstname + ".\n"
		msg += "Votre identifiant est : " + dst_user.login + ".\n"
		msg += "Votre mot de passe est : " + dst_user.password + ".\n"
		msg += "\nCet e-mail a été auto généré, merci de ne pas répondre.\n"
		msg += "\nSlts,\n" + app.user.name + " " + app.user.firstname

		server = SMTP(app.university.email_server)
		server.set_debuglevel(1)
		server.sendmail(app.user.email, dst_user.email, msg)
		server.quit()

	def connect(self):
		"""connection dialog"""

		self.connected_user = None
		self.connect_dialog.set_keep_above(True)
		self.connect_dialog.run()
		return self.connected_user

	def add(self, obj):
		"""add user dialog, if response is RESPONSE_OK, call
		self.mail for """

		self.current_obj = obj
		self.name.set_text("")
		self.firstname.set_text("")
		self.email.set_text("")
		self.login.set_text("")
		self.dialog.obj.set_title("Création d'un utilisateur")
		self.dialog.valid.connect("clicked", self.on_dialog_add)
		result = self.dialog.obj.run()
		print "result add : " + str(result)
		self.dialog.obj.hide()
		if result == gtk.RESPONSE_OK:
			self.mail(obj)
		self.current_obj = None
		return result

	def change(self, obj):
		"""change user dialog, get object fields and fill dialog
		fields"""

		self.current_obj = obj
		self.name.set_text(obj.name)
		self.firstname.set_text(obj.firstname)
		self.email.set_text(obj.email)
		self.login.set_text(obj.login)
		self.dialog.obj.set_title("Modification de l'utilisateur " + obj.name)
		self.dialog.valid.connect("clicked", self.on_dialog_change)

		result = self.dialog.obj.run()
		self.dialog.obj.hide()
		self.current_obj = None
		return result

	def menu_display(self, obj, event, init_func = None):
		self.current_obj = obj
		self.init_func = init_func
		self.menu.show_all()
		self.menu.popup(None, None, None, event.button, event.time)

	def menu_admins_display(self, obj, event, init_func = None):
		self.current_obj = obj
		self.init_func = init_func
		self.menu_admins.show_all()
		self.menu_admins.popup(None, None, None, event.button, event.time)

	def menu_managers_display(self, obj, event, init_func = None):
		self.current_obj = obj
		self.init_func = init_func
		self.menu_managers.show_all()
		self.menu_managers.popup(None, None, None, event.button, event.time)

	def menu_teachers_display(self, obj, event, init_func = None):
		self.current_obj = obj
		self.init_func = init_func
		self.menu_teachers.show_all()
		self.menu_teachers.popup(None, None, None, event.button, event.time)

	def menu_students_display(self, obj, event, init_func = None):
		self.current_obj = obj
		self.init_func = init_func
		self.menu_students.show_all()
		self.menu_students.popup(None, None, None, event.button, event.time)

	def get_dialog_fields(self):
		"""get field of the dialog_user and fill user
		 object with that"""

		obj = self.current_obj
		obj.name = self.name.get_text()
		obj.firstname = self.firstname.get_text()
		obj.login = self.login.get_text()
		obj.email = self.email.get_text()

	# dialog callbacks
	def on_dialog_cancel(self, widget):
		"""close dialog_user"""

		self.dialog.obj.response(gtk.RESPONSE_CANCEL)

	def on_dialog_add(self, widget):
		"""call get_dialog_fields, and call db.session_query,
		 response gtk.RESPONSE_OK"""

		from Settings import Settings
		from Planning import Planning

		print "ON DIALOG ADD on : " + str(self.current_obj)
		if not self.current_obj:
			print "ERROR ON ADD"

		def query(db, obj):
			"""callback for db.session_query, this query
			 add obj to session and call db.session_try_commit"""

			db.session.add(obj.settings)
			db.session.add(obj.planning)
			db.session.add(obj)
			db.session_try_commit()
		obj = self.current_obj
		self.get_dialog_fields()
		obj.settings = Settings()
		obj.planning = Planning()
		obj.password = self.password(app.university.password_length)
		db.session_query(query, obj,
		    str("Insert user " + obj.login + "( name:" + obj.name +
		    ", firstname:" + obj.firstname + ", email:" + obj.email +
		    ") in db"))
		self.dialog.obj.response(gtk.RESPONSE_OK)

	def on_dialog_change(self, widget):
		"""call get_dialog_fields, call db.session_try_commit,
		 response gtk.RESPONSE_OK"""

		self.get_dialog_fields()
		db.session_try_commit()
		self.dialog.obj.response(gtk.RESPONSE_OK)

	def on_connect(self, widget):
		"""get login and password and check if there are valid by
		calling auth(), if not call connect_error dialog"""

		from Settings import Settings

		# XXX remove this ?
		#app.contentmgr.status_bar.add_action('progress', 4)
		login = self.user.get_text()
		passwd = self.passwd.get_text()
		self.user.set_text('')
		self.passwd.set_text('')
		print "user : %s, passwd : %s" % (login, passwd)
		self.connected_user = auth(login, passwd)
		if self.connected_user != None:
			self.connect_dialog.destroy()
		else:
			self.connect_dialog.hide()
			self.connect_error.set_keep_above(True)
			self.connect_error.run()

	def on_connect_dialog_close(self, widget):
		"""close connect_dialog"""

		self.connect_dialog.destroy()

	def on_connect_error_close(self, widget):
		""" close connect_error_dialog"""
		from User import User
		from Planning import Planning
		from Settings import Settings

		self.user.grab_focus()
		self.connect_error.hide()

		# XXX temp hack for dev to bypass auth/have a fix account
		"""def query(db, empty):
			return db.session.query(User).get(1)
		self.connected_user = db.session_query(query, None,
		    "user: connect for dev: query(User).get(1)")

		if not self.connected_user:
			def insert(db, empty):
				user = User()
				user.name = "ROOT"
				user.firstname = "Charlie"
				user.login = "root"
				user.password = "63a9f0ea7bb98050796b649e85481845" #md5('root')
				user.type = 'admin'
				user.email = 'leo@asystant.net'
				user.planning = Planning()
				user.settings = Settings()
				user.id_class = 0
				db.session.add(user.planning)
				db.session.add(user.settings)
				db.session.add(user)
				db.session_try_commit()
				return user
			self.connected_user = db.session_query(insert, None,
			    "for dev: insert user root, passwd root")"""

	# menu callbacks
	def on_menu_add(self, widget):
		obj = self.current_obj
		if callable(self.init_func):
			self.init_func(obj)
		if self.add(obj) == gtk.RESPONSE_OK:
			TreeMgmt.replug_self(obj.parent)
		else:
			# clean all relation for later commit
			obj.student_class = None
			obj.manager_class = []
			obj.campus = []
			obj.cursus = []
			obj.teacher_campus = []
		self.current_obj = None

	def on_menu_edit(self, widget):
		obj = self.current_obj
		if self.change(obj) == gtk.RESPONSE_OK:
			TreeMgmt.replug_parents(obj)
		self.current_obj = None

	def on_menu_delete(self, widget):
		obj = self.current_obj
		self.dialog_confirmation.set_markup("Etes vous sûre de vouloir supprimer l'utilisateur " + obj.name + " " + obj.firstname + " ?")
		if self.dialog_confirmation.run() == gtk.RESPONSE_OK:
			db.session.delete(obj)
			db.session_try_commit()
			TreeMgmt.replug_parents(obj)
		self.dialog_confirmation.hide()
		self.current_obj = None

	def on_menu_reset(self, widget):
		obj = self.current_obj
		self.dialog_confirmation.set_markup("Etes vous sûre de " +
		    "vouloir réinitialiser le mot de passe de l'utilisateur " +
		    obj.name + " " + obj.firstname + " ?")
		if self.dialog_confirmation.run() == gtk.RESPONSE_OK:
			obj.password = self.password(app.university.password_length)
			db.session_try_commit()
			self.mail(obj)
		self.dialog_confirmation.hide()
		self.current_obj = None

class User(object):
	# Actions
	ADD_STUDENT_ACTION = 1
	ADD_CLASS_MANAGER_ACTION = 2
	ADD_CAMPUS_MANAGER_ACTION = 3
	ADD_CAMPUS_TEACHER_ACTION = 4
	ADD_CURSUS_MANAGER_ACTION = 5
	ADD_ADMINISTRATOR_ACTION = 6
	# Separators / group of items
	ADMINISTRATORS_GROUP = 7
	CURSUS_MANAGERS_GROUP = 8
	CAMPUS_MANAGERS_GROUP = 9
	CAMPUS_TEACHERS_GROUP = 10
	CLASS_MANAGERS_GROUP = 11
	CLASS_TEACHERS_GROUP = 12
	CLASS_STUDENTS_GROUP = 13

	# TreeMgmt Callbacks
	def cb_tree_isplugable(self, tree, id):
		if (self.row[id].action == self.ADMINISTRATORS_GROUP or
		    self.row[id].action == self.CURSUS_MANAGERS_GROUP or
		    self.row[id].action == self.CAMPUS_MANAGERS_GROUP or
		    self.row[id].action == self.CAMPUS_TEACHERS_GROUP or
		    self.row[id].action == self.CLASS_MANAGERS_GROUP or
		    self.row[id].action == self.CLASS_STUDENTS_GROUP or
		    self.row[id].action == self.CLASS_TEACHERS_GROUP):
			return True
		return False

	def cb_tree_plug(self, tree, iter, id):
		"""plug object's childs in the tree"""
		if self.row[id].action == self.ADMINISTRATORS_GROUP:
			def query(db, empty):
				q = db.session.query(User)
				return q.filter(User.type == "admin").all()
			administratorlist = db.session_query(query, None,
			    'user: administratorlist = ' +
			    'query(User).filter(User.type == "admin").all()')
			for admin in administratorlist:
				tree.plug(iter, admin, self)
			tree.plug_action(iter, User(), self,
			    self.ADD_ADMINISTRATOR_ACTION, self)
		elif self.row[id].action == self.CURSUS_MANAGERS_GROUP:
			parent = self.row[id].obj_parent
			for manager in parent.managers:
				tree.plug(iter, manager, parent, self)
			tree.plug_action(iter, User(), parent,
			    self.ADD_CURSUS_MANAGER_ACTION, self)
		elif self.row[id].action == self.CAMPUS_MANAGERS_GROUP:
			parent = self.row[id].obj_parent
			for manager in parent.managers:
				tree.plug(iter, manager, parent, self)
			tree.plug_action(iter, User(), parent,
			    self.ADD_CAMPUS_MANAGER_ACTION, self)
		elif self.row[id].action == self.CAMPUS_TEACHERS_GROUP:
			parent = self.row[id].obj_parent
			for teacher in parent.teachers:
				tree.plug(iter, teacher, parent, self)
			tree.plug_action(iter, User(), parent,
			    self.ADD_CAMPUS_TEACHER_ACTION, self)
		elif self.row[id].action == self.CLASS_MANAGERS_GROUP:
			parent = self.row[id].obj_parent
			for manager in parent.managers:
				tree.plug(iter, manager, parent, self)
			tree.plug_action(iter, User(), parent,
			    self.ADD_CLASS_MANAGER_ACTION, self)
		elif self.row[id].action == self.CLASS_STUDENTS_GROUP:
			parent = self.row[id].obj_parent
			for student in parent.students:
				tree.plug(iter, student, parent, self)
			tree.plug_action(iter, User(), parent,
			    self.ADD_STUDENT_ACTION, self)
		elif self.row[id].action == self.CLASS_TEACHERS_GROUP:
			parent = self.row[id].obj_parent
			def query(db, parent):
				from User import User
				from Event import Event
				from Planning import Planning
				from Course import Course
				q = db.session.query(User).join(Event)
				q = q.join(Planning)
				q = q.filter(Planning.id == parent.id_planning)
				return q.all()
			teachers = db.session_query(query, parent,
			    'user: teachers = ' +
			    'query(User).join(Event).join(Planning)' +
			    '.filter(Planning.id == ' +
			    str(parent.id_planning) + ').execute()')
			if teachers:
				for teacher in teachers:
					tree.plug(iter, teacher, parent, self)

	def cb_tree_pixbuf(self, tree, id):
		"""return the pixbuf for the tree"""
		image = gtk.Image()
		if (self.row[id].action == self.ADD_STUDENT_ACTION or
		    self.row[id].action == self.ADD_CLASS_MANAGER_ACTION or
		    self.row[id].action == self.ADD_CAMPUS_MANAGER_ACTION or
		    self.row[id].action == self.ADD_CAMPUS_TEACHER_ACTION or
		    self.row[id].action == self.ADD_CURSUS_MANAGER_ACTION or
		    self.row[id].action == self.ADD_ADMINISTRATOR_ACTION):
			image.set_from_file(os.path.normpath('graphics/images/user_add.png'))
		elif (self.row[id].action == self.ADMINISTRATORS_GROUP or
		    self.row[id].action == self.CURSUS_MANAGERS_GROUP or
		    self.row[id].action == self.CAMPUS_MANAGERS_GROUP or
		    self.row[id].action == self.CAMPUS_TEACHERS_GROUP or
		    self.row[id].action == self.CLASS_MANAGERS_GROUP or
		    self.row[id].action == self.CLASS_STUDENTS_GROUP or
		    self.row[id].action == self.CLASS_TEACHERS_GROUP):
			image.set_from_file(os.path.normpath('graphics/images/user_group.png'))
		elif self.type == 'admin':
			image.set_from_file(os.path.normpath('graphics/images/administrator.png'))
		elif self.type == 'manager':
			image.set_from_file(os.path.normpath('graphics/images/manager.png'))
		elif self.type == 'teacher':
			image.set_from_file(os.path.normpath('graphics/images/teacher.png'))
		elif self.type == 'student':
			image.set_from_file(os.path.normpath('graphics/images/student.png'))
		else:
			image.set_from_file(os.path.normpath('graphics/images/user.png'))
		return image.get_pixbuf()

	def cb_tree_name(self, tree, id):
		"""return the name for the tree"""
		if self.row[id].action == self.ADD_STUDENT_ACTION:
			return "Nouvel étudiant"
		elif (self.row[id].action == self.ADD_CLASS_MANAGER_ACTION or
		    self.row[id].action == self.ADD_CAMPUS_MANAGER_ACTION or
		    self.row[id].action == self.ADD_CURSUS_MANAGER_ACTION):
			return "Nouveau manager"
		elif self.row[id].action == self.ADD_ADMINISTRATOR_ACTION:
			return "Nouvel administrateur"
		elif self.row[id].action == self.ADD_CAMPUS_TEACHER_ACTION:
			return "Nouvel enseignant"
		elif self.row[id].action == self.ADMINISTRATORS_GROUP:
			return "Administrateurs"
		elif (self.row[id].action == self.CURSUS_MANAGERS_GROUP or
		    self.row[id].action == self.CAMPUS_MANAGERS_GROUP or
		    self.row[id].action == self.CLASS_MANAGERS_GROUP):
			return "Managers"
		elif self.row[id].action == self.CAMPUS_TEACHERS_GROUP:
			return "Enseignants"
		elif self.row[id].action == self.CLASS_STUDENTS_GROUP:
			return "Etudiants"
		elif self.row[id].action == self.CLASS_TEACHERS_GROUP:
			return "Encadrants"
		return self.name + " " + self.firstname

	def cb_tree_tooltip_text(self, tree, id):
		"""return the tooltip text for the tree"""
		if self.row[id].action == self.ADD_STUDENT_ACTION:
			return "Double cliquer pour ajouter un étudiant"
		elif (self.row[id].action == self.ADD_CLASS_MANAGER_ACTION or
		    self.row[id].action == self.ADD_CAMPUS_MANAGER_ACTION or
		    self.row[id].action == self.ADD_CURSUS_MANAGER_ACTION):
			return "Double cliquer pour ajouter un manager"
		elif self.row[id].action == self.ADD_ADMINISTRATOR_ACTION:
			return "Double cliquer pour ajouter un administrateur"
		elif self.row[id].action == self.ADD_CAMPUS_TEACHER_ACTION:
			return "Double cliquer pour ajouter un enseignant"
		elif self.row[id].action == self.ADMINISTRATORS_GROUP:
			def query(db, empty):
				from User import User
				q = db.session.query(User)
				return q.filter(User.type == "admin").count()
			nb_admin = db.session_query(query, None,
			    'user: nb_admin = ' +
			    'query(User).filter(User.type == "admin").count()')
			return str("Administrateurs de " +
			    str(self.row[id].obj_parent.name) + ", " +
			    str(nb_admin) + " membre" +
			    str(["", "s"][nb_admin > 1]))
		elif self.row[id].action == self.CURSUS_MANAGERS_GROUP:
			parent = self.row[id].obj_parent
			return str("Managers du cursus " +
			    str(parent.name) + ", " +
			    str(len(parent.managers)) + " membre" +
			    str(["", "s"][len(parent.managers) > 1]))
		elif self.row[id].action == self.CAMPUS_MANAGERS_GROUP:
			parent = self.row[id].obj_parent
			return str("Managers du campus " +
			    str(parent.name) + ", " +
			    str(len(parent.managers)) + " membre" +
			    str(["", "s"][len(parent.managers) > 1]))
		elif self.row[id].action == self.CAMPUS_TEACHERS_GROUP:
			parent = self.row[id].obj_parent
			return str("Enseignants du campus " +
			    str(parent.name) + ", " +
			    str(len(parent.teachers)) + " membre" +
			    str(["", "s"][len(parent.teachers) > 1]))
		elif self.row[id].action == self.CLASS_MANAGERS_GROUP:
			parent = self.row[id].obj_parent
			return str("Managers de la classe " +
			    str(parent.name) + ", " +
			    str(len(parent.managers)) + " membre" +
			    str(["", "s"][len(parent.managers) > 1]))
		elif self.row[id].action == self.CLASS_STUDENTS_GROUP:
			parent = self.row[id].obj_parent
			return str("Etudiants de la classe " +
			    str(parent.name) + ", " +
			    str(len(parent.students)) + " membre" +
			    str(["", "s"][len(parent.students) > 1]))
		elif self.row[id].action == self.CLASS_TEACHERS_GROUP:
			parent = self.row[id].obj_parent
			def query(db, parent):
				from User import User
				from Event import Event
				from Planning import Planning
				q = db.session.query(User).join(Event)
				q = q.join(Planning)
				q = q.filter(Planning.id == parent.id_planning)
				return q.count()
			nb_teachers = db.session_query(query, parent,
			    'user: nb_teachers = ' +
			    'query(User).join(Event).join(Planning)' +
			    '.filter(Planning.id == ' +
			    str(parent.id_planning) + ').count()')
			return str("Enseignants de la classe " +
			    str(parent.name) + ", " +
			    str(nb_teachers) + " membre" +
			    str(["", "s"][nb_teachers > 1]))

		if self.type == 'admin':
			desc = "Administrateur "
		elif self.type == 'manager':
			desc = "Manager "
		elif self.type == 'teacher':
			desc = "Enseignent "
		elif self.type == 'student':
			desc = "Etudiant "
		else:
			desc = "Utilisateur "
		desc += self.name + " " + self.firstname + " " + self.email
		if TreeMgmt.parent_action(self, id) == self.CAMPUS_TEACHERS_GROUP:
			# XXX complete tooltip : <nb_cours> <volume horaire_tt>
			pass
		elif TreeMgmt.parent_action(self, id) == self.CLASS_TEACHERS_GROUP:
			# XXX complete tooltip : list(<cours> <volume horaire>)
			pass
		return desc

	def on_tree_rightclick(self, tree, event, id):
		"""call when the user do a right click on the tree row"""
		if self.row[id].action == self.ADMINISTRATORS_GROUP:
			user = User()
			user.type = "admin"
			user.parent = self
			interface_user.menu_admins_display(user, event)
		elif self.row[id].action == self.CURSUS_MANAGERS_GROUP:
			user = User()
			user.type = "manager"
			user.parent = self
			user.link =  [self.row[id].obj_parent]
			def link(obj):
				obj.cursus = obj.link
			interface_user.menu_managers_display(user, event, link)
		elif self.row[id].action == self.CAMPUS_MANAGERS_GROUP:
			user = User()
			user.type = "manager"
			user.parent = self
			user.link = [self.row[id].obj_parent]
			def link(obj):
				obj.campus = obj.link
			interface_user.menu_managers_display(user, event, link)
		elif self.row[id].action == self.CAMPUS_TEACHERS_GROUP:
			user = User()
			user.type = "teacher"
			user.parent = self
			user.link = [self.row[id].obj_parent]
			def link(obj):
				obj.teacher_campus = obj.link
			interface_user.menu_teachers_display(user, event, link)
		elif self.row[id].action == self.CLASS_MANAGERS_GROUP:
			user = User()
			user.type = "manager"
			user.parent = self
			user.link = [self.row[id].obj_parent]
			def link(obj):
				obj.manager_class = obj.link
			interface_user.menu_managers_display(user, event, link)
		elif self.row[id].action == self.CLASS_STUDENTS_GROUP:
			user = User()
			user.type = "student"
			user.parent = self
			user.link = self.row[id].obj_parent
			def link(obj):
				obj.student_class = obj.link
			interface_user.menu_students_display(user, event, link)
		elif not self.row[id].action:
			interface_user.menu_display(self, event)

	def on_tree_selected(self, tree, id):
		"""call when the user double click on the tree row"""
		if self.row[id].action == self.ADD_STUDENT_ACTION:
			self.type = "student"
			self.student_class = self.row[id].obj_parent
			if interface_user.add(self) == gtk.RESPONSE_OK:
				TreeMgmt.replug_parents(self)
			else:
				self.student_class = None
		elif self.row[id].action == self.ADD_CLASS_MANAGER_ACTION:
			self.type = "manager"
			self.manager_class = [self.row[id].obj_parent]
			if interface_user.add(self) == gtk.RESPONSE_OK:
				TreeMgmt.replug_parents(self)
			else:
				self.manager_class = None
		elif self.row[id].action == self.ADD_CAMPUS_MANAGER_ACTION:
			self.type = "manager"
			self.campus = [self.row[id].obj_parent]
			if interface_user.add(self) == gtk.RESPONSE_OK:
				TreeMgmt.replug_parents(self)
			else:
				self.campus = None
		elif self.row[id].action == self.ADD_CAMPUS_TEACHER_ACTION:
			self.type = "teacher"
			self.teacher_campus = [self.row[id].obj_parent]
			if interface_user.add(self) == gtk.RESPONSE_OK:
				TreeMgmt.replug_parents(self)
			else:
				self.teacher_campus = None
		elif self.row[id].action == self.ADD_CURSUS_MANAGER_ACTION:
			self.type = "manager"
			self.cursus = [self.row[id].obj_parent]
			if interface_user.add(self) == gtk.RESPONSE_OK:
				TreeMgmt.replug_parents(self)
			else:
				self.cursus = []
		elif self.row[id].action == self.ADD_ADMINISTRATOR_ACTION:
			self.type = "admin"
			if interface_user.add(self) == gtk.RESPONSE_OK:
				TreeMgmt.replug_parents(self)
		elif not self.row[id].action:
			self.planning.display(app.contentmgr)

	def is_admin(self):
		"""check if user is admin (return True or False)"""

		if (self.type == 'admin'):
			return True
		else:
			return False

	def is_manager(self):
		"""check if user is manager (return True or False)"""

		if (self.type == 'manager'):
			return True
		else:
			return False

	def is_teacher(self):
		"""check if user is teacher (return True or False)"""

		if (self.type == 'teacher'):
			return True
		else:
			return False

	def is_student(self):
		"""check if user is student (return True or False)"""

		if (self.type == 'student'):
			return True
		else:
			return False

	def cb_combobox(self):
		return self.name + " " + self.firstname

	# db_fill callback
	def cb_fill(self, number, prefix):
		"""callback for fill the db"""

		def fill_insert(user):
			from Planning import Planning
			import Event
			from datetime import date
			from Settings import Settings
			user.name = prefix + "_" + str(i)
			user.firstname = "firstname"
			user.login = prefix + "_" + str(i)
			user.email = "fromano@asystant.net"
			passwd = "user"+str(i)
			md5passwd = md5.new(passwd)
			user.password = md5passwd.hexdigest()
			if user.cursus or user.campus or user.manager_class:
				user.type = 'manager'
			elif user.student_class:
				user.type = 'student'
			elif user.teacher_campus:
				user.type = 'teacher'
			else:
				user.type = 'admin'

			Event.fill_date = date(date.today().year, date.today().month, 1)

			user.planning = Planning()
			user.planning.cb_fill(number * 10)
			user.settings = Settings()
			db.session.add(user.settings)
			db.session.add(user)

			if app.verbose:
				print str("fill user : (" +
				    str(user.type) + ", " +
				    str(user.name) + ", " +
				    str(passwd) +")")

		for i in range(number - 1):
			user = User()
			user.student_class = self.student_class
			user.campus = self.campus
			user.teacher_campus = self.teacher_campus
			user.cursus = self.cursus
			user.manager_class = self.manager_class
			fill_insert(user)
		i = number
		fill_insert(self)

def auth(login, passwd):
	"""check if the login and password combination is valid"""

	from db import db
	db.session_init()
	md5passwd = md5.new(passwd)
	print "login : %s, passwd : %s, md5passwd : %s" % (login, passwd, md5passwd.hexdigest())
	def query(db, login):
		return db.session.query(User).filter(User.login==login).first()
	user = db.session_query(query, login,
	    "auth : query(User).filter(User.login==login(" + str(login) + ").first()")
	if user == None or user.password != md5passwd.hexdigest():
		return None
	else:
		return user

def init_graphics():
	""" initialize graphics interface_user"""

	global interface_user
	interface_user = UserInterface()

def init_db():
	"""define table user and mapping"""

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper
	# Dependencies
	from Planning import Planning
	from Class import Class
	from Cursus import Cursus
	from Campus import Campus

	t_user = Table('user', db.metadata,
		Column('id',					types.Integer,
			Sequence('user_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),

		Column('name',					types.VARCHAR(255),
			nullable	= False),

		Column('firstname',				types.VARCHAR(255),
			nullable	= False),

		Column('login',					types.VARCHAR(64),
			nullable	= False,
			unique		= True),

		Column('password',				types.VARCHAR(255),
			nullable	= False),

		Column('email',					types.VARCHAR(255),
			nullable	= False),

		Column('type',					types.Enum(
			    'admin','manager','teacher','student'),
			nullable	= False),

		Column('id_planning',				types.Integer,
			ForeignKey('planning.id'),
			nullable	= False),

		Column('id_class',				types.Integer,
			ForeignKey('class.id')),
	)

	t_user_cursus = Table('user_cursus', db.metadata,
		Column('id_user',				types.Integer,
			ForeignKey('user.id'),
			nullable	= False),

		Column('id_cursus',				types.Integer,
			ForeignKey('cursus.id'),
			nullable	= False),
	)

	t_user_campus = Table('user_campus', db.metadata,
		Column('id_user',				types.Integer,
			ForeignKey('user.id'),
			nullable	= False),

		Column('id_campus',				types.Integer,
			ForeignKey('campus.id'),
			nullable	= False),
	)

	t_teacher_campus = Table('teacher_campus', db.metadata,
		Column('id_user',				types.Integer,
			ForeignKey('user.id'),
			nullable	= False),

		Column('id_campus',				types.Integer,
			ForeignKey('campus.id'),
			nullable	= False),
	)

	t_user_class = Table('user_class', db.metadata,
		Column('id_user',				types.Integer,
			ForeignKey('user.id'),
			nullable	= False),

		Column('id_class',				types.Integer,
			ForeignKey('class.id'),
			nullable	= False),
	)

	mapper(User, t_user, properties = {
		'planning'	: relationship(Planning,
			backref		= backref('type_user', uselist = False)),

		'student_class'	: relationship(Class, backref = "students"),

		'cursus'	: relationship(Cursus,
			secondary	= t_user_cursus,
			backref		= 'managers'),

		'campus'	: relationship(Campus,
			secondary	= t_user_campus,
			backref		= 'managers'),

		'manager_class'	: relationship(Class,
			secondary	= t_user_class,
			backref		= 'managers'),

		'teacher_campus': relationship(Campus,
			secondary	= t_teacher_campus,
			backref		= 'teachers'),
	})

