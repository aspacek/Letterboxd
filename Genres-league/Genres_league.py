######################
## Genres_league.py ##
######################

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

sys.path.insert(0, "../General-league-routines")
from Findstrings import findstrings
from Getstrings import getstrings
from Numsort import numsort
from Getuserfilms import getuserfilms
from Getfilminfo import getfilminfo

##
## Written by Alex Spacek
## December 2020 - January 2021
##

############################################################################
############################################################################

def genresleague(type,user,films,ratings,genres,runtimes):

	if type == 'normal':
		# Ask for username:
		print('\nNote: Letterboxd username needs to match how it appears in the profile URL.')
		print('      i.e. letterboxd.com/<username>/')
		user = input('\nEnter Letterboxd username: ')
	
	# Backup previous output file and open a new one:
	printoutpath = Path('Saved-data-files/Output-'+user+'.txt')
	printoutpathexists = 0
	if printoutpath.exists():
		printoutpathexists = 1
		copyfile('Saved-data-files/Output-'+user+'.txt','Saved-data-files/Output-'+user+'-saved.txt')
	resultsfile = open('Saved-data-files/Output-'+user+'.txt','w')

	# Save backups of all output files in case something goes wrong:
	outputpath1 = Path('Saved-data-files/Genres-league-data-'+user+'.csv')
	outputpath2 = Path('Saved-data-files/Genres-league-data-'+user+'-X.csv')
	outputpath3 = Path('Saved-data-files/Genres-league-data-'+user+'-other.csv')
	outputpath4 = Path('Saved-data-files/Genres-league-data-'+user+'-other2.csv')
	outputpath1exists = 0
	outputpath2exists = 0
	outputpath3exists = 0
	outputpath4exists = 0
	if outputpath1.exists():
		outputpath1exists = 1
		copyfile('Saved-data-files/Genres-league-data-'+user+'.csv','Saved-data-files/Genres-league-data-'+user+'-saved.csv')
	if outputpath2.exists():
		outputpath2exists = 1
		copyfile('Saved-data-files/Genres-league-data-'+user+'-X.csv','Saved-data-files/Genres-league-data-'+user+'-X-saved.csv')
	if outputpath3.exists():
		outputpath3exists = 1
		copyfile('Saved-data-files/Genres-league-data-'+user+'-other.csv','Saved-data-files/Genres-league-data-'+user+'-other-saved.csv')
	if outputpath4.exists():
		outputpath4exists = 1
		copyfile('Saved-data-files/Genres-league-data-'+user+'-other2.csv','Saved-data-files/Genres-league-data-'+user+'-other2-saved.csv')
	
	if type == 'normal':
		# Get user films:
		films,ratings = getuserfilms(user)

		# Get film info:
		films,ratings,genres,runtimes = getfilminfo(films,ratings,['genres','runtimes'])
	
	# Remove any blank genre names or films with no genres:
	xfilms = []
	xratings = []
	xgenres = []
	xruntimes = []
	for i in range(len(films)):
		if genres[i] != '' and genres[i] != 'none':
			xfilms = xfilms+[films[i]]
			xratings = xratings+[ratings[i]]
			xgenres = xgenres+[genres[i]]
			xruntimes = xruntimes+[runtimes[i]]
	films = [val for val in xfilms]
	ratings = [val for val in xratings]
	genres = [val for val in xgenres]
	runtimes = [val for val in xruntimes]
	
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
	
	# Film by film, get the genre
	# Then check all other genres
	# Compile all films by the same genre together
	# Note which films were used to avoid repeats
	new_genres = []
	number_seen = []
	number_rated = []
	count = -1
	checked = [0 for i in films]
	for i in range(len(films)):
		if checked[i] == 0:
			checked[i] = 1
			if runtimes[i] >= 40:
				skipflag = 0
				if ignorefilms == 1:
					for j in range(len(filmstoignore)):
						if filmstoignore[j] == 'xallx' or filmstoignore[j] == films[i]:
							skipflag = 1
				if skipflag == 0:
					count = count+1
					new_genres = new_genres+[genres[i]]
					number_seen = number_seen+[1]
					if ratings[i] == '0':
						number_rated = number_rated+[0]
					else:
						number_rated = number_rated+[1]
					for j in range(len(films)):
						if checked[j] == 0:
							if genres[j] == genres[i]:
								checked[j] = 1
								if runtimes[j] >= 40:
									skipflag2 = 0
									if ignorefilms == 1:
										for k in range(len(filmstoignore)):
											if filmstoignore[k] == 'xallx' or filmstoignore[k] == films[j]:
												skipflag2 = 1
									if skipflag2 == 0:
										number_seen[count] = number_seen[count]+1
										if ratings[j] != '0':
											number_rated[count] = number_rated[count]+1
	
	# Rank genres by number of films rated:
	number_rated_temp = [val for val in number_rated]
	new_genres_temp = [val for val in new_genres]
	srated,sgenres = numsort(number_rated_temp,new_genres_temp,1,1)
	number_rated_temp = [val for val in number_rated]
	number_seen_temp = [val for val in number_seen]
	srated,sseen = numsort(number_rated_temp,number_seen_temp,0,1)
	
	# Also rank genres by number of films watched:
	number_seen_temp = [val for val in number_seen]
	new_genres_temp = [val for val in new_genres]
	sseen2,sgenres2 = numsort(number_seen_temp,new_genres_temp,1,1)
	number_seen_temp = [val for val in number_seen]
	number_rated_temp = [val for val in number_rated]
	sseen2,srated2 = numsort(number_seen_temp,number_rated_temp,0,1)
	
	# Keep all genres with at least 20 rated films
	# Get average rating
	finalgenres = []
	finalavgratings = []
	finalseen = []
	finalrated = []
	for i in range(len(sgenres)):
		if srated[i] >= 20:
			finalgenres = finalgenres+[sgenres[i]]
			finalseen = finalseen+[sseen[i]]
			finalrated = finalrated+[srated[i]]
			ratingsum = 0
			ratingnum = 0
			for j in range(len(films)):
				if genres[j] == sgenres[i]:
					if runtimes[j] >= 40:
						if ratings[j] != '0':
							skipflag = 0
							if ignorefilms == 1:
								for k in range(len(filmstoignore)):
									if filmstoignore[k] == 'xallx' or filmstoignore[k] == films[j]:
										skipflag = 1
							if skipflag == 0:
								ratingsum = ratingsum+int(ratings[j])
								ratingnum = ratingnum+1
			ratingavg = ratingsum/ratingnum
			finalavgratings = finalavgratings+[ratingavg]
	
	# Sort by average rating:
	finalavgratings_temp = [val for val in finalavgratings]
	finalgenres_temp = [val for val in finalgenres]
	sfavgratings,sfgenres = numsort(finalavgratings_temp,finalgenres_temp,1,1)
	finalavgratings_temp = [val for val in finalavgratings]
	finalseen_temp = [val for val in finalseen]
	sfavgratings,sfseen = numsort(finalavgratings_temp,finalseen_temp,0,1)
	finalavgratings_temp = [val for val in finalavgratings]
	finalrated_temp = [val for val in finalrated]
	sfavgratings,sfrated = numsort(finalavgratings_temp,finalrated_temp,0,1)
	
	# Get print details for final genres, films, and average ratings
	sfgenres_print = []
	sffilms_print = [[] for i in range(len(sfgenres))]
	sffilms_count = []
	sfavgratings_print = []
	sfseen_print = []
	sfrated_print = []
	for i in range(len(sfgenres)):
		sfgenres_print = sfgenres_print+[sfgenres[i]]
		sffilms_count = sffilms_count+[0]
		for j in range(len(films)):
			if genres[j] == sfgenres[i]:
				if runtimes[j] >= 40:
					skipflag = 0
					if ignorefilms == 1:
						for k in range(len(filmstoignore)):
							if filmstoignore[k] == 'xallx' or filmstoignore[k] == films[j]:
								skipflag = 1
					if skipflag == 0:
						sffilms_count[i] = sffilms_count[i]+1
						if ratings[j] == '0':
							sffilms_print[i] = sffilms_print[i]+['   '+films[j]]
						else:
							sffilms_print[i] = sffilms_print[i]+['** '+films[j]]
		sfavgratings_print = sfavgratings_print+[str(sfavgratings[i]/2)]
		sfseen_print = sfseen_print+[str(sfseen[i])]
		sfrated_print = sfrated_print+[str(sfrated[i])]
	
	# Save the results to a temporary file:
	with open('Saved-data-files/Genres-league-data-'+user+'-temp-new.csv', mode='w') as outfile:
		csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for i in range(len(sfgenres_print)):
			csvwriter.writerow([sfgenres_print[i],sffilms_count[i],sfavgratings_print[i],sfseen_print[i],sfrated_print[i]])
			for j in range(sffilms_count[i]):
				csvwriter.writerow([sffilms_print[i][j]])
	
	# Check if saved file exists:
	datapath = Path('Saved-data-files/Genres-league-data-'+user+'.csv')
	datapathexists = 0
	if datapath.exists():
		datapathexists = 1
		resultsfile.write('\n******************************')
		resultsfile.write('\n** LEAGUE RESULTS CHANGES ****')
		resultsfile.write('\n******************************')
		# Read it in:
		savedgenres = []
		savedfilms_count = []
		savedfilms = []
		savedavgratings = []
		savedseen = []
		savedrated = []
		with open('Saved-data-files/Genres-league-data-'+user+'.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			count = 0
			flag = 0
			i = -1
			for row in csv_reader:
				if count == 0:
					savedgenres = savedgenres+[row[0]]
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
		if sfgenres_print != savedgenres:
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
			for i in range(len(savedgenres)):
				removegenresflag = 0
				j = 0
				while removegenresflag == 0 and j < len(sfgenres_print):
					if savedgenres[i] == sfgenres_print[j]:
						removegenresflag = 1
						if savedavgratings[i] != sfavgratings_print[j]:
							resultsfile.write('\n'+savedgenres[i]+' - Avg Rating Changed To '+sfavgratings_print[j])
						if savedseen[i] != sfseen_print[j]:
							resultsfile.write('\n'+savedgenres[i]+' - Num Seen Changed To '+sfseen_print[j])
						if savedrated[i] != sfrated_print[j]:
							resultsfile.write('\n'+savedgenres[i]+' - Num Rated Changed To '+sfrated_print[j])
						for k in range(savedfilms_count[i]):
							film_match = 0
							m = 0
							while film_match == 0 and m < sffilms_count[j]:
								if savedfilms[i][k] == sffilms_print[j][m]:
									film_match = 1
								m = m+1
							if film_match == 0:
								resultsfile.write('\n'+savedgenres[i]+' - Film Removed From List Or Changed - '+savedfilms[i][k])
					j = j+1
				if removegenresflag == 0:
					resultsfile.write('\n'+savedgenres[i]+' - Genre Removed From List! (somehow)')
			# Find out new entries to add:
			for i in range(len(sfgenres_print)):
				newgenresflag = 0
				j = 0
				while newgenresflag == 0 and j < len(savedgenres):
					if sfgenres_print[i] == savedgenres[j]:
						newgenresflag = 1
						for k in range(sffilms_count[i]):
							film_match = 0
							m = 0
							while film_match == 0 and m < savedfilms_count[j]:
								if sffilms_print[i][k] == savedfilms[j][m]:
									film_match = 1
								m = m+1
							if film_match == 0:
								resultsfile.write('\n'+sfgenres_print[i]+' - New film added - '+sffilms_print[i][k])
					j = j+1
				if newgenresflag == 0:
					resultsfile.write('\n'+sfgenres_print[i]+' - New Genre To Add!')
					resultsfile.write('\n - Avg Rating = '+sfavgratings_print[i])
					resultsfile.write('\n - Num Seen = '+sfseen_print[i])
					resultsfile.write('\n - Num Rated = '+sfrated_print[i])
			# Print old and new rankings together:
			maxval = max(len(savedgenres),len(sfgenres_print))
			resultsfile.write('\n')
			resultsfile.write('\nRankings Old/New')
			for i in range(maxval):
				if i < len(savedgenres) and i < len(sfgenres_print):
					resultsfile.write('\n('+str(i+1)+') '+savedgenres[i]+' -- '+sfgenres_print[i])
				elif i >= len(savedgenres):
					resultsfile.write('\n('+str(i+1)+')            -- '+sfgenres_print[i])
				elif i >= len(sfgenres_print):
					resultsfile.write('\n('+str(i+1)+') '+savedgenres[i]+' --           ')
		else:
			resultsfile.write('\nNo Difference! Nothing New To Add!')
	
	# Print out limited results:
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** LEAGUE RESULTS ************')
	resultsfile.write('\n******************************')
	for i in range(len(sfgenres_print)):
		resultsfile.write('\n')
		resultsfile.write('\n('+str(i+1)+')')
		resultsfile.write('\n'+sfgenres_print[i])
		resultsfile.write('\nAvg rating = '+sfavgratings_print[i])
		resultsfile.write('\nNumber seen = '+sfseen_print[i])
		resultsfile.write('\nNumber rated = '+sfrated_print[i])
	
	# Copy old save file to a temporary file:
	if datapathexists == 1:
		copyfile('Saved-data-files/Genres-league-data-'+user+'.csv','Saved-data-files/Genres-league-data-'+user+'-temp-old.csv')
	# Copy new temporary file to the save file:
	copyfile('Saved-data-files/Genres-league-data-'+user+'-temp-new.csv','Saved-data-files/Genres-league-data-'+user+'.csv')
	
	# Also keep all genres with 19 rated films:
	finalgenresX = []
	finalseenX = []
	finalratedX = []
	for i in range(len(sgenres2)):
		if srated2[i] == 19:
			finalgenresX = finalgenresX+[sgenres2[i]]
			finalseenX = finalseenX+[sseen2[i]]
			finalratedX = finalratedX+[srated2[i]]
	
	# Save the results to a temporary file:
	with open('Saved-data-files/Genres-league-data-'+user+'-X-temp-new.csv', mode='w') as outfile:
		csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for i in range(len(finalgenresX)):
			csvwriter.writerow([finalgenresX[i],finalseenX[i],finalratedX[i]])
	
	# Check if saved file exists:
	datapathX = Path('Saved-data-files/Genres-league-data-'+user+'-X.csv')
	datapathXexists = 0
	if datapathX.exists():
		datapathXexists = 1
		resultsfile.write('\n')
		resultsfile.write('\n******************************')
		resultsfile.write('\n** ALMOST RESULTS CHANGES ****')
		resultsfile.write('\n******************************')
		# Read it in:
		savedgenresX = []
		savedseenX = []
		savedratedX = []
		with open('Saved-data-files/Genres-league-data-'+user+'-X.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				savedgenresX = savedgenresX+[row[0]]
				savedseenX = savedseenX+[int(row[1])]
				savedratedX = savedratedX+[int(row[2])]
		# Check if the results are different:
		differentflagX = 0
		if finalgenresX != savedgenresX:
			differentflagX = 1
		elif finalseenX != savedseenX:
			differentflagX = 1
		elif finalratedX != savedratedX:
			differentflagX = 1
		if differentflagX == 1:
			# Find out the differences and entries to be removed:
			for i in range(len(savedgenresX)):
				removegenresflagX = 0
				j = 0
				while removegenresflagX == 0 and j < len(finalgenresX):
					if savedgenresX[i] == finalgenresX[j]:
						removegenresflagX = 1
						if savedseenX[i] != finalseenX[j]:
							resultsfile.write('\n'+savedgenresX[i]+' - Num Seen Changed To '+str(finalseenX[j]))
						if savedratedX[i] != finalratedX[j]:
							resultsfile.write('\n'+savedgenresX[i]+' - Num Rated Changed To '+str(finalratedX[j]))
					j = j+1
				if removegenresflagX == 0:
					resultsfile.write('\n'+savedgenresX[i]+' - Genre Removed From List! (somehow)')
			# Find out new entries to add:
			for i in range(len(finalgenresX)):
				newgenresflagX = 0
				j = 0
				while newgenresflagX == 0 and j < len(savedgenresX):
					if finalgenresX[i] == savedgenresX[j]:
						newgenresflagX = 1
					j = j+1
				if newgenresflagX == 0:
					resultsfile.write('\n'+finalgenresX[i]+' - New Genre To Add!')
					resultsfile.write('\n - Num Seen = '+str(finalseenX[i]))
					resultsfile.write('\n - Num Rated = '+str(finalratedX[i]))
		else:
			resultsfile.write('\nNo Difference! Nothing New To Add!')
	
	# Copy old save file to a temporary file:
	if datapathXexists == 1:
		copyfile('Saved-data-files/Genres-league-data-'+user+'-X.csv','Saved-data-files/Genres-league-data-'+user+'-X-temp-old.csv')
	# Copy new temporary file to the save file:
	copyfile('Saved-data-files/Genres-league-data-'+user+'-X-temp-new.csv','Saved-data-files/Genres-league-data-'+user+'-X.csv')
	
	# Print 19-rated genre candidates
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** ALMOST RESULTS ************')
	resultsfile.write('\n******************************')
	for i in range(len(finalgenresX)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finalgenresX[i])
		resultsfile.write('\nNumber seen = '+str(finalseenX[i]))
		resultsfile.write('\nNumber rated = '+str(finalratedX[i]))
	
	# Also keep all genres with at least 20 watched films and less than 19 rated films
	# Rank by number seen, then number rated:
	finalgenres2 = []
	finalseen2 = []
	finalrated2 = []
	for i in range(len(sgenres2)):
		if sseen2[i] >= 20 and srated2[i] <= 18:
			if len(finalgenres2) > 0:
				ratesortflag = 0
				j = 0
				maxloc = -1
				minloc = -1
				while ratesortflag == 0 and j < len(finalgenres2):
					if finalseen2[j] == sseen2[i]:
						if finalrated2[j] > srated2[i]:
							maxloc = j
						elif finalrated2[j] == srated2[i]:
							loc = j
							ratesortflag = 1
						elif minloc == -1 and finalrated2[j] < srated2[i]:
							minloc = j
					j = j+1
				# No other genres with the same number seen ranked yet
				# Put current genre at the end of the list:
				if ratesortflag == 0 and maxloc == -1 and minloc == -1:
					finalgenres2 = finalgenres2+[sgenres2[i]]
					finalseen2 = finalseen2+[sseen2[i]]
					finalrated2 = finalrated2+[srated2[i]]
				# Same number seen already ranked, but only with higher number rated
				# Put current genre at the end of the list:
				elif ratesortflag == 0 and maxloc > -1 and minloc == -1:
					finalgenres2 = finalgenres2+[sgenres2[i]]
					finalseen2 = finalseen2+[sseen2[i]]
					finalrated2 = finalrated2+[srated2[i]]
				# Same number seen already ranked, but only with lower number rated
				# Put current genre just above the location of the first lower number rated:
				elif ratesortflag == 0 and maxloc == -1 and minloc > -1:
					finalgenres2.insert(minloc,sgenres2[i])
					finalseen2.insert(minloc,sseen2[i])
					finalrated2.insert(minloc,srated2[i])
				# Same number seen already ranked, with both higher and lower number rated
				# Put current genre just above the location of the first lower number rated:
				elif ratesortflag == 0 and maxloc > -1 and minloc > -1:
					finalgenres2.insert(minloc,sgenres2[i])
					finalseen2.insert(minloc,sseen2[i])
					finalrated2.insert(minloc,srated2[i])
				# Same number seen already ranked, exacted number rated found
				# Put current genre just above the location of the first same number rated:
				elif ratesortflag == 1:
					finalgenres2.insert(loc,sgenres2[i])
					finalseen2.insert(loc,sseen2[i])
					finalrated2.insert(loc,srated2[i])
				# Shouldn't get this far:
				else:
					sys.exit('ERROR - in main code - Something wrong with num seen + num rated sorting.')
			else:
				finalgenres2 = finalgenres2+[sgenres2[i]]
				finalseen2 = finalseen2+[sseen2[i]]
				finalrated2 = finalrated2+[srated2[i]]
	
	# Save the results to a temporary file:
	with open('Saved-data-files/Genres-league-data-'+user+'-other-temp-new.csv', mode='w') as outfile:
		csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for i in range(len(finalgenres2)):
			csvwriter.writerow([finalgenres2[i],finalseen2[i],finalrated2[i]])
	
	# Check if saved file exists:
	datapath2 = Path('Saved-data-files/Genres-league-data-'+user+'-other.csv')
	datapath2exists = 0
	if datapath2.exists():
		datapath2exists = 1
		resultsfile.write('\n')
		resultsfile.write('\n******************************')
		resultsfile.write('\n** REWATCH RESULTS CHANGES ***')
		resultsfile.write('\n******************************')
		# Read it in:
		savedgenres2 = []
		savedseen2 = []
		savedrated2 = []
		with open('Saved-data-files/Genres-league-data-'+user+'-other.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				savedgenres2 = savedgenres2+[row[0]]
				savedseen2 = savedseen2+[int(row[1])]
				savedrated2 = savedrated2+[int(row[2])]
		# Check if the results are different:
		differentflag2 = 0
		if finalgenres2 != savedgenres2:
			differentflag2 = 1
		elif finalseen2 != savedseen2:
			differentflag2 = 1
		elif finalrated2 != savedrated2:
			differentflag2 = 1
		if differentflag2 == 1:
			# Find out the differences and entries to be removed:
			for i in range(len(savedgenres2)):
				removegenresflag2 = 0
				j = 0
				while removegenresflag2 == 0 and j < len(finalgenres2):
					if savedgenres2[i] == finalgenres2[j]:
						removegenresflag2 = 1
						if savedseen2[i] != finalseen2[j]:
							resultsfile.write('\n'+savedgenres2[i]+' - Num Seen Changed To '+str(finalseen2[j]))
						if savedrated2[i] != finalrated2[j]:
							resultsfile.write('\n'+savedgenres2[i]+' - Num Rated Changed To '+str(finalrated2[j]))
					j = j+1
				if removegenresflag2 == 0:
					resultsfile.write('\n'+savedgenres2[i]+' - Genre Removed From List! (somehow)')
			# Find out new entries to add:
			for i in range(len(finalgenres2)):
				newgenresflag2 = 0
				j = 0
				while newgenresflag2 == 0 and j < len(savedgenres2):
					if finalgenres2[i] == savedgenres2[j]:
						newgenresflag2 = 1
					j = j+1
				if newgenresflag2 == 0:
					resultsfile.write('\n'+finalgenres2[i]+' - New Genre To Add!')
					resultsfile.write('\n - Num Seen = '+str(finalseen2[i]))
					resultsfile.write('\n - Num Rated = '+str(finalrated2[i]))
		else:
			resultsfile.write('\nNo Difference! Nothing New To Add!')
	
	# Copy old save file to a temporary file:
	if datapath2exists == 1:
		copyfile('Saved-data-files/Genres-league-data-'+user+'-other.csv','Saved-data-files/Genres-league-data-'+user+'-other-temp-old.csv')
	# Copy new temporary file to the save file:
	copyfile('Saved-data-files/Genres-league-data-'+user+'-other-temp-new.csv','Saved-data-files/Genres-league-data-'+user+'-other.csv')
	
	# Print most-watched genre candidates
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** REWATCH RESULTS ***********')
	resultsfile.write('\n******************************')
	for i in range(len(finalgenres2)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finalgenres2[i])
		resultsfile.write('\nNumber seen = '+str(finalseen2[i]))
		resultsfile.write('\nNumber rated = '+str(finalrated2[i]))
	
	# Also show the rest of the genres
	# Rank by number seen, then number rated:
	finalgenres3 = []
	finalseen3 = []
	finalrated3 = []
	for i in range(len(sgenres2)):
		if sseen2[i] < 20 and srated2[i] <= 18:
			if len(finalgenres3) > 0:
				ratesortflag = 0
				j = 0
				maxloc = -1
				minloc = -1
				while ratesortflag == 0 and j < len(finalgenres3):
					if finalseen3[j] == sseen2[i]:
						if finalrated3[j] > srated2[i]:
							maxloc = j
						elif finalrated3[j] == srated2[i]:
							loc = j
							ratesortflag = 1
						elif minloc == -1 and finalrated3[j] < srated2[i]:
							minloc = j
					j = j+1
				# No other genres with the same number seen ranked yet
				# Put current genre at the end of the list:
				if ratesortflag == 0 and maxloc == -1 and minloc == -1:
					finalgenres3 = finalgenres3+[sgenres2[i]]
					finalseen3 = finalseen3+[sseen2[i]]
					finalrated3 = finalrated3+[srated2[i]]
				# Same number seen already ranked, but only with higher number rated
				# Put current genre at the end of the list:
				elif ratesortflag == 0 and maxloc > -1 and minloc == -1:
					finalgenres3 = finalgenres3+[sgenres2[i]]
					finalseen3 = finalseen3+[sseen2[i]]
					finalrated3 = finalrated3+[srated2[i]]
				# Same number seen already ranked, but only with lower number rated
				# Put current genre just above the location of the first lower number rated:
				elif ratesortflag == 0 and maxloc == -1 and minloc > -1:
					finalgenres3.insert(minloc,sgenres2[i])
					finalseen3.insert(minloc,sseen2[i])
					finalrated3.insert(minloc,srated2[i])
				# Same number seen already ranked, with both higher and lower number rated
				# Put current genre just above the location of the first lower number rated:
				elif ratesortflag == 0 and maxloc > -1 and minloc > -1:
					finalgenres3.insert(minloc,sgenres2[i])
					finalseen3.insert(minloc,sseen2[i])
					finalrated3.insert(minloc,srated2[i])
				# Same number seen already ranked, exacted number rated found
				# Put current genre just above the location of the first same number rated:
				elif ratesortflag == 1:
					finalgenres3.insert(loc,sgenres2[i])
					finalseen3.insert(loc,sseen2[i])
					finalrated3.insert(loc,srated2[i])
				# Shouldn't get this far:
				else:
					sys.exit('ERROR - in main code - Something wrong with num seen + num rated sorting.')
			else:
				finalgenres3 = finalgenres3+[sgenres2[i]]
				finalseen3 = finalseen3+[sseen2[i]]
				finalrated3 = finalrated3+[srated2[i]]
	
	# Save the results to a temporary file:
	with open('Saved-data-files/Genres-league-data-'+user+'-other2-temp-new.csv', mode='w') as outfile:
		csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for i in range(len(finalgenres3)):
			csvwriter.writerow([finalgenres3[i],finalseen3[i],finalrated3[i]])
	
	# Check if saved file exists:
	datapath3 = Path('Saved-data-files/Genres-league-data-'+user+'-other2.csv')
	datapath3exists = 0
	if datapath3.exists():
		datapath3exists = 1
		resultsfile.write('\n')
		resultsfile.write('\n******************************')
		resultsfile.write('\n** THE REST RESULTS CHANGES **')
		resultsfile.write('\n******************************')
		# Read it in:
		savedgenres3 = []
		savedseen3 = []
		savedrated3 = []
		with open('Saved-data-files/Genres-league-data-'+user+'-other2.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				savedgenres3 = savedgenres3+[row[0]]
				savedseen3 = savedseen3+[int(row[1])]
				savedrated3 = savedrated3+[int(row[2])]
		# Check if the results are different:
		differentflag3 = 0
		if finalgenres3 != savedgenres3:
			differentflag3 = 1
		elif finalseen3 != savedseen3:
			differentflag3 = 1
		elif finalrated3 != savedrated3:
			differentflag3 = 1
		if differentflag3 == 1:
			# Find out the differences and entries to be removed:
			for i in range(len(savedgenres3)):
				removegenresflag3 = 0
				j = 0
				while removegenresflag3 == 0 and j < len(finalgenres3):
					if savedgenres3[i] == finalgenres3[j]:
						removegenresflag3 = 1
						if savedseen3[i] != finalseen3[j]:
							resultsfile.write('\n'+savedgenres3[i]+' - Num Seen Changed To '+str(finalseen3[j]))
						if savedrated3[i] != finalrated3[j]:
							resultsfile.write('\n'+savedgenres3[i]+' - Num Rated Changed To '+str(finalrated3[j]))
					j = j+1
				if removegenresflag3 == 0:
					resultsfile.write('\n'+savedgenres3[i]+' - Genre Removed From List! (somehow)')
			# Find out new entries to add:
			for i in range(len(finalgenres3)):
				newgenresflag3 = 0
				j = 0
				while newgenresflag3 == 0 and j < len(savedgenres3):
					if finalgenres3[i] == savedgenres3[j]:
						newgenresflag3 = 1
					j = j+1
				if newgenresflag3 == 0:
					resultsfile.write('\n'+finalgenres3[i]+' - New Genre To Add!')
					resultsfile.write('\n - Num Seen = '+str(finalseen3[i]))
					resultsfile.write('\n - Num Rated = '+str(finalrated3[i]))
		else:
			resultsfile.write('\nNo Difference! Nothing New To Add!')
	
	# Copy old save file to a temporary file:
	if datapath3exists == 1:
		copyfile('Saved-data-files/Genres-league-data-'+user+'-other2.csv','Saved-data-files/Genres-league-data-'+user+'-other2-temp-old.csv')
	# Copy new temporary file to the save file:
	copyfile('Saved-data-files/Genres-league-data-'+user+'-other2-temp-new.csv','Saved-data-files/Genres-league-data-'+user+'-other2.csv')
	
	# Print the rest of the genre candidates
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** THE REST RESULTS **********')
	resultsfile.write('\n******************************')
	for i in range(len(finalgenres3)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finalgenres3[i])
		resultsfile.write('\nNumber seen = '+str(finalseen3[i]))
		resultsfile.write('\nNumber rated = '+str(finalrated3[i]))
	
	# Print out full results for everything:
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** FULL LEAGUE RESULTS *******')
	resultsfile.write('\n******************************')
	for i in range(len(sfgenres_print)):
		resultsfile.write('\n')
		resultsfile.write('\n('+str(i+1)+')')
		resultsfile.write('\n'+sfgenres_print[i])
		resultsfile.write('\nAvg rating = '+sfavgratings_print[i])
		resultsfile.write('\nNumber seen = '+sfseen_print[i])
		resultsfile.write('\nNumber rated = '+sfrated_print[i])
		for j in range(sffilms_count[i]):
			resultsfile.write('\n'+sffilms_print[i][j])
	
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** FULL ALMOST RESULTS *******')
	resultsfile.write('\n******************************')
	for i in range(len(finalgenresX)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finalgenresX[i])
		resultsfile.write('\nNumber seen = '+str(finalseenX[i]))
		resultsfile.write('\nNumber rated = '+str(finalratedX[i]))
		for j in range(len(films)):
			if genres[j] == finalgenresX[i]:
				if runtimes[j] >= 40:
					skipflag = 0
					if ignorefilms == 1:
						for k in range(len(filmstoignore)):
							if filmstoignore[k] == 'xallx' or filmstoignore[k] == films[j]:
								skipflag = 1
					if skipflag == 0:
						if ratings[j] == '0':
							resultsfile.write('\n   '+films[j])
						else:
							resultsfile.write('\n** '+films[j])
	
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** FULL REWATCH RESULTS ******')
	resultsfile.write('\n******************************')
	for i in range(len(finalgenres2)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finalgenres2[i])
		resultsfile.write('\nNumber seen = '+str(finalseen2[i]))
		resultsfile.write('\nNumber rated = '+str(finalrated2[i]))
		for j in range(len(films)):
			if genres[j] == finalgenres2[i]:
				if runtimes[j] >= 40:
					skipflag = 0
					if ignorefilms == 1:
						for k in range(len(filmstoignore)):
							if filmstoignore[k] == 'xallx' or filmstoignore[k] == films[j]:
								skipflag = 1
					if skipflag == 0:
						if ratings[j] == '0':
							resultsfile.write('\n   '+films[j])
						else:
							resultsfile.write('\n** '+films[j])
	
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** FULL THE REST RESULTS *****')
	resultsfile.write('\n******************************')
	for i in range(len(finalgenres3)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finalgenres3[i])
		resultsfile.write('\nNumber seen = '+str(finalseen3[i]))
		resultsfile.write('\nNumber rated = '+str(finalrated3[i]))
		for j in range(len(films)):
			if genres[j] == finalgenres3[i]:
				if runtimes[j] >= 40:
					skipflag = 0
					if ignorefilms == 1:
						for k in range(len(filmstoignore)):
							if filmstoignore[k] == 'xallx' or filmstoignore[k] == films[j]:
								skipflag = 1
					if skipflag == 0:
						if ratings[j] == '0':
							resultsfile.write('\n   '+films[j])
						else:
							resultsfile.write('\n** '+films[j])
	
	# Close output file:
	resultsfile.write('\n')
	resultsfile.close()
	print('')
	print('Results saved to Genres-league/Saved-data-files/Output-'+user+'.txt')
	print('')
	
	# Remove temporary files:
	if printoutpathexists == 1:
		os.remove('Saved-data-files/Output-'+user+'-saved.txt')
	if outputpath1exists == 1:
		os.remove('Saved-data-files/Genres-league-data-'+user+'-saved.csv')
	if outputpath2exists == 1:
		os.remove('Saved-data-files/Genres-league-data-'+user+'-X-saved.csv')
	if outputpath3exists == 1:
		os.remove('Saved-data-files/Genres-league-data-'+user+'-other-saved.csv')
	if outputpath4exists == 1:
		os.remove('Saved-data-files/Genres-league-data-'+user+'-other2-saved.csv')
	os.remove('Saved-data-files/Genres-league-data-'+user+'-temp-new.csv')
	os.remove('Saved-data-files/Genres-league-data-'+user+'-X-temp-new.csv')
	os.remove('Saved-data-files/Genres-league-data-'+user+'-other-temp-new.csv')
	os.remove('Saved-data-files/Genres-league-data-'+user+'-other2-temp-new.csv')
	if datapathexists == 1:
		os.remove('Saved-data-files/Genres-league-data-'+user+'-temp-old.csv')
	if datapathXexists == 1:
		os.remove('Saved-data-files/Genres-league-data-'+user+'-X-temp-old.csv')
	if datapath2exists == 1:
		os.remove('Saved-data-files/Genres-league-data-'+user+'-other-temp-old.csv')
	if datapath3exists == 1:
		os.remove('Saved-data-files/Genres-league-data-'+user+'-other2-temp-old.csv')
