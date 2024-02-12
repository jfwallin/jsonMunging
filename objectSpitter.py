
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


if __name__ == "__main__":

    moduleList = []
    fn = "demo10.json"
    f = open(fn, "r")
    lines = []
    for l in f:
        lines.append(l)
    f.close()

    olist = []
    for ii, l in enumerate(lines):
        moduleList.append(json.loads(l))
        print('Module ' + str(ii) + ": " + moduleList[-1]['moduleName'])

        for o in moduleList[-1]['objects']:
            # print(o['name'])
            olist.append(o)

    # find similar objects
    finalOlist = []
    for i in range(len(olist)):
        duplicate = False
        for j in range(i+1, len(olist)):
            if olist[i]['name'] == olist[j]['name'] or olist[i]['name'][:-2] == olist[j]['name'][:-2]:
                duplicate = True

        if not duplicate:
            finalOlist.append(olist[i])

    finalOlist.sort(key=lambda x: x['name'])

    print("Final list:")
    for o in finalOlist:
        print(o['name'], o['type'])
        # print(json.dumps(o))
        print(json.dumps(o, indent=4))
        ff = open("objects/" + o['name'] + ".json", "w")
        ff.write(json.dumps(o, indent=4))
        ff.close()