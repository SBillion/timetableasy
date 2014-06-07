import gtk

import sys
import os
import copy

from db import db
from Timetableasy import app
from Campus import Campus

class ContentMgmt(object):

	def __init__(self):
		from Status_Bar import Status_Bar
		from TreeMgmt import TreeMgmt
		from GtkMapper import GtkMapper

		GtkMapper('graphics/gui.glade', self, app.debug)

		self.status_bar = Status_Bar(self.statusbar.obj,
		    self.statusbar.image_loader,
		    self.statusbar.status_icon,
		    self.statusbar.label_date)

		def cursus_populate(tree):
			iter = tree.plug(None, app.university, None)
			tree.treeview.expand_row(tree.treestore.get_path(iter),
			    False)
		self.cursustree = TreeMgmt(["Objects"], None, "cursus", cursus_populate)

		def campus_populate(tree):
			iter = tree.plug(None, app.university, None)
			tree.treeview.expand_row(tree.treestore.get_path(iter),
			    False)
		self.campustree = TreeMgmt(["Objects"], None, "campus", campus_populate)

		self.menu_cursus.add(self.cursustree.treeview)
		self.menu_cursus.show_all()

		self.menu_campus.add(self.campustree.treeview)
		self.menu_cursus.show_all()

		self.hpaned_last_pos = 280
		self.objects = []
		self.tabs_check_visibility()

	def show(self):
		self.main.obj.show_all()

	# tabs callbacks :
	def tabs_is_displayed(self, caller):
		return caller in self.objects

	def tabs_go_to(self, caller):
		self.maintabs.set_current_page(self.objects.index(caller))
		self.tabs_update_menu(caller)

	def tabs_update_menu(self, caller):
		for child in self.menu_action.get_children():
			self.menu_action.remove(child)
		if hasattr(caller, 'menu'):
			self.menu_action.pack_start(caller.menu, True, True)

	def tabs_check_visibility(self):
		if(self.maintabs.get_n_pages() > 1):
			if not self.maintabs.get_show_tabs():
				self.maintabs.set_show_tabs(True)
		else:
			self.maintabs.set_show_tabs(False)

	def tabs_add_icon_to_button(self, button):
		image = gtk.Image()
		image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
		iconBox = gtk.HBox(False, 0)
		iconBox.pack_start(image, True, False, 0)
		button.set_relief(gtk.RELIEF_NONE)
		settings = button.get_settings()
		(w,h)=gtk.icon_size_lookup_for_settings(settings, gtk.ICON_SIZE_MENU)
		button.set_size_request(w + 4, h + 4)
		button.add(iconBox)
		button.show_all()

	def tabs_create(self, text, caller):
		# append object to list
		self.objects.append(caller)

		# main view, tab stuff
		if not hasattr(caller, 'view'):
			return
		tabLabel = gtk.Label(text)
		tabLabel.set_justify(gtk.JUSTIFY_LEFT)
		tabButton = gtk.Button()
		tabButton.connect('clicked', self.tabs_remove, caller)
		self.tabs_add_icon_to_button(tabButton)
		tabBox = gtk.HBox(False, 2)
		tabBox.pack_start(tabLabel, True)
		tabBox.pack_start(tabButton, False)
		eventBox = gtk.EventBox()
		eventBox.add(tabBox)
		eventBox.show_all()
		self.maintabs.append_page(caller.view, eventBox)
		self.maintabs.set_tab_reorderable(caller.view, True)
		self.tabs_check_visibility()

		# menu relative to view, menu stuff
		self.maintabs.set_current_page(self.maintabs.get_n_pages()-1)
		self.tabs_update_menu(caller)
		# finish by show all
		caller.view.show_all()
		# set action expander active on left
		self.menu.action.obj.set_expanded(True)

	def tabs_remove(self, button, caller):
		index = self.objects
		if self.maintabs.get_current_page() == index:
			# move to the first caller before deleting all
			if len(self.objects) > 1:
				if index == 0:
					index = 1
				else:
					index = 0
				self.tabs_got_to(self.objects[index])
			# clean menu_action (we don't switch)
			else:
				for child in self.menu_action.get_children():
					self.menu_action.remove(child)
		self.objects.remove(caller)
		self.maintabs.remove(caller.view)
		self.maintabs.queue_draw_area(0,0,-1,-1)
		self.tabs_check_visibility()
		# clean object memory
		self.tabs_execute("clean", self, caller)

	def tabs_execute(self, callback, arg = None, tab = None):
		if tab:
			func = getattr(tab, callback, None)
			if callable(func):
				func(arg)
			return
		for tab in self.objects:
			func = getattr(tab, callback, None)
			if callable(func):
				func(arg)

	def on_tabs_switch(self, notebook, page, page_num):
		caller = self.objects[page_num]
		self.tabs_update_menu(caller)
		func = getattr(caller, "cb_check_opt_availability", None)
		if callable(func):
			func()

	# window + menu callbacks :
	def on_main_destroy(self, widget, data=None):
		gtk.main_quit()

	"""
	def on_show(self, widget):
		print 'test'
		#app.connect()
	"""

	def on_about(self, widget, data=None):
		self.aboutdialog.run()

	def on_about_response(self, widget, responseid, data=None):
		self.aboutdialog.hide()

	def on_myplanningmenu_activate(self, widget, data=None):
		app.user.planning.display(self)
		self.hpaned_show()

	def on_campusmenu_activate(self, widget, data=None):
		self.campus = Campus()
		self.campus.create_planning_view()
		self.hpaned_show()

	def on_cursusmenu_activate(self, widget, data=None):
		# XXX
		pass

	def on_adminmenu_activate(self, widget, data=None):
		app.university.edit()

	def on_offline_mode_toggled(self, widget, data=None):
		if (widget.get_active()):
			self.dialog_offline.run()
			self.status_bar.set_connection_status(2)
			self.status_bar.add_action('icon', 7)

		else:
			self.status_bar.set_connection_status(1)
			self.status_bar.add_action('icon', 8)

	def on_dialog_offline_quit(self, widget, data=None):
		self.dialog_offline.hide()

	def on_sync_button_clicked(self, widget, data=None):
		db.synchronize()
		self.dialog_offline.hide()

	def on_settings_activate(self, widget, data=None):
		app.settings.display()

	def on_password_activate(self, widget, data=None):
		from User import interface_user
		interface_user.password_edit()

	# hpaned callbacks
	def hpaned_show(self):
		self.hpaned.obj.set_position(self.hpaned_last_pos)
		self.menubar.hpaned_menuitem.set_active(True)

	def hpaned_hide(self):
		self.hpaned.obj.set_position(0)
		self.menubar.hpaned_menuitem.set_active(False)

	def on_hpaned_notify(self, widget, data=None):
		if (data.name == 'position'):
			pos = widget.get_property('position')
			if (pos > 0 and pos <= 100):
				self.hpaned_hide()
			if (pos > 100 and pos < 280):
				self.hpaned_show()
			if (pos >= 280 and pos <= 450):
				self.hpaned_last_pos = pos
			if (pos > 450):
				widget.set_position(450)

	def on_hpaned_menuitem_toggled(self, widget, data=None):
		if (widget.get_active()):
			self.hpaned_show()
		else:
			self.hpaned_hide()

	# expander callbacks
	def expander_expand(self, widget, action=True):
		if(action == True):
			self.menu.obj.set_child_packing(widget, True, True, 0, gtk.PACK_START)
			widget.set_expanded(True)
		else:
			self.menu.obj.set_child_packing(widget, False, True, 0, gtk.PACK_START)
			widget.set_expanded(False)

	def on_expander_activate(self, widget, data=None):
		if (widget.get_expanded()):
			self.menu.obj.set_child_packing(widget, False, True, 0, gtk.PACK_START)
		else:
			self.menu.obj.set_child_packing(widget, True, True, 0, gtk.PACK_START)

	# tree callbacks
	def on_reload_cursus_tree_clicked(self, widget):
		self.cursustree.replug(None)

	def on_reload_campus_tree_clicked(self, widget):
		self.campustree.replug(None)
