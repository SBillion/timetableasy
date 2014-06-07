make builddeb
lintian -IviE --display-experimental --pedantic -L ">=wishlist" --color auto --show-overrides --checksums ../timetableasy_1.0_i386.changes >../log.txt

