#############################
## Follow-films-toplist.py ##
#############################

# sys module - reads in input values
#            - exits program on error
import sys

import requests

import numpy as np

sys.path.insert(0, "../General-league-routines")
from Findstrings import findstrings
from Getstrings import getstrings
from Numsort import numsort

##
## Written by Alex Spacek
## January 2021
##

############################################################################
############################################################################

# Ask for username:
print('\nCompute the top films by average rating,')
print('by the users that the entered username follows.')
print('\nNote: Letterboxd username needs to match how it appears in the profile URL.')
print('      i.e. letterboxd.com/<username>/')
user = input('\nEnter Letterboxd username: ')

# How many top films?:
number = int(input('\nEnter the number of top films to get: '))

# Minimum number of ratings:
min_ratings = int(input('\nEnter the minimum number of ratings a film should have: '))

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

# Go through all users and get all of their film ratings:
full_films = []
full_ratings = []
full_counts = []
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
		# Now loop through the rest of the pages:
		for pagecount in range(pages-1):
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

	# Add films and ratings to the total list:
	for j in range(len(films)):
		if ratings[j] != '0' and films[j] != '' and films[j] != ' ':
			k = 0
			found_flag = 0
			while found_flag == 0 and k < len(full_films):
				if films[j] == full_films[k]:
					found_flag = 1
					full_ratings[k] = full_ratings[k]+int(ratings[j])/2
					full_counts[k] = full_counts[k]+1
				k = k+1
			if found_flag == 0:
				full_films = full_films+[films[j]]
				full_ratings = full_ratings+[int(ratings[j])/2]
				full_counts = full_counts+[1]

# Convert all ratings to averages:
full_averages = []
for i in range(len(full_ratings)):
	full_averages = full_averages+[full_ratings[i]/full_counts[i]]

# Save the 20 most popular:
full_counts_temp = [val for val in full_counts]
full_films_temp = [val for val in full_films]
popular_counts,popular_films = numsort(full_counts_temp,full_films_temp,1,1)
popular_counts = popular_counts[:20]
popular_films = popular_films[:20]

# Apply the min_ratings criteria given:
cut_films = []
cut_averages = []
cut_counts = []
for i in range(len(full_films)):
	if full_counts[i] >= min_ratings:
		cut_films = cut_films+[full_films[i]]
		cut_averages = cut_averages+[full_averages[i]]
		cut_counts = cut_counts+[full_counts[i]]

# Sort by highest rating first:
cut_averages_temp = [val for val in cut_averages]
cut_films_temp = [val for val in cut_films]
sorted_averages,sorted_films = numsort(cut_averages_temp,cut_films_temp,1,1)
cut_averages_temp = [val for val in cut_averages]
cut_counts_temp = [val for val in cut_counts]
sorted_averages,sorted_counts = numsort(cut_averages_temp,cut_counts_temp,0,1)

# Only take the top number given:
final_films = [val for val in sorted_films]
final_averages = [val for val in sorted_averages]
final_counts = [val for val in sorted_counts]
if len(final_films) > number:
	final_films = final_films[:number]
	final_averages = final_averages[:number]
	final_counts = final_counts[:number]

# Print out results:
print('')
print('*****************************************************')
print('*****************************************************')
print('')
print('The top '+str(number)+' rated films, by the users that '+user+' follows.')
print('\nThe minimum number of ratings to qualify = '+str(min_ratings))
print('')
print('Ranking / Avg Rating / # Ratings / Film')
print('--------/------------/-----------/-----')
for i in range(len(final_films)):
	print('{:<7d} / {:<10.3f} / {:<9d} / {}'.format(i+1,final_averages[i],final_counts[i],final_films[i]))
print('')
print('The 20 most popular films:\n')
print('Ranking / # Ratings / Film')
print('--------/-----------/-----')
for i in range(len(popular_films)):
	print('{:<7d} / {:<9d} / {}'.format(i+1,popular_counts[i],popular_films[i]))
print('')
