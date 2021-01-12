"My repository for all my various Letterboxd routines."

All programs tested using Python 3.7.9.

Explaining all folders/programs:

Directors League:
	* To run the Directors League program, in the Directors-league folder, do:
		> python Run_directors_league.py
	* It will ask for a username,
		which is taken from the user's Letterboxd URL, i.e.
		letterboxd.com/<username>/
	* You can omit films from the Directors League statistics,
		for a particular director of a film or for all directors of a film.
		You put them in the file Films-that-dont-count.txt.
		The format is:
		<film_name>,<who>
		Where <film_name> is the film's name from its Letterboxd URL, i.e.
		letterboxd.com/film/<film_name>/
		And <who> is either a director's name as it appears in the crew, i.e.
		<film_name>,Patty Jenkins
		Or "xallx" to remove that film for all directors, i.e.
		<film_name>,xallx
		Examples:
			To not count Fantasia 2000 for James Algar
			(but still count it for the other directors):
			fantasia-2000,James Algar
			To not count Fantasia 2000 for all of its directors:
			fantasia-2000,xallx
	* The folder Saved-data-files contains the results in:
		Output-<username>.txt
	* The folder Saved-data-files also contains saved data files,
		for each <username>, if a previous run has been done.
		These files are used to give any specific changes in the results
		if the program is run again.

Actors League:
	* To run the Actors League program, in the Actors-league folder, do:
		> python Run_actors_league.py
	* It will ask for a username,
		which is taken from the user's Letterboxd URL, i.e.
		letterboxd.com/<username>/
	* You can omit films from the Actors League statistics,
		for a particular actor in a film or for all actors in a film.
		You put them in the file Films-that-dont-count.txt.
		The format is:
		<film_name>,<who>
		Where <film_name> is either the film's name from its Letterboxd URL, i.e.
		letterboxd.com/film/<film_name>/
		Or "xallx" to remove all films by the given actor;
		And <who> is either an actor's name as it appears in the cast, i.e.
		<film_name>,Joseph Gordon-Levitt
		Or "xallx" to remove that film for all directors, i.e.
		<film_name>,xallx
		Examples:
			To not count Danny DeVito at all in the statistics:
			xallx,Danny DeVito			
			To not count Hercules for Danny DeVito
			(but still count it for the other actors):
			hercules-1997,Danny DeVito
			To not count Hercules for any of its actors:
			hercules-1997,xallx
	* The folder Saved-data-files contains the results in:
		Output-<username>.txt
	* The folder Saved-data-files also contains saved data files,
		for each <username>, if a previous run has been done.
		These files are used to give any specific changes in the results
		if the program is run again.
