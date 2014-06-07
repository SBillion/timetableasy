import pygtk
pygtk.require("2.0")
import gtk



class ComboMgmt(object) :
	def __init__(self, combo, list, obj_crt = None, txt = None):
		from db import db

		self.completement = gtk.EntryCompletion()
		self.iter = None
		self.list_store = gtk.ListStore(str, object)
		for obj in list:
			func = getattr(obj, "cb_combobox", None)
			if callable(func):
				name = func()
			else:
				name = obj.name


			iter = self.list_store.append([name, obj])
			if obj_crt == obj:
				self.iter = iter


		self.combo = combo
		self.combo.set_model(self.list_store)
		self.combo.set_text_column(0)
		self.completement.set_model(self.list_store)
		self.saisie = self.combo.get_child()
		self.saisie.set_completion(self.completement)
		self.completement.set_text_column(0)
		self.completement.set_inline_completion(True)
		self.completement.set_popup_completion(True)
		self.completement.set_inline_selection(True)
		self.completement.connect('match-selected', self.match_cb)
		self.saisie.connect('activate', self.activate_cb)
		self.saisie.connect('changed', self.change_cb)
		self.str = ''
		self.treemodelfilter = self.list_store.filter_new()
		self.treemodelfilter.set_visible_func(self.myfilter)
		#self.combo.set_model(self.treemodelfilter)
		#if self.iter:
		#	path = self.list_store.get_path(self.iter)
		#	self.iter = self.treemodelfilter.get_iter(path)
		if self.iter:
			self.combo.set_active_iter(self.iter)
		elif txt:
			self.saisie.set_text(txt)

	def get_selected_object(self):
		iter = self.combo.get_active_iter()
		if iter:
			return self.list_store.get_value(iter, 1)
		return None

	def match_cb(self, completement, model, iter):
		return

	def activate_cb(self, saisie):
		texte = saisie.get_text()
		if texte:
			if texte not in [ligne[0] for ligne in self.list_store]:
				self.list_store.append([texte])
		return

	def myfilter(self, model, iter):
		value = model.get_value(iter, 0)
		if value.find(self.str) == -1:
			return False
		return True

	def change_cb(self, saisie):
		self.str = saisie.get_text()
		self.treemodelfilter.refilter()
		return
