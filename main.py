import os
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime
from twisted.internet import endpoints, reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.web import resource, server, static
import json 
import serial
import time
import random # Just for testing, you can replace this with your actual CRGB array

update_timestamp = 0
update_interval = 0.01

permissionsJSONData = {}
redwhite = "\033[25;33;49m"
homecursor = "\033[H"
clearscreen = "\033[J"
screenf = redwhite + homecursor + clearscreen
bold = "\033[1m"
unbold = "\033[22m"
ul = "\033[4m"
unul = "\033[24m"
boldul = bold + ul
unboldul = unbold + unul
end = "\033[0m"

currentParams = [0,100,0,50]

class Simple(resource.Resource):
    isLeaf = True
    def getChild(self, path, request):
        if path == b"":
            return self
        return resource.Resource.getChild(self, path, request)
    
    def render_GET(self, request):
        file_path =  b"./" + str(request.path.decode()).encode()
        print("\x1b[3m\x1b[90m" + str(request.path).replace("b","") + " served as " + str(file_path).replace("b","") + end)
        return static.File(file_path).getContent()
        

    
    def render_POST(self, request):
        request.setHeader(b"Access-Control-Allow-Origin", b"*")
        content = str(request.content.read().decode("utf-8"))
        resp = self.postHandler(content)
        # print(content + " --> " + str(resp))
        return str(str(resp)).encode()
        
    def postHandler(self, content):
        global currentParams
        if "Ping" in content:
            return "Cur" + str(currentParams)
        elif "Set[" in content:
            print(content.replace('Set','').replace('%','').replace(' ',''))
            currentParams = json.loads((content.replace('Set','').replace('%','').replace(' ','')))
            updateStrip()
            return "OK"
        elif "Custom;" in content:
            arduino.write(content.split(';')[1].encode())
            return "OK"
        else:
            return "OK"

def interpolate_color(color1, color2, ratio):
    interpolated_color = [int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(color1, color2)]
    return interpolated_color

def updateStrip():
    global update_timestamp
    
    current_time = time.time()
    
    if current_time - update_timestamp < update_interval:
        print("Rate limit exceeded. Skipping update.")
        return
    
    update_timestamp = current_time
    
    # Your existing updateStrip() logic here
    brightness = currentParams[0]
    wb = currentParams[1]
    
    # Calculate normalized white balance
    wb_normalized = wb / 100
    
    # Define color points for cool white and warm white
    cool_white_color = [0, 255]
    warm_white_color = [255, 0]
    
    # Interpolate color based on white balance
    interpolated_color = interpolate_color(cool_white_color, warm_white_color, wb_normalized)
    
    # Calculate brightness scaling factor
    brightness_normalized = brightness / 100
    
    # Apply brightness scaling to interpolated color
    final_color = [int(val * brightness_normalized) for val in interpolated_color]
    
    ww, cw = final_color
    
    print(f"ww: {ww}, cw: {cw}")
    
    write = f'C {ww} {cw}'
    arduino.write(write.encode())
    print(write)

def main():
    print("[_dormctrl] Starting...")
    f = Factory()
    site = server.Site(Simple())
    endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
    endpoint.listen(site)
    reactor.listenTCP(8000, f)
    print("[_dormctrl] UI is running at: http://localhost:8080/")
    reactor.run()

if __name__ == "__main__":
    
    print("--[_dormctrl]--")
    
    arduino = serial.Serial('COM4', 115200, timeout=1)
    print("[_dormctrl] Communication port opened successfully.")
    

    main()
