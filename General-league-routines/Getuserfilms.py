#####################
## Getuserfilms.py ##
#####################

# sys module - reads in input values
#            - exits program on error
import sys

import requests

from Findstrings import findstrings
from Getstrings import getstrings

##
## Written by Alex Spacek
## January 2020
##

############################################################################
############################################################################

def getuserfilms(user):
	# The base url:
	url = 'https://letterboxd.com/'+user+'/films/'
	# Grab source code for the first page:
	r = requests.get(url)
	source = r.text
	# Find the number of pages
	pages = int(getstrings('last','href="/'+user+'/films/page/','/">',source))
	# Initialize results:
	films = []
	ratings = []
	# Start on page 1, get the films:
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
	return films,ratings
