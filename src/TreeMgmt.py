import gtk
import gobject

import time
import threading
import thread

class TreeRowMgmt(object):

	def __init__(self, tree, iter, iter_parent, obj, obj_parent, action):
		self.tree = tree
		self.iter = iter
		self.iter_parent = iter_parent
		self.obj = obj
		self.obj_parent = obj_parent
		self.action = action
		self.childs = []
		self.expanded = False
		self.row_parent = None
		self.id = 0

	def add_child(self, child):
		self.childs.append(child)
		child.row[self.tree.id].id = len(self.childs) - 1
		child.row[self.tree.id].row_parent = self


class TreeRowMgmtSeparator(object):

	def __init__(self, func, obj, text, pixbuf = None, tooltip = None):
		self.func = func
		self.obj = obj
		self.pixbuf = pixbuf
		self.text = text
		self.tooltip = tooltip

	# TreeMgmt Callbacks
	def cb_tree_plug(self, tree, iter, id):
		"""plug object's childs in the tree"""
		self.func(self.obj, tree, iter, self)

	def cb_tree_pixbuf(self, tree, id):
		"""return the pixbuf for the tree"""
		return self.pixbuf

	def cb_tree_name(self, tree, id):
		"""return the name for the tree"""
		return self.text

	def cb_tree_tooltip_text(self, tree, id):
		"""return the tooltip text for the tree"""
		return self.tooltip


class TreeMgmt(object):

	def __init__(self, column_names, column_callbacks,
	    tree_id, populate_func):
		# init var
		self.id = tree_id
		self.column_names = column_names
		self.column_callbacks = column_callbacks
		self.click_simulated = False
		self.__next = None
		self.start_editing = None

		# Model
		#self.treestore = gtk.TreeStore(object, str)
		self.treestore = gtk.TreeStore(object, str, gtk.gdk.Pixbuf, str)

		# View
		self.treeview = gtk.TreeView()
		#self.treeview.set_search_column(0)
		#self.treeview.set_tooltip_column(1)
		self.treeview.set_search_column(1)
		self.treeview.set_tooltip_column(3)
		self.treeview.set_property('headers-visible', False);
		self.treeview.set_property('has-tooltip', True);

		# Controller
		self.treeview.connect('button_press_event', self.button_press_event)
		self.treeview.connect('row-activated', self.row_activated)
		self.treeview.connect('row-expanded', self.row_expanded)

		self.tvcolumn = [None] * len(self.column_names)
		self.tvcolumn[0] = gtk.TreeViewColumn(self.column_names[0])
		cellpb = gtk.CellRendererPixbuf()
		self.tvcolumn[0].pack_start(cellpb, False)
		self.tvcolumn[0].set_attributes(cellpb, pixbuf=2)
		#self.tvcolumn[0].set_cell_data_func(cellpb, self.pixbuf)
		cell = gtk.CellRendererText()
		cell.connect_after( 'edited', self.edited, 0)
		cell.connect_after( 'editing-started', self.editing_started, 0)
		cell.connect_after( 'editing-canceled', self.editing_canceled, 0)
		self.tvcolumn[0].pack_start(cell, True)
		self.tvcolumn[0].set_attributes(cell, text=1)
		#self.tvcolumn[0].set_cell_data_func(cell, self.name)
		self.treeview.append_column(self.tvcolumn[0])
		if len(self.column_names) > 1:
			i = len(self.column_names)
			# XXX debug
			print "XXX len(self.column_names): " + str(i)
			for n in range(1, len(self.column_names)):
				cell = gtk.CellRendererText()
				self.tvcolumn[n] = gtk.TreeViewColumn(self.column_names[n], cell)
				self.tvcolumn[n].set_cell_data_func(cell, self.rendercell, n)
				self.treeview.append_column(self.tvcolumn[n])

		# link view and model
		self.treeview.set_model(self.treestore)

		self.root = TreeRowMgmt(self, None, None, None, None, False)

		self.populate_func = populate_func
		self.populate_func(self)

	def column_visible(self, visible = True):
		if (visible == False):
			self.treeview.set_property('headers-visible', False);
			return
		self.treeview.set_property('headers-visible', True);

	def plug(self, iter_parent, obj, obj_parent, parent = None):
		iter = self.plug_action(iter_parent, obj, obj_parent, None,
		    parent)

		func = getattr(obj, "cb_tree_isplugable", None)
		if callable(func):
			is_plugable = func(self, self.id)
		else:
			is_plugable = True

		tmp_iter = None
		if is_plugable:
			func = getattr(obj, "cb_tree_plug", None)
			if callable(func):
				# insert a temporary child to have the expand button
				tmp_iter = self.treestore.prepend(iter,
				    [self, "Chargement...", None,
				    "Merci de patienter"])
		obj.row[self.id].tmp_iter = tmp_iter;

		return iter

	def plug_group(self, iter_parent, obj, obj_parent, action_id,
	    parent = None):
		iter = self.plug_action(iter_parent, obj, obj_parent, action_id,
		    parent)

		func = getattr(obj, "cb_tree_isplugable", None)
		if callable(func):
			is_plugable = func(self, self.id)
		else:
			is_plugable = True

		tmp_iter = None
		if is_plugable:
			func = getattr(obj, "cb_tree_plug", None)
			if callable(func):
				# insert a temporary child to have the expand button
				tmp_iter = self.treestore.prepend(iter,
				    [self, None, None, None])
		obj.row[self.id].tmp_iter = tmp_iter;

		return iter

	def plug_action(self, iter_parent, obj, obj_parent, action_id,
	    parent = None):
		iter = self.treestore.prepend(iter_parent, [obj, None, None, None])

		if not hasattr(obj, 'row'):
			obj.row = {}
		obj.row[self.id] = TreeRowMgmt(self, iter, iter_parent, obj,
		    obj_parent, action_id)
		if parent:
			parent.row[self.id].add_child(obj)
		elif obj_parent:
			obj_parent.row[self.id].add_child(obj)
		else:
			self.root.add_child(obj)

		func = getattr(obj, "cb_tree_name", None)
		if callable(func):
			self.treestore.set_value(iter, 1, func(self, self.id))

		func = getattr(obj, "cb_tree_pixbuf", None)
		if callable(func):
			self.treestore.set_value(iter, 2, func(self, self.id))

		func = getattr(obj, "cb_tree_tooltip_text", None)
		if callable(func):
			self.treestore.set_value(iter, 3, func(self, self.id))

		return iter

	def unplug(self, obj):
		self.treestore.remove(obj.row[self.id].iter)

	def replug(self, obj):
		if not obj:
			for child in self.root.childs:
				self.treestore.remove(child.row[self.id].iter)
			self.root.childs = []
			self.populate_func(self)
			return

		for child in obj.row[self.id].childs:
			self.treestore.remove(child.row[self.id].iter)
		obj.row[self.id].childs = []
		iter = obj.row[self.id].iter

		self.refresh_obj(obj, iter)

		self.treeview.expand_row(
		    self.treestore.get_path(obj.row[self.id].iter),
		    False)

	@classmethod
	def replug_parents(cls, obj):
		if not hasattr(obj, 'row'):
			return
		# replug each tree parent
		for id in obj.row:
			obj.row[id].tree.replug(obj.row[id].row_parent.obj)

	@classmethod
	def replug_self(cls, obj):
		if not hasattr(obj, 'row'):
			return
		for id in obj.row:
			obj.row[id].tree.replug(obj)

	@classmethod
	def parent_action(cls, obj, id):
		if not hasattr(obj, 'row'):
			return None
		if obj.row[id].row_parent:
			return obj.row[id].row_parent.obj.row[id].action
		return None

	# callback for cell rendering
	# XXX remove this function, first study the "cb_tree_iseditable" case
	def name(self, column, cell, model, iter):
		obj = model.get_value(iter, 0)
		func = getattr(obj, "cb_tree_name", None)
		if callable(func):
			text = func(self, self.id)
		else:
			text = None
		cell.set_property('text', text)
		func = getattr(obj, "cb_tree_iseditable", None)
		if callable(func):
			edit = func(self, 0, self.id)
		else:
			edit = False
		cell.set_property('editable', edit)

	def rendercell(self, column, cell, model, iter, columnno):
		obj = model.get_value(iter, 0)
		func = getattr(obj, self.column_callbacks[columnno], None)
		if callable(func):
			text = func(self, self.id)
		else:
			text = None
		cell.set_property('text', text)
		func = getattr(obj, "cb_tree_iseditable", None)
		if callable(func):
			edit = func(self, columnno, self.id)
		else:
			edit = False
		cell.set_property('editable', edit)

	# action callback
	def editing_started(self, cell, editable, path, column):
		self.start_editing = cell

	def editing_canceled(self, cell, column):
		self.start_editing = None

	def edited( self, cell, path, new_text, column ):
		self.start_editing = None
		obj = self.treestore.get_value(self.treestore.get_iter(path), 0)
		# XXX hack to have editing and selecting functionnalities
		if cell.get_property('text') != new_text:
			func = getattr(obj, "on_edited", None)
			if callable(func):
				return func(self, new_text, self.id)

	def button_press_event(self, widget, event):
		# XXX hack to allow row-activated with editing, keep it ?
		if event.button == 1:
			if event.type == gtk.gdk._2BUTTON_PRESS:
				#if self.start_editing:
				#	self.start_editing.stop_editing(True)
				x = int(event.x)
				y = int(event.y)
				pthinfo = self.treeview.get_path_at_pos(x, y)
				if pthinfo is not None:
					path, col, cellx, celly = pthinfo
					self.treeview.set_cursor(path, col, 0)
					self.treeview.emit("row-activated", path, col)
				return True

		elif event.button == 3:
			x = int(event.x)
			y = int(event.y)
			pthinfo = self.treeview.get_path_at_pos(x, y)
			if pthinfo is not None:
				path, col, cellx, celly = pthinfo
				obj = self.treestore.get_value(self.treestore.get_iter(path), 0)
				self.treeview.grab_focus()
				self.treeview.set_cursor(path, col, 0)
				func = getattr(obj, "on_tree_rightclick", None)
				if callable(func):
					return func(self, event, self.id)

	def row_activated(self, treeview, path, column):
		obj = self.treestore.get_value(self.treestore.get_iter(path), 0)
		func = getattr(obj, "on_tree_selected", None)
		if callable(func):
			return func(self, self.id)

	def row_expanded(self, treeview, iter, path):
		obj = self.treestore.get_value(self.treestore.get_iter(path), 0)
		if obj.row[self.id].expanded:
			return
		self.refresh_obj(obj, iter)

	def refresh_obj(self, obj, iter):
		obj.row[self.id].expanded = True

		func = getattr(obj, "cb_tree_plug", None)
		if callable(func):
			func(self, iter, self.id)

		func = getattr(obj, "cb_tree_name", None)
		if callable(func):
			self.treestore.set_value(iter, 1, func(self, self.id))

		func = getattr(obj, "cb_tree_pixbuf", None)
		if callable(func):
			self.treestore.set_value(iter, 2, func(self, self.id))

		func = getattr(obj, "cb_tree_tooltip_text", None)
		if callable(func):
			self.treestore.set_value(iter, 3, func(self, self.id))

		if obj.row[self.id].tmp_iter:
			self.treestore.remove(obj.row[self.id].tmp_iter)
			obj.row[self.id].tmp_iter = None

