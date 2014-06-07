#!/usr/bin/env python

import gobject

import sys
import getopt

from Timetableasy import app

def usage():
	"""affiche les arguments possible au lancement de l'application"""

	print sys.argv[0] + " -orvh? --help"
	print "-o : go into offline mode"
	print "-r : rebuild database (drop all -> create all)"
	print "-v : active verbose mode (display activities)"
	print "-d : active debug mode"
	print "-f X: fill the db for testing with X items"
	print "--help, -h, -? : print this message"

def main():

	# parse command line parameter
	try:
		opts, args = getopt.getopt(sys.argv[1:], "orf:vdh?", ["help"])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	app.debug = False
	app.verbose = False
	app.rebuild = False
	app.db_fill = False
	app.offline = False
	app.settings = None

	for o, a in opts:
		if o == "-v":
			app.verbose = True
		elif o == "-d":
			app.debug = True
		elif o == "-r":
			app.rebuild = True
		elif o == "-f":
			if a.isdigit():
				app.db_fill = True
				app.nb = int(a)
			else:
				print "Warning: -f with a INT plz..."
		elif o == "-o":
			app.offline = True
		elif o in ("-h", "--help", "-?"):
			usage()
			sys.exit()
		else:
			assert False, "unhandled option"

	# thread init require by somes dependencies
	gobject.threads_init()

	# db init
	import db
	db.init()

	# main app run ( windows ... )
	app.connect()
	app.start()

if __name__ == "__main__":
	main()
