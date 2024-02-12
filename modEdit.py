
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


class moduleEditor:

    def __init__(self, ds, theFrame, theWindow, parent=None, windowName=None):

        self.moduleFrame = theFrame
        self.theWindow = theWindow
        self.theWindow.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.moduleList = []
        self.lines = []
        self.moduleButtonList = []
        self.editingEnabled = True
        self.ds = ds
        self.parent = parent
        self.moduleName = ds['moduleName']
        self.windowName = windowName

        path = "./"
        outputPath = "./"
        verbose = True
        self.sc = sceneConverter(path, outputPath, verbose)

    def on_closing(self):
        print("closing")

        closeOK = messagebox.askyesnocancel(
            "Exit Editor", "Do you want to: \n Yes - Exit and save your changes \n No - Exit and discard your changes \n Cancel the exit?")
        if closeOK == True:
            print("sending the signal")
            print("parent", self.parent)
            self.parent.signalJsonEditorClosed(json.dumps(self.ds))
            self.theWindow.destroy()
        elif closeOK == False:
            self.parent.signalJsonEditorClosed()
            self.theWindow.destroy()
        else:
            pass

    def createMenus(self):
        self.menubar = tk.Menu(self.theWindow)
        self.theWindow.config(menu=self.menubar)

        self.fileMenu = tk.Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="Close", command=self.on_closing)
        # self.fileMenu.add_command(label="Save", command=self.saveFile)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)

        editmenu = tk.Menu(self.menubar, tearoff=0)
        editmenu.add_command(
            label="Delete Clips", command=lambda: self.createModuleButtons("Delete Clips"))
        editmenu.add_command(
            label="Reorder Clips", command=lambda: self.createModuleButtons("Reorder Clips"))
        editmenu.add_command(
            label="Add Clip", command=lambda: self.createModuleButtons("Add Clips"))
        editmenu.add_command(label="Clone Clip",
                             command=lambda: self.createModuleButtons("Clone Clips"))
        editmenu.add_command(label="Clone Object",
                             command=lambda: self.createModuleButtons("Clone Object"))
        editmenu.add_separator()
        editmenu.add_command(label="Import an Object",
                             command=self.importObject)
        editmenu.add_command(
            label="Import Object List from Excel", command=self.importFromExcel)
        editmenu.add_command(label="Delete Objects", 
                             command=lambda: self.createModuleButtons("Delete Object"))

        editmenu.add_command(label="Print Assets",
                             command=self.printAssets)

        self.menubar.add_cascade(label="Edit", menu=editmenu)
        # self.theWindow.configure(menu=self.menubar)

    # create a grid of buttons for the objects vs the clips

    def createGrid(self):
        if not 'objects' in self.ds or not 'clips' in self.ds:
            messagebox.showerror("Error", "No objects or clips in dataset")
            return

        self.createMenus()
        self.processModule()
        self.createModuleButtons()

        # print(self.dfModule)

    def processModule(self):

        ds = self.ds
        
        for o in ds['objects']:
            if o == "" or o == [] or o == None:
                ds['objects'].remove(o)
                
        try: 
            print("objects", ds['objects'])
            olist = ds['objects']
            self.objectNames = [o['name'] for o in olist]
        except:
            self.objectNames = []

        try: 
            self.clipNames = [c['clipName'] for c in ds['clips']]
        except:
            self.clipNames = []
            
        self.dfModule = pd.DataFrame(columns=['Object Name'] + self.clipNames)

        self.clipList = []
        for c in ds['clips']:
            objMods = []
            for o in c['objectChanges']:
                objMods.append(o['name'])
            self.clipList.append(objMods)

        # clist = ['Object Name'] + clipnames
        # dfActions = pd.DataFrame(columns=['Object Name'] + self.clipNames)
        self.dfModule['Object Name'] = (self.objectNames)

        for c in ds['clips']:
            self.dfModule[c['clipName']] = ""
            for o in c['objectChanges']:
                # print("cliplist", c['clipName'], o['name'])
                self.dfModule.loc[self.dfModule['Object Name']
                                  == o['name'], c['clipName']] = "X"
            # print("--")

    def createModuleButtons(self, action=None):

        print("action", action)
        for widget in self.moduleFrame.winfo_children():
            widget.destroy()

        label = tk.Label(self.moduleFrame, text=self.windowName)
        label.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S)
        label.config(font=("Courier", 18))

        buttonCount = 0
        self.moduleButtonList = []

        # start with the object buttons
        objectColumn = 2
        rowStart = 5

        self.reorderMenus = []
        self.theOptions = list(range(len(self.clipNames)))
        self.currentOrder = copy.deepcopy(self.theOptions)
        self.orderList = []

        if action == "Delete Clips":
            row = rowStart - 2
            columnStart = objectColumn + 1
            for i in range(len(self.clipNames)):
                self.moduleButtonList.append(
                    tk.Button(self.moduleFrame, text="Delete ", command=lambda i=i, buttonCount=buttonCount: self.deleteClip(i, buttonCount)))
                self.moduleButtonList[-1].grid(row=row, column=i+columnStart, columnspan=1,
                                               sticky=tk.W+tk.E+tk.N+tk.S)
                print(i, buttonCount, self.clipNames[i])
                buttonCount += 1

        if action == "Clone Clips":
            row = rowStart - 2
            columnStart = objectColumn + 1
            for i in range(len(self.clipNames)):
                self.moduleButtonList.append(
                    #    tk.Button(self.moduleFrame, text="Delete " + self.clipNames[i], command=lambda i=i, buttonCount=buttonCount: self.deleteClip(i, buttonCount)))
                    tk.Button(self.moduleFrame, text="Clone ", command=lambda i=i, buttonCount=buttonCount: self.cloneClip(i, buttonCount)))
                self.moduleButtonList[-1].grid(row=row, column=i+columnStart, columnspan=1,
                                               sticky=tk.W+tk.E+tk.N+tk.S)
                print(i, buttonCount, self.clipNames[i])
                buttonCount += 1

        if action == "Reorder Clips":
            row = rowStart - 2
            columnStart = objectColumn + 1
            for i in range(len(self.clipNames)):
                self.orderList.append(tk.IntVar())
                self.orderList[-1].set(i)

                self.reorderMenus.append(tk.OptionMenu(
                    self.moduleFrame, self.orderList[-1],  *
                    self.theOptions,
                    command=self.updateMenus))
                self.reorderMenus[-1].grid(row=row,
                                           column=i+columnStart, sticky=tk.EW)

        if action == "Add Clips":
            self.addClip()

        for i in range(len(self.objectNames)):
            self.moduleButtonList.append(
                tk.Button(self.moduleFrame, text=self.objectNames[i], command=lambda i=i, buttonCount=buttonCount: self.editObject(i, buttonCount)))
            self.moduleButtonList[-1].grid(row=i+rowStart, column=objectColumn, columnspan=1,
                                           sticky=tk.W+tk.E+tk.N+tk.S)
            buttonCount += 1
            if action == "Clone Object":
                print("clone!!!!")
                self.moduleButtonList.append(
                    tk.Button(self.moduleFrame, text="Clone", command=lambda i=i, buttonCount=buttonCount: self.cloneObject(i, buttonCount)))
                self.moduleButtonList[-1].grid(row=rowStart + i, column=objectColumn-1,
                                               columnspan=1,
                                               sticky=tk.W+tk.E+tk.N+tk.S)
                buttonCount += 1
                
            if action == "Delete Object":
                print("delete!!!!")
                columnStart = objectColumn - 1
                self.moduleButtonList.append(
                    tk.Button(self.moduleFrame, text="Delete", command=lambda i=i, buttonCount=buttonCount: self.deleteObject(i, buttonCount)))
                self.moduleButtonList[-1].grid(row=rowStart + i, column=columnStart,
                                                columnspan=1,
                                                sticky=tk.W+tk.E+tk.N+tk.S)
                buttonCount += 1

        if action == None:
            self.moduleButtonList.append(
                tk.Button(self.moduleFrame, text="New Object", command=self.newObject))
            self.moduleButtonList[-1].grid(row=rowStart + len(self.objectNames)+1, column=objectColumn,
                                           columnspan=1,
                                           sticky=tk.W+tk.E+tk.N+tk.S)
            buttonCount += 1

        # now the clip buttons on the top
        clipStart = objectColumn + 1
        for i in range(len(self.clipNames)):
            self.moduleButtonList.append(
                tk.Button(self.moduleFrame, text=self.clipNames[i], command=lambda i=i, buttonCount=buttonCount: self.editClip(i, buttonCount)))
            self.moduleButtonList[-1].grid(row=rowStart-1, column=i+clipStart, columnspan=1,
                                           sticky=tk.W+tk.E+tk.N+tk.S)
            buttonCount += 1

        for i in range(len(self.objectNames)):
            for j in range(len(self.clipNames)):
                if self.dfModule.iloc[i, j+1] == "X":
                    self.moduleButtonList.append(
                        tk.Button(self.moduleFrame, text="X", command=lambda i=i, j=j, buttonCount=buttonCount: self.editObjectModification(i, j, buttonCount)))
                    self.moduleButtonList[-1].grid(row=i+rowStart, column=j+clipStart, columnspan=1,
                                                   sticky=tk.W+tk.E+tk.N+tk.S)
                else:
                    self.moduleButtonList.append(
                        tk.Button(self.moduleFrame, text="", command=lambda i=i, j=j, buttonCount=buttonCount: self.editObjectModification(i, j, buttonCount)))
                    self.moduleButtonList[-1].grid(row=i+rowStart, column=j+clipStart, columnspan=1,
                                                   sticky=tk.W+tk.E+tk.N+tk.S)
                buttonCount += 1

        if action == "Reorder Clips":
            self.moduleButtonList.append(
                tk.Button(self.moduleFrame, text="Reorder", command=self.acceptNewOrder))
            self.moduleButtonList[-1].grid(row=rowStart + len(self.objectNames)+1, column=2, columnspan=2,
                                           sticky=tk.W+tk.E+tk.N+tk.S)

        for i in range(len(self.moduleButtonList)):
            self.moduleButtonList[i].configure(bg='white')

    # def reorderClips(self):
    #    print("reorder!!!")

    def importObject(self):
        print('import object')

        if self.editingEnabled == False:
            okToContinue = messagebox.askyesno(
                "Edit new object?",
                "Are you sure you want to open a new object?  You are curently editing object:" + str(self.moduleID))
            if okToContinue == False:
                return

        fn = fd.askopenfilename()
        try:
            f = open(fn, "r")
            ll = []
            for l in f:
                ll.append(l)
            f.close()

            lines = "".join(ll)
            try:
                dstmp = json.loads(lines)
            except:
                messagebox.showerror("Error", "Error in json file")

            o1 = copy.deepcopy(dstmp)
            self.ds['objects'].append(o1)
            print('objects =', self.ds['objects'])
            #self.ds['objects'][-1]['name'] = self.ds['objects'][-1]['name'] + "_clone"
            self.processModule()
            self.createModuleButtons()
            #dsModule = copy.deepcopy(dstmp)
            #self.moduleList.append(dsModule)
            #self.moduleID = len(self.moduleList) - 1
            #self.showModule2()

            # showModule2()
        except:
            messagebox.showerror("Error", "Error loading json - invalid file")
        # showModule2()
        
        

# THIS ISN'T WORKING !!!!!!!!!!!!!!!!!


    def importFromExcel(self):
        print('import from excel')
        fn = fd.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        try:
            df2 = pd.read_excel(fn)  # ,sheet_name="Sheet3")
        except:
            messagebox.showerror(
                "Error", "Cannot parse your file as an Excel file")
        # drop any unnamed columns
        cols = df2.columns
        for i in range(10):
            if 'Unnamed: ' + str(i) in cols:
                df2.drop('Unnamed: ' + str(i), axis=1, inplace=True)

        print("fn is ", fn)
        cols = df2.columns.to_list()
        if "x" in cols:
            print("x is in cols")

            if 'x' in cols:
                df2 = self.sc.combineColumns(
                    df2, 'position', ['x', 'y', 'z'], ['x', 'y', 'z'])
            if 'rx' in cols:
                df2 = self.sc.combineColumns(
                    df2, 'rotation', ['rx', 'ry', 'rz'], ['x', 'y', 'z'])
            if 'sx' in cols:
                df2 = self.sc.combineColumns(
                    df2, 'scale', ['sx', 'sy', 'sz'], ['x', 'y', 'z'])
            if 'tmp' in cols:
                df2 = self.sc.combineColumns(df2, 'tmp', ['textField', 'textColor', 'fontSize', 'wrapText'], [
                    'textField', 'color', 'fontSize', 'wrapText'])
            if 'ex' in cols:
                df2 = self.sc.combineColumns(df2, 'eulerAngles', [
                    'ex', 'ey', 'ez'], ['x', 'y', 'z'])

        print(df2)
        oo = self.sc.createJsonFromDataFrame(df2)
        for o in oo:
            newObjectName = o['name']
            print(newObjectName, o)
            if newObjectName in self.objectNames:
                print("object already exists")
                if messagebox.askyesno("Overwrite", "Object " + newObjectName + " already exists. Overwrite?"):
                    print("overwrite")
                    for i in range(len(self.ds['objects'])):
                        if self.ds['objects'][i]['name'] == newObjectName:
                            self.ds['objects'][i] = copy.deepcopy(o)
                            break
            else:
                self.ds['objects'].append(copy.deepcopy(o))
        self.createModuleButtons()

    def cloneObject(self, i, buttonCount):
        print("clone object", i, buttonCount)
        self.ds['objects'].append(copy.deepcopy(self.ds['objects'][i]))
        self.ds['objects'][-1]['name'] = self.ds['objects'][-1]['name'] + "_clone"
        self.processModule()
        self.createModuleButtons()
        
        
    def deleteObject(self, i, buttonCount):
        print("delete object", i, buttonCount)
        yn = messagebox.askyesno("Delete Object", 
                                 "Are you sure you want to delete object and all its references within clips? " + 
                                 self.ds['objects'][i]['name'] + "?")
        if yn == False:
            self.processModule()
            self.createModuleButtons()
            return
        
        objectName = self.ds['objects'][i]['name']
        self.ds['objects'].pop(i)
        self.processModule()
        self.createModuleButtons()
        
        for c in self.ds['clips']:
            clipName = c['clipName']
            for oo in c['objectChanges']:
                if oo['name'] == objectName:
                    print("found object in clip ", clipName)
                    c['objectChanges'].remove(oo)
                    #break


    def newObject(self):
        print('new object')
        tentry = askstring("Object Name", "What is the object's name?")
        otmp = {"type": "Prefabs/clickableSphere",
                "position": {"x": 0.0, "y": 0.0, "z": 1.5},
                "scale": {"x": 1.0, "y": 1.0, "z": 1.0},
                "name": tentry,
                "parent": "[_DYNAMIC]",
                }
        print('new object name is ', tentry)
        if tentry != None:
            self.ds['objects'].append(copy.deepcopy(otmp))
            self.processModule()
            self.createModuleButtons()
            

        

    def acceptNewOrder(self, theEvent=None):
        ds1 = copy.deepcopy(self.ds)
        currentClips = ds1['clips']
        newClips = []
        for i in range(len(self.currentOrder)):
            for j in range(len(self.currentOrder)):
                kk = self.orderList[j].get()
                if kk == i:
                    print(i, j, kk)
                    newClips.append(currentClips[j])
        ds1['clips'] = copy.deepcopy(newClips)

        self.ds = copy.deepcopy(ds1)

        self.processModule()
        self.createModuleButtons()

    def deleteClip(self, i, buttonID):
        del self.ds['clips'][i]
        self.processModule()
        self.createModuleButtons()

    def cloneClip(self, i, buttonID):
        clipTmp = copy.deepcopy(self.ds['clips'][i])
        clipTmp['clipName'] = clipTmp['clipName'] + ' (clone)'
        self.ds['clips'].append(clipTmp)
        self.processModule()
        self.createModuleButtons()

    def addClip(self):
        clipTmp = {'clipName': 'New Clip', 'timeToEnd': 3,
                   'autoAdvance': False, 'objectChanges': [],
                   'audioClipString': ""}
        self.ds['clips'].append(clipTmp)
        self.processModule()
        self.createModuleButtons()
    # def updateMenus(self, value):

    #    print(value)

    def updateMenus(self, theEvent=None):
        oldList = copy.deepcopy(self.currentOrder)
        newList = []
        for i in range(len(self.orderList)):
            newList.append(self.orderList[i].get())

        update = self.reOrderList(oldList, newList)
        for i in range(len(self.orderList)):
            self.orderList[i].set(update[i])
            self.currentOrder[i] = update[i]

    def reOrderList(self, oldList, newList):
        # both list must be the same length
        assert len(oldList) == len(newList)

        # find the index of the change - both lists must be the same
        changeIndex = -1
        for i in range(len(oldList)):
            if oldList[i] != newList[i]:
                assert changeIndex == -1
                changeIndex = i
                oldValue = oldList[i]
                newValue = newList[i]

        update = []
        if changeIndex > -1:
            # update the lists
            if oldValue > newValue:
                for i, v in enumerate(newList):
                    if v >= newValue and i != changeIndex and v < oldValue:
                        v = v + 1
                    update.append(v)
            else:
                for i, v in enumerate(newList):
                    if v <= newValue and i != changeIndex and v > oldValue:
                        v = v - 1
                    update.append(v)
        else:
            for v in oldList:   # no changes, so return the original list
                update.append(v)
        return update



    def printAssets(self):
        for o in self.ds['objects']:
            print("object", o['name'])
            if 'texture' in o:
                print("  -texture", o['texture'])
            if 'audioClipString' in o:
                print("  -audioClipString", o['audioClipString'])
            if 'componentsToAdd' in o:
                print("  -componentsToAdd", o['componentsToAdd'])
            if 'tmp' in o:
                print("  -tmp", o['tmp'])


# import an object - ditto
# import a list of objects  - this IS needed

# edit assets - images/textures/sounds
# rename assets

    def editObject(self, i, buttonID):

        if self.editingEnabled == False:
            messagebox.showerror(
                "Error", "You are already editing an object.  Please finish that edit before starting another one.")
            return

        self.objectBeingEdited = i
        self.clipBeingEdited = None
        self.editingEnabled = False
        self.buttonIndex = buttonID
        self.moduleButtonList[self.buttonIndex].configure(bg='red')

        dstmp = self.ds['objects'][i]
        print('editing Object ', i, dstmp['name'])

        theWindow = tk.Toplevel(self.theWindow)
        theWindow.title("JSON Editor")
        theWindow.geometry('1000x700')
        theWindow.configure(background='white')

        ttheFrame = VerticalScrolledFrame(theWindow)
        ttheFrame.pack(fill=tk.BOTH, expand=True)
        theFrame = ttheFrame.interior
        # ds = self.moduleList[i]
        oname = "Object: " + dstmp['name']
        jsObj = jsonEditor(dstmp, theFrame, theWindow, self, oname)
        jsObj.showModule2()

    def editClip(self, i, buttonID):

        if self.editingEnabled == False:
            messagebox.showerror(
                "Error", "You are already editing an object.  Please finish that edit before starting another one.")
            return

        print('editing clip', i)
        self.objectBeingEdited = None
        self.clipBeingEdited = i
        self.editingEnabled = False
        self.buttonIndex = buttonID

        self.moduleButtonList[self.buttonIndex].configure(bg='red')

        dstmp = self.ds['clips'][i]
        print('editing Clip ', i, dstmp['clipName'])

        theWindow = tk.Toplevel(self.theWindow)
        theWindow.title("JSON Editor")
        theWindow.geometry('1000x1300')
        theWindow.configure(background='white')

        ttheFrame = VerticalScrolledFrame(theWindow)
        ttheFrame.pack(fill=tk.BOTH, expand=True)
        theFrame = ttheFrame.interior
        # ds = self.moduleList[i]
        oname = "Clip: " + dstmp['clipName']
        jsObj = jsonEditor(dstmp, theFrame, theWindow, self, oname)
        jsObj.showModule2()

    def editObjectModification(self, i, j, buttonID):

        if self.editingEnabled == False:
            messagebox.showerror(
                "Error", "You are already editing an object.  Please finish that edit before starting another one.")
            return

        self.objectBeingEdited = i
        self.clipBeingEdited = j
        self.editingEnabled = False
        self.buttonIndex = buttonID
        self.moduleButtonList[self.buttonIndex].configure(bg='red')

        # print("")
        # print('editing object modification', i, j)
        dstmp = self.ds['clips'][j]
        # print('editing Clip ', j, dstmp['clipName'])
        # print("the object modification is ", self.objectNames[i])
        # print("---")

        found = False
        objectIndex = -1
        for kk, o in enumerate(dstmp['objectChanges']):
            if o['name'] == self.objectNames[i]:
                found = True
                objectIndex = kk

        if found == False:
            # print("no object  found")
            dsEdit = self.ds['objects'][i]  # a copy of the base object

        else:
            # print("object  found")
            dsEdit = dstmp['objectChanges'][objectIndex]  # the current edit

        # self.editingEnabled = False
        # self.moduleBeingEdited = i

        theWindow = tk.Toplevel(self.theWindow)
        theWindow.title("JSON Editor")
        theWindow.geometry('1000x1300')
        theWindow.configure(background='white')

        ttheFrame = VerticalScrolledFrame(theWindow)
        ttheFrame.pack(fill=tk.BOTH, expand=True)
        theFrame = ttheFrame.interior
        # ds = self.moduleList[i]
        oname = "Clip: " + dstmp['clipName'] + \
            " - Object: " + self.objectNames[i]
        jsObj = jsonEditor(dsEdit, theFrame, theWindow, self, oname)
        jsObj.showModule2()

    def signalJsonEditorClosed(self, dsString=None):

        # the idea is to figure out the key being used, and then figure out the
        # element number within the list.  The keyData has the starting and ending
        # of the elements in this list.  So, we just substract the actual line
        # number from the starting line number, and that gives us the index.
        print("signaled closed", self)
        print("ids = ", self.objectBeingEdited, self.clipBeingEdited)
        self.editingEnabled = True
        self.moduleButtonList[self.buttonIndex].configure(bg='white')

        if dsString != None:
            ds = json.loads(dsString)
            self.editingEnabled = True

            if ds != None:
                if self.clipBeingEdited != None:
                    if self.objectBeingEdited != None:
                        # if this is modification to an existing object change, find the clip and updated it
                        for i, obj in enumerate(self.ds['clips'][self.clipBeingEdited]['objectChanges']):
                            if obj['name'] == self.objectNames[self.objectBeingEdited]:
                                self.ds['clips'][self.clipBeingEdited]['objectChanges'][i] = ds
                                return
                        # if we did not find the object change, append it
                        self.ds['clips'][self.clipBeingEdited]['objectChanges'].append(
                            ds)

                    else:
                        # just the clip
                        self.ds['clips'][self.clipBeingEdited] = ds
                        print("clips merged ")
                else:
                    if self.objectBeingEdited != None:
                        self.ds['objects'][self.objectBeingEdited] = ds
                        print("merged clip into file")
                    else:
                        print(" no clip or object id")

        self.processModule()
        self.createModuleButtons()
