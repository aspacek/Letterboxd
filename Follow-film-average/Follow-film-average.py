############################
## Follow-film-average.py ##
############################

# sys module - reads in input values
#            - exits program on error
import sys

import requests

import numpy as np

sys.path.insert(0, "../General-league-routines")
from Findstrings import findstrings
from Getstrings import getstrings

##
## Written by Alex Spacek
## January 2021
##

############################################################################
############################################################################

# Ask for username:
print('\nCompute the average rating of a film by the users followed by the entered username.')
print('\nNote: Letterboxd username needs to match how it appears in the profile URL.')
print('      i.e. letterboxd.com/<username>/')
user = input('\nEnter Letterboxd username: ')

# Ask for film:
print('\nNote: Film name needs to match how it appears in the film URL.')
print('      i.e. letterboxd.com/film/<filmname>/')
film = input('\nEnter film name: ')

# Get all usernames that the given username follows:
# Initialize results:
users = []
# The base url of followers:
url = 'https://letterboxd.com/'+user+'/following/'
# Grab source code for first page:
r = requests.get(url)
source = r.text
# Start on page 1:
# Find the users:
users = users+getstrings('all','class="avatar -a40" href="/','/"',source)
# Now loop through the rest of the pages:
page = 2
# Check if a second page exists:
lastpage = '<div class="paginate-nextprev paginate-disabled"><span class="next">'
if source.find(lastpage) == -1:
	flag = 0
else:
	flag = 1
while flag == 0:
	# Grab source code of the page:
	r = requests.get(url+'page/'+str(page)+'/')
	source = r.text
	# Check if it's the last page:
	if source.find(lastpage) != -1:
		flag = 1
	# Find the users:
	users = users+getstrings('all','class="avatar -a40" href="/','/"',source)
	# Advance the page
	page = page+1
# Take only unique users:
users = list(set(users))

# Go through all users, see if they've rated the given film, and if so get the rating:
film_ratings = []
for i in range(len(users)):
	print('')
	print('User '+str(i+1)+'/'+str(len(users))+' - '+users[i])
	# The base url:
	url = 'https://letterboxd.com/'+users[i]+'/films/'
	# Grab source code for the first page:
	r = requests.get(url)
	source = r.text
	# Find the number of pages
	# Check if there's only one:
	pages_check = list(findstrings('/films/page/',source))
	if pages_check == []:
		pages = 1
	else:
		pages = int(getstrings('last','href="/'+users[i]+'/films/page/','/">',source))
	# Initialize results:
	films = []
	ratings = []
	# Start on page 1, get the films:
	# Check if there are any films:
	films_check = list(findstrings('No films yet',source))
	if films_check != []:
		print('This user has no films!')
	else:
		films = films+getstrings('all','data-film-slug="/film/','/"',source)
		# Also get the ratings:
		# Grab all film info blocks:
		film_blocks = getstrings('all','data-film-slug="/film/','</p>',source)
		# For each, check if there is a rating, and if so, get it:
		for i in range(len(film_blocks)):
			ratings_check = list(findstrings('-darker rated-',film_blocks[i]))
			if ratings_check == []:
				ratings = ratings+['0']
			else:
				ratings = ratings+[getstrings('first','-darker rated-','">',film_blocks[i])]
		print('Page 1/'+str(pages)+' Done')
		# See if we've encountered the film yet:
		film_flag = 0
		for j in range(len(films)):
			if films[j] == film:
				film_flag = 1
				if ratings[j] != '0':
					film_ratings = film_ratings+[int(ratings[j])/2]
		# Now loop through the rest of the pages:
		pagecount = 0
		while film_flag == 0 and pagecount < pages-1:
			# Start on page 2:
			page = str(pagecount + 2)
			# Grab source code of the page:
			r = requests.get(url+'page/'+page+'/')
			source = r.text
			# Get the films:
			films = films+getstrings('all','data-film-slug="/film/','/"',source)
			# Also get the ratings:
			# Grab all film info blocks:
			film_blocks = getstrings('all','data-film-slug="/film/','</p>',source)
			# For each, check if there is a rating, and if so, get it:
			for i in range(len(film_blocks)):
				ratings_check = list(findstrings('-darker rated-',film_blocks[i]))
				if ratings_check == []:
					ratings = ratings+['0']
				else:
					ratings = ratings+[getstrings('first','-darker rated-','">',film_blocks[i])]
			print('Page '+page+'/'+str(pages)+' Done')
			# See if we've encountered the film yet:
			for j in range(len(films)):
				if films[j] == film:
					film_flag = 1
					if ratings[j] != '0':
						film_ratings = film_ratings+[int(ratings[j])/2]
			pagecount = pagecount+1

if film_ratings == []:
	print('')
	print('*****************************************************')
	print('*****************************************************')
	print('')
	print('Film = '+film)
	print('Username = '+user)
	print('')
	print('No one that the entered username follows has rated the film!')
	print('')
else:

	# Compute number of users who have given each rating:
	rated_0p5 = 0
	rated_1 = 0
	rated_1p5 = 0
	rated_2 = 0
	rated_2p5 = 0
	rated_3 = 0
	rated_3p5 = 0
	rated_4 = 0
	rated_4p5 = 0
	rated_5 = 0
	for i in range(len(film_ratings)):
		if film_ratings[i] == 0.5:
			rated_0p5 = rated_0p5+1
		elif film_ratings[i] == 1:
			rated_1 = rated_1+1
		elif film_ratings[i] == 1.5:
			rated_1p5 = rated_1p5+1
		elif film_ratings[i] == 2:
			rated_2 = rated_2+1
		elif film_ratings[i] == 2.5:
			rated_2p5 = rated_2p5+1
		elif film_ratings[i] == 3:
			rated_3 = rated_3+1
		elif film_ratings[i] == 3.5:
			rated_3p5 = rated_3p5+1
		elif film_ratings[i] == 4:
			rated_4 = rated_4+1
		elif film_ratings[i] == 4.5:
			rated_4p5 = rated_4p5+1
		elif film_ratings[i] == 5:
			rated_5 = rated_5+1
	
	# Print out results:
	print('')
	print('*****************************************************')
	print('*****************************************************')
	print('')
	print('The average rating has been compiled for the entered film,')
	print('by the users that the entered username follows.')
	print('Film = '+film)
	print('Username = '+user)
	print('')
	print('Average rating = {:5.3f}'.format(np.average(film_ratings)))
	print('')
	print('Number of users that username follows = '+str(len(users)))
	print('Number of them who have rated the film = '+str(len(film_ratings)))
	print('Percentage of them who have rated the film = {:5.1f}%'.format(len(film_ratings)/len(users)*100))
	print('')
	print('Number per rating:')
	print('0.5 = '+str(rated_0p5))
	print('1.0 = '+str(rated_1))
	print('1.5 = '+str(rated_1p5))
	print('2.0 = '+str(rated_2))
	print('2.5 = '+str(rated_2p5))
	print('3.0 = '+str(rated_3))
	print('3.5 = '+str(rated_3p5))
	print('4.0 = '+str(rated_4))
	print('4.5 = '+str(rated_4p5))
	print('5.0 = '+str(rated_5))
	print('')
