
import json
import ipywidgets as widgets
import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy


import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as sctxt
from tkinter import filedialog as fd
from tkinter.simpledialog import askstring


from jsonEdit import jsonEditor
from scrolledFrame import VerticalScrolledFrame
from excelToJson import sceneConverter


class assetEditor:

    def __init__(self, theFrame, theWindow,
                 parent, moduleList):

        self.moduleList = moduleList

    def viewAssets(self):

        self.processAssets()

        self.findAllKeywords()
        newDictionary = self.combineDictionaries(self.assetList)
        df = pd.DataFrame(newDictionary)

        self.formLists(df)

        bb = self.filterAssets(df)

        # set the keyword
        ii = 0
        t = self.audioClipList[ii]
        targetAsset = 'audioClip'
        dfName = 'audioClipString'

        t = self.textureList[ii]
        targetAsset = 'texture'
        dfname = 'texture'

        # filter the data frame for that keyword in the correct column
        ee = df[df[targetAsset] == t]

        # loop through the asset data frame by row
        for ind in ee.index:
            moduleID = ee['moduleIndex'][ind]
            moduleName = ee['moduleName'][ind]
            objectName = ee['objectName'][ind]
            clipName = ee['clipName'][ind]
            element = ee['element'][ind]
            # print(ee[ind])
            print('moduleName', moduleName)

            # grab the module from the module list that aligns with this asset entry
            mtmp = self.moduleList[moduleID]
            print(ind, moduleID, moduleName, objectName, clipName, element, t)
            otmp = mtmp['objects']
            ctmp = mtmp['clips']

            if clipName is None:
                for o in otmp:  # if this is just an object, find the asset
                    if o['name'] == objectName:
                        if dfName in o:
                            tt = o[dfName]
                            print("object", moduleID, moduleName, objectName,
                                  clipName, element,  tt, t)

            else:
                for c in ctmp:  # if this is a clip, loop thorugh the object changes
                    if c['clipName'] == clipName:
                        print('clipName', c['clipName'], clipName)
                        # print(c)
                        if dfName in c:
                            tt = c[dfName]
                            print("clip", moduleID, moduleName, objectName,
                                  clipName, element,  tt, t)
                        for o in c['objectChanges']:
                            if o['name'] == objectName:
                                if dfName in o:
                                    tt = o[dfName]
                                    print("clip-object", moduleID, moduleName, objectName,
                                          clipName, element,  tt, t)

            # print(moduleID, moduleName, objectName,
            #      clipName, element,  tt, t)

            print("------------------")

            # if clipName is None:
            #    otmp = mtmp['objects'][objectName]
            # else:
            #    otmp = mtmp['clips'][clipName]['objectChanges'][objectName]

            # if element is None:
            #    xx = otmp['texture']
            # else:
            #    xx = otmp['elements'][element]['texture']

            #print(moduleName, objectName, clipName, element, xx, t)

        #print(t, ee['moduleName'].tolist())

    def findAllKeywords(self):
        self.moduleKeywordList = []
        self.objectKeywordList = []
        self.clipKeywordList = []

        for m in self.moduleList:
            for k in m.keys():
                if k not in self.moduleKeywordList:
                    self.moduleKeywordList.append(k)

            if 'objects' in m:
                for o in m['objects']:
                    for k in o.keys():
                        if k not in self.objectKeywordList:
                            self.objectKeywordList.append(k)
            if 'clips' in m:
                for c in m['clips']:
                    for k in c.keys():
                        if k not in self.clipKeywordList:
                            self.clipKeywordList.append(k)

                    for o in c['objectChanges']:
                        for k in o.keys():
                            if k not in self.objectKeywordList:
                                self.objectKeywordList.append(k)

            #        self.findAllKeywordsInObject(o)
            # if 'clips' in m:
            #    for c in m['clips']:
            #        self.findAllKeywordsInClip(c)

        print(self.moduleKeywordList)
        print(self.objectKeywordList)
        print(self.clipKeywordList)

    def changesToObjects(self, objectList):
        # go through the objects and find out which attributres
        # are different from the first object.  If the attribute
        # is not present in the later objectts, it hasn't changed.
        # If it is present, but the value is the same, it hasn't changed.
        # If it is present and the value is different, it has changed.
        ocurrent = objectList[0]
        for o in objectList[1:]:
            for k in ocurrent.keys():
                if k in o:
                    if ocurrent[k] == o[k]:
                        o.pop(k)
            ocurrent = o

    def locateAssets(self, df, asset, istart, iend):
        for i in range(istart, iend):
            print(i)

    def replaceAssets(self, oldAsset, newAsset, replacementList, istart, iend):

        for i in range(istart, iend):
            aa = self.moduleList[i]

    def filterAssets(self, df):
        bb = df[(df['moduleName'] == 'Sizes and Scales Earth and Moon')]
#        bb = df[(df['moduleName'] == moduleName) &
#                (df['clipName'] == clipName) &
#                (df['objectName'] == objectName)]
        return bb

    def formLists(self, localDF):
        cc = localDF[localDF['component'].isna() ==
                     False]['component'].tolist()
        self.componentList = list(set(cc))

        cc = localDF[localDF['texture'].isna() == False]['texture'].tolist()
        self.textureList = list(set(cc))

        cc = localDF[localDF['audioClip'].isna() ==
                     False]['audioClip'].tolist()
        self.audioClipList = list(set(cc))

        cc = localDF[localDF['tmp'].isna() == False]['tmp'].tolist()
        self.tmpList = list(set(cc))

    def processAssets(self):
        self.assetList = []
        for im, m in enumerate(self.moduleList):
            if 'objects' in m:
                for o in m['objects']:
                    self.assetList = self.assetList + \
                        self.compileObjectAssets(
                            o, im, m['moduleName'], o['name'], None)
            if 'clips' in m:
                for c in m['clips']:
                    self.assetList = self.assetList + \
                        self.compileObjectAssets(
                            c, im, m['moduleName'], o['name'], c['clipName'])

                    if 'objectChanges' in c:
                        for oc in c['objectChanges']:
                            self.assetList = self.assetList + \
                                self.compileObjectAssets(
                                    o, im, m['moduleName'], o['name'], c['clipName'])

    def combineDictionaries(self, dlist):
        newDictionary = {}
        for k, v in dlist[0].items():
            newDictionary[k] = []

        for i in range(1, len(dlist)):
            for k, v in dlist[i].items():
                if k not in newDictionary:
                    newDictionary[k] = []

        for i in range(len(dlist)):
            for k, v in dlist[i].items():
                newDictionary[k].append(v)
            for k, v in newDictionary.items():
                if k not in dlist[i]:
                    newDictionary[k].append(None)

        return newDictionary

    def compileObjectAssets(self, o, im, mname, oname, clipname):

        localAssetList = []
        objectAssetTemplate = {'moduleIndex': im, 'moduleName': mname, 'objectName': oname, 'clipName': clipname, 'element': None,
                               'texture': None, 'audioClip': None, 'component': None, 'tmp': None}

        if 'texture' in o:
            aa = copy.deepcopy(objectAssetTemplate)
            aa['texture'] = o['texture']
            localAssetList.append(aa)
        if 'audioClipString' in o:
            aa = copy.deepcopy(objectAssetTemplate)
            aa['audioClip'] = o['audioClipString']
            localAssetList.append(aa)
            #print('audioClipString', o['audioClipString'])

        if 'componentsToAdd' in o:
            cc = o['componentsToAdd']
            for i, com in enumerate(cc):
                aa = copy.deepcopy(objectAssetTemplate)
                aa['component'] = com
                aa['element'] = i
                localAssetList.append(aa)
        if 'tmp' in o:
            aa = copy.deepcopy(objectAssetTemplate)
            aa['tmp'] = o['tmp']
            aa['component'] = None
            localAssetList.append(aa)

        return localAssetList


if __name__ == "__main__":
    print('assetEdit.py')

    moduleList = []
    fn = "demo10.json"
    f = open(fn, "r")
    lines = []
    for l in f:
        lines.append(l)
    f.close()

    for ii, l in enumerate(lines):
        moduleList.append(json.loads(l))
        print('Module ' + str(ii) + ": " + moduleList[-1]['moduleName'])
    ae = assetEditor(None, None, None, moduleList)
    ae.viewAssets()
