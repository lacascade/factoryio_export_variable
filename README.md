# factoryio_export_variable
 Export Variable Modbus to tsv format writen in python
 The export can be used to initialize the variable table in EcoStruxure from Schneider
 The factory io save file format is xml. This file describe the scene but also the objects and the driver.
 The script read through the xml node to extract a list of variables with their type and adresses in order to import them directly to EcoStruxure.

 How to use it :
* run the script
![Start](/images/interface_accueil.png)
* step 1 : select a driver in the list, by default "ModbusTCPClient" is selected
* step 2 : select a brand for the plc, by default "Schneider" is selected and is the only one currently
* step 3 : select the scene saved from factoryIO
![Choose File](/images/interface_selection_fichier.png)
* step 4 : choose the name and place where to store the export
![Export File](/images/interface_choix_export.png)
![End](/images/interface_fin.png)
* import the .txt file as the table variable in EcoStruxure

# Update 2020/03/26 :
Possibility of exporting to PCVUE and JSON format.
For PCVUE :
* generate the xml file (PCVUE entry)
* open PCVUE, select in the menu bar "Configuration / Smart Generators"
![Menu Bar](/images/pcvue_smart_generator.png)
* in the dialog box, select "Nouvel import"
![Nouvel import](/images/pcvue_select_xml_import.png)
* choose a name for your import and select the xml file previously generated
![Smart generator](/images/pcvue_smart_generator_xml.png)
* variables have been added to your project
![Final import](/images/pcvue_import_final.png)

For PCVUE the variable type is measure by default, for "BOOL" or "EBOOL" type it's bit.


What is not currently not working efficiently is the adress of variables.
Haven't tried with all the options for the driver list.