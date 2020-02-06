#Copyright (c) 2020 LACASCADE Aurélien

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#the Software, and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#!usr/bin/python
# -*- coding: utf-8 -*-
 
# Python 3
import tkinter as tk
from tkinter import filedialog
import xml.dom.minidom
import csv
import time
 
class App(tk.Tk):
 
    def __init__(self):
        tk.Tk.__init__(self)
        self.initWidgets()
 
    def initWidgets(self):
        self.bt = tk.Button(self, text="Traiter fichier", command=self.openFile)
        self.bt.grid(row=0, column=0)
 
        self.text = tk.Text(self, width=80, height=30)
        self.text.grid(row=1, column=0)
 
    def openFile(self):
        filepath = filedialog.askopenfilename(filetypes=[('text files','.factoryio')])
        # attention, les fichiers factoryio sont encodés avec un BOM
        with open(filepath, 'r', encoding='utf-8-sig') as FILE:
            content = parse_xml_drivers(FILE)
 
        export_to_csv(content)
        self.text.insert("end", "Traitement fini !")


def parse_xml_drivers(e):
    # use the parse() function to load and parse an XML file
    doc = xml.dom.minidom.parse(e)
    # Creons la sortie
    b = []
    # allons chercher le noeud GroupIO dans la liste des objets
    GroupIOs = doc.getElementsByTagName("GroupIO")
    for GroupIO in GroupIOs:
        for node in GroupIO.childNodes:
            # Nous récupérons alors la liste des items avec le type de variable, le nom et l'adresse
            if (node.nodeType != node.TEXT_NODE):
                b.append(create_obj_line(node))
    return b

def export_to_csv(dict_data):
    # Export au format TSV
    csv_columns = ['mnemonique','adresse','variable','remarque']
    csv_file = "export_"+time.strftime("%Y%m%d-%H%M%S")+".txt"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter='\t')
            #writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def prepare_ladder_var(s):
    # Nous ne gardons que les caracteres ASCII valides
    o = "".join(i for i in s if (ord(i)<123) and ord(i)> 47)
    return o

def create_obj_line(n):
    # Nous créons une ligne
    i = 'EBOOL' if('Binary' in n.tagName) else 'INT'
    e = int(n.getAttribute('Address')) 
    if('Output' in n.tagName):
        e += 16
    a = '%m'+str(e) if('Binary' in n.tagName) else '%mw'+str(e)
    o = {'variable' : i,
    'adresse' : a,
    'mnemonique' : prepare_ladder_var(n.getAttribute('Name')),
    'remarque' : n.getAttribute('Name')}
    return o
 
#------------------------------------------------------------------------------
if __name__ == '__main__':
    app = App()
    app.mainloop()

