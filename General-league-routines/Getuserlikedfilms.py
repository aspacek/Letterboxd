##########################
## Getuserlikedfilms.py ##
##########################

# sys module - reads in input values
#            - exits program on error
import sys

import requests

from Findstrings import findstrings
from Getstrings import getstrings

##
## Written by Alex Spacek
## Copied from Getuserfilms.py
## January 2021
## Last updated: March 2025
##

############################################################################
############################################################################

def getuserlikedfilms(user):
	# The base url:
	url = 'https://letterboxd.com/'+user+'/likes/films/'
	# Grab source code for the first page:
	r = requests.get(url)
	source = r.text
	# Find the number of pages
	# Grab a bunch of page numbers as strings
	pages = getstrings('all','/page/','/">',source)
	# Turn them into integers
	pages = [int(num) for num in pages]
	# Get the largest number, which should represent the total number of pages
	pages = max(pages)
	# Initialize results:
	films = []
	ratings = []
	# Start on page 1, get the films:
	films = films+getstrings('all','data-film-slug="','"',source)
	# Also get the ratings:
	# Also get the ratings:
	# Grab all film info blocks:
	film_blocks = getstrings('all','<li class="poster-container">','</li>',source)
	# For each, check if there is a rating, and if so, get it:
	for block in film_blocks:
		ratings_check = list(findstrings('-darker rated-',block))
		if ratings_check == []:
			ratings = ratings+['0']
		else:
			ratings = ratings+[getstrings('first','-darker rated-','"',block)]
	print('')
	print('Page 1/'+str(pages)+' Done')
	# Now loop through the rest of the pages:
	for page in range(pages-1):
		# Start on page 2:
		page = str(page + 2)
		# Grab source code of the page:
		r = requests.get(url+'page/'+page+'/')
		source = r.text
		# Get the films:
		films = films+getstrings('all','data-film-slug="','"',source)
		# Also get the ratings:
		# Grab all film info blocks:
		film_blocks = getstrings('all','<li class="poster-container">','</li>',source)
		# For each, check if there is a rating, and if so, get it:
		for block in film_blocks:
			ratings_check = list(findstrings('-darker rated-',block))
			if ratings_check == []:
				ratings = ratings+['0']
			else:
				ratings = ratings+[getstrings('first','-darker rated-','"',block)]
		print('Page '+page+'/'+str(pages)+' Done')
	return films,ratings
