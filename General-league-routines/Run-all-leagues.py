########################
## Run-all-leagues.py ##
########################

import os
import sys

from Getuserfilms import getuserfilms
from Getfilminfo import getfilminfo

sys.path.insert(0, "../Directors-league")
from Directors_league import directorsleague
sys.path.insert(0, "../Actors-league")
from Actors_league import actorsleague
sys.path.insert(0, "../Years-league")
from Years_league import yearsleague
sys.path.insert(0, "../Genres-league")
from Genres_league import genresleague

##
## Written by Alex Spacek
## January 2021
##

############################################################################
############################################################################

# Ask for username:
print('\nNote: Letterboxd username needs to match how it appears in the profile URL.')
print('      i.e. letterboxd.com/<username>/')
user = input('\nEnter Letterboxd username: ')

# Get user films:
films,ratings = getuserfilms(user)

# Get film info:
films,ratings,directors,actors,years,genres,runtimes = getfilminfo(films,ratings,['directors','actors','years','genres','runtimes'])

# Save film info:
save_films = [val for val in films]
save_ratings = [val for val in ratings]
save_directors = [val for val in directors]
save_actors = [val for val in actors]
save_years = [val for val in years]
save_genres = [val for val in genres]
save_runtimes = [val for val in runtimes]

# Run Directors League
if os.getcwd() == '/Users/aes/Dropbox/My Mac (Alexanders-MacBook-Pro)/Desktop/Github/Letterboxd/General-league-routines':
	os.chdir('../Directors-league')
	type = 'super'
	films = [val for val in save_films]
	ratings = [val for val in save_ratings]
	directors = [val for val in save_directors]
	runtimes = [val for val in save_runtimes]
	directorsleague(type,user,films,ratings,directors,runtimes)
	print('Directors League has been run!')
else:
	sys.exit('ERROR - in main program - Not in General-league-routines directory, cant go to and run Directors League.')

# Run Actors League
if os.getcwd() == '/Users/aes/Dropbox/My Mac (Alexanders-MacBook-Pro)/Desktop/Github/Letterboxd/Directors-league':
	os.chdir('../Actors-league')
	type = 'super'
	films = [val for val in save_films]
	ratings = [val for val in save_ratings]
	actors = [val for val in save_actors]
	runtimes = [val for val in save_runtimes]
	actorsleague(type,user,films,ratings,actors,runtimes)
	print('Actors League has been run!')
else:
	sys.exit('ERROR - in main program - Not in Directors-league directory, cant go to and run Actors League.')

# Run Years League
if os.getcwd() == '/Users/aes/Dropbox/My Mac (Alexanders-MacBook-Pro)/Desktop/Github/Letterboxd/Actors-league':
	os.chdir('../Years-league')
	type = 'super'
	films = [val for val in save_films]
	ratings = [val for val in save_ratings]
	years = [val for val in save_years]
	runtimes = [val for val in save_runtimes]
	yearsleague(type,user,films,ratings,years,runtimes)
	print('Years League has been run!')
else:
	sys.exit('ERROR - in main program - Not in Actors-league directory, cant go to and run Years League.')

# Run Genres League
if os.getcwd() == '/Users/aes/Dropbox/My Mac (Alexanders-MacBook-Pro)/Desktop/Github/Letterboxd/Years-league':
	os.chdir('../Genres-league')
	type = 'super'
	films = [val for val in save_films]
	ratings = [val for val in save_ratings]
	genres = [val for val in save_genres]
	runtimes = [val for val in save_runtimes]
	genresleague(type,user,films,ratings,genres,runtimes)
	print('Genres League has been run!')
else:
	sys.exit('ERROR - in main program - Not in Years-league directory, cant go to and run Genres League.')

# Head back to original directory:
if os.getcwd() == '/Users/aes/Dropbox/My Mac (Alexanders-MacBook-Pro)/Desktop/Github/Letterboxd/Genres-league':
	os.chdir('../General-league-routines')
else:
	sys.exit('ERROR - in main program - Not in Genres-league directory, cant smoothly finish the program.')
if os.getcwd() == '/Users/aes/Dropbox/My Mac (Alexanders-MacBook-Pro)/Desktop/Github/Letterboxd/General-league-routines':
	print('\nDone!\n')
else:
	sys.exit('ERROR - in main program - Not in General-league-routines directory, cant smoothly finish the program.')
