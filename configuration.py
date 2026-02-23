from netmiko import ConnectHandler
import json
import re

def maskConversion(decimal):
    temp = 128
    temp_2 = 0
    output = ""
    for i in range(32):
        if(i % 8 == 0 and i > 1):
            output += str(temp_2)
            output += "."
            temp_2 = 0
            temp = 128
        
        if(i < decimal):
            temp_2 += temp
        
        temp = int(temp/2)

    return output + str(temp_2)


class Router:
    router_id = 0
    def __init__(self, device):
        self.device = device
        self.router_id = Router.router_id
        Router.router_id += 1
        self.path = f"interfaces_router_{self.router_id}.json"
    
    def connectDevice(self):
        connect = ConnectHandler(**self.device)
        connect.enable()
        return connect
    
    def saveOutput(self, command):
        connection = self.connectDevice()
        output = connection.send_command(command)
        connection.disconnect()

        return output

    def saveInterfaces(self):
        data = {}
        output1 = self.saveOutput("show ip interface brief")
        output2 = self.saveOutput("show ip interface")


        output1 = output1.splitlines()

        for line in output1[1:]:
            parts = line.split()

            mask = re.search(rf"Internet address is {parts[1]}/(\d{{1,2}})", output2)
            mask1 = 0
            if mask:
                mask1 = mask.group(1)
            
            data[parts[0]] = {
                "ip address": parts[1],
                "mask": mask1,
                "method": parts[3],
                "status": parts[4]
            }

        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    def updateInterfaces(self):
        connection = self.connectDevice()
        connection.config_mode()

        with open(self.path, "r") as f:
            interfaceParam = json.load(f)
        
        for key in interfaceParam:
            interfaceCommand = f"interface {key}"
            ipCommand = f"ip address {interfaceParam[key]["ip address"]} {maskConversion(int(interfaceParam[key]["mask"]))}"
            if(interfaceParam[key]["status"] == "up"):
                statusCommand = "no shutdown"
            else:
                statusCommand = "shutdown"
            print(ipCommand)
            if(interfaceParam[key]["method"] != "DHCP"):
                connection.send_config_set([interfaceCommand, ipCommand, statusCommand])
        
        connection.disconnect
        



device = {
    "device_type": "cisco_xe",
    "host": "192.168.88.3",
    "username": "cisco",
    "password": "cisco123!"
}
router1 = Router(device)
#router1.saveInterfaces()
router1.updateInterfaces()



