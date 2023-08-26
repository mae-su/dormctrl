import json
import os
import subprocess
import sys
import threading
from collections import OrderedDict
from datetime import datetime
#from selenium import webdriver
from src import cardswipe, jsonHelper
from twisted.internet import endpoints, reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.web import resource, server, static
logJSONData = {}
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
latestSignIns = []

dir = "./data/"  # This is where files will be stored on the pi.
firstboot = False
kioskIP = "127.0.0.1"

def entry(b=None):
  if b is None:
    j = jsonHelper.getJson(dir + "secrets.json")["entryDenied"]
    if j == "False":
      return False
    if j == "True":
      return True
  else:
    j = jsonHelper.getJson(dir + "secrets.json")
    j["entryDenied"] = str(b)
    jsonHelper.setJson(dir + "secrets.json",j)

def isinstalled(dir):
    try:
        if os.path.exists(dir):
            return True
    except:
        print(dir + " not found.")
        return False

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
        
        
        if content.startswith("%"):
            resp = self.adminPostHandler(content.strip("%"))
            if True:
                print("[Admin] " + content.strip("%") + " --> " + str(resp))
            return str("%" + str(resp)).encode()
        elif content.startswith("+"):
            resp = self.UIPostHandler(content.strip("+"))
            if True:
                print("[UI] " + content.strip("+") + " --> " + resp)
            return str("+" + str(resp)).encode()
        
    def UIPostHandler(self, content):
        if "Ping" in content:
          if entry():
            return str("entryDenied")
          else:
            return str("entryAllowed")
             
        ##process web POSTS here
        if "SignInReq;" in content:
          try:
            result = checkID(content.split(";")[1])
          except Exception as e:
            print(e)
          if result[0] == "Incorrect":
            latestSignIns.append("Incorrect sign in attempted.")
            return "Incorrect"
          else:
            latestSignIns.append(result[0] + " is signing in...")
            return str("Authorize;" + result[0] + ";" + ";".join(result[1]))
        if "Unlock;" in content:
          ID = content.split(";")[1]
          latestSignIns.append(checkID(ID)[0] + " has signed in.")
          machines = content.split(";")[2].split(",")
          log(ID,machines)
          if debug:
              print("[DEBUG] Card swipe called.")
          else:
              cardswipe.main(IP=kioskIP)
              return "Log Success;"
        if content == "Ipaddr":
            return str("Ipaddr;" + subprocess.getoutput("hostname -I"))  # send IP address
        else:
            return "OK"

def main():
    try:
        if not os.path.exists(dir):
            install(print)
    except:
        install(print)
    print("[MMRKV2] Kiosk is starting...")
    f = Factory()
    site = server.Site(Simple())
    endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
    endpoint.listen(site)
    reactor.listenTCP(8000, f)
    print("[MMRKV2] Kiosk UI is running at: http://localhost:8080/ui/")
    print("[MMRKV2] Admin UI is running at: http://localhost:8080/admin/")
    try:
        command = "chromium-browser http://localhost:8080/ui/ --kiosk"
        subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[MMRKV2] Kiosk UI opened successfully.")
    except:
        print("[MMRKV2] An error occurred while opening the UI on the kiosk. Please open the UI manually.")
    try:
        subprocess.Popen(['python', '/home/pi/MMRK-V2/backend/KioskHardwareAgent.py'])
    except:
      print("[MMRKV2] An error occurred while launching the hardware agent on the kiosk. Please launch it manually.")
    reactor.run()


def install(out):
    def selfout(s):
        out("[MMRKV2 Installer] " + s)
    selfout("Installing directory at: " + dir)
    try:
        os.mkdir(dir)
    except Exception as e:
        selfout("Failed to create storage directory. \n" + str(e))

    try:
        selfout("Creating JSONs: ")
        jsonHelper.createJSON(dir + "log.json")
        jsonHelper.createJSON(dir + "permissions.json")
        jsonHelper.createJSON(dir + "secrets.json")
        selfout("Done.")
        selfout("Writing format to secrets.json with defaults:")
        j = jsonHelper.getJson(dir + "secrets.json")
        j["entryDenied"] = str(False)
        selfout("'entryDenied' : 'False'  |  Kiosk is currently accepting entry.")
        j["authcode"] = "00000"
        selfout("'authcode':'00000'  |  Admin PIN is currently 00000.")
        j["downloadPath"] = ""
        selfout("'downloadPath':''  |  Download path is currently unset.")
        jsonHelper.setJson(dir + "secrets.json",j)
        

    except Exception as e:
        selfout("Failed to create JSONs. \n" + str(e))
    selfout("Success! Please set a five digit admin PIN and downloadPath in secrets.json.")

def log(ID, machines):
    logdata = jsonHelper.getJson(dir + "log.json")
    logdata [datetime.now().timestamp()] = {
        "ID":ID,
        "machines":machines
    }
    jsonHelper.setJson(dir + "log.json",logdata)

def getName(data,ID):
    if ID in data:
      
      return data[ID]['firstname'] + " " + data[ID]['lastname']
def checkID(ID):
    permissions = jsonHelper.getJson(dir + "permissions.json")
    if ID in permissions:
      
      return [permissions[ID]['firstname'],permissions[ID]['machines']]
    else:
      return ["Incorrect"]

if __name__ == "__main__":
    # Change this before debugging, unless you run the program with the --debug flag.
    debug = False

    if debug or "--debug" in sys.argv:
        import os
        dir = "./data/"
        kioskIP = "192.168.86.80"
    main()
