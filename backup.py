from netmiko import ConnectHandler
from pathlib import Path
import difflib
from datetime import datetime
import json
showCommand = "sh run"
outputFile = "output.txt"
compareFile = "compare.txt"
device = {}
with open("devices.json", 'r') as f:
    temp =  json.load(f)
    device = temp["device1"]


def connectDevice(deviceParameters):
    connection = ConnectHandler(**deviceParameters) #Create tthe connection,
#** unpacks the dictionary into keyword arguments:
# connection = ConnectHandler(device_type="cisco_xe", host="192.168.88.3", username="cisco", password="cisco123!")
    
    connection.enable() #priviliged mode 
    return connection

def saveOutput(PATH, command, device):
    connection = connectDevice(device)
    with open(PATH, 'w') as f:
        f.write(connection.send_command(command))

    connection.disconnect()


def compareOutput(PATH, command, device):
    tempPath = "tempPath.txt"
    connection = connectDevice(device)
    with open(tempPath, 'w') as f:
        f.write(connection.send_command(command))
    
    with open(tempPath, 'r') as f1, open(PATH, 'r') as f2:
        
       

         line1 = f1.readlines()[6:]
         line2 = f2.readlines()[6:]

    diff = difflib.unified_diff(
        line1,
        line2,
        fromfile=PATH,
        tofile=tempPath,
        lineterm=""
    )
    connection.disconnect()
    Path(tempPath).unlink()
    return "\n".join(diff)

with open(compareFile, "a") as f:
    x = compareOutput(outputFile, showCommand, device)
    if(x != ""):
        f.write(f"__________________________________________\n{datetime.now()}\n___________________________________________\n")
        f.write(x)
        saveOutput(outputFile, showCommand, device)
    

