#########################
## Directors-league.py ##
#########################

# sys module - reads in input values
#            - exits program on error
import sys

# csv module - read and write csv files
import csv

# numpy module - compute average and standard deviation
import numpy as np

import requests

import time

import locale

from pathlib import Path

from shutil import copyfile

import os

##
## Written by Alex Spacek
## November 2020 - December 2020
##

##################################
def findstrings(substring,string):
	lastfound = -1
	while True:
		lastfound = string.find(substring,lastfound+1)
		if lastfound == -1:  
			break
		yield lastfound

##################################################
def getstrings(which,prestring,poststring,source):
	# First find the start of the number of pages string:
	length = len(prestring)
	prevalue = list(findstrings(prestring,source))
	if len(prevalue) > 0:
		# If first instance wanted:
		if which == 'first':
			prevalue = [prevalue[0]+length]
		# If last instance wanted:
		elif which == 'last':
			prevalue = [prevalue[-1]+length]
		# If all instances wanted:
		elif which == 'all':
			prevalue = [item+length for item in prevalue]
		else:
			sys.exit('ERROR - in function "getstrings" - Invalid input for "which"')
	else:
		return ''
	# Find the location of the end of string, and get the strings:
	strings = []
	for beginning in prevalue:
		end = source.find(poststring,beginning)
		value = source[beginning:end]
		strings = strings+[value]
	# If just one string desired, return a scalar, otherwise return the array:
	if which == 'first' or which == 'last':
		return strings[0]
	elif which == 'all':
		return strings

###################################################
def numsort(arraytosort,arraytomatch,isstring,highestfirst):
	# Make sure array lengths match:
	if len(arraytosort) != len(arraytomatch):
		sys.exit('ERROR - in function "numsort" - Array lengths do not match.')
	# Initialize final arrays:
	finalarraytosort = [-1 for i in arraytosort]
	if isstring == 1:
		finalarraytomatch = ['-1' for i in arraytomatch]
	else:
		finalarraytomatch = [-1 for i in arraytomatch]
	# Sort with highest value first:
	if highestfirst == 1:
		# Loop through everything until sorted:
		flag = 0
		loc = 0
		while flag == 0:
			# Find max value:
			maxval = max(arraytosort)
			# Put all max values next in the final arrays:
			toremove = []
			for i in range(len(arraytosort)):
				if arraytosort[i] == maxval:
					finalarraytosort[loc] = arraytosort[i]
					finalarraytomatch[loc] = arraytomatch[i]
					loc = loc+1
					toremove = toremove+[i]
			# Remove values already used, from back to front:
			toremove.reverse()
			for i in range(len(toremove)):
				del arraytosort[toremove[i]]
				del arraytomatch[toremove[i]]
			# If arrays are empty, done:
			if arraytosort == []:
				flag = 1
		# Make sure arrays are completely filled:
		for i in range(len(finalarraytosort)):
			if finalarraytosort[i] == -1:
				sys.exit('ERROR - in function "numsort" - Arrays not sorted correctly.')
			if isstring == 1:
				if finalarraytomatch[i] == '-1':
					sys.exit('ERROR - in function "numsort" - Arrays not sorted correctly.')
			else:
				if finalarraytomatch[i] == -1:
					sys.exit('ERROR - in function "numsort" - Arrays not sorted correctly.')
	# Sort with lowest value first:
	else:
		sys.exit('ERROR - in function "numsort" - highestfirst = 0 not implemented yet.')
	return finalarraytosort,finalarraytomatch

############################################################################
############################################################################

# Ask for username:
user = input('\nEnter Letterboxd username: ')

# Save backups of all output files in case something goes wrong:
outputpath1 = Path('Directors-league-data-'+user+'.csv')
outputpath2 = Path('Directors-league-data-'+user+'-X.csv')
outputpath3 = Path('Directors-league-data-'+user+'-other.csv')
outputpath1exists = 0
outputpath2exists = 0
outputpath3exists = 0
if outputpath1.exists():
	outputpath1exists = 1
	copyfile('Directors-league-data-'+user+'.csv','Directors-league-data-'+user+'-saved.csv')
if outputpath2.exists():
	outputpath2exists = 1
	copyfile('Directors-league-data-'+user+'-X.csv','Directors-league-data-'+user+'-X-saved.csv')
if outputpath3.exists():
	outputpath3exists = 1
	copyfile('Directors-league-data-'+user+'.csv','Directors-league-data-'+user+'-other-saved.csv')

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

# For each film, get director(s) and year:
print('')
starttime = time.time()
directors = []
years = []
runtimes = []
extra_films = []
extra_ratings = []
extra_directors = []
extra_years = []
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
	years = years+[getstrings('first','releaseYear: "','",',source)]
	# Get the runtime, if there is one:
	runtime_check = getstrings('first','<p class="text-link text-footer">\n\t\t\t\t','More details at',source)
	if runtime_check == '\n\t\t\t\t\n\t\t\t\t\t':
		runtimes = runtimes+[-1]
	else:
		runtime = getstrings('first','<p class="text-link text-footer">\n\t\t\t\t','&nbsp;min',source)
		locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
		runtime_int = locale.atoi(runtime)
		runtimes = runtimes+[runtime_int]
	# Get the director(s):
	# Check on the number of directors:
	director_check = list(findstrings('<h3><span>Director</span></h3>',source))
	# If there are multiple directors or no directors:
	if director_check == []:
		nodirector_check = list(findstrings('<h3><span>Directors</span></h3>',source))
		if nodirector_check == []:
			directors = directors+['none']
		else:
			subtext = getstrings('first','<h3><span>Directors</span></h3>','</div>',source)
			directors_temp = getstrings('all','class="text-slug">','</a>',subtext)
			for j in range(len(directors_temp)):
				if j == 0:
					directors = directors+[directors_temp[j]]
				else:
					extra_films = extra_films+[films[i]]
					extra_ratings = extra_ratings+[ratings[i]]
					extra_directors = extra_directors+[directors_temp[j]]
					extra_years = extra_years+[years[i]]
					extra_runtimes = extra_runtimes+[runtimes[i]]
	# If there is one director:
	else:
		subtext = getstrings('first','<h3><span>Director</span></h3>','</div>',source)
		directors = directors+[getstrings('first','class="text-slug">','</a>',subtext)]
	if (i+1)%50 == 0:
		print('Films '+str(i+1)+'/'+str(len(films))+' Done')
		currenttime = time.time()
		elapsedtime = currenttime-starttime
		timeperfilm = elapsedtime/(i+1)
		filmsleft = len(films)-(i+1)
		timeleft = filmsleft*timeperfilm
		print('Estimated time remaining = '+str(int(timeleft/60))+' min')

films = films+extra_films
ratings = ratings+extra_ratings
directors = directors+extra_directors
years = years+extra_years
runtimes=runtimes+extra_runtimes

# Read in films to ignore when grabbing filmographies:
ignorefilmsdatapath = Path('Films-that-dont-count.txt')
ignorefilms = 0
if ignorefilmsdatapath.exists():
	ignorefilms = 1
	filmstoignore = []
	whotoignore = []
	with open('Films-that-dont-count.txt') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			filmstoignore = filmstoignore+[row[0]]
			whotoignore = whotoignore+[row[1]]

# Film by film, get the director
# Then check all other directors
# Compile all films by the same director together
# Note which films were used to avoid repeats
new_directors = []
number_seen = []
number_rated = []
count = -1
checked = [0 for i in films]
for i in range(len(films)):
	if checked[i] == 0:
		checked[i] = 1
		if directors[i] != 'none':
			if runtimes[i] >= 40:
				skipflag = 0
				if ignorefilms == 1:
					for j in range(len(filmstoignore)):
						if filmstoignore[j] == films[i]:
							if whotoignore[j] == 'all' or whotoignore[j] == directors[i]:
								skipflag = 1
				if skipflag == 0:
					count = count+1
					new_directors = new_directors+[directors[i]]
					number_seen = number_seen+[1]
					if ratings[i] == '0':
						number_rated = number_rated+[0]
					else:
						number_rated = number_rated+[1]
					for j in range(len(films)):
						if checked[j] == 0:
							if directors[j] == directors[i]:
								checked[j] = 1
								if runtimes[j] >= 40:
									skipflag2 = 0
									if ignorefilms == 1:
										for k in range(len(filmstoignore)):
											if filmstoignore[k] == films[j]:
												if whotoignore[k] == 'all' or whotoignore[k] == directors[j]:
													skipflag2 = 1
									if skipflag2 == 0:
										number_seen[count] = number_seen[count]+1
										if ratings[j] != '0':
											number_rated[count] = number_rated[count]+1

# Rank directors by number of films rated:
number_rated_temp = [val for val in number_rated]
new_directors_temp = [val for val in new_directors]
srated,sdirectors = numsort(number_rated_temp,new_directors_temp,1,1)
number_rated_temp = [val for val in number_rated]
number_seen_temp = [val for val in number_seen]
srated,sseen = numsort(number_rated_temp,number_seen_temp,0,1)

# Also rank directors by number of films watched:
number_seen_temp = [val for val in number_seen]
new_directors_temp = [val for val in new_directors]
sseen2,sdirectors2 = numsort(number_seen_temp,new_directors_temp,1,1)
number_seen_temp = [val for val in number_seen]
number_rated_temp = [val for val in number_rated]
sseen2,srated2 = numsort(number_seen_temp,number_rated_temp,0,1)

# Keep all directors with at least 5 rated films
# Get average rating
finaldirectors = []
finalavgratings = []
finalseen = []
finalrated = []
for i in range(len(sdirectors)):
	if srated[i] >= 5:
		finaldirectors = finaldirectors+[sdirectors[i]]
		finalseen = finalseen+[sseen[i]]
		finalrated = finalrated+[srated[i]]
		ratingsum = 0
		ratingnum = 0
		for j in range(len(films)):
			if directors[j] == sdirectors[i]:
				if runtimes[j] >= 40:
					if ratings[j] != '0':
						skipflag = 0
						if ignorefilms == 1:
							for k in range(len(filmstoignore)):
								if filmstoignore[k] == films[j]:
									if whotoignore[k] == 'all' or whotoignore[k] == sdirectors[i]:
										skipflag = 1
						if skipflag == 0:
							ratingsum = ratingsum+int(ratings[j])
							ratingnum = ratingnum+1
		ratingavg = ratingsum/ratingnum
		finalavgratings = finalavgratings+[ratingavg]

# Save the results to a temporary file:
with open('Directors-league-data-'+user+'-temp-new.csv', mode='w') as outfile:
	csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for i in range(len(finaldirectors)):
		csvwriter.writerow([finaldirectors[i],finalavgratings[i],finalseen[i],finalrated[i]])

# Check if saved file exists:
datapath = Path('Directors-league-data-'+user+'.csv')
datapathexists = 0
if datapath.exists():
	datapathexists = 1
	print('')
	print('******************************')
	print('******************************')
	# Read it in:
	saveddirectors = []
	savedavgratings = []
	savedseen = []
	savedrated = []
	with open('Directors-league-data-'+user+'.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			saveddirectors = saveddirectors+[row[0]]
			savedavgratings = savedavgratings+[float(row[1])]
			savedseen = savedseen+[int(row[2])]
			savedrated = savedrated+[int(row[3])]
	# Check if the results are different:
	differentflag = 0
	if finaldirectors != saveddirectors:
		differentflag = 1
	elif finalavgratings != savedavgratings:
		differentflag = 1
	elif finalseen != savedseen:
		differentflag = 1
	elif finalrated != savedrated:
		differentflag = 1
	if differentflag == 1:
		# Find out the differences and entries to be removed:
		for i in range(len(saveddirectors)):
			removedirectorflag = 0
			j = 0
			while removedirectorflag == 0 and j < len(finaldirectors):
				if saveddirectors[i] == finaldirectors[j]:
					removedirectorflag = 1
					if savedavgratings[i] != finalavgratings[j]:
						print(saveddirectors[i]+' - Avg Rating Changed To '+str(finalavgratings[j]/2))
					if savedseen[i] != finalseen[j]:
						print(saveddirectors[i]+' - Num Seen Changed To '+str(finalseen[j]))
					if savedrated[i] != finalrated[j]:
						print(saveddirectors[i]+' - Num Rated Changed To '+str(finalrated[j]))
				j = j+1
			if removedirectorflag == 0:
				print(saveddirectors[i]+' - Director Removed From List! (somehow)')
		# Find out new entries to add:
		for i in range(len(finaldirectors)):
			newdirectorflag = 0
			j = 0
			while newdirectorflag == 0 and j < len(saveddirectors):
				if finaldirectors[i] == saveddirectors[j]:
					newdirectorflag = 1
				j = j+1
			if newdirectorflag == 0:
				print(finaldirectors[i]+' - New Director To Add!')
				print(' - Avg Rating = '+str(finalavgratings[i]/2))
				print(' - Num Seen = '+str(finalseen[i]))
				print(' - Num Rated = '+str(finalrated[i]))
	else:
		print('No Difference! Nothing New To Add!')

# Copy old save file to a temporary file:
if datapathexists == 1:
	copyfile('Directors-league-data-'+user+'.csv','Directors-league-data-'+user+'-temp-old.csv')
# Copy new temporary file to the save file:
copyfile('Directors-league-data-'+user+'-temp-new.csv','Directors-league-data-'+user+'.csv')

# Sort by average rating:
finalavgratings_temp = [val for val in finalavgratings]
finaldirectors_temp = [val for val in finaldirectors]
sfavgratings,sfdirectors = numsort(finalavgratings_temp,finaldirectors_temp,1,1)
finalavgratings_temp = [val for val in finalavgratings]
finalseen_temp = [val for val in finalseen]
sfavgratings,sfseen = numsort(finalavgratings_temp,finalseen_temp,0,1)
finalavgratings_temp = [val for val in finalavgratings]
finalrated_temp = [val for val in finalrated]
sfavgratings,sfrated = numsort(finalavgratings_temp,finalrated_temp,0,1)

# Print final directors, films, and average ratings
print('')
print('******************************')
print('******************************')
for i in range(len(sfdirectors)):
	print('')
	print(sfdirectors[i])
	for j in range(len(films)):
		if directors[j] == sfdirectors[i]:
			if runtimes[j] >= 40:
				skipflag = 0
				if ignorefilms == 1:
					for k in range(len(filmstoignore)):
						if filmstoignore[k] == films[j]:
							if whotoignore[k] == 'all' or whotoignore[k] == sfdirectors[i]:
								skipflag = 1
				if skipflag == 0:
					if ratings[j] == '0':
						print('   '+films[j])
					else:
						print('** '+films[j])
	print('Avg rating = '+str(sfavgratings[i]/2))
	print('Number seen = '+str(sfseen[i]))
	print('Number rated = '+str(sfrated[i]))

# Also keep all directors with 4 rated films:
finaldirectorsX = []
finalseenX = []
finalratedX = []
for i in range(len(sdirectors2)):
	if srated2[i] == 4:
		finaldirectorsX = finaldirectorsX+[sdirectors2[i]]
		finalseenX = finalseenX+[sseen2[i]]
		finalratedX = finalratedX+[srated2[i]]

# Save the results to a temporary file:
with open('Directors-league-data-'+user+'-X-temp-new.csv', mode='w') as outfile:
	csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for i in range(len(finaldirectorsX)):
		csvwriter.writerow([finaldirectorsX[i],finalseenX[i],finalratedX[i]])

# Check if saved file exists:
datapathX = Path('Directors-league-data-'+user+'-X.csv')
datapathXexists = 0
if datapathX.exists():
	datapathXexists = 1
	print('')
	print('******************************')
	print('******************************')
	# Read it in:
	saveddirectorsX = []
	savedseenX = []
	savedratedX = []
	with open('Directors-league-data-'+user+'-X.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			saveddirectorsX = saveddirectorsX+[row[0]]
			savedseenX = savedseenX+[int(row[1])]
			savedratedX = savedratedX+[int(row[2])]
	# Check if the results are different:
	differentflagX = 0
	if finaldirectorsX != saveddirectorsX:
		differentflagX = 1
	elif finalseenX != savedseenX:
		differentflagX = 1
	elif finalratedX != savedratedX:
		differentflagX = 1
	if differentflagX == 1:
		# Find out the differences and entries to be removed:
		for i in range(len(saveddirectorsX)):
			removedirectorflagX = 0
			j = 0
			while removedirectorflagX == 0 and j < len(finaldirectorsX):
				if saveddirectorsX[i] == finaldirectorsX[j]:
					removedirectorflagX = 1
					if savedseenX[i] != finalseenX[j]:
						print(saveddirectorsX[i]+' - Num Seen Changed To '+str(finalseenX[j]))
					if savedratedX[i] != finalratedX[j]:
						print(saveddirectorsX[i]+' - Num Rated Changed To '+str(finalratedX[j]))
				j = j+1
			if removedirectorflagX == 0:
				print(saveddirectorsX[i]+' - Director Removed From List! (somehow)')
		# Find out new entries to add:
		for i in range(len(finaldirectorsX)):
			newdirectorflagX = 0
			j = 0
			while newdirectorflagX == 0 and j < len(saveddirectorsX):
				if finaldirectorsX[i] == saveddirectorsX[j]:
					newdirectorflagX = 1
				j = j+1
			if newdirectorflagX == 0:
				print(finaldirectorsX[i]+' - New Director To Add!')
				print(' - Num Seen = '+str(finalseenX[i]))
				print(' - Num Rated = '+str(finalratedX[i]))
	else:
		print('No Difference! Nothing New To Add!')

# Copy old save file to a temporary file:
if datapathXexists == 1:
	copyfile('Directors-league-data-'+user+'-X.csv','Directors-league-data-'+user+'-X-temp-old.csv')
# Copy new temporary file to the save file:
copyfile('Directors-league-data-'+user+'-X-temp-new.csv','Directors-league-data-'+user+'-X.csv')

# Print 4-rated director candidates, films
print('')
print('******************************')
print('******************************')
for i in range(len(finaldirectorsX)):
	print('')
	print(finaldirectorsX[i])
	print('Number seen = '+str(finalseenX[i]))
	print('Number rated = '+str(finalratedX[i]))
	for j in range(len(films)):
		if directors[j] == finaldirectorsX[i]:
			if runtimes[j] >= 40:
				skipflag = 0
				if ignorefilms == 1:
					for k in range(len(filmstoignore)):
						if filmstoignore[k] == films[j]:
							if whotoignore[k] == 'all' or whotoignore[k] == finaldirectorsX[i]:
								skipflag = 1
				if skipflag == 0:
					if ratings[j] == '0':
						print('   '+films[j])
					else:
						print('** '+films[j])

# Also keep all directors with at least 5 watched films and less than 4 rated films
# Rank by number seen, then number rated:
finaldirectors2 = []
finalseen2 = []
finalrated2 = []
for i in range(len(sdirectors2)):
	if sseen2[i] >= 5 and srated2[i] <= 3:
		if len(finaldirectors2) > 0:
			ratesortflag = 0
			j = 0
			maxloc = -1
			minloc = -1
			while ratesortflag == 0 and j < len(finaldirectors2):
				if finalseen2[j] == sseen2[i]:
					if finalrated2[j] > srated2[i]:
						maxloc = j
					elif finalrated2[j] == srated2[i]:
						loc = j
						ratesortflag = 1
					elif minloc == -1 and finalrated2[j] < srated2[i]:
						minloc = j
				j = j+1
			# No other directors with the same number seen ranked yet
			# Put current director at the end of the list:
			if ratesortflag == 0 and maxloc == -1 and minloc == -1:
				finaldirectors2 = finaldirectors2+[sdirectors2[i]]
				finalseen2 = finalseen2+[sseen2[i]]
				finalrated2 = finalrated2+[srated2[i]]
			# Same number seen already ranked, but only with higher number rated
			# Put current director at the end of the list:
			elif ratesortflag == 0 and maxloc > -1 and minloc == -1:
				finaldirectors2 = finaldirectors2+[sdirectors2[i]]
				finalseen2 = finalseen2+[sseen2[i]]
				finalrated2 = finalrated2+[srated2[i]]
			# Same number seen already ranked, but only with lower number rated
			# Put current director just above the location of the first lower number rated:
			elif ratesortflag == 0 and maxloc == -1 and minloc > -1:
				finaldirectors2.insert(minloc,sdirectors2[i])
				finalseen2.insert(minloc,sseen2[i])
				finalrated2.insert(minloc,srated2[i])
			# Same number seen already ranked, with both higher and lower number rated
			# Put current director just above the location of the first lower number rated:
			elif ratesortflag == 0 and maxloc > -1 and minloc > -1:
				finaldirectors2.insert(minloc,sdirectors2[i])
				finalseen2.insert(minloc,sseen2[i])
				finalrated2.insert(minloc,srated2[i])
			# Same number seen already ranked, exacted number rated found
			# Put current director just above the location of the first same number rated:
			elif ratesortflag == 1:
				finaldirectors2.insert(loc,sdirectors2[i])
				finalseen2.insert(loc,sseen2[i])
				finalrated2.insert(loc,srated2[i])
			# Shouldn't get this far:
			else:
				sys.exit('ERROR - in main code - Something wrong with num seen + num rated sorting.')
		else:
			finaldirectors2 = finaldirectors2+[sdirectors2[i]]
			finalseen2 = finalseen2+[sseen2[i]]
			finalrated2 = finalrated2+[srated2[i]]

# Save the results to a temporary file:
with open('Directors-league-data-'+user+'-other-temp-new.csv', mode='w') as outfile:
	csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for i in range(len(finaldirectors2)):
		csvwriter.writerow([finaldirectors2[i],finalseen2[i],finalrated2[i]])

# Check if saved file exists:
datapath2 = Path('Directors-league-data-'+user+'-other.csv')
datapath2exists = 0
if datapath2.exists():
	datapath2exists = 1
	print('')
	print('******************************')
	print('******************************')
	# Read it in:
	saveddirectors2 = []
	savedseen2 = []
	savedrated2 = []
	with open('Directors-league-data-'+user+'-other.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			saveddirectors2 = saveddirectors2+[row[0]]
			savedseen2 = savedseen2+[int(row[1])]
			savedrated2 = savedrated2+[int(row[2])]
	# Check if the results are different:
	differentflag2 = 0
	if finaldirectors2 != saveddirectors2:
		differentflag2 = 1
	elif finalseen2 != savedseen2:
		differentflag2 = 1
	elif finalrated2 != savedrated2:
		differentflag2 = 1
	if differentflag2 == 1:
		# Find out the differences and entries to be removed:
		for i in range(len(saveddirectors2)):
			removedirectorflag2 = 0
			j = 0
			while removedirectorflag2 == 0 and j < len(finaldirectors2):
				if saveddirectors2[i] == finaldirectors2[j]:
					removedirectorflag2 = 1
					if savedseen2[i] != finalseen2[j]:
						print(saveddirectors2[i]+' - Num Seen Changed To '+str(finalseen2[j]))
					if savedrated2[i] != finalrated2[j]:
						print(saveddirectors2[i]+' - Num Rated Changed To '+str(finalrated2[j]))
				j = j+1
			if removedirectorflag2 == 0:
				print(saveddirectors2[i]+' - Director Removed From List! (somehow)')
		# Find out new entries to add:
		for i in range(len(finaldirectors2)):
			newdirectorflag2 = 0
			j = 0
			while newdirectorflag2 == 0 and j < len(saveddirectors2):
				if finaldirectors2[i] == saveddirectors2[j]:
					newdirectorflag2 = 1
				j = j+1
			if newdirectorflag2 == 0:
				print(finaldirectors2[i]+' - New Director To Add!')
				print(' - Num Seen = '+str(finalseen2[i]))
				print(' - Num Rated = '+str(finalrated2[i]))
	else:
		print('No Difference! Nothing New To Add!')

# Copy old save file to a temporary file:
if datapath2exists == 1:
	copyfile('Directors-league-data-'+user+'-other.csv','Directors-league-data-'+user+'-other-temp-old.csv')
# Copy new temporary file to the save file:
copyfile('Directors-league-data-'+user+'-other-temp-new.csv','Directors-league-data-'+user+'-other.csv')

# Print most-watched director candidates, films
print('')
print('******************************')
print('******************************')
for i in range(len(finaldirectors2)):
	print('')
	print(finaldirectors2[i])
	print('Number seen = '+str(finalseen2[i]))
	print('Number rated = '+str(finalrated2[i]))
	for j in range(len(films)):
		if directors[j] == finaldirectors2[i]:
			if runtimes[j] >= 40:
				skipflag = 0
				if ignorefilms == 1:
					for k in range(len(filmstoignore)):
						if filmstoignore[k] == films[j]:
							if whotoignore[k] == 'all' or whotoignore[k] == finaldirectors2[i]:
								skipflag = 1
				if skipflag == 0:
					if ratings[j] == '0':
						print('   '+films[j])
					else:
						print('** '+films[j])

# Remove temporary files:
if outputpath1exists == 1:
	os.remove('Directors-league-data-'+user+'-saved.csv')
if outputpath2exists == 1:
	os.remove('Directors-league-data-'+user+'-X-saved.csv')
if outputpath3exists == 1:
	os.remove('Directors-league-data-'+user+'-other-saved.csv')
os.remove('Directors-league-data-'+user+'-temp-new.csv')
os.remove('Directors-league-data-'+user+'-X-temp-new.csv')
os.remove('Directors-league-data-'+user+'-other-temp-new.csv')
if datapathexists == 1:
	os.remove('Directors-league-data-'+user+'-temp-old.csv')
if datapathXexists == 1:
	os.remove('Directors-league-data-'+user+'-X-temp-old.csv')
if datapath2exists == 1:
	os.remove('Directors-league-data-'+user+'-other-temp-old.csv')
