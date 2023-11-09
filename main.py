
from twisted.internet import endpoints, reactor
from twisted.internet.protocol import Factory
from twisted.web import resource, server, static
import json 
import serial
import time
from rich import print
# Global variables
update_timestamp = 0
update_interval = 0.01
brightness_slider = None
white_balance_slider = None
arduino = None
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
currentParams = [20,100,0]

class Simple(resource.Resource):
    isLeaf = True
    def getChild(self, path, request):
        if path == b"":
            return self
        return resource.Resource.getChild(self, path, request)
    
    def render_GET(self, request):
        file_path =  b"./" + str(request.path.decode()).encode()
        
        print(str(request.path).replace("b","") + " served as " + str(file_path).replace("b",""))
        return static.File(file_path).getContent()

    def render_POST(self, request):
        request.setHeader(b"Access-Control-Allow-Origin", b"*")
        content = str(request.content.read().decode("utf-8"))
        resp = self.postHandler(content)
        return str(str(resp)).encode()
    
    def postHandler(self, content):
        global currentParams
        if "Ping" in content:
            return "Cur" + str(currentParams)
        elif "Set[" in content:
            # print(content.replace('Set','').replace('%','').replace(' ',''))
            currentParams = json.loads((content.replace('Set','').replace('%','').replace(' ','')))
            updateStrip(input_brightness=currentParams[0],input_wb = currentParams[1])
            return "OK"
        elif "Custom;" in content:
            arduino.write(content.split(';')[1].encode())
        elif "pwrOn" in content:
            print(f'Powering on to parameters {currentParams}')
            currentParams[2] = 1  
            fadeStrip(0,currentParams[0],50,currentParams[1],0.5)
            return "OK"
        elif "pwrOff" in content:
            currentParams[2] = 0
            if currentParams[0] < 3: #some tolerance for minor brightness update errors
                currentParams[0] = 20
                currentParams[1] = 100
                updateStrip(input_brightness=0,input_wb=0,rate_limit=0)
            
            else:
                fadeStrip(currentParams[0],0,currentParams[1],50,0.5)
            return "OK"
        else:
            return "OK"

def updateStrip(rate_limit = update_interval, input_brightness=currentParams[0],input_wb = currentParams[1]):
    global update_timestamp
    current_time = time.time()
    if current_time - update_timestamp < rate_limit:
        pass
        # print("Rate limit exceeded. Skipping update.")
    else:
        update_timestamp = current_time
        # Your existing updateStrip() logic here
        brightness = input_brightness * 2.551
        wb = input_wb
        if wb < 50:
            cw = int(brightness)
        else:
            cw = int(((-5.1 * wb) + 510) * (brightness / 255))
        if wb < 50:
            ww = int((5.1 * brightness / 255) * wb)
        else:
            ww = int(brightness)
        print(f"Channels interpolated | Warm: {ww}, Cool: {cw}")
        write = f'C {ww} {cw}'
        arduino.write(write.encode())

def fadeStrip(pre1, post1, pre2, post2, period):
    delta1 = post1 - pre1
    delta2 = post2 - pre2
    steps = 255  # Define the number of steps for the fade
    delay_interval = period / steps
    for i in range(steps):
        time.sleep(delay_interval)  # Sleep for the fraction of the period
        step_ratio = i / (steps - 1)  # Use steps - 1 to get the correct ratio
        current_brightness = pre1 + (delta1 * step_ratio)
        current_wb = pre2 + (delta2 * step_ratio)
        updateStrip(input_brightness=current_brightness, input_wb=current_wb,rate_limit=0.005)
    time.sleep(delay_interval)
    updateStrip(input_brightness=post1, input_wb=post2,rate_limit=0)

def main():
    print("[_dormctrl] Starting...")
    
    global arduino
    
    arduino = serial.Serial('COM3', 115200, timeout=1)
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