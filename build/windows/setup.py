# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe
import glob
import sys


data_files = [
	(r'graphics', glob.glob('..\graphics\*.glade')),
	(r'graphics\images', glob.glob('..\graphics\images\*.png')),
	(r'graphics\images', glob.glob('..\graphics\images\*.gif')),
	(r'graphics\images', glob.glob('..\graphics\images\*.jpg')),
	(r'graphics\fullcalendar', glob.glob('../graphics/fullcalendar/*.*')),
	(r'graphics\fullcalendar\jquery', glob.glob('../graphics/fullcalendar/jquery/*.*')),
	(r'graphics\fullcalendar\theme\default', glob.glob('../graphics/fullcalendar/theme/default/*.*')),
	(r'graphics\fullcalendar\theme\blue', glob.glob('../graphics/fullcalendar/theme/blue/*.*')),
	(r'graphics\fullcalendar\theme\lightness', glob.glob('../graphics/fullcalendar/theme/lightness/*.*')),
	(r'graphics\fullcalendar\theme\pepper', glob.glob('../graphics/fullcalendar/theme/pepper/*.*')),
	(r'graphics\fullcalendar\theme\eggplant', glob.glob('../graphics/fullcalendar/theme/eggplant/*.*')),
	(r'graphics\fullcalendar\theme\mint', glob.glob('../graphics/fullcalendar/theme/mint/*.*')),
	(r'graphics\fullcalendar\theme\default\images', glob.glob('../graphics/fullcalendar/theme/default/images/*.*')),
	(r'graphics\fullcalendar\theme\blue\images', glob.glob('../graphics/fullcalendar/theme/blue/images/*.*')),
	(r'graphics\fullcalendar\theme\ligthness\images', glob.glob('../graphics/fullcalendar/theme/lightness/images/*.*')),
	(r'graphics\fullcalendar\theme\pepper\images', glob.glob('../graphics/fullcalendar/theme/pepper/images/*.*')),
	(r'graphics\fullcalendar\theme\eggplant\images', glob.glob('../graphics/fullcalendar/theme/eggplant/images/*.*')),
	(r'graphics\fullcalendar\theme\mint\images', glob.glob('../graphics/fullcalendar/theme/mint/images/*.*'))]
ico_file = '../windows/icon_planning.ico'
setup(name='Timetableasy',
		version='1.0',
		author='Fabien ROMANO, Léo STEVENIN, Denis DESCHAUX-BLANC, Sébastien BILLION',
		data_files=data_files,
		console = [{
			"script" :'main.py',
			"icon_resources" : [(0, ico_file)]
			}]
	)
