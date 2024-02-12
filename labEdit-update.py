# lab editor
# John Wallin, 2024-02-12
# Middle Tennessee State University

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
from modEdit import moduleEditor
from assetEdit import assetEditor


class labEditor:

    def __init__(self, ds, theFrame, theWindow):

        self.moduleFrame = theFrame
        self.theWindow = theWindow
        self.theWindow.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.moduleList = []
        self.lines = []
        self.moduleButtonList = []
        self.editingEnabled = True
        self.ds = ds
        self.originalLab = None
        self.labFormat = "old"

    def on_closing(self):
        print("closing")
        self.theWindow.destroy()
        exit()

    def openLab(self, fn=None):

        self.moduleList = []
        print("openLab", fn)
        if fn == None:
            fn = fd.askopenfilename()
        try:
            f = open(fn, "r")
            ll = f.read()
            f.close()
            
            dtmp = json.loads(ll)
            alist = dtmp['ActivityModules']            
            self.lines = []
            for a in alist:
                #ss = json.dumps(a, indent=4)
                self.lines.append(a)
            self.originalLab = copy.deepcopy(dtmp)
            messagebox.showinfo("Info", "Lab loaded successfully - transmission format")
            self.labFormat = "new"
            
        except:
            # if this fails, then try the old format
            try:
                fn = fd.askopenfilename()
                f = open(fn, "r")
                self.lines = []
                for l in f:
                    self.lines.append(l)
                f.close()
                messagebox.showinfo("Info", "Lab loaded successfully - old format")
                self.labFormat = "old"
                
            except:                
                messagebox.showerror(
                    "Error", "Error loading module - invalid file")

        try:
            for l in self.lines:
                self.moduleList.append(json.loads(l))
        except:
            messagebox.showerror("Error", "Error in lab json files")

        self.moduleID = 0
        self.dsModule = self.moduleList[self.moduleID]
        self.currentFileName = fn
        self.showModule2()

    def createModuleList(self):
        self.moduleList = []
        if self.moduleID > -1:
            for i in range(len(self.lines)):
                dtmp = json.loads(self.lines[i])
                self.moduleList.append(copy.deepcopy(dtmp))

        else:
            self.moduleList.append(copy.deepcopy(self.ds))
            self.moduleID = 0

    def openJson(self):  # not working

        if self.editingEnabled == False:
            okToContinue = messagebox.askyesno(
                "Edit new module?",
                "Are you sure you want to open a new module?  You are curently editing module" + str(self.moduleID))
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

            print('lines = ', lines)
            dsModule = copy.deepcopy(dstmp)
            self.moduleList.append(dsModule)
            self.moduleID = len(self.moduleList) - 1
            self.showModule2()

            # showModule2()
        except:
            messagebox.showerror("Error", "Error loading json - invalid file")
        # showModule2()

    def saveJson(self):
        if self.moduleID < 0 or self.moduleID > len(self.moduleList):
            messagebox.showerror(
                "Error",  "Select a module before exporting it")
            return
        fn = fd.asksaveasfilename()
        try:
            dstmp = self.moduleList[self.moduleID]
            f = open(fn, "w")
            f.write(json.dumps(dstmp, indent=4))
            f.close()
        except:
            messagebox.showerror("Error", "Error saving json file")

    def saveLab(self, fn=None, labFormat=None):


        newLabTemplate = {
            "Transmission": "true",
            "Lab_ID": "Moon Phase Lab",
            "Author": "John Wallin",
            "CourseName": "Introduction to Astronomy",
            "EstimatedLength": "5 minutres",
            "NumModules": "1",
            "Objectives": [
                "Learn to identify moon phases"
            ],
            "ActivityModules":[],
            "Assets": []
        }
        if labFormat == "new" and self.labFormat == "old":
            print("old lab being saved as new lab")
            self.originalLab = copy.deepcopy(newLabTemplate)
            self.labFormat = "new"
        
        elif labFormat == None:
            labFormat = self.labFormat
        
              
        if labFormat == "old":
            print("saveLab old format")
            if fn == None:
                overwrite = messagebox.askyesno(
                    "Overwrite", "Overwrite existing file?")
                if overwrite == False:
                    fn = fd.asksaveasfilename()
                else:
                    fn = self.currentFileName
            try:
                f = open(fn, "w", encoding="utf-8")
                for i in range(len(self.moduleList)):
                    print(i, self.moduleList[i]['moduleName'])
                    ll = json.dumps(
                        self.moduleList[i], ensure_ascii=False)
                    f.write(ll+"\n")
                f.close()
            except:
                messagebox.showerror("Error", "Error saving lab file")
        else:
            print("saveLab new format")
            if fn == None:
                overwrite = messagebox.askyesno(
                    "Overwrite", "Overwrite existing file?")
                if overwrite == False:
                    fn = fd.asksaveasfilename()
                else:
                    fn = self.currentFileName
        
            try:
                print("opening")
                f = open(fn, "w", encoding="utf-8")
                newModule = copy.deepcopy(self.originalLab)
                newModule['ActivityModules'] = []
                print("ducksfsdfwswe")
                for i in range(len(self.moduleList)):
                    #print("sdfsffw", i, self.moduleList[i]['moduleName'])
                    newModule['ActivityModules'].append(self.moduleList[i])
                print("dumping")
                ll = json.dumps(newModule, ensure_ascii=False)
                f.write(ll+"\n")
                f.close()
                
                
                    
                #for i in range(len(self.moduleList)):
                #    print(i, self.moduleList[i]['moduleName'])
                #    ll = json.dumps(
                #        self.moduleList[i], ensure_ascii=False)
                #    f.write(ll+"\n")
                #f.close()
            except:
                messagebox.showerror("Error", "Error saving lab file")
        
        
        

    def closeFile(self):

        print("closeFile")

    def changeModuleID(self, newModuleID):
        self.moduleID = newModuleID
        dsModule = self.moduleList[self.moduleID]

    def moduleButtonActive(self, imodule):
        if imodule > len(self.moduleButtonIndex):
            print("ERROR: moduleButtonActive",
                  imodule, len(self.moduleButtonIndex))
        else:
            for i in range(len(self.moduleButtonIndex)):
                j = self.moduleButtonIndex[i]
                if i == imodule:
                    self.moduleButtonList[j].config(bg="lightblue")
                else:
                    self.moduleButtonList[j].config(bg="white")
            self.changeModuleID(imodule)

    def openModule(self, i):
        print("openModule", i)

        self.editingEnabled = False
        self.moduleBeingEdited = i
        self.moduleButtonActive(i)

        theWindow = tk.Toplevel(self.theWindow)
        theWindow.title("Module Editor")
        theWindow.geometry('1000x800')
        theWindow.configure(background='white')

        ttheFrame = VerticalScrolledFrame(theWindow)
        ttheFrame.pack(fill="both", expand=True)
        theFrame = ttheFrame.interior
        ds = self.moduleList[i]

        print("openModule", i, ds['moduleName'])
        jsModule = moduleEditor(ds, theFrame, theWindow,
                                self, ds['moduleName'])
        jsModule.createGrid()

        #jsObj = jsonEditor(ds, theFrame, theWindow, self)
        # jsObj.showModule2()

    def editModule(self, i):
        print("Edit", i)

        self.editingEnabled = False
        self.moduleBeingEdited = i
        self.moduleButtonActive(i)

        theWindow = tk.Toplevel(self.theWindow)
        theWindow.title("Edit Module")
        theWindow.geometry('1000x700')
        theWindow.configure(background='white')

        ttheFrame = VerticalScrolledFrame(theWindow)
        ttheFrame.pack(fill="both", expand=True)
        theFrame = ttheFrame.interior
        ds = self.moduleList[i]
        jsObj = jsonEditor(ds, theFrame, theWindow, self, ds['moduleName'])
        jsObj.showModule2()

    def signalJsonEditorClosed(self, ds=None):

        # the idea is to figure out the key being used, and then figure out the
        # element number within the list.  The keyData has the starting and ending
        # of the elements in this list.  So, we just substract the actual line
        # number from the starting line number, and that gives us the index.
        print("signaled closed", self)

        if ds != None:
            self.moduleList[self.moduleBeingEdited] = json.loads(ds)
        self.editingEnabled = True
        self.moduleID = -1
        self.moduleButtonActive(-1)
        self.showModule2()

    def showAssets(self):

        print("showAssets")

        self.editingEnabled = False

        theWindow = tk.Toplevel(self.theWindow)
        theWindow.title("Module Editor")
        theWindow.geometry('1000x800')
        theWindow.configure(background='white')

        ttheFrame = VerticalScrolledFrame(theWindow)
        ttheFrame.pack(fill="both", expand=True)
        theFrame = ttheFrame.interior

        assetModule = assetEditor(theFrame, theWindow,
                                  self, self.moduleList)
        assetModule.viewAssets()

    def assetCallback(self, newlab):
        print("assetCallback", newlab)

    def createModuleFrame(self, specialOption=None):

        if specialOption == None:
            infoColumn = -1
            labelColumn = 0
            # sublabelColumn = 2
            dataColumn = 1
            openColumn = 2
            editColumn = 3
        else:
            infoColumn = 0
            labelColumn = 1
            # sublabelColumn = 2
            dataColumn = 1
            openColumn = 2
            editColumn = 3

        checkBox = []
        theOptions = list(range(len(self.moduleList)))

        self.deleteModule = len(self.moduleList) * [0]
        self.moduleOrderList = len(self.moduleList) * [0]
        self.currentModuleOrder = copy.deepcopy(theOptions)
        self.moduleButtonList = []

        rr = 0
        keyCount = 0
        buttonCount = 0
        self.moduleButtonIndex = []
        for i in range(len(self.moduleList)):

            if self.editingEnabled == False:
                specialOption = None

            if specialOption == "Delete":
                self.deleteModule[keyCount] = tk.IntVar()
                checkBox.append(tk.Checkbutton(self.moduleFrame, text=str(keyCount),
                                               variable=self.deleteModule[keyCount], onvalue=1, offvalue=0,
                                               background='white'))
                checkBox[-1].grid(row=rr, column=infoColumn, sticky=tk.N)
                # print(k, keyCount, len(deleteList), len(cb))

            if specialOption == "Reorder":

                self.moduleOrderList[keyCount] = tk.IntVar()
                self.moduleOrderList[keyCount].set(theOptions[keyCount])
                checkBox.append(tk.OptionMenu(self.moduleFrame, self.moduleOrderList[keyCount], *theOptions,
                                              command=self.updateModuleMenus))
                checkBox[-1].grid(row=rr, column=infoColumn, sticky=tk.W)

            if specialOption == "Clone":
                checkBox.append(tk.Button(self.moduleFrame, text="Clone", bg="white",
                                          command=lambda i=i: self.cloneModule(i)))
                checkBox[-1].grid(row=rr, column=infoColumn, sticky=tk.W)

            self.moduleButtonList.append(tk.Button(self.moduleFrame,
                                                   text="Module " +
                                                   str(i) + "  " +
                                                   self.moduleList[i]['moduleName'],
                                                   bg="white", command=lambda i=i: self.moduleButtonActive(i)))
            self.moduleButtonList[-1].grid(row=rr,
                                           column=labelColumn, sticky=tk.W)

            # if buttonCount == self.moduleID:
            #    self.moduleButtonList[-1].config(bg="lightblue")
            # else:
            self.moduleButtonList[i].config(bg="white")
            self.moduleButtonIndex.append(buttonCount)
            buttonCount = buttonCount + 1

            self.moduleButtonList.append(tk.Button(self.moduleFrame, text="Open", bg="white",
                                                   command=lambda i=i: self.openModule(i)))
            self.moduleButtonList[-1].grid(row=rr,
                                           column=openColumn, sticky=tk.W)
            buttonCount = buttonCount + 1

            self.moduleButtonList.append(tk.Button(self.moduleFrame, text="Edit", bg="white",
                                                   command=lambda i=i: self.editModule(i)))
            self.moduleButtonList[-1].grid(row=rr,
                                           column=editColumn, sticky=tk.W)
            buttonCount = buttonCount + 1

            rr = rr + 1
            keyCount = keyCount + 1

        if specialOption == "Delete":
            print("delete module button!")
            self.moduleButtonList.append(tk.Button(self.moduleFrame, text="Delete Modules",
                                                   bg="white", command=lambda: self.removeModules()))
            self.moduleButtonList[-1].grid(row=rr,
                                           column=labelColumn, sticky=tk.W)

        elif specialOption == "Reorder Modules":
            self.moduleButtonList.append(tk.Button(self.moduleFrame, text="Reorder Modules",
                                                   bg="white", command=lambda: self.reorderModules()))
            self.moduleButtonList[-1].grid(row=rr,
                                           column=labelColumn, sticky=tk.W)

        else:
            self.moduleButtonList.append(tk.Button(self.moduleFrame, text="Add Module",
                                                   bg="white", command=lambda: self.addModule()))
            self.moduleButtonList[-1].grid(row=rr,
                                           column=labelColumn, sticky=tk.W)
            self.moduleButtonList.append(tk.Button(self.moduleFrame, text="Import Module",
                                                   bg="white", command=lambda: self.openJson()))
            self.moduleButtonList[-1].grid(row=rr,
                                           column=dataColumn, sticky=tk.W)

    def cloneModule(self, i):
        print("clone module", i)
        self.moduleList.append(copy.deepcopy(self.moduleList[i]))
        self.moduleList[-1]['moduleName'] = self.moduleList[-1]['moduleName'] + \
            " (clone)"
        for widget in self.moduleFrame.winfo_children():
            widget.destroy()
        self.createModuleFrame()

    def removeModules(self):

        print("delete module")
        s = "Are you sure you want to delete these modules?"
        acceptDelete = tk.messagebox.askyesno("Delete the modules", s)
        if acceptDelete == True:

            mdlist = []
            for i in range(len(self.moduleList)):
                mtmp = self.moduleList[i]

                if self.deleteModule[i].get() == 1:
                    mdlist.append(mtmp)

        for mtmp in mdlist:
            self.moduleList.remove(mtmp)

        for widget in self.moduleFrame.winfo_children():
            widget.destroy()
        # createModuleList()
        self.createModuleFrame()

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

    def updateModuleMenus(self, aa):

        oldList = copy.deepcopy(self.currentModuleOrder)
        newList = []
        for i in range(len(self.moduleOrderList)):
            newList.append(self.moduleOrderList[i].get())

        update = self.reOrderList(oldList, newList)
        for i in range(len(self.moduleOrderList)):
            self.moduleOrderList[i].set(update[i])
            self.currentModuleOrder[i] = update[i]

    def reorderModules(self):

        print("starting reorder")

        moduleListTmp = []
        for i in range(len(self.moduleList)):
            for j in range(len(self.moduleList)):
                if self.currentModuleOrder[j] == i:
                    moduleListTmp.append(self.moduleList[j])

        self.moduleList = copy.deepcopy(moduleListTmp)

        for i in range(len(self.moduleList)):
            print(i, self.moduleList[i]['moduleName'])

        for widget in self.moduleFrame.winfo_children():
            widget.destroy()

        # createModuleList()
        self.createModuleFrame()

        # print("accept")

    def addModule(self):

        if self.editingEnabled == False:
            return

        print("adding Module")
        tentry = askstring("Module Name", "What is the module's name?")

        genericModule = {
            "moduleName": "",
            "specificName": "",
            "prefabName": "demoPrefab",
            "prerequisiteActivities": [],
            "educationalObjectives": [
                ""
            ],
            "instructions": [
                "click on something... anything!"
            ],
            "numRepeatsAllowed": 0,
            "numGradableRepeatsAllowed": 0,
            "gradingCriteria": "",
            "currentScore": 0.0,
            "bestScore": 0.0,
            "completed": False,
            "currentSubphase": 0,
            "subphaseNames": [],
            "urlJson": "",
            "json": "",
            "timeToEnd": 15.0,
            "endUsingButton": True,
            "objects": [
            ],
            "clips": []
        }

        genericModule['moduleName'] = tentry
        ds = copy.deepcopy(genericModule)
        print("moduleLIst length", len(self.moduleList))

        self.moduleList.append(ds)
        print("moduleLIst length", len(self.moduleList))
        # createModuleList()
        self.createModuleFrame()
        self.showModule2()
        
    def saveLabNewFormat(self):
        self.saveLab(labFormat="new")
    
    def saveLabOldFormat(self):
        self.saveLab(labFormat="old")
        

    def showModule2(self, displayOptions=None):

        rstart = 1

        # FILE MENU OPTIONS
        menubar = tk.Menu(self.theWindow)
        filemenu = tk.Menu(menubar, tearoff=0)
        #filemenu.add_command(label="New", command=self.donothing)
        filemenu.add_command(
            label="Open Lab", command=lambda: self.openLab())
        # filemenu.add_command(
        #    label="Open JSON", command=lambda: self.openJson())

        # filemenu.add_command(label="Close", command=self.closeFile)

        filemenu.add_command(
            label="Save Lab", command=lambda: self.saveLab())
        filemenu.add_command(label="Save Lab As",
                             command=lambda: self.saveLab())
        filemenu.add_command(label="Save lab as new format and new name",
                             command=lambda: self.saveLabNewFormat())
        filemenu.add_command(label="Save lab as old format and new name",
                             command=lambda: self.saveLabOldFormat())
        filemenu.add_separator()
        filemenu.add_command(label="Close Window", command=self.on_closing)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0)

        # editmenu.add_command(label="Add", command=lambda: self.modifyData("Add"))
        editmenu.add_command(
            label="Add Module", command=lambda: self.addModule())
        editmenu.add_command(
            label="Delete", command=lambda: self.showModule2("Delete"))
        editmenu.add_command(
            label="Reorder", command=lambda: self.showModule2("Reorder"))
        editmenu.add_command(
            label="Clone Module", command=lambda: self.showModule2('Clone'))

        editmenu.add_command(label="Import Json Module from File",
                             command=lambda: self.openJson())
        editmenu.add_command(label="Export Json Module to File",
                             command=lambda: self.saveJson())

        menubar.add_cascade(label="Edit", menu=editmenu)

        assetmemu = tk.Menu(menubar, tearoff=0)
        assetmemu.add_command(label="Show assets",
                              command=lambda: self.showAssets())
        menubar.add_cascade(label="Assets", menu=assetmemu)

        self.theWindow.configure(menu=menubar)

        for widget in self.moduleFrame.winfo_children():
            widget.destroy()

        ss = "Lab Editor"

        title = tk.Label(self.moduleFrame, text=ss,
                         font=("Arial Bold", 20), background="#ffffff")
        title.grid(column=0, row=0, columnspan=3, sticky=tk.NSEW)

        for widget in self.moduleFrame.winfo_children():
            widget.destroy()
        self.createModuleFrame(displayOptions)


if __name__ == "__main__":

    genericModule = {
        "moduleName": "",
        "specificName": "",
        "prefabName": "demoPrefab",
        "prerequisiteActivities": [],
        "educationalObjectives": [
            ""
        ],
        "instructions": [
            "click on something... anything!"
        ],
        "numRepeatsAllowed": 0,
        "numGradableRepeatsAllowed": 0,
        "gradingCriteria": "",
        "currentScore": 0.0,
        "bestScore": 0.0,
        "completed": False,
        "currentSubphase": 0,
        "subphaseNames": [],
        "urlJson": "",
        "json": "",
        "timeToEnd": 15.0,
        "endUsingButton": True,
        "objects": [
        ],
        "clips": []
    }

    theWindow = tk.Tk()
    theWindow.title("Lab Editor")
    theWindow.geometry('800x600')
    theWindow.configure(background='white')

    theFrame = tk.Frame(theWindow, background="#ffffff",
                        width=700, height=500, padx=15, pady=5)
    theFrame.pack(fill="both", expand=True, padx=20, pady=20)

    lEditor = labEditor(genericModule, theFrame, theWindow)

    print(os.listdir())

    fn = "aaa8.json"
    fn = 'modules/AAnewmodule.json'
    fn = "demo10 - Copy.json"
    #fn = "Full_Lab_Transmission.json"
    fn = "Full_Lab_Transmission.json"
    #fn = fd.askopenfilename()
    
    
    lEditor.openLab(fn=fn)
    
    #f = open(fn, "r")
    #lEditor.lines = []
    #for l in f:
    #    lEditor.lines.append(l)
    #f.close()

    #for l in lEditor.lines:
    #    lEditor.moduleList.append(json.loads(l))

    #lEditor.moduleID = 0
    #lEditor.dsModule = lEditor.moduleList[lEditor.moduleID]
    #lEditor.currentFileName = fn

    lEditor.showModule2()
    # buildEntryFrame(self, rstart=1, expandLists=False, specialOption=None)
    tk.mainloop()
