import gtk

import xml.dom.pulldom as xml
from os.path import normpath

class GtkMap(object):

	def __init__(self, obj, widget_mapping, mapper_mapping):
		self.obj = obj
		self.hidden = False
		self.father = None
		self.map = {}
		self.widget_mapping = widget_mapping
		self.mapper_mapping = mapper_mapping

	def add_child(self, name, child):
		map = GtkMap(child, name[2], name[3])
		map.father = self
		self.map_child(name, map)
		return map

	def map_child(self, name, map):
		if self.hidden:
			self.father.map_child(name, map)
		else:
			if name[1] == True:
				map.hidden = True
			else:
				self.map[name[0]] = map

	def __display__(self, prec):
		for id in self.map.keys():
			map = self.map[id]
			txt = prec + "." + id
			tab = 6 - len(txt) / 8
			for i in range(tab):
				txt += '\t'
			if map.widget_mapping:
				txt += " : widget self." + id
			elif map.mapper_mapping:
				if len(map.map) == 0:
					txt += " : widget self." + id
				else:
					txt += " : mapper self." + id
			print txt
			map.__display__(prec + "." + id)

	def __getattr__(self, name):
		if name in self.map:
			child = self.map[name]
			if len(child.map) == 0:
				return child.obj
			return child
		return None

class GtkMapper(object):

	def __init__(self, file, obj, debug = False):
		self.file = file
		self.obj = obj
		self.builder = gtk.Builder()
		self.glade = GtkMap(None, False, False)

		self.builder.add_from_file(normpath(file))
		self.builder.connect_signals(obj)

		doc = xml.parse(normpath(file))
		father = self.glade
		last = None
		level = 0

		for event, node in doc:
			if event == xml.START_ELEMENT:
				if node.localName == "object":
					name = node.attributes.get('id').value
					child = self.builder.get_object(name)
					name = self.resolve_name(name)
					last = father.add_child(name, child)
					if name[2] == True:
						setattr(self.obj, name[0], child)
					if name[3] == True:
						setattr(self.obj, name[0], last)
				elif node.localName == "child":
					level += 1
					father = last
					last = None
			elif event == xml.END_ELEMENT:
				if node.localName == "child":
					level -= 1
					last = father
					father = father.father
		if debug:
			print ''
			print 'file ' + self.file + ' : '
			self.glade.__display__("root")
			print ''

	def resolve_name(self, name):
		part = name.rpartition('.')
		if not part[0]:
			return (part[2], False, False, False)
		subpart = part[0].rpartition('.')
		if part[2] == '~':
			return (subpart[2], True, False, False)
		elif part[2] == '$':
			return (subpart[2], False, True, False)
		elif part[2] == '^':
			return (subpart[2], False, False, True)
		return (part[2], False, False, False)
