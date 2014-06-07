import gtk

from db import db
from Timetableasy import app

# Themes
planning_themes = {
	'db'	:	{
					'pepper'		: 0,
					'default'		: 1,
					'blue'			: 2,
					'eggplant'		: 3,
					'lightness'		: 4,
					'mint'			: 5,
				},
	'db_inv':	{
					0				: 'pepper',
					1				: 'default',
					2				: 'blue',
					3				: 'eggplant',
					4				: 'lightness',
					5				: 'mint',
				},
	'disp'	:	{
					'Defaut'		: 0,
					'Gris'			: 1,
					'Bleu'			: 2,
					'Constraste'	: 3,
					'Lightness'		: 4,
					'Mint'			: 5,
				}
}


class Settings(object):

	def load_settings(self):
		""" """
		app.settings = self

	def init_graphics(self):
		from GtkMapper import GtkMapper
		if hasattr(self, "init"):
			return
		self.init = True
		GtkMapper('graphics/dialog_settings.glade', self, app.debug)

	def display(self):
		"""check user settings and initialize fields, run dialog"""

		self.init_graphics()
		if (self.display_date):
			self.dialog.hour_activate.set_active(0)
		else:
			self.dialog.hour_activate.set_active(1)
		self.dialog.planning_theme.set_active(planning_themes['db'][app.settings.planning_theme])
		self.dialog.obj.run()

	def on_settings_close(self, widget, data=None):
		"""close dialog_settings"""

		self.dialog.obj.hide()

	def on_settings_response(self, widget, response, data=None):
		if (response == gtk.RESPONSE_DELETE_EVENT):
			self.dialog.obj.hide()

	def on_hour_activate_changed(self, widget, data=None):
		"""when user change this setting, call check_date_display
		 for hide or display date, and call db.session_try_commit()
		 """

		hour_activate = widget.get_active_text().lower()
		if hour_activate == "oui":
			self.display_date = 1
		else:
			self.display_date = 0
		app.contentmgr.status_bar.check_date_display()
		db.session_try_commit()

	def on_planning_theme_changed(self, widget, data=None):
		"""when user change this setting, parse the selected theme
		in fullcalendar theme corresponding, call db.session_try_commit()
		and app.contentmgr.tabs_execute for change the theme"""

		app.settings.planning_theme = planning_themes['db_inv'][planning_themes['disp'][widget.get_active_text()]]
		db.session_try_commit()
		app.contentmgr.tabs_execute('change_theme', app.settings.planning_theme)

def init():
	"""define table settings and mapping"""

	# Database definition
	from sqlalchemy import types, orm
	from sqlalchemy.schema import Column, Table, Sequence, ForeignKey
	from sqlalchemy.orm import relationship, backref, relation, mapper

	from User import User

	t_settings = Table('settings', db.metadata,
		Column('id',					types.Integer,
			Sequence('settings_seq_id', optional = True),
			nullable	= False,
			primary_key	= True),

		Column('id_user',				types.Integer,
			ForeignKey('user.id'),
			nullable	= False),

		Column('display_date',				types.Boolean(255),
			nullable	= False,
			default		= True),

		Column('planning_theme',			types.Enum(
			    'default','pepper','blue','eggplant','lightness','mint'),
			nullable	= False,
			default		= 'pepper'),
	)

	mapper(Settings, t_settings, properties = {
		'user'		: relationship(User,
			backref		= backref('settings',
				uselist		= False,
				cascade		= "all, delete-orphan")),
	})
