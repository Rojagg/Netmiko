from netmiko import ConnectHandler
import json
import re
showCommand = "sh ip inter br"
outputFile = "interfaces.txt"
compareFile = "compare.txt"
device = {
    "device_type": "cisco_xe",
    "host": "192.168.88.3",
    "username": "cisco",
    "password": "cisco123!"
}
def connectDevice(device):
    connect = ConnectHandler(**device)
    connect.enable()
    return connect

def saveOutput(command, device):
    connection = connectDevice(device)
    output = connection.send_command(command)

    connection.disconnect()
    return output

def saveInterfaces(FILE):
    data = {}
    output = saveOutput("sh ip inter br", device)
    output2 = saveOutput("sh ip inter", device)

    output = output.splitlines()
    for line in output[1:]:
        parts = line.split()
        mask = re.search(rf"Internet address is {parts[1]}/(\d{{1,2}})", output2)
        
        if mask:
            data[parts[0]] ={
                
                "ip address": parts[1],
                "mask": convertMask(int(mask.group(1))),
                "method": parts[3],
                "status": parts[4],
                "protocol": parts[5]
            }

    with open(FILE, 'w') as f:
        json.dump(data, f, indent=4)


def updateInterfaces(FILE):
    connect = connectDevice(device)
    connect.config_mode()
    with open(FILE, "r") as f:
        config = json.load(f)
        for key in config:
            ipAddress = config[key]["ip address"]
            if config[key]["method"] == "manual":

                commands = [f"interface {key}", f"ip address {config[key]["ip address"]} 255.255.255.0"]
                connect.send_config_set(commands)

def convertMask(decimalMask):
    string =""
    temp = 128
    temp2 = 0
    for i in range(32):
        if(i > 0 and i%8 == 0):
            string += str(temp2)
            string += "."
            temp = 128
            temp2 = 0
        if(decimalMask > i):
            temp2 += temp
        
        temp = int(temp/2)

    return string+ str(temp2)



#updateInterfaces("interfaces.json")
saveInterfaces("interfaces.json")


#updateInterfaces("interfaces.json")
####Parse interface information to json


####Change json can be commited into the router
####IP address, VLAN?