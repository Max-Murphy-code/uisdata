# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 16:59:54 2021

@author: 15144
"""

from io import BytesIO
from io import StringIO
from zipfile import ZipFile
import re
import requests  # Dependency
import pandas as pd  # Dependency

class bdds:
    """The bdds Class allows to download a BDDS archive, access the datasets and
    the Readme files within. To instantiate the class pick a UIS dataset from
    the list below (use the name in quote excluding the parenthesis)

    Parameter
    ----------
    datasetName : str {"SDG" (SDG 1&4), "OPRI" (Other Policy Relevant Indicators),
     "SCI" (R&D), INNO (Innovation), "CLTE" (Cultural Employment), "CLTT" (Cultural Trade),
     "FILM" (Feature Films), "SDG11", "DEM" (Demographic and Socio-economic), "EDU" (Non-core archive, last updated Feb.2020)}

    Once the class is instantiated with a specific dataset, the following methods can be called:
    readmeFile
    dataTables
        subsetData
        addMetadata
        addLabels
        allLabelMerge
        allMetaDataMerge
        allLabelMetaMerge
        uniqueVal
        searchList

    The indent shows the parent/child relationship e.g. subsetData can only be called
    when the dataTables method as been called.
    """
    # The init function will instantiate the class by saving a specific dataset's URL to a variable
    def __init__(self, datasetName):
        self.url = self.getURL(datasetName)  # Call getURL function that downloads the csv list of dataset-url
        self.dsNameLength = len(datasetName) + 1  # DataSet name length passed to dataTable method
        self.read_URL_ZIP = None  # Instance var: used in other method (provokes a warning if not added here)
        self.zip_File_List = None  # Instance var: used in other method (provokes a warning if not added here)
        self.testName = str(datasetName)
        # print(self.testName)

    # !!! CSV url Hardcoded
    def getURL(self, datasetName):
        """Download the external CSV file containing datset names and the URLs to
            of all BDDS archive. Returns a link to download a BDDS archive

        Parameter
        ----------
            datasetName: Str
                The name of the dataset instantiated

        Returns
        -------
            URL
                a url of a bdds archive
        """
        # !!! Hardcoded URL. Note the name of each dataset in the file e.g. SDG...
        # ...must be exactly as the name of files prefix SDG_DATA_NATIONAL.csv
        csv_url = "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/python/BDDS_DatasetList_Name-URL.csv"
        urlData = requests.get(csv_url).content  # download file @ url location returns URL response object
        dsNameURLdf = pd.read_csv(StringIO(urlData.decode('utf-8')))  # read the CSV as a dataFrame
        dsNameURLdict = dict(zip(dsNameURLdf.dataset, dsNameURLdf.url))  # transforms the dataFrame to a dict
        dsURL = dsNameURLdict[datasetName]  # gets the archive's URL from dict
        return dsURL

    # Transforms all the csv files in Pandas dataFrame and save them to a dict
    def dataTables(self):
        """Download the archive, extracts and saves all the .CSV files as DataFrames (Pandas) to a dictionary.

        Parameter
        ----------
            none

        Returns
        -------
            Dict
                a dictionary of the dataFrames contained in a BDDS archive
        """
        # Download Zip file from BDDS website and extract a list of file names from the zip
        get_URL_object = requests.get(self.url)  # download file @ url location returns URL response object
        read_URL = BytesIO(get_URL_object.content)  # gives file-like access to URL response object
        self.read_URL_ZIP = ZipFile(read_URL)  # instance Var: read file-like object as zip file
        self.zip_File_List = self.read_URL_ZIP.namelist()  # instance Var: listing names of files in the zip

        # Produce a dictionary containing all tables as dataFrame
        dataset_dict = {}
        for name in self.zip_File_List:
            if not str.lower("README") in str.lower(name):  # If file not named README, process as dataFrame
                asString = self.read_URL_ZIP.read(name).decode('utf8')  # Read and decode specific list item as string
                readString = StringIO(asString)  # Give file-like access to string
                df = pd.read_csv(readString, low_memory=False)  # Read as a Pandas dataFrame
                trim_name = name[self.dsNameLength:-4]  # Remove specific DS name and file extension from df name
                dataset_dict[trim_name] = df  # Add dataFrame to dataset_dict
        return dataset_dict

    # Produces the readme in a string variable
    def readmeFile(self):
        """Extracts the README file from the ZIP archive

        Parameter
        ----------
            none

        Returns
        -------
            Variable
                a Var with the README content
        """
        for name in self.zip_File_List:
            if str.lower("README") in str.lower(name):  # If file named README, process as String
                readme = self.read_URL_ZIP.read(name).decode('utf8')  # Read and decode specific list item as string
        return readme

    # General functions, wrappers and utilities
    def subsetData(self, adataSet, yearList, geoList, indicatorList, geoType="Country"):
        """Subsets the data

        Parameters
        ----------
            adataSet : dataFrame
                a dataFrame to be subsetted
            yearList: a list of int
                a list of years to include in the subset
            geoList: a list of str
                a list of either 3-letter ISO country code or regions to include in the subset
            indicatorList: a list of str
                a list of indicator codes to include in the subset
            geoType: str, {'Country','Region'} default is 'Country'
                a str to specify geography type either Country or Region

        Returns
        -------
            DataFrame
                a DataFrame subsetted by a list of years, countries/regions and indicators
        """
        if geoType == "Country":
            aSubset = adataSet[(adataSet['YEAR'].isin(yearList)) &
                               (adataSet['COUNTRY_ID'].isin(geoList)) &
                               (adataSet['INDICATOR_ID'].isin(indicatorList))
                               ]
        elif geoType == "Region":
            aSubset = adataSet[(adataSet['YEAR'].isin(yearList)) &
                               (adataSet['REGION_ID'].isin(geoList)) &
                               (adataSet['INDICATOR_ID'].isin(indicatorList))
                               ]
        return aSubset

    def addMetadata(self, datasetNoMeta, metaDataSub, metadataType):
        """Merges the metadata to the data. This function only works on NATIONAL data.

        Parameters
        ----------
            datasetNoMeta: DataFrame
                a DataFrame receiving the metadata from another DataFrame
            metaDataSub: DataFrame
                a DataFrame giving metadata to another DataFrame
            metadataType: str e.g. {'Source:Data sources','Under Coverage:Students or individuals'}
                a string specifying the type of metadata merged to the dataset
                (the uniqueVal function can provide a list of all metadata type)

        Returns
        -------
            DataFrame
                a DataFrame with an extra column for a specific metadata type
        """
        # Subsetting the metadataset by metadata type
        metadataSubByType = metaDataSub[metaDataSub['TYPE'] == metadataType]
        # Joining metadata texts with the same YEAR/COUNTRY_ID/INDICATOR_ID/TYPE combination
        metaDataSubJoined = metadataSubByType.groupby(['YEAR', 'COUNTRY_ID', 'INDICATOR_ID', 'TYPE']) \
            ['METADATA'].apply(' | '.join).reset_index()
        dataSubsetWithMeta = pd.merge(datasetNoMeta, metaDataSubJoined, how='left',
                                      on=['YEAR', 'COUNTRY_ID', 'INDICATOR_ID'])
        return dataSubsetWithMeta

    def addLabels(self, dataSetNoLabel, labelSet, keyVariable):
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

    def uniqueVal(self, aDataSet, columnName):
        """Gets all unique values from a column

        Parameter
        ----------
            aDataSet: DataFrame
                a DataFrame containing the data
            columnName: String
                a String for the column name on which to gather unique values

        Returns
        -------
            List
                a list of unique values
        """
        uniqueVal = aDataSet[columnName].drop_duplicates().sort_values().dropna().to_list()
        return uniqueVal

    # !!!Hardcode to search in the "LABEL" file, "INDICATOR_ID" column
    # Could reorder searchTerm list of user for speed gain (?)
    def searchList(self, dataTableDict, searchTermList, indic_or_region="Indic"):
        """Searches all cells of a column for a specific term. Returns an
            INDICATOR_ID or REGION_ID containing the full search string.

        Parameter
        ----------
            dataTableDict: Dictionary
                a dictionary containing all the dataFrame of a BDDS archive
            searchTermList: List
                list of search terms
            indic_or_region: Str {'Indic', 'Region'} default is 'Indic'
                string specifying the type of data to search for; either Indicators or Regions

        Returns
        -------
            List
                a list containing all the search results (no duplicates)
        """
        def searchIt():
            for terms in searchTermList:  # Loop through all search Terms in searchTermList
                for indicOrRegion in fullListOfItems:  # Loop the search Term within the list of unique INDICATOR_ID or REGION_ID
                    match = re.search(terms, indicOrRegion)  # Try to match the search Term within a INDICATOR_ID or REGION_ID
                    if match:
                        if indicOrRegion not in matchList:  # If indicators is not already in the list append to matchList
                            matchList.append(indicOrRegion)
        matchList = []
        if indic_or_region == "Indic":
            fullListOfItems = dataTableDict["LABEL"]["INDICATOR_ID"].to_list()
            searchIt()
        elif indic_or_region == "Region":
            fullListOfItems = dataTableDict["REGION"]["REGION_ID"].to_list()
            searchIt()
        return matchList

    def allLabelMerge(self, dataTableDict, aDataSet, geoType="Country"):
        """Merges all labels to a dataset

        Parameter
        ----------
            dataTableDict: Dictionary
                a dictionary containing all the dataFrame of a BDDS
            aDataSet: DataFrame
                a DataFrame on which to merge labels
            geoType: str, {'Country','Region'} default is 'Country'
                a string specifying the type of data in the dataset

        Returns
        -------
            DataFrame
                a DataFrame containing extra columns with the country/indicator labels
        """
        if geoType == "Country":
            aSetWithAllLabels = self.addLabels(aDataSet, dataTableDict["COUNTRY"], keyVariable="COUNTRY_ID")
            aSetWithAllLabels = self.addLabels(aSetWithAllLabels, dataTableDict["LABEL"], keyVariable="INDICATOR_ID")
        elif geoType == "Region":
            aSetWithAllLabels = self.addLabels(aDataSet, dataTableDict["LABEL"], keyVariable="INDICATOR_ID")
        return aSetWithAllLabels

    def allMetaMerge(self, dataTableDict, aDataSet):
        """Merges all metadata to a dataset. This function only works on NATIONAL data.

        Parameter
        ----------
            dataTableDict: Dictionary
                a dictionary containing all the dataFrame of a BDDS archive
            aDataSet: DataFrame
                a DataFrame on which to merge labels

        Returns
        -------
            DataFrame
                a DataFrame containing extra columns with the country/indicator labels
        """
        # Get all types of metadata
        allMetaType = self.uniqueVal(dataTableDict["METADATA"], "TYPE")
        dsWithMeta = aDataSet  # Keep var: Loop will updates this df with new metadata after each iteration
        # Loop over list of metadata type and
        for item in allMetaType:
            dsWithMeta = self.addMetadata(dsWithMeta, dataTableDict["METADATA"], item)
        return dsWithMeta

    def allLabelMetaMerge(self, dataTableDict, yearList, geoList, indicatorList, geoType="Country"):
        """Wrapper to subset and merge all labels and metadata in a single process

        Parameter
        ----------
            dataTableDict: Dict
                a dictionary containing all the dataFrame of a BDDS archive
            yearList: List
                a list containing the years to include in the subset
            geoList: List
                a list of either 3-letter ISO country code or regions to include in the subset
            indicatorList: List
                a list containing the indicators to include in the subset
            geoType: str {'Country', 'Region'}
                a string specifying the type of data in the dataset

        Returns
        -------
            DataFrame
                a DataFrame, a subset with all metadata and labels merged
        """
        if geoType == "Country":
            subset = self.subsetData(dataTableDict["DATA_NATIONAL"], yearList, geoList, indicatorList,
                                     geoType="Country")
            subset = self.allLabelMerge(dataTableDict, subset)
            subset = self.allMetaMerge(dataTableDict, subset)
        elif geoType == "Region":
            subset = self.subsetData(dataTableDict["DATA_REGIONAL"], yearList, geoList, indicatorList, geoType="Region")
            subset = self.allLabelMerge(dataTableDict, subset, geoType="Region")
            # subset = self.allMetaMerge( dataTableDict, subset)   #No metadata for REGIONAL provided to date
        return subset

