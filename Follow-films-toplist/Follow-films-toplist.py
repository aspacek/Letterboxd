#############################
## Follow-films-toplist.py ##
#############################

# sys module - reads in input values
#            - exits program on error
import sys

import requests

import numpy as np

# csv module - read and write csv files
import csv

from pathlib import Path

from shutil import copyfile

import os

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

# Backup previous output file and open a new one:
printoutpath = Path('Saved-data-files/Output-'+user+'-'+str(number)+'-'+str(min_ratings)+'.txt')
printoutpathexists = 0
if printoutpath.exists():
	printoutpathexists = 1
	copyfile('Saved-data-files/Output-'+user+'-'+str(number)+'-'+str(min_ratings)+'.txt','Saved-data-files/Output-'+user+'-'+str(number)+'-'+str(min_ratings)+'-saved.txt')
resultsfile = open('Saved-data-files/Output-'+user+'-'+str(number)+'-'+str(min_ratings)+'.txt','w')

# Save backups of all output files in case something goes wrong:
outputpath1 = Path('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv')
outputpath2 = Path('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv')
outputpath1exists = 0
outputpath2exists = 0
if outputpath1.exists():
	outputpath1exists = 1
	copyfile('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv','Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'-saved.csv')
if outputpath2.exists():
	outputpath2exists = 1
	copyfile('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv','Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'-saved.csv')

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

# Save the results to a temporary file:
with open('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-new.csv', mode='w') as outfile:
	csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for i in range(len(final_films)):
		csvwriter.writerow([final_films[i],str(final_averages[i]),str(final_counts[i])])
with open('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-new.csv', mode='w') as outfile:
	csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for i in range(len(popular_films)):
		csvwriter.writerow([popular_films[i],str(popular_counts[i])])

# Check if saved files exist:
datapath1 = Path('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv')
datapath1exists = 0
if datapath1.exists():
	datapath1exists = 1
	resultsfile.write('\n******************************')
	resultsfile.write('\n** OVERALL RESULTS CHANGES ***')
	resultsfile.write('\n******************************')
	# Read it in:
	savedfilms = []
	savedaverages = []
	savedcounts = []
	with open('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			savedfilms = savedfilms+[row[0]]
			savedaverages = savedaverages+[float(row[1])]
			savedcounts = savedcounts+[int(row[2])]
	# Check if the results are different:
	differentflag = 0
	if final_films != savedfilms:
		differentflag = 1
	if differentflag == 1:
		# Find the differences:
		for i in range(len(final_films)):
			if final_films[i] != savedfilms[i]:
				found = 0
				j = 0
				while found == 0 and j < len(savedfilms):
					if savedfilms[j] == final_films[i]:
						found = 1
						resultsfile.write('\n'+final_films[i]+' moved from '+str(j+1)+' to '+str(i+1))
					j = j+1
				if found == 0:
					resultsfile.write('\n'+final_films[i]+' added to the list at '+str(i+1))
		for i in range(len(savedfilms)):
			if savedfilms[i] != final_films[i]:
				found = 0
				j = 0
				while found == 0 and j < len(final_films):
					if final_films[j] == savedfilms[i]:
						found = 1
					j = j+1
				if found == 0:
					resultsfile.write('\n'+savedfilms[i]+' removed from the list')
	else:
		resultsfile.write('\nNo changes to overall results!')
datapath2 = Path('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv')
datapath2exists = 0
if datapath2.exists():
	datapath2exists = 1
	resultsfile.write('\n******************************')
	resultsfile.write('\n** POPULAR RESULTS CHANGES ***')
	resultsfile.write('\n******************************')
	# Read it in:
	savedfilms = []
	savedcounts = []
	with open('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			savedfilms = savedfilms+[row[0]]
			savedcounts = savedcounts+[int(row[1])]
	# Check if the results are different:
	differentflag = 0
	if popular_films != savedfilms:
		differentflag = 1
	elif popular_counts != savedcounts:
		differentflag = 1 
	if differentflag == 1:
		# Just print the two lists:
		resultsfile.write('\nNum - Old - New')
		for i in range(len(popular_films)):
			resultsfile.write('\n('+str(i+1)+') '+savedfilms[i]+' '+str(savedcounts[i])+' - '+popular_films[i]+' '+str(popular_counts[i]))
	else:
		resultsfile.write('\nNo changes to popular results!')

# Copy old save files to temporary files:
if datapath1exists == 1:
	copyfile('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv','Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-old.csv')
if datapath2exists == 1:
	copyfile('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv','Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-old.csv')
# Copy new temporary files to the save files:
copyfile('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-new.csv','Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv')
copyfile('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-new.csv','Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'.csv')

# Print out results:
resultsfile.write('\n*****************************************************')
resultsfile.write('\n*****************************************************')
resultsfile.write('\n')
resultsfile.write('\nThe top '+str(number)+' rated films, by the users that '+user+' follows.')
resultsfile.write('\n')
resultsfile.write('\nThe minimum number of ratings to qualify = '+str(min_ratings))
resultsfile.write('\n')
resultsfile.write('\nRanking / Avg Rating / # Ratings / Film')
resultsfile.write('\n--------/------------/-----------/-----')
for i in range(len(final_films)):
	resultsfile.write('\n{:<7d} / {:<10.3f} / {:<9d} / {}'.format(i+1,final_averages[i],final_counts[i],final_films[i]))
resultsfile.write('\n')
resultsfile.write('\nThe 20 most popular films:\n')
resultsfile.write('\nRanking / # Ratings / Film')
resultsfile.write('\n--------/-----------/-----')
for i in range(len(popular_films)):
	resultsfile.write('\n{:<7d} / {:<9d} / {}'.format(i+1,popular_counts[i],popular_films[i]))
resultsfile.write('\n')

# Close output file:
resultsfile.close()
print('')
print('Results saved to Follow-films-toplist/Saved-data-files/Output-'+user+'-'+str(number)+'-'+str(min_ratings)+'.txt')
print('')

# Remove temporary files:
if printoutpathexists == 1:
	os.remove('Saved-data-files/Output-'+user+'-'+str(number)+'-'+str(min_ratings)+'-saved.txt')
if outputpath1exists == 1:
	os.remove('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'-saved.csv')
if outputpath2exists == 1:
	os.remove('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'-saved.csv')
os.remove('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-new.csv')
os.remove('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-new.csv')
if datapath1exists == 1:
	os.remove('Saved-data-files/Follow-films-toplist-data-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-old.csv')
if datapath2exists == 1:
	os.remove('Saved-data-files/Follow-films-toplist-counts-'+user+'-'+str(number)+'-'+str(min_ratings)+'-temp-old.csv')
