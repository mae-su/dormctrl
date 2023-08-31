from collections import OrderedDict
from datetime import datetime
from twisted.internet import endpoints, reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.web import resource, server, static
import json 
import serial
import time

# Global variables
update_timestamp = 0
update_interval = 0.01
currentParams = [0, 100, 0, 50]
brightness_slider = None
white_balance_slider = None
arduino = None

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
currentParams = [0,100]

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
    else:
        update_timestamp = current_time
        # Your existing updateStrip() logic here
        brightness = currentParams[0] * 2.551
        wb = currentParams[1]
        if wb < 50:
            cw = int(brightness)
        else:
            cw = int(((-5.1 * wb) + 510) * (brightness / 255))
        if wb < 50:
            ww = int((5.1 * brightness / 255) * wb)
        else:
            ww = int(brightness)
        print(f"ww: {ww}, cw: {cw}")
        write = f'C {ww} {cw}'
        arduino.write(write.encode())
        # print(write)

def main():
    print("[_dormctrl] Starting...")
    
    global arduino
    
    arduino = serial.Serial('COM4', 115200, timeout=1)
    print("[_dormctrl] Communication port opened successfully.")
    
    f = Factory()
    site = server.Site(Simple())
    endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
    endpoint.listen(site)
    reactor.listenTCP(8000, f)
    
    print("[_dormctrl] UI is running at: http://localhost:8080/")
    
    reactor.run()

if __name__ == "__main__":
    print("--[_dormctrl]--")
    main()