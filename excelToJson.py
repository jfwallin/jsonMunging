import json
import ipywidgets as widgets
import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy

# set up the helper routines to load the jsons
# written by J Wallin


class sceneConverter:

    def __init__(self, path, outputPath, verbose):
        self.path = path
        self.outputPath = outputPath
        self.verbose = verbose

    def jsonFromFile(self, fname):
        f = open(fname, "r")
        s = f.read()
        f.close()
        return json.loads(s)

    def jsonToFile(self, fname):
        print(fname)

    def listFiles(self, assetPath):
        finalList = []
        fullList = os.listdir(assetPath)
        for f in fullList:
            if f.find("json") == len(f)-4:
                print(f)
                finalList.append(f)
        return finalList

    def loadFileIntoDictionary(self, flist):
        jdata = {}
        for f in flist:
            jdata[f] = self.jsonFromFile(self.path + f)
        return jdata

    def writeScene(self, myScene, verbose):
        # save it to an output file
        outputFile = self.myScene["jsonFileName"]
        print(os.path.isfile(self.outputPath + outputFile))

        # if there is a file already there
        print(self.outputPath + outputFile)
        fileExists = os.path.isfile(self.outputPath + outputFile)

        if self.verbose:
            while (fileExists or outputFile == ""):

                print("This is a listing of files in this path: ")
                flist = os.listdir(self.outputPath)
                for f in flist:
                    print(f)
                yn = input("The file " + self.outputPath + outputFile +
                           " already exists \n Do you want to overwrite it? ")
                if yn == "y" or yn == "Y":
                    fileExists = False
                else:
                    outputFile = input("What is the new name for our file? ")
                    fileExists = os.path.isfile(self.outputPath + outputFile)

        print("\nWriting " + self.outputPath+outputFile + "\n\n")

        # form the final scene as a string
        self.myScene["jsonFileName"] = outputFile
        finalJson = json.dumps(self.myScene, indent=4)
        f = open(self.outputPath + outputFile, "w", encoding='utf-8')
        f.write(json.dumps(self.myScene, ensure_ascii=False, indent=4))
        f.close()

    def createScene(self, moduleDescription, sceneData, olist, verbose=False):
        sceneData["objects"] = olist

        # make a copy of the generic scene for the activity file
        myScene = self.jdata['genericActivity.json'].copy()

        # apply the module description data ot the sceneObject
        myScene.update(moduleDescription)
        myScene.update(sceneData)

        # we can dump the scene to see what it looks like so far
        if verbose:
            print("This is the Scene\n\n\n")
            print(json.dumps(myScene, indent=4))

        self.writeScene(myScene, verbose)

    # this is a code stub for merging two activity files together

    def concatenateScenes(self, outputPath, outputFile, sceneList):

        print(outputPath, outputFile)
        # open the new file
        f = open(outputPath + outputFile, 'w', encoding='utf-8')

        for i in range(len(sceneList)):
            print("  \n scene")
            print(i)
            currentScene = sceneList[i]
            print(currentScene)

            # read in the files
            fn1 = outputPath + currentScene
            s1 = self.jsonFromFile(fn1)

            # Dump the file - but do NOT use any indents.  This will flatten
            # the file into a single line.  We then write it out as a line with a newline character.
            a1 = json.dumps(s1, ensure_ascii=False)
            f.write(a1 + "\n")

        # close it
        f.close()

    def findAllAttributes(self, olist):
        allKeys = []
        for o in olist:
            keyList = list(o.keys())
            allKeys = list(set(allKeys + keyList))
        return allKeys

    def parseObject(self, obj):

        name = ""
        if "name" in obj:
            name = obj["name"]

        position = ""
        if "position" in obj:
            position = obj["position"]

        rotation = ""
        if "rotation" in obj:
            rotation = obj["rotation"]

        scale = ""
        if "scale" in obj:
            scale = obj["scale"]

        parentName = ""
        if "parentName" in obj:
            parentName = obj["parentName"]

        mytype = ""
        if 'type' in obj:
            mytype = obj['type']

        components = ""
        if "componentsToAdd" in obj:
            components = obj["componentsToAdd"]

        return name, position, rotation, scale, parentName, mytype, components

    def createDataFrame(self, olist, mylist):
        alist = self.findAllAttributes(olist)

        for a in alist:
            if a not in mylist:
                mylist.append(a)

        #df = pd.DataFrame(columns=mylist)
        # for o in olist:
        #    df = df.append(o, ignore_index=True)
        pp = pd.DataFrame(data=olist, columns=mylist)

        return pp

    def createJsonFromDataFrame(self, df):
        olist = []
        delList = []
        for i in range(len(df)):
            o = df.iloc[i].to_dict()
            o['enabled'] = True

            delList = []
            for k in o.keys():
                v = o[k]

                if type(v) == float:
                    if np.isnan(v):
                        delList.append(k)
            # print(delList)
            for d in delList:
                del o[d]
            olist.append(o)
        return olist

    def combineValues(self, df, valueList, outputList=[]):
        newDictionary = {}
        if len(outputList) != len(valueList):
            outputList = valueList

        nanPresent = False
        for i in range(len(valueList)):
            v = valueList[i]
            ov = outputList[i]

            if v in df:
                newDictionary[ov] = df[v]
                if type(df[v]) == float or type(df[v]) == np.float64 or type(df[v]) == np.float32:
                    if np.isnan(df[v]):
                        nanPresent = True
            else:
                print("The key ", v, " is not in the dataframe!")
                exit()
        return newDictionary, nanPresent

    # combines columns into a single column

    def combineColumns(self, dftmp, newColumn, valueList, outputList=[]):
        columnValues = []
        for i in range(len(dftmp)):

            dfRow = dftmp.iloc[i]
            newDictionary, nanPresent = self.combineValues(
                dfRow, valueList, outputList)

            if nanPresent == False:
                columnValues.append(newDictionary)
            else:
                columnValues.append(np.nan)

        dftmp[newColumn] = columnValues

        cols = dftmp.columns.tolist()
        ii1 = cols.index(valueList[0])
        ii2 = cols.index(valueList[-1])

        # REARRANGE, BUT KEEP ORIGINAL TARGET COLUMN
        #dftmp = dftmp[cols[:ii+1] + cols[-len(valueList):] + cols[ii+1:len(cols)-len(valueList)]]

        # REARRANGE, BUT REMOVE ORIGINAL TARGET COLUMN
        dftmp = dftmp[cols[:ii1] + [cols[-1]] + cols[ii2+1:-1]]
        #df.drop(targetColumn, axis=1, inplace=True)

        return dftmp

    # Split an embedded data structure into multiple columns

    def splitColumns(self, dftmp, targetColumn, valueList, outputList=[]):

        if len(outputList) != len(valueList):
            outputList = valueList

        # create the new column structure
        newColumns = {}
        for i in range(len(outputList)):
            newColumns[outputList[i]] = []

        for i in range(len(dftmp)):  # loop over the rows

            dfRow = dftmp.iloc[i]
            newDictionary = dfRow[targetColumn]

            if type(newDictionary) == str or type(newDictionary) == dict:
                for j in range(len(valueList)):
                    v = valueList[j]
                    ov = outputList[j]

                    if type(newDictionary) == str:
                        newDictionary1 = newDictionary.replace("'", "\"")
                        nd = json.loads(str(newDictionary1))
                        vv = nd[v]
                    newColumns[ov].append(vv)

            elif type(newDictionary) == float or type(newDictionary) == np.float64 or type(newDictionary) == np.float32:
                if np.isnan(newDictionary):
                    for j in range(len(valueList)):
                        v = valueList[j]
                        ov = outputList[j]
                        newColumns[ov].append(np.nan)

        for k in newColumns.keys():
            dftmp[k] = newColumns[k]

        # rearrange the column order
        cols = dftmp.columns.tolist()
        ii = cols.index(targetColumn)

        # REARRANGE, BUT KEEP ORIGINAL TARGET COLUMN
        #dftmp = dftmp[cols[:ii+1] + cols[-len(valueList):] + cols[ii+1:len(cols)-len(valueList)]]

        # REARRANGE, BUT REMOVE ORIGINAL TARGET COLUMN
        dftmp = dftmp[cols[:ii] +
                      cols[-len(valueList):] + cols[ii+1:len(cols)-len(valueList)]]
        #df.drop(targetColumn, axis=1, inplace=True)

        return dftmp


if __name__ == "__main__":
    testCase = 4

    path = "./"
    outputPath = "./"
    verbose = True
    sc = sceneConverter(path, outputPath, verbose)
    # %run ./sceneObjects1.ipynb
    # print(olist)

    # creating a data frame from a legacy script
    if testCase == 1:

        # this is the perferred order of the attributes
        # object list oo is created

        mylist = ['enabled', 'name', 'parentName', 'type', 'position',
                  'rotation', 'scale', 'tmp', 'texture', 'componentsToAdd']
        df = sc.createDataFrame(olist, mylist)
        # df.to_excel("testobj2.xlsx")
        print(df)

    if testCase == 2:

        # read a sample excel file with embedded json
        df1 = pd.read_excel("testobj.xlsx", sheet_name="Sheet3")

        # turn excel into json
        oo = sc.createJsonFromDataFrame(df1)
        for o1 in oo:
            print(o1)

    # combine columns into a json within a single column
    if testCase == 3:
        df2 = pd.read_excel("testobj2.xlsx")  # ,sheet_name="Sheet3")
        df2 = sc.combineColumns(
            df2, 'position', ['x', 'y', 'z'], ['x', 'y', 'z'])
        df2 = sc.combineColumns(
            df2, 'rotation', ['rx', 'ry', 'rz'], ['x', 'y', 'z'])
        df2 = sc.combineColumns(
            df2, 'scale', ['sx', 'sy', 'sz'], ['x', 'y', 'z'])
        df2 = sc.combineColumns(df2, 'tmp', ['textField', 'textColor', 'fontSize', 'wrapText'], [
            'textField', 'color', 'fontSize', 'wrapText'])
        df2 = sc.combineColumns(df2, 'eulerAngles', [
            'ex', 'ey', 'ez'], ['x', 'y', 'z'])
        print(df2)

        olist = sc.createJsonFromDataFrame(df2)
        # for o1 in olist:
        #    print(json.dumps(o1, indent=4))

    if testCase == 4:
        df1 = pd.read_excel("testobj.xlsx", sheet_name="Sheet3")
        cc = df1.columns.tolist()
        for i in range(10):
            if 'Unnamed: ' + str(i) in cc:
                df1.drop('Unnamed', axis=1, inplace=True)

        df1 = sc.splitColumns(
            df1, 'position', ['x', 'y', 'z'], ['x', 'y', 'z'])
        df1 = sc.splitColumns(
            df1, 'rotation', ['x', 'y', 'z'], ['rx', 'ry', 'rz'])
        df1 = sc.splitColumns(
            df1, 'scale', ['x', 'y', 'z'], ['sx', 'sy', 'sz'])
        df1 = sc.splitColumns(df1, 'tmp', ['textField', 'color', 'fontSize', 'wrapText'], [
            'textField', 'textColor', 'fontSize', 'wrapText'])
        df1 = sc.splitColumns(df1, 'eulerAngles', [
                              'x', 'y', 'z'], ['ex', 'ey', 'ez'])
        print(df1)

        # os.listdir()
        # os.remove("testobj2.xlsx")
        # df1.to_excel("testobj2.xlsx")
        # df1
        # df1

    if testCase == 5:
        df2 = pd.read_excel("testobj2.xlsx")  # ,sheet_name="Sheet3")
        cc = df2.columns.tolist()
        for i in range(10):
            if 'Unnamed: ' + str(i) in cc:
                df2.drop('Unnamed: ' + str(i), axis=1, inplace=True)

        # for o1 in olist:
        #    print(json.dumps(o1, indent=4))

        df2 = sc.combineColumns(
            df2, 'position', ['x', 'y', 'z'], ['x', 'y', 'z'])
        df2 = sc.combineColumns(
            df2, 'rotation', ['rx', 'ry', 'rz'], ['x', 'y', 'z'])
        df2 = sc.combineColumns(
            df2, 'scale', ['sx', 'sy', 'sz'], ['x', 'y', 'z'])
        df2 = sc.combineColumns(df2, 'tmp', ['textField', 'textColor', 'fontSize', 'wrapText'], [
            'textField', 'color', 'fontSize', 'wrapText'])
        df2 = sc.combineColumns(df2, 'eulerAngles', [
            'ex', 'ey', 'ez'], ['x', 'y', 'z'])
        olist = sc.createJsonFromDataFrame(df2)
        for o1 in olist:
            print(json.dumps(o1, indent=4))
    # print(df2)

# df3 = pd.read_excel("testobj3.xlsx") #,sheet_name="Sheet3")
# df3
#oo = createJsonFromDataFrame(df3)
# for o1 in oo:
#    print(o1)
# os.listdir()
# os.remove("testobj3.xlsx")
# df2.to_excel("testobj3.xlsx")
