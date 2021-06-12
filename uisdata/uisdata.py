# -*- coding: utf-8 -*-

"""
Created on Wed Jun 23 2020 
Last update on Thu Feb 25 2021

This file provides a full walkthrough using Pandas for:
    1-loading the CSV files in memory
    2-creating a subset based on lists of countries, indicators and years
    3-adding metadata to the subset
    4-adding indicator and country labels to the subset
    5-returning the subset file to CSV format
"""

import pandas as pd
import numpy as np

###### Input files ############################################################
# Specify the path of the folder containing the BDDS files:
path = 'C:\\BDDS\\NATMON\\'

###### Loading CSV in memory ##################################################
eduDataSet = pd.read_csv(path+'NATMON_DATA_NATIONAL.csv')     #Data file
metadataSet = pd.read_csv(path + 'NATMON_METADATA.csv')       #Metadata file
countryLabels = pd.read_csv(path+'NATMON_COUNTRY.csv')        #Country code/labels file
eduLabels = pd.read_csv(path+'NATMON_LABEL.csv')              #Indicator code/labels file

###### Creating subsets of the data ###########################################
"""
Extracting a list of sorted unique values for the Year, Countries and Indicators
that will serve as the default parameters in the following function
"""
allYears = np.sort(eduDataSet["YEAR"].unique())
recentYears = allYears[-4:]  #New variable with the latest four years

allCountries = np.sort(eduDataSet["COUNTRY_ID"].unique())

#Changing numeral indicators to string and extracting unique values
eduDataSet["INDICATOR_ID"] = eduDataSet["INDICATOR_ID"].astype(str)
allIndicators = np.sort(eduDataSet["INDICATOR_ID"].unique())

def subsetData(dataSet, yearList=recentYears,\
               countryList=allCountries, indicatorList=allIndicators):
    """Subsets the data

    Parameters
    ----------
        dataSet : DataFrame
            a DataFrame to be subsetted
        yearList: a list of int, default is recentYears
            a list of years
        countryList: a list of str, defaults is allCountries
            a list of 3-letter ISO country code
        indicatorList: a list of str, default is allIndicators
            a list of indicator codes
    Returns
    -------
        DataFrame
            a DataFrame subsetted by a list of years, countries and indicators
    """
    aSubset = dataSet[(dataSet['YEAR'].isin(yearList)) &\
                      (dataSet['COUNTRY_ID'].isin(countryList)) &\
                          (dataSet['INDICATOR_ID'].isin(indicatorList))]
    return aSubset

###### Merging metadata and data subsets ######################################
def addMetadata(dataSub, metaDataSub, metadataType='Source:Data sources'):
    """Merges the metadata to the data

    Parameters
    ----------
    dataSub: DataFrame
        a DataFrame receving the metadata from another DataFrame
    metaDataSub: DataFrame
        a DataFrame giving metadata to another DataFrame
    metadataType: str {'Source:Data sources','Under Coverage:Students or individuals'}
        a string for specifying the type of metadata merged to the dataset (note
        that the number of metadata type will vary across datasets and over time)

    Returns
    -------
        DataFrame
            a DataFrame with an extra column of metadata
    """
    #Subsetting the metadataset by metadata type
    metadataSubByType = metaDataSub[metaDataSub['TYPE'] == metadataType]
    #Joining metadata texts with the same YEAR/COUNTRY_ID/INDICATOR_ID/TYPE combination
    metaDataSubJoined = metadataSubByType.groupby(['YEAR', 'COUNTRY_ID', 'INDICATOR_ID', 'TYPE'])\
                        ['METADATA'].apply(' | '.join).reset_index()
    dataSubsetWithMeta = pd.merge(dataSub, metaDataSubJoined, how ='left', \
                         on = ['YEAR', 'COUNTRY_ID', 'INDICATOR_ID'])
    return dataSubsetWithMeta

###### Examples; Subsetting and adding metadata ################################
"""Example 1
Subsetting by using the default parameters i.e. last 4 years, all countries and all indicators
"""
#Data subset
defaultDataSubset = subsetData(eduDataSet)
#print(defaultDataSubset[0:2])

#Metadata subset
defaultMetadataSubset = subsetData(metadataSet)

#Merging metadata with data subset using default metadata type
defaultSubsetWithSource = addMetadata(defaultDataSubset, metadataSet)

"""Example 2:
Subsetting by specifying all the parameters into a list
"""
#Defining the list of year, country and indicator of interest
yearsSubset = [2012, 2014, 2015, 2017]
countrySubset = np.array(['ARG', 'KWT', 'SWE', 'ZWE'])
indicSubset = np.array(['NART.1.Q1.F.LPIA','MYS.1T8.AG25T99',\
                        'GER.1', 'SAP.1', 'AIR.1.Glast'])

#Data subset
myDataSubset = subsetData(eduDataSet, yearsSubset, countrySubset, indicSubset)

#Metadata subset
myMetadataSubset = subsetData(metadataSet, yearsSubset, countrySubset, indicSubset)

#Merging metadata with data subset using specified metadata type
mySubsetWithUnderCov = addMetadata(myDataSubset, myMetadataSubset,\
                                   'Under Coverage:Students or individuals')

mySubsetWith_UnderCov_Source = addMetadata(mySubsetWithUnderCov, myMetadataSubset)

###### Adding labels ##########################################################
def addLabels(dataSetNoLabel, labelSet, keyVariable):
    """Adds labels to a dataset
    Adds an additional column with the country or indicators name.

    Parameters
    ----------
    dataSetNoLabel: DataFrame
        the DataFrame containing the data
    labelSet: DataFrame
        the DataFrame containing the labels
    keyVariable: str {'INDICATOR_ID', 'COUNTRY_ID'}
        a string specifying the key variable for the merge

    Returns
    -------
        DataFrame
            a DataFrame with extra columns for labels
    """
    dataSetWithLabels = pd.merge(dataSetNoLabel, labelSet, how='left', on=[keyVariable])
    return dataSetWithLabels

#Adding country labels
mySubetWith_Meta_countryLabel = addLabels(mySubsetWith_UnderCov_Source,\
                                          countryLabels, 'COUNTRY_ID')
#Adding indicator labels (to the previous subset with labels)
mySubsetWith_Meta_allLabels = addLabels(mySubetWith_Meta_countryLabel,\
                                        eduLabels, 'INDICATOR_ID')

###### Export to CSV ##########################################################
mySubsetWith_Meta_allLabels.to_csv(path+'PythonTutorial.csv')
