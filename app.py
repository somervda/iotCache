from microdot_asyncio import Microdot,Request
from settings import Settings
import network
import ntptime
import time
from  machine import Pin
import json
import os
# import ssl

# Used to append a 3 digit sequence number to a timestamp
# to make values unique within a second
_sequence = 0



def getUniqueTimestamp(timestamp):
    global _sequence
    # Timestamp transaction in seconds since the epoch
    _sequence += 1
    if _sequence > 999:
        _sequence =0
    return "{}".format(timestamp) + "{:03d}".format(_sequence)

def writeIOTData(iotData):
    # Basic validation
    if not isinstance(iotData, dict):
        return "iotData is not a dict"
    timestamp = time.time()
    if  "appID" not in iotData:
        return "iotData is missing appId"
    if  "deviceID" not in iotData:
        return "iotData is missing deviceId"
    if  "user" not in iotData:
        return "iotData is missing user"
    user = iotData.get("user","")
    if not user in settings.getUSERS():
        return "Invalid User"
    del iotData['user']
    iotData["iotTimestamp"] = timestamp
    # Try writing out the iotData
    try:
        fileName = getUniqueTimestamp(timestamp) + ".json"
        with open("/data/" + fileName, "w") as datafile:
            json.dump(iotData, datafile)
        return "Ok"
    except  Exception as e: 
        return str(e)

def dir_exists(dirName):
    try:
        return (os.stat(dirName)[0] & 0x4000) != 0
    except OSError:
        return False

# Get the system settings and initialize environment

# Load Setting
settings = Settings()

# Set up LED
led = Pin("LED", Pin.OUT)
led.on()

# Create a data directory if one isn't set up

if not dir_exists("data"):
    os.mkdir("data")

# Connect to network and get the NTP time

wlan = network.WLAN(network.STA_IF)
print("Connecting to " + settings.getSSID() + ":")
wlan.active(True)
wlan.ifconfig(('192.168.1.30', '255.255.255.0',
               '192.168.1.1', '192.168.1.1'))
wlan.connect(settings.getSSID(), settings.getPASSWORD())
while not wlan.isconnected() and wlan.status() >= 0:
    # Slow LED flash while connecting
    print(".", end="")
    led.off()
    time.sleep(0.5)
    led.on()
    time.sleep(.5)

time.sleep(2)
print("Connected! IP Address = " + wlan.ifconfig()[0])
# Short delay before getting ntp time
# There is a known timing bug with this so try again
# if it fails.
try:
    ntptime.host = settings.getNTP()
    print(ntptime.host)
    ntptime.timeout = 2
    ntptime.settime()
except:
    print("ntptime error! Rebooting...")
    time.sleep(1)
    machine.reset()



print("UMT time：%s" % str(time.localtime()))
for x in range(0, 10):
    # Quick flash to indicate we are connected
    time.sleep(.05)
    led.on()
    time.sleep(.05)

    led.off()


# ************************************************************
#                   MicroDot 
# ************************************************************
app = Microdot()

# define iotLogger services
@app.route('/hello')
async def getHello(request):
    return 'Ok'

@app.post('/write')
async def writeIOTPost(request):
    iotData = request.json
    result = writeIOTData(iotData)
    if result=="Ok":
        return result, 200
    else:
        return result,500


@app.get('/write')
async def writeIOTGet(request):
    iotData=json.loads(request.args["iotData"])
    print(iotData,request)
    result = writeIOTData(iotData)
    print(result)
    if result=="Ok":
        return result, 200
    else:
        return result,500

@app.get('/read')
async def getIOT(request):
    # Get any available iotData json file in the 
    # /data folder , return the content to the requester and delete
    # the file
    try:
        user = request.args["user"]
    except:
        return "Invalid User"
    if not user in settings.getUSERS():
        return "Invalid User"
    for fileName in os.listdir("data"):
        with open("data/" + fileName, "r") as iotDataFile:
            iotData = json.load(iotDataFile)
        # print (iotData)
        os.remove("data/" + fileName)
        return iotData
    return "None"


print("*** starting ***")
# If using ssl 
# see https://microdot.readthedocs.io/en/latest/intro.html#web-server-configuration
# and https://www.suse.com/support/kb/doc/?id=000018152
# sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# sslctx.load_cert_chain('cert.pem', 'key.pem')
# app.run(port=4443, debug=True, ssl=sslctx)
app.run(debug=True, port=settings.getPORT())
