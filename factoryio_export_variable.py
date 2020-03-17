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
from tkinter import messagebox
import xml.dom.minidom
import csv
import time
 
# Liste des drivers dans FactoryIO
driver_list = ["ModbusTCPClient"]
driver_name = ""

# Liste des drivers offset FactoryIO
driver_offset_list = ["BitInputOffset",
    "BitOutputOffset",
    "FloatInputOffset",
    "FloatOutputOffset",
    "IntInputOffset",
    "IntOutputOffset",
    "NumericInputOffset",
    "NumericOutputOffset"]

# Marque du logiciel plc
brand_name_list = ["Schneider"]
brand_name = ""


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.initWidgets()
 
    def initWidgets(self):

        self.title("Interface export variable")

        self.lbl_driver = tk.Label(self, text="1. Sélectionner le driver")
        self.lbl_driver.grid(row=0, column=0, sticky="w")
        
        opt_driver_name = tk.StringVar()
        opt_driver_name.set(driver_list[0])
        self.opt_driver = tk.OptionMenu(self, opt_driver_name, *driver_list)
        self.opt_driver.grid(row=0, column=20, sticky="w")

        self.lbl_brand = tk.Label(self, text="2. Sélectionner la marque de l'automate")
        self.lbl_brand.grid(row=1, column=0, sticky="w")

        opt_brand_name = tk.StringVar()
        opt_brand_name.set(brand_name_list[0])
        self.opt_brand = tk.OptionMenu(self, opt_brand_name, *brand_name_list)
        self.opt_brand.grid(row=1, column=20, sticky="w")

        self.lbl_file = tk.Label(self, text="3. Sélectionner le fichier")
        self.lbl_file.grid(row=2, column=0, sticky="w")

        self.bt_file = tk.Button(self, text="Fichier", command=self.openFile)
        self.bt_file.grid(row=2, column=20, sticky="w")

        self.lbl_export = tk.Label(self, text="4. Exporter le fichier")
        self.lbl_export.grid(row=3, column=0, sticky="w")

        self.bt_export = tk.Button(self, text="Export", command=self.export)
        self.bt_export.grid(row=3, column=20, sticky="w")
 
        self.lbl_txt = tk.Label(self, text="5. Résultat")
        self.lbl_txt.grid(row=4, column=0, sticky="w")

    def openFile(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("text files",".factoryio")])
        self.lbl_export["text"] = "3. Fichier sélectionné : "+self.filepath
        
    def export(self):
        self.path = filedialog.asksaveasfilename(filetypes=[("text files", ".txt"), ("all files", "*")],defaultextension=".txt")
        if not self.path:
            return False
        # Attention, les fichiers factoryio sont encodés avec un BOM
        with open(self.filepath, "r", encoding="utf-8-sig") as FILE:
            content = parse_xml_drivers(FILE)
        # Export des variables
        export_to_csv(content,self)
        return True

def parse_xml_drivers(e):
    # Utilisons la fonction parse pour analyser le DOM
    doc = xml.dom.minidom.parse(e)
    # Creons la sortie
    output = []
    # Variable tempo pour la liste des Modbus
    driver_item = []
    driver_name = driver_list[0]
    driver_offset = {}
    # Une fois récupéré le noeud nous allons chercher le ModbusTCPClient
    drivers = doc.getElementsByTagName(driver_name)
    for driver in drivers[0].childNodes:
        if ((driver.nodeType != driver.TEXT_NODE) and (driver.hasAttribute("PointIOKey"))):
            driver_item.append({"tagname":driver.tagName,"PointIOKey":driver.getAttribute("PointIOKey")})
        # Lecture des Offset
        if ((driver.nodeType != driver.TEXT_NODE) and (driver.tagName == "PointIOOffset")):
            for driver_offset_item in driver_offset_list:
                driver_offset[driver_offset_item]=(0,int(driver.getAttribute(driver_offset_item)))[driver.hasAttribute(driver_offset_item)]
    # allons chercher le noeud GroupIO dans la liste des objets
    GroupIOs = doc.getElementsByTagName("GroupIO")
    for GroupIO in GroupIOs:
        for node in GroupIO.childNodes:
            # Nous récupérons alors la liste des items avec le type de variable, le nom et l"adresse
            if (node.nodeType != node.TEXT_NODE):
                output.append(create_obj_line(node,driver_item,driver_offset))
    return output

def export_to_csv(dict_data,e):
    # Export au format TSV
    csv_columns = ["mnemonique","adresse","variable","remarque"]
    #csv_file = e.directory+"export_"+time.strftime("%Y%m%d-%H%M%S")+".txt"
    try:
        with open(e.path, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter="\t")
            for data in dict_data:
                writer.writerow(data)
            e.lbl_txt["text"] = "Traitement fini : "+e.path
            tk.messagebox.showinfo(title="Traitement fini", message="Fichier généré : "+e.path)
    except IOError:
        e.lbl_txt["text"] = "I/O error"

def prepare_ladder_var(s):
    # Nous ne gardons que les caracteres ASCII valides
    o = "".join(i for i in s if (ord(i)<123) and ord(i)> 47)
    return o

def create_obj_line(node_tag,c,offset_list):
    # Nous créons une ligne à partir des attributs des noeuds
    # Attention, il faut chercher par les key
    PIO_item = search_PointIOKey(c, node_tag.getAttribute("Key"))
    # Sélection du type
    var_type = ("INT","EBOOL") ["Binary" in node_tag.tagName]
    if PIO_item is None:
        adr = ""
    else:
        # Adresse
        offset = return_offset(node_tag,PIO_item,offset_list)
        adresse_int = int(node_tag.getAttribute("Address")) + offset
        adr = ("%mw"+str(adresse_int),"%m"+str(adresse_int)) ["Input" in node_tag.tagName]
    object_line = {"variable" : var_type,
    "adresse" : adr,
    "mnemonique" : prepare_ladder_var(node_tag.getAttribute("Name")),
    "remarque" : node_tag.getAttribute("Name")}
    return object_line

def search_PointIOKey(values, PointIOKey):
    # Retourne un objet cherche par les PointIOKey
    for item in values:
        if PointIOKey == item["PointIOKey"]:
            return item
    return None

def return_offset(n,i,offset_list):
    # Retourne l"offset
    o = 0
    if(("Output" in i["tagname"]) and ("Binary" in n.tagName)):
        o = offset_list.get("BitOutputOffset",0)
    if(("Input" in i["tagname"]) and ("Binary" in n.tagName)):
        o = offset_list.get("BitInputOffset",0)
    if(("Output" in i["tagname"]) and (("Analogue" in n.tagName) or ("Int" in n.tagName))):
        o = offset_list.get("NumericOutputOffset",0)
    if(("Input" in i["tagname"]) and (("Analogue" in n.tagName) or ("Int" in n.tagName))):
        o = offset_list.get("NumericInputOffset",0)
    return o

 
#------------------------------------------------------------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()

