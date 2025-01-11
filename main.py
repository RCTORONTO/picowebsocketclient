import network
#import uWebsocket
import usocket as socket
import ubinascii as binascii
import urandom as random
from wsprotocol import Websocket
import _thread

import ure as re
import ustruct as struct
import urandom as random
from ucollections import namedtuple

#import ussl
import json
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import rp2
import sys
from machine import Pin, Timer

led = machine.Pin("LED", machine.Pin.OUT)
timer = Timer()
    
#ssid = 'GEE'
#password = 'rytechnet11'

devID = '99'
devName = 'PICOW'
devType = 'picobase'


ws_host="192.168.0.x"
ws_port=8090
ws_path="/chatserver"

wsIsConnected = False
ThreadLock = _thread.allocate_lock()

debugit = False

class WebsocketClient(Websocket):
    is_client = True

def ledblink(timer):
    led.toggle()
def ledoff():
    led.off()
def ledon():
    led.on()
def senddevicestatus():
    global ws
    data = {
        "mType":"device-status",
        "devID":devID,
        "devName":devName,
        "devType":devType,
        "status":0
        }
    for i in range(25): 
        data["status"] = i
        ws.send(json.dumps(data))
        sleep(1)


def wsconnect():
    global wsIsConnected
    wsIsConnected = False
    #if debugit:print("opening websocket 192.168.0.22:8090")
    sock = socket.socket()
    addr = socket.getaddrinfo("192.168.0.x",80)
    
    try:
        #if debugit:print("connecting to socket...")
        sock.connect(addr[0][4])
        
    except KeyboardInterrupt:
        return
    except Exception as err:
        sock.close()
        #if debugit:print("error ",err)
        return
    except socket.error as error:
        #if debugit:print("this error {}",error)
        return
        
    #if debugit:print("awaiting receive")
    def send_header(header, *args):
        #if debugit:print("SENT", str(header), *args)
        sock.write(header % args + '\r\n')
            #sock.write(header % args)

        # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                        for _ in range(16)))[:-1]

    send_header(b'GET /chatserver HTTP/1.1')
    send_header(b'Host: 192.168.0.x:80')
    send_header(b'Connection: Upgrade')
    send_header(b'User-Agent: PICO-W (MICROPYTHON)')
    send_header(b'Upgrade: WebSocket')
    send_header(b'Sec-WebSocket-Key: %s', key)
    send_header(b'Sec-WebSocket-Version: 13')
    #send_header(b'Origin: http://192.168.0.x:8090')
    send_header(b'')

    header = sock.readline()[:-2]
    try:
        assert header.startswith(b'HTTP/1.1 101 '), header
    except AssertionError:
        #if debugit:print("FAILED to receive handshake")
        sock.close()
        wsIsConnected = False
        return
    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header:
        #if debugit:print(str(header))
        header = sock.readline()[:-2]
        
    wsIsConnected = True
    return WebsocketClient(sock)
    
def ws_handle_response(response):
    mType = response['mType']
    #print(mType)
    if mType == "AUTHREQUEST":
        #if debugit:print("mType was AUTHREQUEST")
        ws_send_auth()
    elif mType == "device-control-cmd":
        #if debugit:print("device control message")
        if response['thestate'] == "5":
            senddevicestatus()
        else:
            _thread.start_new_thread(ThreadTask, (list(response['thestate'])))        
    
def ws_send_auth():
    global ws
    global devID
    global devName
    global devType
    #if debugit:print("sending AUTH")
    data = {
        "mType":"AUTH",
        "devID":devID,
        "devName":devName,
        "devType":devType
    }
    ws.send(json.dumps(data))
    
def ThreadTask(thestate):
    #if debugit:print("starting task with state", thestate)
    if thestate == "0":
        timer.deinit()
        ledoff()
    elif thestate == "1":
        timer.deinit()
        ledon()
    elif thestate == "2":
        timer.init(freq=2.5, mode=Timer.PERIODIC, callback=ledblink)
        ledblink(timer)

        
global ws
#ledon()
while True:
    #if wlan.isconnected() == True and wsIsConnected == True:
    if wsIsConnected == True:
        try:
            response = json.loads(ws.recv())
            #if debugit:print(response)
            ws_handle_response(response)
        except KeyboardInterrupt:
            #if debugit:print("KeyboardInterrupt1")
            break
        except:
            #if debugit:print("websocket recv error")
            ws.close()
            wsIsConnected = False   
    else:
        if wsIsConnected == False:
            sleep(3)
            ws=wsconnect()
