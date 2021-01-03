#####################
## Years-league.py ##
#####################

# sys module - reads in input values
#            - exits program on error
import sys

# csv module - read and write csv files
import csv

import requests

import time

import locale

from pathlib import Path

from shutil import copyfile

import os

##
## Written by Alex Spacek
## December 2020 - January 2020
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
print('\nNote: Letterboxd username needs to match how it appears in the profile URL.')
print('      i.e. letterboxd.com/<username>/')
user = input('\nEnter Letterboxd username: ')

# Save backups of all output files in case something goes wrong:
outputpath1 = Path('Saved-data-files/Years-league-data-'+user+'.csv')
outputpath2 = Path('Saved-data-files/Years-league-data-'+user+'-X.csv')
outputpath3 = Path('Saved-data-files/Years-league-data-'+user+'-other.csv')
outputpath1exists = 0
outputpath2exists = 0
outputpath3exists = 0
if outputpath1.exists():
	outputpath1exists = 1
	copyfile('Saved-data-files/Years-league-data-'+user+'.csv','Saved-data-files/Years-league-data-'+user+'-saved.csv')
if outputpath2.exists():
	outputpath2exists = 1
	copyfile('Saved-data-files/Years-league-data-'+user+'-X.csv','Saved-data-files/Years-league-data-'+user+'-X-saved.csv')
if outputpath3.exists():
	outputpath3exists = 1
	copyfile('Saved-data-files/Years-league-data-'+user+'-other.csv','Saved-data-files/Years-league-data-'+user+'-other-saved.csv')

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

# For each film, get the year:
print('')
starttime = time.time()
years = []
runtimes = []
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
	if (i+1)%50 == 0:
		print('Films '+str(i+1)+'/'+str(len(films))+' Done')
		currenttime = time.time()
		elapsedtime = currenttime-starttime
		timeperfilm = elapsedtime/(i+1)
		filmsleft = len(films)-(i+1)
		timeleft = filmsleft*timeperfilm
		print('Estimated time remaining = '+str(int(timeleft/60))+' min')

# Read in films to ignore:
ignorefilmsdatapath = Path('Films-that-dont-count.txt')
ignorefilms = 0
if ignorefilmsdatapath.exists():
	ignorefilms = 1
	filmstoignore = []
	with open('Films-that-dont-count.txt') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			filmstoignore = filmstoignore+[row[0]]

# Film by film, get the year
# Then check all other years
# Compile all films from the same year together
# Note which films were used to avoid repeats
new_years = []
number_seen = []
number_rated = []
count = -1
checked = [0 for i in films]
for i in range(len(films)):
	if checked[i] == 0:
		checked[i] = 1
		if years[i] != 'none':
			if runtimes[i] >= 40:
				skipflag = 0
				if ignorefilms == 1:
					for j in range(len(filmstoignore)):
						if filmstoignore[j] == films[i]:
							skipflag = 1
				if skipflag == 0:
					count = count+1
					new_years = new_years+[years[i]]
					number_seen = number_seen+[1]
					if ratings[i] == '0':
						number_rated = number_rated+[0]
					else:
						if int(ratings[i]) >= 6:
							number_rated = number_rated+[1]
						else:
							number_rated = number_rated+[0]
					for j in range(len(films)):
						if checked[j] == 0:
							if years[j] == years[i]:
								checked[j] = 1
								if runtimes[j] >= 40:
									skipflag2 = 0
									if ignorefilms == 1:
										for k in range(len(filmstoignore)):
											if filmstoignore[k] == films[j]:
												skipflag2 = 1
									if skipflag2 == 0:
										number_seen[count] = number_seen[count]+1
										if ratings[j] != '0' and int(ratings[j]) >= 6:
											number_rated[count] = number_rated[count]+1

# Rank years by number of films rated:
number_rated_temp = [val for val in number_rated]
new_years_temp = [val for val in new_years]
srated,syears = numsort(number_rated_temp,new_years_temp,1,1)
number_rated_temp = [val for val in number_rated]
number_seen_temp = [val for val in number_seen]
srated,sseen = numsort(number_rated_temp,number_seen_temp,0,1)

# Also rank years by number of films watched:
number_seen_temp = [val for val in number_seen]
new_years_temp = [val for val in new_years]
sseen2,syears2 = numsort(number_seen_temp,new_years_temp,1,1)
number_seen_temp = [val for val in number_seen]
number_rated_temp = [val for val in number_rated]
sseen2,srated2 = numsort(number_seen_temp,number_rated_temp,0,1)

# Keep all years with at least 10 rated films
# Get average rating of all 3+ star films
finalyears = []
finalavgratings = []
finalseen = []
finalrated = []
for i in range(len(syears)):
	if srated[i] >= 10:
		finalyears = finalyears+[syears[i]]
		finalseen = finalseen+[sseen[i]]
		finalrated = finalrated+[srated[i]]
		ratingsum = 0
		ratingnum = 0
		for j in range(len(films)):
			if years[j] == syears[i]:
				if runtimes[j] >= 40:
					if ratings[j] != '0' and int(ratings[j]) >= 6:
						skipflag = 0
						if ignorefilms == 1:
							for k in range(len(filmstoignore)):
								if filmstoignore[k] == films[j]:
									skipflag = 1
						if skipflag == 0:
							ratingsum = ratingsum+int(ratings[j])
							ratingnum = ratingnum+1
		ratingavg = ratingsum/ratingnum
		finalavgratings = finalavgratings+[ratingavg]

# Sort by average rating:
finalavgratings_temp = [val for val in finalavgratings]
finalyears_temp = [val for val in finalyears]
sfavgratings,sfyears = numsort(finalavgratings_temp,finalyears_temp,1,1)
finalavgratings_temp = [val for val in finalavgratings]
finalseen_temp = [val for val in finalseen]
sfavgratings,sfseen = numsort(finalavgratings_temp,finalseen_temp,0,1)
finalavgratings_temp = [val for val in finalavgratings]
finalrated_temp = [val for val in finalrated]
sfavgratings,sfrated = numsort(finalavgratings_temp,finalrated_temp,0,1)

# Get print details for final years, films, and average ratings
sfyears_print = []
sffilms_print = [[] for i in range(len(sfyears))]
sffilms_count = []
sfavgratings_print = []
sfseen_print = []
sfrated_print = []
for i in range(len(sfyears)):
	sfyears_print = sfyears_print+[sfyears[i]]
	sffilms_count = sffilms_count+[0]
	for j in range(len(films)):
		if years[j] == sfyears[i]:
			if runtimes[j] >= 40:
				skipflag = 0
				if ignorefilms == 1:
					for k in range(len(filmstoignore)):
						if filmstoignore[k] == films[j]:
							skipflag = 1
				if skipflag == 0:
					sffilms_count[i] = sffilms_count[i]+1
					if ratings[j] == '0':
						sffilms_print[i] = sffilms_print[i]+['   '+films[j]]
					elif int(ratings[j]) < 6:
						sffilms_print[i] = sffilms_print[i]+['-- '+films[j]]
					else:
						sffilms_print[i] = sffilms_print[i]+['** '+films[j]]
	sfavgratings_print = sfavgratings_print+[str(sfavgratings[i]/2)]
	sfseen_print = sfseen_print+[str(sfseen[i])]
	sfrated_print = sfrated_print+[str(sfrated[i])]

# Save the results to a temporary file:
with open('Saved-data-files/Years-league-data-'+user+'-temp-new.csv', mode='w') as outfile:
	csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for i in range(len(sfyears_print)):
		csvwriter.writerow([sfyears_print[i],sffilms_count[i],sfavgratings_print[i],sfseen_print[i],sfrated_print[i]])
		for j in range(sffilms_count[i]):
			csvwriter.writerow([sffilms_print[i][j]])

# Check if saved file exists:
datapath = Path('Saved-data-files/Years-league-data-'+user+'.csv')
datapathexists = 0
if datapath.exists():
	datapathexists = 1
	print('')
	print('******************************')
	print('** LEAGUE RESULTS CHANGES ****')
	print('******************************')
	# Read it in:
	savedyears = []
	savedfilms_count = []
	savedfilms = []
	savedavgratings = []
	savedseen = []
	savedrated = []
	with open('Saved-data-files/Years-league-data-'+user+'.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		count = 0
		flag = 0
		i = -1
		for row in csv_reader:
			if count == 0:
				savedyears = savedyears+[row[0]]
				savedfilms_count = savedfilms_count+[int(row[1])]
				savedavgratings = savedavgratings+[row[2]]
				savedseen = savedseen+[row[3]]
				savedrated = savedrated+[row[4]]
				i = i+1
				count = savedfilms_count[i]
				flag = 1
			else:
				if flag == 1:
					flag = 0
					savedfilms = savedfilms+[[row[0]]]
					count = count-1
				else:
					savedfilms[i] = savedfilms[i]+[row[0]]
					count = count-1
	# Check if the results are different:
	differentflag = 0
	if sfyears_print != savedyears:
		differentflag = 1
	elif sfavgratings_print != savedavgratings:
		differentflag = 1
	elif sfseen_print != savedseen:
		differentflag = 1
	elif sfrated_print != savedrated:
		differentflag = 1
	elif sffilms_count != savedfilms_count:
		differentflag = 1
	elif len(sffilms_print) != len(savedfilms):
		differentflag = 1
	else:
		for i in range(len(sffilms_print)):
			if len(sffilms_print[i]) != len(savedfilms[i]):
				differentflag = 1
			else:
				for j in range(sffilms_count[i]):
					film_in_both = 0
					k = 0
					while film_in_both == 0 and k < savedfilms_count[i]:
						if sffilms_print[i][j] == savedfilms[i][k]:
							film_in_both = 1
						k = k+1
					if film_in_both == 0:
						differentflag = 1
	if differentflag == 1:
		# Find out the differences and entries to be removed:
		for i in range(len(savedyears)):
			removeyearflag = 0
			j = 0
			while removeyearflag == 0 and j < len(sfyears_print):
				if savedyears[i] == sfyears_print[j]:
					removeyearflag = 1
					if savedavgratings[i] != sfavgratings_print[j]:
						print(savedyears[i]+' - Avg Rating Changed To '+sfavgratings_print[j])
					if savedseen[i] != sfseen_print[j]:
						print(savedyears[i]+' - Num Seen Changed To '+sfseen_print[j])
					if savedrated[i] != sfrated_print[j]:
						print(savedyears[i]+' - Num Rated Changed To '+sfrated_print[j])
					for k in range(savedfilms_count[i]):
						film_match = 0
						m = 0
						while film_match == 0 and m < sffilms_count[j]:
							if savedfilms[i][k] == sffilms_print[j][m]:
								film_match = 1
							m = m+1
						if film_match == 0:
							print(savedyears[i]+' - Film Removed From List Or Changed - '+savedfilms[i][k])
				j = j+1
			if removeyearflag == 0:
				print(savedyears[i]+' - Year Removed From List! (somehow)')
		# Find out new entries to add:
		for i in range(len(sfyears_print)):
			newyearflag = 0
			j = 0
			while newyearflag == 0 and j < len(savedyears):
				if sfyears_print[i] == savedyears[j]:
					newyearflag = 1
					for k in range(sffilms_count[i]):
						film_match = 0
						m = 0
						while film_match == 0 and m < savedfilms_count[j]:
							if sffilms_print[i][k] == savedfilms[j][m]:
								film_match = 1
							m = m+1
						if film_match == 0:
							print(sfactors_print[i]+' - New film added - '+sffilms_print[i][k])
				j = j+1
			if newyearflag == 0:
				print(sfyears_print[i]+' - New Year To Add!')
				print(' - Avg Rating = '+sfavgratings_print[i])
				print(' - Num Seen = '+sfseen_print[i])
				print(' - Num Rated = '+sfrated_print[i])
	else:
		print('No Difference! Nothing New To Add!')

# Print out results:
print('')
print('******************************')
print('** LEAGUE RESULTS ************')
print('******************************')
for i in range(len(sfyears_print)):
	print('')
	print(sfyears_print[i])
	print('Avg rating = '+sfavgratings_print[i])
	print('Number seen = '+sfseen_print[i])
	print('Number rated = '+sfrated_print[i])

# Copy old save file to a temporary file:
if datapathexists == 1:
	copyfile('Saved-data-files/Years-league-data-'+user+'.csv','Saved-data-files/Years-league-data-'+user+'-temp-old.csv')
# Copy new temporary file to the save file:
copyfile('Saved-data-files/Years-league-data-'+user+'-temp-new.csv','Saved-data-files/Years-league-data-'+user+'.csv')

# Also keep all years with 9 rated films:
finalyearsX = []
finalseenX = []
finalratedX = []
for i in range(len(syears2)):
	if srated2[i] == 9:
		finalyearsX = finalyearsX+[syears2[i]]
		finalseenX = finalseenX+[sseen2[i]]
		finalratedX = finalratedX+[srated2[i]]

# Save the results to a temporary file:
with open('Saved-data-files/Years-league-data-'+user+'-X-temp-new.csv', mode='w') as outfile:
	csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for i in range(len(finalyearsX)):
		csvwriter.writerow([finalyearsX[i],finalseenX[i],finalratedX[i]])

# Check if saved file exists:
datapathX = Path('Saved-data-files/Years-league-data-'+user+'-X.csv')
datapathXexists = 0
if datapathX.exists():
	datapathXexists = 1
	print('')
	print('******************************')
	print('** ALMOST RESULTS CHANGES ****')
	print('******************************')
	# Read it in:
	savedyearsX = []
	savedseenX = []
	savedratedX = []
	with open('Saved-data-files/Years-league-data-'+user+'-X.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			savedyearsX = savedyearsX+[row[0]]
			savedseenX = savedseenX+[int(row[1])]
			savedratedX = savedratedX+[int(row[2])]
	# Check if the results are different:
	differentflagX = 0
	if finalyearsX != savedyearsX:
		differentflagX = 1
	elif finalseenX != savedseenX:
		differentflagX = 1
	elif finalratedX != savedratedX:
		differentflagX = 1
	if differentflagX == 1:
		# Find out the differences and entries to be removed:
		for i in range(len(savedyearsX)):
			removeyearflagX = 0
			j = 0
			while removeyearflagX == 0 and j < len(finalyearsX):
				if savedyearsX[i] == finalyearsX[j]:
					removeyearflagX = 1
					if savedseenX[i] != finalseenX[j]:
						print(savedyearsX[i]+' - Num Seen Changed To '+str(finalseenX[j]))
					if savedratedX[i] != finalratedX[j]:
						print(savedyearsX[i]+' - Num Rated Changed To '+str(finalratedX[j]))
				j = j+1
			if removeyearflagX == 0:
				print(savedyearsX[i]+' - Year Removed From List! (somehow)')
		# Find out new entries to add:
		for i in range(len(finalyearsX)):
			newyearflagX = 0
			j = 0
			while newyearflagX == 0 and j < len(savedyearsX):
				if finalyearsX[i] == savedyearsX[j]:
					newyearflagX = 1
				j = j+1
			if newyearflagX == 0:
				print(finalyearsX[i]+' - New Year To Add!')
				print(' - Num Seen = '+str(finalseenX[i]))
				print(' - Num Rated = '+str(finalratedX[i]))
	else:
		print('No Difference! Nothing New To Add!')

# Copy old save file to a temporary file:
if datapathXexists == 1:
	copyfile('Saved-data-files/Years-league-data-'+user+'-X.csv','Saved-data-files/Years-league-data-'+user+'-X-temp-old.csv')
# Copy new temporary file to the save file:
copyfile('Saved-data-files/Years-league-data-'+user+'-X-temp-new.csv','Saved-data-files/Years-league-data-'+user+'-X.csv')

# Print 9-rated year candidates
print('')
print('******************************')
print('** ALMOST RESULTS ************')
print('******************************')
for i in range(len(finalyearsX)):
	print('')
	print(finalyearsX[i])
	print('Number seen = '+str(finalseenX[i]))
	print('Number rated = '+str(finalratedX[i]))

# Also keep all years with at least 10 watched films and less than 9 rated films
# Rank by number seen, then number rated:
finalyears2 = []
finalseen2 = []
finalrated2 = []
for i in range(len(syears2)):
	if sseen2[i] >= 10 and srated2[i] <= 8:
		if len(finalyears2) > 0:
			ratesortflag = 0
			j = 0
			maxloc = -1
			minloc = -1
			while ratesortflag == 0 and j < len(finalyears2):
				if finalseen2[j] == sseen2[i]:
					if finalrated2[j] > srated2[i]:
						maxloc = j
					elif finalrated2[j] == srated2[i]:
						loc = j
						ratesortflag = 1
					elif minloc == -1 and finalrated2[j] < srated2[i]:
						minloc = j
				j = j+1
			# No other years with the same number seen ranked yet
			# Put current year at the end of the list:
			if ratesortflag == 0 and maxloc == -1 and minloc == -1:
				finalyears2 = finalyears2+[syears2[i]]
				finalseen2 = finalseen2+[sseen2[i]]
				finalrated2 = finalrated2+[srated2[i]]
			# Same number seen already ranked, but only with higher number rated
			# Put current year at the end of the list:
			elif ratesortflag == 0 and maxloc > -1 and minloc == -1:
				finalyears2 = finalyears2+[syears2[i]]
				finalseen2 = finalseen2+[sseen2[i]]
				finalrated2 = finalrated2+[srated2[i]]
			# Same number seen already ranked, but only with lower number rated
			# Put current year just above the location of the first lower number rated:
			elif ratesortflag == 0 and maxloc == -1 and minloc > -1:
				finalyears2.insert(minloc,syears2[i])
				finalseen2.insert(minloc,sseen2[i])
				finalrated2.insert(minloc,srated2[i])
			# Same number seen already ranked, with both higher and lower number rated
			# Put current year just above the location of the first lower number rated:
			elif ratesortflag == 0 and maxloc > -1 and minloc > -1:
				finalyears2.insert(minloc,syears2[i])
				finalseen2.insert(minloc,sseen2[i])
				finalrated2.insert(minloc,srated2[i])
			# Same number seen already ranked, exacted number rated found
			# Put current year just above the location of the first same number rated:
			elif ratesortflag == 1:
				finalyears2.insert(loc,syears2[i])
				finalseen2.insert(loc,sseen2[i])
				finalrated2.insert(loc,srated2[i])
			# Shouldn't get this far:
			else:
				sys.exit('ERROR - in main code - Something wrong with num seen + num rated sorting.')
		else:
			finalyears2 = finalyears2+[syears2[i]]
			finalseen2 = finalseen2+[sseen2[i]]
			finalrated2 = finalrated2+[srated2[i]]

# Save the results to a temporary file:
with open('Saved-data-files/Years-league-data-'+user+'-other-temp-new.csv', mode='w') as outfile:
	csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	for i in range(len(finalyears2)):
		csvwriter.writerow([finalyears2[i],finalseen2[i],finalrated2[i]])

# Check if saved file exists:
datapath2 = Path('Saved-data-files/Years-league-data-'+user+'-other.csv')
datapath2exists = 0
if datapath2.exists():
	datapath2exists = 1
	print('')
	print('******************************')
	print('** REWATCH RESULTS CHANGES ***')
	print('******************************')
	# Read it in:
	savedyears2 = []
	savedseen2 = []
	savedrated2 = []
	with open('Saved-data-files/Years-league-data-'+user+'-other.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			savedyears2 = savedyears2+[row[0]]
			savedseen2 = savedseen2+[int(row[1])]
			savedrated2 = savedrated2+[int(row[2])]
	# Check if the results are different:
	differentflag2 = 0
	if finalyears2 != savedyears2:
		differentflag2 = 1
	elif finalseen2 != savedseen2:
		differentflag2 = 1
	elif finalrated2 != savedrated2:
		differentflag2 = 1
	if differentflag2 == 1:
		# Find out the differences and entries to be removed:
		for i in range(len(savedyears2)):
			removeyearflag2 = 0
			j = 0
			while removeyearflag2 == 0 and j < len(finalyears2):
				if savedyears2[i] == finalyears2[j]:
					removeyearflag2 = 1
					if savedseen2[i] != finalseen2[j]:
						print(savedyears2[i]+' - Num Seen Changed To '+str(finalseen2[j]))
					if savedrated2[i] != finalrated2[j]:
						print(savedyears2[i]+' - Num Rated Changed To '+str(finalrated2[j]))
				j = j+1
			if removeyearflag2 == 0:
				print(savedyears2[i]+' - Year Removed From List! (somehow)')
		# Find out new entries to add:
		for i in range(len(finalyears2)):
			newyearflag2 = 0
			j = 0
			while newyearflag2 == 0 and j < len(savedyears2):
				if finalyears2[i] == savedyears2[j]:
					newyearflag2 = 1
				j = j+1
			if newyearflag2 == 0:
				print(finalyears2[i]+' - New Year To Add!')
				print(' - Num Seen = '+str(finalseen2[i]))
				print(' - Num Rated = '+str(finalrated2[i]))
	else:
		print('No Difference! Nothing New To Add!')

# Copy old save file to a temporary file:
if datapath2exists == 1:
	copyfile('Saved-data-files/Years-league-data-'+user+'-other.csv','Saved-data-files/Years-league-data-'+user+'-other-temp-old.csv')
# Copy new temporary file to the save file:
copyfile('Saved-data-files/Years-league-data-'+user+'-other-temp-new.csv','Saved-data-files/Years-league-data-'+user+'-other.csv')

# Print most-watched year candidates
print('')
print('******************************')
print('** REWATCH RESULTS ***********')
print('******************************')
for i in range(len(finalyears2)):
	print('')
	print(finalyears2[i])
	print('Number seen = '+str(finalseen2[i]))
	print('Number rated = '+str(finalrated2[i]))

# Print out full results for everything:
print('')
print('******************************')
print('** FULL LEAGUE RESULTS *******')
print('******************************')
for i in range(len(sfyears_print)):
	print('')
	print(sfyears_print[i])
	for j in range(sffilms_count[i]):
		print(sffilms_print[i][j])
	print('Avg rating = '+sfavgratings_print[i])
	print('Number seen = '+sfseen_print[i])
	print('Number rated = '+sfrated_print[i])

print('')
print('******************************')
print('** FULL ALMOST RESULTS *******')
print('******************************')
for i in range(len(finalyearsX)):
	print('')
	print(finalyearsX[i])
	print('Number seen = '+str(finalseenX[i]))
	print('Number rated = '+str(finalratedX[i]))
	for j in range(len(films)):
		if years[j] == finalyearsX[i]:
			if runtimes[j] >= 40:
				skipflag = 0
				if ignorefilms == 1:
					for k in range(len(filmstoignore)):
						if filmstoignore[k] == films[j]:
							skipflag = 1
				if skipflag == 0:
					if ratings[j] == '0':
						print('   '+films[j])
					elif int(ratings[j]) < 6:
						print('-- '+films[j])
					else:
						print('** '+films[j])

print('')
print('******************************')
print('** FULL REWATCH RESULTS ******')
print('******************************')
for i in range(len(finalyears2)):
	print('')
	print(finalyears2[i])
	print('Number seen = '+str(finalseen2[i]))
	print('Number rated = '+str(finalrated2[i]))
	for j in range(len(films)):
		if years[j] == finalyears2[i]:
			if runtimes[j] >= 40:
				skipflag = 0
				if ignorefilms == 1:
					for k in range(len(filmstoignore)):
						if filmstoignore[k] == films[j]:
							skipflag = 1
				if skipflag == 0:
					if ratings[j] == '0':
						print('   '+films[j])
					elif int(ratings[j]) < 6:
						print('-- '+films[j])
					else:
						print('** '+films[j])

# Remove temporary files:
if outputpath1exists == 1:
	os.remove('Saved-data-files/Years-league-data-'+user+'-saved.csv')
if outputpath2exists == 1:
	os.remove('Saved-data-files/Years-league-data-'+user+'-X-saved.csv')
if outputpath3exists == 1:
	os.remove('Saved-data-files/Years-league-data-'+user+'-other-saved.csv')
os.remove('Saved-data-files/Years-league-data-'+user+'-temp-new.csv')
os.remove('Saved-data-files/Years-league-data-'+user+'-X-temp-new.csv')
os.remove('Saved-data-files/Years-league-data-'+user+'-other-temp-new.csv')
if datapathexists == 1:
	os.remove('Saved-data-files/Years-league-data-'+user+'-temp-old.csv')
if datapathXexists == 1:
	os.remove('Saved-data-files/Years-league-data-'+user+'-X-temp-old.csv')
if datapath2exists == 1:
	os.remove('Saved-data-files/Years-league-data-'+user+'-other-temp-old.csv')
