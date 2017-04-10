# !/usr/bin/python
# Description: Maltego Transform that takes the dataset and extracts entities of money transfered

from __future__ import division
import sys
import datetime
import pandas as pd
import numpy as np
import requests
from collections import OrderedDict
from MaltegoTransform import *

# Function returns countries where money was transferred to
def getCountriesToo(me, query=None, trans=None):
	me.parseArguments(sys.argv)
	if any(trans['drzavaStranke'].str.contains(query.upper())):
		countryFrom = trans.loc[(trans.drzavaStranke == query.upper())]
		countryPrint = np.unique(countryFrom.drzavaPrejemnika,return_index=False)
		sumCountry = 0
		allSums = getSum(countryPrint, countryFrom)		
		for i in countryPrint:
			sumCountry = countryFrom[countryFrom['drzavaPrejemnika'] == i]['znesek'].sum()
			comma = intWithCommas(sumCountry)	
			intPrint = int(round(sumCountry/allSums*100,0))
			test = me.addEntity("nemi.countryToo",i)			
			test.setWeight(intPrint)			
			test.addAdditionalFields("value", "Sum transfer (EUR):", True, str(comma))
			test.addAdditionalFields("countryFrom", "Country From: ", True, str(query.upper()))
	else:
		me.addUIMessage("Country not in the list")		
		
	return me

def getCompany(me, query=None, trans=None):
	me = MaltegoTransform()
	#country = me.getVar("nemi.countrytoo")
	#print countr

	countryFrom = trans.loc[(trans.drzavaStranke == country.upper())]
	if any(countryFrom['drzavaPrejemnika'].str.contains(query.upper())):
		countryTo = countryFrom.loc[(trans.drzavaPrejemnika == query.upper())]
		companyPrint = countryTo.prejemnik
		allSums = getSum(companyPrint, countryTo)		
						
		for i in companyPrint:
			sumCountry = countryTo[countryTo['prejemnik'] == i]['znesek'].sum()
			address = countryFrom[countryTo['prejemnik'] == i]['sedezPrejemnika']
			addressPrint = np.unique(address,return_index=False)			
			getReason = countryTo[countryTo['prejemnik'] == i]['namenNakazila']			
			comma = intWithCommas(sumCountry)			
			test = me.addEntity("Maltego.Phrase",i)
			#test.addProperty('value','Sum transfer: ','strict', sumCountry)
			#test.setLinkColor('0xFF0000')
			test.addAdditionalFields("value", "Sum transfer EUR:", True, str(comma))
			for j in addressPrint:			
				test.addAdditionalFields("Address", "Address:", True, j)
			#test.addAdditionalFields("value", "Reason: ", True, getReason)
	else:
		me.addUIMessage("Country not in the list")		
		
	return me

def getSummary(me, query=None, trans=None):
	me.parseArguments(sys.argv)
	if any(trans['drzavaStranke'].str.contains(query.upper())):
		countryFrom = trans.loc[(trans.drzavaStranke == query.upper())]
		countryPrint = np.unique(countryFrom.drzavaPrejemnika,return_index=False)
		companyPrint = np.unique(countryFrom.prejemnik,return_index=False)
		numOfCompanies = int(len(companyPrint))
		numOfCountries = int(len(countryPrint))
		allSums = getSum(trans, query)		
		countrySums = getSum(countryPrint, countryFrom)		
		intPercent = int(round(countrySums/allSums*100,0))
		comma = intWithCommas(countrySums)
		commaAll = intWithCommas(allSums)		
		test = me.addEntity("nemi.summary",query.upper())
		test.addAdditionalFields("all", "Total money in 2016 (EUR):", True, str(commaAll))
		test.addAdditionalFields("country", "Number of countries:", True, str(numOfCountries))
		test.addAdditionalFields("company", "Number of companies:", True, str(numOfCompanies))
		test.addAdditionalFields("value", "Sum transfer (EUR):", True, str(comma))		
		test.addAdditionalFields("percent", "Percent transfer (%):", True, str(intPercent))
	else:
		me.addUIMessage("Country not in the list")		
		
	return me

# Function adds a comma for 1000 separator
# Value passed: transaction sum
def intWithCommas(x):
	#if type(x) not in [type(0), type(0L)]:
	#        raise TypeError("Parameter must be an integer.")
	if x < 0:
        	return '-' + intWithCommas(-x)
    	result = ''
    	while x >= 1000:
        	x, r = divmod(x, 1000)
        	result = ",%03d%s" % (r, result)
    	return "%d%s" % (x, result)

# Function returns the sum of all firms of money transferred to a country
# Values passed: unique values for countries and a set of transactions
def getSum(countryPrint, countryFrom):
	final, sums = [], [] 
	if type(countryPrint) is np.ndarray:
		for i in countryPrint:				
			sumCountry = countryFrom[countryFrom['drzavaPrejemnika'] == i]['znesek'].sum()
			sums.append(sumCountry) 
			final = sum(sums)
		return final
	else:
		final = countryPrint['znesek'].sum()
		return final

#**********************************************************************************
functions = {
             	'getCountriesToo': getCountriesToo,		#lists countries 
		'getCompany': getCompany,			#lists companies	
		'getSummary': getSummary			#country summary
		}

#**********************************************************************************

# Main function  
if __name__ == '__main__':
	transform = sys.argv[1]
	inputVar = sys.argv[2]
	me = MaltegoTransform()    
	try:
		trans = pd.read_excel("Maltego/UPPD/Data/nakazila_maltego.xls")
	except exception as e:
		me.addUIMessage(str(e))
	m_result = functions[transform](me, inputVar, trans)
   	m_result.returnOutput()


