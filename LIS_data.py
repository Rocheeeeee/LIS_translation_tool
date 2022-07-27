import pandas as pd

class LIS_Data:
    """
        A class for saving all rows of client's LIS data.

    """
    def __init__(self, patient_id, test_name:str):
        #patient ID in client's raw data
        self.__ID = patient_id 
        #client LIS test name, save it as all upper class letter
        self.__testName = test_name
        #self.arrivalTime
        #self.resultTime
        #corresponding roche test names found in panel def
        self.__rocheTest = [] 
        #number of Assay corresponding to LIS test name
        self.__numberOfRocheTest = 0  
        # 1 for there are corresponding roche test in panel def, default 0 for match not found
        self.__matchFound = 0  

        self.__sourceDict = ''

        self.__similarTest = ''

        self.__confidenceScore = 0


# get attributes
    def getId(self):
        return self.__ID

    def getTestName(self):
        return self.__testName

    def getRocheTest(self):
        return self.__rocheTest

    def getMatchFound(self):
        return self.__matchFound

    def getNumberOfRocheTest(self):
        return self.__numberOfRocheTest

    def getSourceDict(self):
        return self.__sourceDict

    def getSimilarTest(self):
        return self.__similarTest

    def getConfidenceScore(self):
        return self.__confidenceScore

# set attributes
    def setRocheTest(self, rocheName):
        self.__rocheTest = rocheName

    def setMatchFound(self):
        self.__matchFound = 1

    def setNumberOfRocheTest(self, num):
        self.__numberOfRocheTest = num

    def setSourceDict(self, source_dict):
        self.__sourceDict = source_dict

    def setSimilarTest(self, similar_test):
        self.__similarTest = similar_test
        
    def setConfidenceScore(self, score: int):
        self.__confidenceScore = score



class LIS_Dict:
    def __init__(self, test_name:str):
        self.__LISName = test_name
        self.__assayName = []
        self.__include = 1
        self.__material = ''

    def getLISName(self):
        return self.__LISName

    def getAssayName(self):
        return self.__assayName

    def getInclude(self):
        return self.__include

    def getMaterial(self):
        return self.__material

    def setInclude(self, flag:bool):
        self.__include = flag
    
    def setMaterial(self, material:str):
        self.__material = material

    def setAssayName(self, inputNames):
        #for panel definition
        #inputNames is rest of the columns in a row except Test Name, Include, Material
        tempList = []
        for name in inputNames:
            if name != None:
                tempList.append(str(name))
        self.__assayName = tempList
    
    def setRocheName(self, rocheName:str):
        # for saving roche test names from roche_test_by_platform
        self.__assayName = rocheName