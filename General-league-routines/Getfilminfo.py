####################
## Getfilminfo.py ##
####################

# sys module - reads in input values
#            - exits program on error
import sys

import requests

import time

import locale

from Findstrings import findstrings
from Getstrings import getstrings

##
## Written by Alex Spacek
## January 2021
##

############################################################################
############################################################################

def getfilminfo(films,ratings,what):
	# For each film, get director(s) and year:
	starttime = time.time()
	what_dir = 0
	what_act = 0
	what_yr = 0
	what_gen = 0
	what_run = 0
	for i in range(len(what)):
		if what[i] == 'directors':
			what_dir = 1
			directors = []
		if what[i] == 'actors':
			what_act = 1
			actors = []
		if what[i] == 'years':
			what_yr = 1
			years = []
		if what[i] == 'genres':
			what_gen = 1
			genres = []
		if what[i] == 'runtimes':
			what_run = 1
			runtimes = []
	if what_dir == 1 or what_act == 1 or what_gen == 1:
		extra_films = []
		extra_ratings = []
		if what_dir == 1:
			extra_directors = []
		if what_act == 1:
			extra_actors = []
		if what_yr == 1:
			extra_years = []
		if what_gen == 1:
			extra_genres = []
		if what_run == 1:
			extra_runtimes = []
	for i in range(len(films)):
		# The base url of the film's page:
		url = 'https://letterboxd.com/film/'+films[i]+'/'
		# Grab source code for the film's page:
		r = requests.get(url)
		source = r.text
		# Get the film title:
		film_name = getstrings('last','name: "','",',source)
		# Get the film year:
		if what_yr == 1:
			years = years+[getstrings('first','<div class="releaseyear"><a href="/films/year/','/">',source)]
		# Get the runtime, if there is one:
		if what_run == 1:
			runtime_check = getstrings('first','<p class="text-link text-footer">\n\t\t\t\t\t\n\t\t\t\t\t','More at',source)
			runtime_check_test = ['0','1','2','3','4','5','6','7','8','9']
			runtime_check_flag = 0
			if runtime_check == '':
				runtime_check_flag = 2
			else:
				for val in runtime_check_test:
					if runtime_check[0] == val:
						runtime_check_flag = 1
			if runtime_check_flag == 0 or runtime_check_flag == 2:
				print('')
				print(url)
				print('No runtime found')
				print('runtime_check_flag = '+str(runtime_check_flag))
				print(runtime_check)
				runtimes = runtimes+[-1]
			else:
				runtime = getstrings('first','<p class="text-link text-footer">\n\t\t\t\t\t','&nbsp;min',source)
				locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
				if runtime != '':
					runtime_int = locale.atoi(runtime)
					runtimes = runtimes+[runtime_int]
				else:
					print('')
					print('** SOMETHING WENT WRONG IN GETTING A RUNTIME **')
					usertime = int(input('Enter the runtime (in minutes) of '+films[i]+': '))
					runtimes = runtimes+[usertime]
					print('')
		# Get the director(s):
		if what_dir == 1:
			# Check on the number of directors:
			director_check = list(findstrings('"sameAs":"/director/',source))
			# If there are multiple directors or no directors:
			if director_check == [] or len(director_check)>1:
				nodirector_check = list(findstrings('"sameAs":"/director/',source))
				if nodirector_check == []:
					directors = directors+['none']
				else:
					subtext = getstrings('first','"director":[{','}]',source)
					directors_temp = getstrings('all','"Person","name":"','"',subtext)
					for j in range(len(directors_temp)):
						if j == 0:
							directors = directors+[directors_temp[j]]
						else:
							extra_films = extra_films+[films[i]]
							extra_ratings = extra_ratings+[ratings[i]]
							extra_directors = extra_directors+[directors_temp[j]]
							if what_act == 1:
								extra_actors = extra_actors+[' ']
							if what_yr == 1:
								extra_years = extra_years+['none']
							if what_gen == 1:
								extra_genres = extra_genres+['none']
							if what_run == 1:
								extra_runtimes = extra_runtimes+[runtimes[i]]
			# If there is one director:
			else:
				subtext = getstrings('first','"director":[{','}]',source)
				directors = directors+[getstrings('first','"Person","name":"','"',subtext)]
		# Get the actors:
		if what_act == 1:
			# Check on the number of actors:
			actor_check = list(findstrings('class="text-slug tooltip">',source))
			# If there are multiple actors:
			if len(actor_check) > 1:
				actors_temp = getstrings('all','class="text-slug tooltip">','</a>',source)
				for j in range(len(actors_temp)):
					if j == 0:
						actors = actors+[actors_temp[j]]
					else:
						extra_films = extra_films+[films[i]]
						extra_ratings = extra_ratings+[ratings[i]]
						extra_actors = extra_actors+[actors_temp[j]]
						if what_dir == 1:
							extra_directors = extra_directors+['none']
						if what_yr == 1:
							extra_years = extra_years+['none']
						if what_gen == 1:
							extra_genres = extra_genres+['none']
						if what_run == 1:
							extra_runtimes = extra_runtimes+[runtimes[i]]
			# If there is one actor:
			elif len(actor_check) == 1:
				actors = actors+[getstrings('first','class="text-slug tooltip">','</a>',source)]
			# If there are no actors:
			else:
				actors = actors+[' ']
		# Get the genres:
		if what_gen == 1:
			# Check on the number of genres:
			genre_check = list(findstrings('/films/genre/',source))
			# Check on the number of "genre" labels to ignore:
			genre_ignore_check = list(findstrings('/films/genre/horror/by/rating/size/small',source))
			# Number of valid genres:
			genre_length = len(genre_check)-len(genre_ignore_check)
			# If there are multiple genres:
			if genre_length > 1:
				genres_temp = getstrings('all','/films/genre/','/"',source)
				for j in range(len(genres_temp)):
					if genres_temp[j] != 'horror/by/rating/size/small':
						if j == 0:
							genres = genres+[genres_temp[j]]
						else:
							extra_films = extra_films+[films[i]]
							extra_ratings = extra_ratings+[ratings[i]]
							extra_genres = extra_genres+[genres_temp[j]]
							if what_dir == 1:
								extra_directors = extra_directors+['none']
							if what_act == 1:
								extra_actors = extra_actors+[' ']
							if what_yr == 1:
								extra_years = extra_years+['none']
							if what_run == 1:
								extra_runtimes = extra_runtimes+[runtimes[i]]
			# If there is one genre:
			elif genre_length == 1:
				flag = 0
				if len(genre_ignore_check) == 0:
					flag = 1
					genres = genres+[getstrings('first','/films/genre/','/"',source)]
				else:
					genres_temp = getstrings('all','/films/genre/','/"',source)
					for j in range(len(genres_temp)):
						if genres_temp[j] != 'horror/by/rating/size/small':
							flag = flag+1
							genres = genres+[genres_temp[j]]
				if flag != 1:
					sys.exit('ERROR - in main program - genre extraction (of one genre) encountered an error.')
			# If there are no genres:
			else:
				genres = genres+['none']
		if (i+1)%50 == 0:
			print('Films '+str(i+1)+'/'+str(len(films))+' Done')
			currenttime = time.time()
			elapsedtime = currenttime-starttime
			timeperfilm = elapsedtime/(i+1)
			filmsleft = len(films)-(i+1)
			timeleft = filmsleft*timeperfilm
			print('Estimated time remaining = '+str(int(timeleft/60))+' min')
	if what_dir == 1 or what_act == 1 or what_gen == 1:
		films = films+extra_films
		ratings = ratings+extra_ratings
		if what_dir == 1:
			directors = directors+extra_directors
		if what_act == 1:
			actors = actors+extra_actors
		if what_yr == 1:
			years = years+extra_years
		if what_gen == 1:
			genres = genres+extra_genres
		if what_run == 1:
			runtimes=runtimes+extra_runtimes
	if what_dir == 1:
		if what_act == 1:
			if what_yr == 1:
				if what_gen == 1:
					if what_run == 1:
						return films,ratings,directors,actors,years,genres,runtimes
					else:
						return films,ratings,directors,actors,years,genres
				else:
					if what_run == 1:
						return films,ratings,directors,actors,years,runtimes
					else:
						return films,ratings,directors,actors,years
			else:
				if what_gen == 1:
					if what_run == 1:
						return films,ratings,directors,actors,genres,runtimes
					else:
						return films,ratings,directors,actors,genres
				else:
					if what_run == 1:
						return films,ratings,directors,actors,runtimes
					else:
						return films,ratings,directors,actors
		else:
			if what_yr == 1:
				if what_gen == 1:
					if what_run == 1:
						return films,ratings,directors,years,genres,runtimes
					else:
						return films,ratings,directors,years,genres
				else:
					if what_run == 1:
						return films,ratings,directors,years,runtimes
					else:
						return films,ratings,directors,years
			else:
				if what_gen == 1:
					if what_run == 1:
						return films,ratings,directors,genres,runtimes
					else:
						return films,ratings,directors,genres
				else:
					if what_run == 1:
						return films,ratings,directors,runtimes
					else:
						return films,ratings,directors
	else:
		if what_act == 1:
			if what_yr == 1:
				if what_gen == 1:
					if what_run == 1:
						return films,ratings,actors,years,genres,runtimes
					else:
						return films,ratings,actors,years,genres
				else:
					if what_run == 1:
						return films,ratings,actors,years,runtimes
					else:
						return films,ratings,actors,years
			else:
				if what_gen == 1:
					if what_run == 1:
						return films,ratings,actors,genres,runtimes
					else:
						return films,ratings,actors,genres
				else:
					if what_run == 1:
						return films,ratings,actors,runtimes
					else:
						return films,ratings,actors
		else:
			if what_yr == 1:
				if what_gen == 1:
					if what_run == 1:
						return films,ratings,years,genres,runtimes
					else:
						return films,ratings,years,genres
				else:
					if what_run == 1:
						return films,ratings,years,runtimes
					else:
						return films,ratings,years
			else:
				if what_gen == 1:
					if what_run == 1:
						return films,ratings,genres,runtimes
					else:
						return films,ratings,genres
				else:
					if what_run == 1:
						return films,ratings,runtimes
					else:
						return films,ratings
