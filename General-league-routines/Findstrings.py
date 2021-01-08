####################
## Findstrings.py ##
####################

##
## Written by Alex Spacek
## January 2021
##

##################################
##################################

def findstrings(substring,string):
	lastfound = -1
	while True:
		lastfound = string.find(substring,lastfound+1)
		if lastfound == -1:  
			break
		yield lastfound
