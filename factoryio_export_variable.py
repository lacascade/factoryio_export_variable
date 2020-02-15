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
 
# Liste des drivers dans FactoryIO
liste_type = ['Advantech4750',
    'Advantech4704',
    'AllenBradleyLogix5000',
    'AllenBradleyMicro800',
    'AllenBradleyMicroLogix',
    'AllenBradleySLC5',
    'Automgen',
    'ControlIO',
    'MHJ',
    'ModbusTCPClient',
    'ModbusTCPServer',
    'OPCClientDA',
    'SiemensLOGOTCP',
    'SiemensS7300S7400TCP',
    'SiemensS71200S71500TCP',
    'SiemensS7PLCSIM']

class App(tk.Tk):
 
    def __init__(self):
        tk.Tk.__init__(self)
        self.initWidgets()
 
    def initWidgets(self):
        self.bt = tk.Button(self, text='Sélectionner le fichier', command=self.openFile)
        self.bt.grid(row=0, column=0)
 
        self.text = tk.Text(self, width=80, height=10)
        self.text.grid(row=1, column=0)
 
    def openFile(self):
        filepath = filedialog.askopenfilename(filetypes=[('text files','.factoryio')])
        # attention, les fichiers factoryio sont encodés avec un BOM
        with open(filepath, 'r', encoding='utf-8-sig') as FILE:
            content = parse_xml_drivers(FILE)
 
        export_to_csv(content)
        self.text.insert("end", "Traitement fini !")
            

def parse_xml_drivers(e):
    # utilisons la fonction parse pour analyser le DOM
    doc = xml.dom.minidom.parse(e)
    # Creons la sortie
    output = []
    # Variable tempo pour la liste des Modbus
    driver_list = []
    driver_name = liste_type[9]
    driver_offset = {}
    driver_offset_list = ['BitInputOffset','BitOutputOffset','FloatInputOffset','FloatOutputOffset','IntInputOffset','IntOutputOffset','NumericInputOffset','NumericOutputOffset']
    # Une fois récupéré le noeud nous allons chercher le ModbusTCPClient
    drivers = doc.getElementsByTagName(driver_name)
    for driver in drivers[0].childNodes:
        if ((driver.nodeType != driver.TEXT_NODE) and (driver.hasAttribute('PointIOKey'))):
            driver_list.append({'tagname':driver.tagName,'PointIOKey':driver.getAttribute('PointIOKey')})
        # Lecture des Offset
        if ((driver.nodeType != driver.TEXT_NODE) and (driver.tagName == 'PointIOOffset')):
            for driver_offset_item in driver_offset_list:
                driver_offset[driver_offset_item]=(0,int(driver.getAttribute(driver_offset_item)))[driver.hasAttribute(driver_offset_item)]
    # allons chercher le noeud GroupIO dans la liste des objets
    GroupIOs = doc.getElementsByTagName("GroupIO")
    for GroupIO in GroupIOs:
        for node in GroupIO.childNodes:
            # Nous récupérons alors la liste des items avec le type de variable, le nom et l'adresse
            if (node.nodeType != node.TEXT_NODE):
                output.append(create_obj_line(node,driver_list,driver_offset))
    return output

def export_to_csv(dict_data):
    # Export au format TSV
    csv_columns = ['mnemonique','adresse','variable','remarque']
    csv_file = "export_"+time.strftime("%Y%m%d-%H%M%S")+".txt"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter='\t')
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def prepare_ladder_var(s):
    # Nous ne gardons que les caracteres ASCII valides
    o = "".join(i for i in s if (ord(i)<123) and ord(i)> 47)
    return o

def create_obj_line(n,c,offset_list):
    # Nous créons une ligne à partir des attributs des noeuds
    # Attention, il faut chercher par les key
    k = n.getAttribute('Key')
    PIO_item = search_PointIOKey(c, k)
    i = ('INT','EBOOL') ['Binary' in n.tagName]
    if PIO_item is None:
        a = ''
    else:
        offset = return_offset(n,PIO_item,offset_list)
        e = int(n.getAttribute('Address')) + offset
        a = ('%mw'+str(e),'%m'+str(e)) ['Input' in n.tagName]
    o = {'variable' : i,
    'adresse' : a,
    'mnemonique' : prepare_ladder_var(n.getAttribute('Name')),
    'remarque' : n.getAttribute('Name')}
    return o

def search_PointIOKey(values, PointIOKey):
    # Retourne un objet cherche par les PointIOKey
    for item in values:
        if PointIOKey == item['PointIOKey']:
            return item
    return None

def return_offset(n,i,offset_list):
    # Retourne l'offset
    o = 0
    if(('Output' in i['tagname']) and ('Binary' in n.tagName)):
        o = offset_list.get('BitOutputOffset',0)
    if(('Input' in i['tagname']) and ('Binary' in n.tagName)):
        o = offset_list.get('BitInputOffset',0)
    if(('Output' in i['tagname']) and (('Analogue' in n.tagName) or ('Int' in n.tagName))):
        o = offset_list.get('NumericOutputOffset',0)
    if(('Input' in i['tagname']) and (('Analogue' in n.tagName) or ('Int' in n.tagName))):
        o = offset_list.get('NumericInputOffset',0)
    print(o,i['tagname'],n.tagName,offset_list)
    return o

 
#------------------------------------------------------------------------------
if __name__ == '__main__':
    app = App()
    app.mainloop()

