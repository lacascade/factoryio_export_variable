# factoryio_export_variable
 Export Variable Modbus to tsv format writen in python
 The export can be used to initialize the variable table in EcoStruxure from Schneider
 The factory io save file format is xml. This file describe the scene but also the objects and the driver.
 The script read through the xml node to extract a list of variables with their type and adresses in order to import them directly to EcoStruxure.

 How to use it :
* run the script
* step 1 : select a driver in the list, by default "ModbusTCPClient" is selected
* step 2 : select a brand for the plc, by default "Schneider" is selected and is the only one currently
* step 3 : select the scene saved from factoryIO
* step 4 : choose the name and place where to store the export
* import the .txt file as the table variable in EcoStruxure

What is not currently not working efficiently is the adress of variables.
Haven't tried with all the options for the driver list.