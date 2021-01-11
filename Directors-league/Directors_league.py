########################
## Directors_league.py ##
########################

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
## November 2020 - January 2021
##

############################################################################
############################################################################

def directorsleague(type,user,films,ratings,directors,runtimes):

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
	outputpath1 = Path('Saved-data-files/Directors-league-data-'+user+'.csv')
	outputpath2 = Path('Saved-data-files/Directors-league-data-'+user+'-X.csv')
	outputpath3 = Path('Saved-data-files/Directors-league-data-'+user+'-other.csv')
	outputpath1exists = 0
	outputpath2exists = 0
	outputpath3exists = 0
	if outputpath1.exists():
		outputpath1exists = 1
		copyfile('Saved-data-files/Directors-league-data-'+user+'.csv','Saved-data-files/Directors-league-data-'+user+'-saved.csv')
	if outputpath2.exists():
		outputpath2exists = 1
		copyfile('Saved-data-files/Directors-league-data-'+user+'-X.csv','Saved-data-files/Directors-league-data-'+user+'-X-saved.csv')
	if outputpath3.exists():
		outputpath3exists = 1
		copyfile('Saved-data-files/Directors-league-data-'+user+'-other.csv','Saved-data-files/Directors-league-data-'+user+'-other-saved.csv')

	if type == 'normal':
		# Get user films:
		films,ratings = getuserfilms(user)

		# Get film info:
		films,ratings,directors,runtimes = getfilminfo(films,ratings,['directors','runtimes'])
	
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
	
	# Get print details for final directors, films, and average ratings
	sfdirectors_print = []
	sffilms_print = [[] for i in range(len(sfdirectors))]
	sffilms_count = []
	sfavgratings_print = []
	sfseen_print = []
	sfrated_print = []
	for i in range(len(sfdirectors)):
		sfdirectors_print = sfdirectors_print+[sfdirectors[i]]
		sffilms_count = sffilms_count+[0]
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
						sffilms_count[i] = sffilms_count[i]+1
						if ratings[j] == '0':
							sffilms_print[i] = sffilms_print[i]+['   '+films[j]]
						else:
							sffilms_print[i] = sffilms_print[i]+['** '+films[j]]
		sfavgratings_print = sfavgratings_print+[str(sfavgratings[i]/2)]
		sfseen_print = sfseen_print+[str(sfseen[i])]
		sfrated_print = sfrated_print+[str(sfrated[i])]
	
	# Save the results to a temporary file:
	with open('Saved-data-files/Directors-league-data-'+user+'-temp-new.csv', mode='w') as outfile:
		csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for i in range(len(sfdirectors_print)):
			csvwriter.writerow([sfdirectors_print[i],sffilms_count[i],sfavgratings_print[i],sfseen_print[i],sfrated_print[i]])
			for j in range(sffilms_count[i]):
				csvwriter.writerow([sffilms_print[i][j]])
	
	# Check if saved file exists:
	datapath = Path('Saved-data-files/Directors-league-data-'+user+'.csv')
	datapathexists = 0
	if datapath.exists():
		datapathexists = 1
		resultsfile.write('\n******************************')
		resultsfile.write('\n** LEAGUE RESULTS CHANGES ****')
		resultsfile.write('\n******************************')
		# Read it in:
		saveddirectors = []
		savedfilms_count = []
		savedfilms = []
		savedavgratings = []
		savedseen = []
		savedrated = []
		with open('Saved-data-files/Directors-league-data-'+user+'.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			count = 0
			flag = 0
			i = -1
			for row in csv_reader:
				if count == 0:
					saveddirectors = saveddirectors+[row[0]]
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
		if sfdirectors_print != saveddirectors:
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
			for i in range(len(saveddirectors)):
				removedirectorflag = 0
				j = 0
				while removedirectorflag == 0 and j < len(sfdirectors_print):
					if saveddirectors[i] == sfdirectors_print[j]:
						removedirectorflag = 1
						if savedavgratings[i] != sfavgratings_print[j]:
							resultsfile.write('\n'+saveddirectors[i]+' - Avg Rating Changed To '+sfavgratings_print[j])
						if savedseen[i] != sfseen_print[j]:
							resultsfile.write('\n'+saveddirectors[i]+' - Num Seen Changed To '+sfseen_print[j])
						if savedrated[i] != sfrated_print[j]:
							resultsfile.write('\n'+saveddirectors[i]+' - Num Rated Changed To '+sfrated_print[j])
						for k in range(savedfilms_count[i]):
							film_match = 0
							m = 0
							while film_match == 0 and m < sffilms_count[j]:
								if savedfilms[i][k] == sffilms_print[j][m]:
									film_match = 1
								m = m+1
							if film_match == 0:
								resultsfile.write('\n'+saveddirectors[i]+' - Film Removed From List Or Changed - '+savedfilms[i][k])
					j = j+1
				if removedirectorflag == 0:
					resultsfile.write('\n'+saveddirectors[i]+' - Director Removed From List! (somehow)')
			# Find out new entries to add:
			for i in range(len(sfdirectors_print)):
				newdirectorflag = 0
				j = 0
				while newdirectorflag == 0 and j < len(saveddirectors):
					if sfdirectors_print[i] == saveddirectors[j]:
						newdirectorflag = 1
						for k in range(sffilms_count[i]):
							film_match = 0
							m = 0
							while film_match == 0 and m < savedfilms_count[j]:
								if sffilms_print[i][k] == savedfilms[j][m]:
									film_match = 1
								m = m+1
							if film_match == 0:
								resultsfile.write('\n'+sfdirectors_print[i]+' - New film added - '+sffilms_print[i][k])
					j = j+1
				if newdirectorflag == 0:
					resultsfile.write('\n'+sfdirectors_print[i]+' - New Director To Add!')
					resultsfile.write('\n - Avg Rating = '+sfavgratings_print[i])
					resultsfile.write('\n - Num Seen = '+sfseen_print[i])
					resultsfile.write('\n - Num Rated = '+sfrated_print[i])
			# Print old and new rankings together:
			maxval = max(len(saveddirectors),len(sfdirectors_print))
			resultsfile.write('\n')
			resultsfile.write('\nRankings Old/New')
			for i in range(maxval):
				if i < len(saveddirectors) and i < len(sfdirectors_print):
					resultsfile.write('\n('+str(i+1)+') '+saveddirectors[i]+' -- '+sfdirectors_print[i])
				elif i >= len(saveddirectors):
					resultsfile.write('\n('+str(i+1)+')            -- '+sfdirectors_print[i])
				elif i >= len(sfdirectors_print):
					resultsfile.write('\n('+str(i+1)+') '+saveddirectors[i]+' --           ')
		else:
			resultsfile.write('\nNo Difference! Nothing New To Add!')
	
	# Print out results:
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** FULL LEAGUE RESULTS *******')
	resultsfile.write('\n******************************')
	for i in range(len(sfdirectors_print)):
		resultsfile.write('\n')
		resultsfile.write('\n('+str(i+1)+')')
		resultsfile.write('\n'+sfdirectors_print[i])
		resultsfile.write('\nAvg rating = '+sfavgratings_print[i])
		resultsfile.write('\nNumber seen = '+sfseen_print[i])
		resultsfile.write('\nNumber rated = '+sfrated_print[i])
		for j in range(sffilms_count[i]):
			resultsfile.write('\n'+sffilms_print[i][j])
	
	# Copy old save file to a temporary file:
	if datapathexists == 1:
		copyfile('Saved-data-files/Directors-league-data-'+user+'.csv','Saved-data-files/Directors-league-data-'+user+'-temp-old.csv')
	# Copy new temporary file to the save file:
	copyfile('Saved-data-files/Directors-league-data-'+user+'-temp-new.csv','Saved-data-files/Directors-league-data-'+user+'.csv')
	
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
	with open('Saved-data-files/Directors-league-data-'+user+'-X-temp-new.csv', mode='w') as outfile:
		csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for i in range(len(finaldirectorsX)):
			csvwriter.writerow([finaldirectorsX[i],finalseenX[i],finalratedX[i]])
	
	# Check if saved file exists:
	datapathX = Path('Saved-data-files/Directors-league-data-'+user+'-X.csv')
	datapathXexists = 0
	if datapathX.exists():
		datapathXexists = 1
		resultsfile.write('\n')
		resultsfile.write('\n******************************')
		resultsfile.write('\n** ALMOST RESULTS CHANGES ****')
		resultsfile.write('\n******************************')
		# Read it in:
		saveddirectorsX = []
		savedseenX = []
		savedratedX = []
		with open('Saved-data-files/Directors-league-data-'+user+'-X.csv') as csv_file:
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
							resultsfile.write('\n'+saveddirectorsX[i]+' - Num Seen Changed To '+str(finalseenX[j]))
						if savedratedX[i] != finalratedX[j]:
							resultsfile.write('\n'+saveddirectorsX[i]+' - Num Rated Changed To '+str(finalratedX[j]))
					j = j+1
				if removedirectorflagX == 0:
					resultsfile.write('\n'+saveddirectorsX[i]+' - Director Removed From List! (somehow)')
			# Find out new entries to add:
			for i in range(len(finaldirectorsX)):
				newdirectorflagX = 0
				j = 0
				while newdirectorflagX == 0 and j < len(saveddirectorsX):
					if finaldirectorsX[i] == saveddirectorsX[j]:
						newdirectorflagX = 1
					j = j+1
				if newdirectorflagX == 0:
					resultsfile.write('\n'+finaldirectorsX[i]+' - New Director To Add!')
					resultsfile.write('\n - Num Seen = '+str(finalseenX[i]))
					resultsfile.write('\n - Num Rated = '+str(finalratedX[i]))
		else:
			resultsfile.write('\nNo Difference! Nothing New To Add!')
	
	# Copy old save file to a temporary file:
	if datapathXexists == 1:
		copyfile('Saved-data-files/Directors-league-data-'+user+'-X.csv','Saved-data-files/Directors-league-data-'+user+'-X-temp-old.csv')
	# Copy new temporary file to the save file:
	copyfile('Saved-data-files/Directors-league-data-'+user+'-X-temp-new.csv','Saved-data-files/Directors-league-data-'+user+'-X.csv')
	
	# Print 4-rated director candidates
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** ALMOST RESULTS ************')
	resultsfile.write('\n******************************')
	for i in range(len(finaldirectorsX)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finaldirectorsX[i])
		resultsfile.write('\nNumber seen = '+str(finalseenX[i]))
		resultsfile.write('\nNumber rated = '+str(finalratedX[i]))
	
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
	with open('Saved-data-files/Directors-league-data-'+user+'-other-temp-new.csv', mode='w') as outfile:
		csvwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for i in range(len(finaldirectors2)):
			csvwriter.writerow([finaldirectors2[i],finalseen2[i],finalrated2[i]])
	
	# Check if saved file exists:
	datapath2 = Path('Saved-data-files/Directors-league-data-'+user+'-other.csv')
	datapath2exists = 0
	if datapath2.exists():
		datapath2exists = 1
		resultsfile.write('\n')
		resultsfile.write('\n******************************')
		resultsfile.write('\n** REWATCH RESULTS CHANGES ***')
		resultsfile.write('\n******************************')
		# Read it in:
		saveddirectors2 = []
		savedseen2 = []
		savedrated2 = []
		with open('Saved-data-files/Directors-league-data-'+user+'-other.csv') as csv_file:
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
							resultsfile.write('\n'+saveddirectors2[i]+' - Num Seen Changed To '+str(finalseen2[j]))
						if savedrated2[i] != finalrated2[j]:
							resultsfile.write('\n'+saveddirectors2[i]+' - Num Rated Changed To '+str(finalrated2[j]))
					j = j+1
				if removedirectorflag2 == 0:
					resultsfile.write('\n'+saveddirectors2[i]+' - Director Removed From List! (somehow)')
			# Find out new entries to add:
			for i in range(len(finaldirectors2)):
				newdirectorflag2 = 0
				j = 0
				while newdirectorflag2 == 0 and j < len(saveddirectors2):
					if finaldirectors2[i] == saveddirectors2[j]:
						newdirectorflag2 = 1
					j = j+1
				if newdirectorflag2 == 0:
					resultsfile.write('\n'+finaldirectors2[i]+' - New Director To Add!')
					resultsfile.write('\n - Num Seen = '+str(finalseen2[i]))
					resultsfile.write('\n - Num Rated = '+str(finalrated2[i]))
		else:
			resultsfile.write('\nNo Difference! Nothing New To Add!')
	
	# Copy old save file to a temporary file:
	if datapath2exists == 1:
		copyfile('Saved-data-files/Directors-league-data-'+user+'-other.csv','Saved-data-files/Directors-league-data-'+user+'-other-temp-old.csv')
	# Copy new temporary file to the save file:
	copyfile('Saved-data-files/Directors-league-data-'+user+'-other-temp-new.csv','Saved-data-files/Directors-league-data-'+user+'-other.csv')
	
	# Print most-watched director candidates
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** REWATCH RESULTS ***********')
	resultsfile.write('\n******************************')
	for i in range(len(finaldirectors2)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finaldirectors2[i])
		resultsfile.write('\nNumber seen = '+str(finalseen2[i]))
		resultsfile.write('\nNumber rated = '+str(finalrated2[i]))
	
	# Print full "almost" and "rewatch" results:
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** FULL ALMOST RESULTS *******')
	resultsfile.write('\n******************************')
	for i in range(len(finaldirectorsX)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finaldirectorsX[i])
		resultsfile.write('\nNumber seen = '+str(finalseenX[i]))
		resultsfile.write('\nNumber rated = '+str(finalratedX[i]))
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
							resultsfile.write('\n   '+films[j])
						else:
							resultsfile.write('\n** '+films[j])
	
	resultsfile.write('\n')
	resultsfile.write('\n******************************')
	resultsfile.write('\n** FULL REWATCH RESULTS ******')
	resultsfile.write('\n******************************')
	for i in range(len(finaldirectors2)):
		resultsfile.write('\n')
		resultsfile.write('\n'+finaldirectors2[i])
		resultsfile.write('\nNumber seen = '+str(finalseen2[i]))
		resultsfile.write('\nNumber rated = '+str(finalrated2[i]))
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
							resultsfile.write('\n   '+films[j])
						else:
							resultsfile.write('\n** '+films[j])
	
	# Close output file:
	resultsfile.write('\n')
	resultsfile.close()
	print('')
	print('Results saved to Directors-league/Saved-data-files/Output-'+user+'.txt')
	print('')
	
	# Remove temporary files:
	if printoutpathexists == 1:
		os.remove('Saved-data-files/Output-'+user+'-saved.txt')
	if outputpath1exists == 1:
		os.remove('Saved-data-files/Directors-league-data-'+user+'-saved.csv')
	if outputpath2exists == 1:
		os.remove('Saved-data-files/Directors-league-data-'+user+'-X-saved.csv')
	if outputpath3exists == 1:
		os.remove('Saved-data-files/Directors-league-data-'+user+'-other-saved.csv')
	os.remove('Saved-data-files/Directors-league-data-'+user+'-temp-new.csv')
	os.remove('Saved-data-files/Directors-league-data-'+user+'-X-temp-new.csv')
	os.remove('Saved-data-files/Directors-league-data-'+user+'-other-temp-new.csv')
	if datapathexists == 1:
		os.remove('Saved-data-files/Directors-league-data-'+user+'-temp-old.csv')
	if datapathXexists == 1:
		os.remove('Saved-data-files/Directors-league-data-'+user+'-X-temp-old.csv')
	if datapath2exists == 1:
		os.remove('Saved-data-files/Directors-league-data-'+user+'-other-temp-old.csv')
