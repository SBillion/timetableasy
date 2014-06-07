# -*- coding: utf-8 -*-
from distutils.core import setup
import glob
import sys

data_files = [
	(r'share/timetableasy/lib', glob.glob('../lib/*.*')),
	(r'share/applications', glob.glob('../usr/share/applications/*.*')),
	(r'bin', glob.glob('../usr/bin/timetableasy')),
	(r'share/timetableasy/src', glob.glob('../../../src/*.*')),
	(r'share/timetableasy/graphics', glob.glob('../../../graphics/*.glade')),
	(r'share/timetableasy/graphics/images', glob.glob('../../../graphics/images/*.png')),
	(r'share/timetableasy/graphics/images', glob.glob('../../../graphics/images/*.gif')),
	(r'share/timetableasy/graphics/images', glob.glob('../../../graphics/images/*.jpg')),
	(r'share/timetableasy/graphics/fullcalendar', glob.glob('../../../graphics/fullcalendar/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/jquery', glob.glob('../../../graphics/fullcalendar/jquery/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/default', glob.glob('../../../graphics/fullcalendar/theme/default/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/blue', glob.glob('../../../graphics/fullcalendar/theme/blue/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/lightness', glob.glob('../../../graphics/fullcalendar/theme/lightness/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/pepper', glob.glob('../../../graphics/fullcalendar/theme/pepper/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/eggplant', glob.glob('../../../graphics/fullcalendar/theme/eggplant/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/mint', glob.glob('../../../graphics/fullcalendar/theme/mint/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/default/images', glob.glob('../../../graphics/fullcalendar/theme/default/images/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/blue/images', glob.glob('../../../graphics/fullcalendar/theme/blue/images/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/ligthness/images', glob.glob('../../../graphics/fullcalendar/theme/lightness/images/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/pepper/images', glob.glob('../../../graphics/fullcalendar/theme/pepper/images/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/eggplant/images', glob.glob('../../../graphics/fullcalendar/theme/eggplant/images/*.*')),
	(r'share/timetableasy/graphics/fullcalendar/theme/mint/images', glob.glob('../../../graphics/fullcalendar/theme/mint/images/*.*')),
	(r'share/timetableasy/',glob.glob('../../../run.sh'))]

setup(name='timetableasy',
		version='1.0',
		author='Fabien ROMANO, Léo STEVENIN, Denis DESCHAUX-BLANC, Sébastien BILLION',
		data_files=data_files)
