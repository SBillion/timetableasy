import MySQLdb
import sqlalchemy
from sqlalchemy import schema, types
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm import clear_mappers
from sqlalchemy import exc
from sqlalchemy.dialects import mysql, sqlite
from sqlalchemy import schema, orm, create_engine

from Timetableasy import app

global db
db = None

class database(object):

	def __init__(self):
		self.session = None
		self.session_offline = None
		self.engine = None
		self.status = False
		self.synchro = False
		self.echo = app.debug
		self.metadata = schema.MetaData()

	def session_init(self):
		# Database session
		if app.offline:
			db.go_offline()
		else:
			db.go_online()
		db.map()
		if app.rebuild:
			db.recreate()
		if app.db_fill:
			db.db_fill(app.nb)

	def go_online(self):
		self.engine = create_engine(
		    'mysql://timetableasy:RnH9tFQVV4A5aJBa@tryphon.fr/timetableasy',
		    echo = self.echo)
		sm = orm.sessionmaker(bind = self.engine, autoflush = False,
		    autocommit = False, expire_on_commit = True)
		self.session = orm.scoped_session(sm)
		try:
			self.engine.connect()
			self.status = True
			return True
		except:
			self.go_offline()
			return False

	def go_offline(self):
		self.engine = create_engine('sqlite:///db_offline.db',
		    echo = self.echo)
		sm = orm.sessionmaker(bind = self.engine, autoflush = False,
		    autocommit = False, expire_on_commit = True)
		self.session = orm.scoped_session(sm)
		self.status = False

	def unicode(self, str):
		if self.status == True:
			str = unicode(str, 'iso8859-15')
			return str
		else:
			return str

	def synchronize(self):
		if self.status == False:
			print "Need to be online to sync"
			return

		if self.synchro == False:
			self.engine_offline = create_engine(
			    'sqlite:///db_offline.db', echo = True)
			sm = orm.sessionmaker(bind = self.engine_offline,
			    autoflush = False, autocommit = False,
			    expire_on_commit = True)
			self.session_offline = orm.scoped_session(sm)
			self.metadata.bind = self.engine_offline
			self.metadata.drop_all(checkfirst = True)
			self.metadata.create_all(checkfirst = False)
			self.metadata.bind = None
			self.synchro = True

		for table in self.metadata.sorted_tables:
			print table.name
			self.metadata.bind = self.engine
			result = table.select().execute()
			self.metadata.bind = self.engine_offline
			for row in result:
				data = {}
				i = 0
				for c in table.c:
					data[c.key] = row[i]
					i += 1
				table.insert(values = data).execute()
			self.metadata.bind = None

	def copy(self, obj_source):
		pk_keys = set([c.key for c in object_mapper(obj_source).primary_key])
		#pk_keys = []
		keys = [p.key for p in object_mapper(obj_source).iterate_properties if (p.key not in pk_keys) & (isinstance(p, sqlalchemy.orm.ColumnProperty))]

		obj_dest = obj_source.__class__.__new__(obj_source.__class__)
		obj_dest.__init__()

		if app.verbose:
			src = "src(" + str(type(obj_source)) + " " + str(obj_source)
			dst = "dst(" + str(type(obj_dest)) + " " + str(obj_dest) + ")"

		for k in keys:
			v = getattr(obj_source, k)
			if (k == "password") & (obj_source != app.user):
				v = "hidden_password"
			else:
				if  type(v) is str:
					v = self.unicode(v)
			if app.verbose:
				src += ", " + str(k) + ": " + str(type(v)) + " " + str(v)
			setattr(obj_dest, k, v)

		if app.verbose:
			src += ")"
			dst += ")"
			print src + "->" + dst

		return obj_dest

	def map(self):
		import User
		User.init_db()
		import Campus
		Campus.init()
		import Class
		Class.init()
		import ClassRoom
		ClassRoom.init()
		import Course
		Course.init()
		import Cursus
		Cursus.init()
		import Event
		Event.init()
		import Period
		Period.init()
		import Planning
		Planning.init()
		import Settings
		Settings.init()
		import University
		University.init()

	def recreate(self):
		self.metadata.drop_all(checkfirst = True, bind = self.engine)
		self.metadata.create_all(checkfirst = True, bind = self.engine)

	def session_try_commit(self):
		if (self.status == False) & (app.rebuild == False) & (app.db_fill == False) & (app.debug == False):
			print "Need to be online to commit modification"
			self.session.rollback()
		else:
			try:
				self.session.commit()
			except Exception as e:
				print "Erreure: " + str(e.args)
				self.session.rollback()

	def session_query(self, query, data, description="Aucune description"):
		# XXX update with status bar
		if app.verbose:
			print description
		try:
			result = query(self, data)
			return result
		except Exception as e:
			print "Error on " + description
			print e.args[0]
			self.session.rollback()
			return None

	def db_fill(self, number):
		from Cursus import Cursus
		from Campus import Campus
		from University import University

		univ = University()
		univ.cb_fill(number)
		del univ
		db.session_try_commit()

		cursus = Cursus()
		cursus.cb_fill(number)
		del cursus
		db.session_try_commit()

		campus = Campus()
		campus.cb_fill(number)
		del campus
		db.session_try_commit()

def init():
	global db
	db = database()
