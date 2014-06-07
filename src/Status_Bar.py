# -*- coding: utf-8 -*-

import pygtk
pygtk.require("2.0")
import gtk

import time
import thread
import os
from datetime import datetime

from Timetableasy import app

connection_status = {
	0	:	{
				'stock' 	: 'gtk-disconnect',
				'tooltip'	: 'Vous êtes actuellement déconnecté.'
			},
	1	:	{
				'stock' 	: 'gtk-connect',
				'tooltip'	: 'Vous êtes actuellement connecté au serveur.'
			},
	2	:	{
				'stock' 	: 'gtk-harddisk',
				'tooltip'	: 'Vous êtes actuellement en mode hors-ligne. Vous pouvez visualiser toutes vos informations.'
			}
}


actions = {
	1	:	{
				'msg'	: 'Terminé',
				'stock'	: None,
				'file'	: None
			},
	2	:	{
				'msg'	: 'Connecté',
				'stock'	: None,
				'file'	: None
			},
	3	:	{
				'msg'	: 'Déconnecté',
				'stock'	: None,
				'file'	: None
			},
	4	:	{
				'msg'	: 'Connexion en cours...',
				'stock'	: None,
				'file'	: None
			},
	5	:	{
				'msg'	: 'Déconnexion en cours...',
				'stock'	: None,
				'file'	: None
			},
	6	:	{
				'msg'	: 'Identification requise',
				'stock'	: 'gtk-dialog-warning',
				'file'	: None
			},
	7	:	{
				'msg'	: 'Passé en mode hors-ligne',
				'stock'	: None,
				'file'	: None
			},
	8	:	{
				'msg'	: 'Passé en mode en-ligne',
				'stock'	: None,
				'file'	: None
			},
	9	:	{
				'msg'	: 'Impossible de contacter le server',
				'stock'	: 'gtk-dialog-warning',
				'file'	: None
			},
}


class Status_Bar(object):

	def __init__(self, statusbar, image_object, icon_object, label_date):
		self.statusbar = statusbar
		self.image = image_object
		self.icon = icon_object
		self.date = label_date
		self.date.hide()
		self.time = None
		self.animation = gtk.gdk.PixbufAnimation('graphics/images/ajax-loader.gif')
		self.add_action('icon', 6)
		self.set_connection_status(0)
		thread.start_new_thread(self.display_date, ())

	def add_action(self, icon_type, action_id, specific_msg = None, specific_icon = None):
		if (icon_type == 'progress'):
			self.time = datetime.fromtimestamp(time.time())
			self.statusbar.push(action_id, actions[action_id]['msg'])
			self.image.set_from_animation(self.animation)
		elif (icon_type == 'icon'):
			if (specific_msg == None and specific_icon == None):
				if (self.time != None):
					diff_time = (datetime.fromtimestamp(time.time()) - self.time)/1000
					status_text = actions[action_id]['msg'] + ' (effectué en : '+ str(diff_time.microseconds) + ' ms)'
					self.time = None
				else:
					status_text = actions[action_id]['msg']

				self.statusbar.push(action_id, status_text)

				if (actions[action_id]['stock'] != None):
					self.image.set_from_stock(actions[action_id]['stock'], gtk.ICON_SIZE_MENU)
				elif (actions[action_id]['file'] != None):
					self.image.set_from_file(os.path.normpath('graphics/images/' + actions[action_id]['file']))
				else:
					self.image.set_from_stock('gtk-info', gtk.ICON_SIZE_MENU)

			else:
				self.statusbar.push(0, specific_msg)

				"""
				s//stock_id = from stock
				f//filepath = from file
				"""

				icon = specific_icon.split('//', 1)
				if (icon[0] == 's'):
					self.image.set_from_stock(icon[1], gtk.ICON_SIZE_MENU)
				elif (icon[0] == 'f'):
					if (os.path.isfile(icon[1])):
						self.image.set_from_file(os.path.normpath('graphics/images/' + icon[1]))
					else:
						self.image.set_from_stock('gtk-info', gtk.ICON_SIZE_MENU)
				else:
					self.image.set_from_stock('gtk-info', gtk.ICON_SIZE_MENU)


	def set_connection_status(self, status_id):
		self.icon.set_from_stock(connection_status[status_id]['stock'], gtk.ICON_SIZE_MENU)
		self.icon.set_tooltip_text(connection_status[status_id]['tooltip'])

	def check_date_display(self):
		if (app.settings.display_date):
			self.date.show()
		else:
			self.date.hide()

	def display_date(self):
		while 1:
			self.date.set_text(time.strftime('%a %d %b %Y, %H:%M:%S',time.localtime()))
			time.sleep(1)
