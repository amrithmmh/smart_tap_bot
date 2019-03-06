#!/usr/bin/env python3
from threading import Thread,Event
import  threading
import serial
import time
import logging
import sys
from flask import Flask,request,Response
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
import csv
import shutil
import formatter
import os

#flask restful api
app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

USER_DATA = {
    "admin": "enigma"
}



busy=False
connected = False
port = '/dev/ttyUSB0'
baud = 250000
#for logging purpose
##logging file
logger = logging.getLogger("SMART_TAP_BOT")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)
fh = logging.FileHandler('logs.log')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


logger_console = logging.getLogger("console_debug")
logger_console.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger_console.addHandler(ch)


#with open('servo_conf.csv', mode='w') as csv_file:
#    fieldnames = ['initial', 'final','feed_rate']
#    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#    writer.writeheader()
#    writer.writerow({'initial':0, 'final': 180,'feed_rate':10000})
try:
    values=csv.DictReader(open("servo_conf.csv"))
    for row in values:
        logger_console.info(" csv file contents {}".format(row))
except:
    logger.error("something went wrong reading csv file {}",sys.exc_info()[0])
    logger_console.error("something went wrong reading csv file {}",sys.exc_info()[0])

disable_flag=False
initial=row['initial']#servo initial angle(up)
final=row['final'] #servo final angle(down)
feed_speed=row['feed_rate']
event = threading.Event()#event to communicate between command send and read serial
logger_console.info("initial {} final{} speed{}".format(initial,final,feed_speed))
#connect to controller
try:
    serial_port = serial.Serial(port, baud,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=1,xonxoff=0,rtscts=0)
except:
    logger.debug("serial port connection exception:",sys.exc_info()[0],"occured.")
    exit()
else:
    logger_console.info("connected to Marlin ;-)")
    serial_port.setDTR(False)
    time.sleep(1)
    serial_port.flushInput()
    serial_port.setDTR(True)

#class
class smart_tap_init(Thread):
    """this class is to initialise smart tap bot"""
    def __init__(self):
        Thread.__init__(self)
        logging.info('{} thread started'.format(self.__class__.__name__))

    def handle_data(self,data):
        """just  wait for M301 to occur"""
        print(data)
        global busy
        if(data.find('M301')!=0):
            logger_console.info("smart tap bot controller online")
            serial_port.flushInput()
            busy=True

    def read_from_port(self,ser):
        global connected
        while not connected:
            connected = True
            global busy
            logger_console.info('busy= {} '.format(busy))
            while (busy!=True):
                if (ser.in_waiting>0):
                    try:
                        reading=(ser.readline(ser.in_waiting)).decode('utf-8')
                    except:
                         print("printer initialize exception:", sys.exc_info()[0])
                    else:
                        self.handle_data(reading)

    def run(self):
        logger_console.debug('{} thread running'.format(self.__class__.__name__))
        global serial_port
        self.read_from_port(serial_port)

class print_serial(Thread):
    """classs just to print serial"""
    def __init__(self):
        Thread.__init__(self)
        logger_console.info('{} thread started'.format(self.__class__.__name__))
    def read_ok(self):
        reading='not_ok'
        while(reading!='ok'):
            if (serial_port.in_waiting>0):
                try:
                    reading=(serial_port.readline(serial_port.in_waiting)).decode('utf-8')
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                else:
                    print(reading)
                    if(reading.find('ok')!=0):
                        break
        logger_console.info("read_ok completed")
    def read_serial(self):
        logger_console.info("reading serial")
        while(True):
            if (serial_port.in_waiting>0):
                try:
                    reading=(serial_port.readline(serial_port.in_waiting)).decode('utf-8')
                except:
                    logger.error("Unexpected error:", sys.exc_info()[0])
                else:
                    print(reading)
                    time.sleep(0.5)
    def run(self):
        logger_console.info('{} thread running'.format(self.__class__.__name__))


class send_gcode(Thread):
    """class to send gcode to controller """
    def __init__(self):
        Thread.__init__(self)
        logger_console.info('{} thread started'.format(self.__class__.__name__))

    def handle_data(self,data):
        logger_console.info("serial: {}".format(data))

    def pass_command(self,CmdStr):
        global busy
        while busy==False:
            pass
        try:
            serial_port.write((("{}\r").format(CmdStr)).encode())
        except:
            logger_console.error("Send command exception:", sys.exc_info())


    def run(self):
        logger_console.info('{} thread running'.format(self.__class__.__name__))


#flask rest api classes for routes

class swipe(Resource):
    """to swipe between startpoint and endpoint"""
    def get(self):
        global initial,final,feed_speed
        startPoint= request.args.get('startPoint', None)
        endPoint= request.args.get('endPoint', None)
        logger.debug("startpoint= {}  endpoint= {}".format(startPoint,endPoint))
        #thread3.read_serial()
        serial_port.flush()
        thread2.pass_command("G0 {} F{}".format(startPoint,feed_speed))
        thread2.pass_command("M400")
        thread2.pass_command("M280 P0 S {}".format(final))
        thread2.pass_command("G0 {} F{}".format(endPoint,feed_speed))
        thread2.pass_command("M400")
        serialread=str((serial_port.readline()).decode())
        while serialread.find('ok')!=0:
            print(serialread)
            serialread=(str(serial_port.readline().decode()))
        #time.sleep(1)
        thread2.pass_command("M280 P0 S{}".format(initial))
        return Response("swipe from {} to {} done".format(startPoint,endPoint), mimetype='text/plain')

class tap(Resource):
    """tap at a point """
    def get(self):
        global initial,final,feed_speed
        Point= request.args.get('Point', None)
        logger.debug("Point from Tap Rest API ={}".format(Point))
        thread2.pass_command("M400")
        thread2.pass_command("G0 {} F{}".format(Point,feed_speed))
        thread2.pass_command("M400")
        thread2.pass_command("M280 P0 S{}".format(final))
        thread2.pass_command("M280 P0 S{}".format(initial))
        return Response("tap to point {} recieved".format(Point), mimetype='text/plain')

class onePointmove(Resource):
    """moves to a specified point"""
    def get(self):
        global feed_speed
        Point= request.args.get('Point', None)
        logger.debug("Point from Tap Rest API ={}".format(Point))
        thread2.pass_command("M400")
        thread2.pass_command("G0 {} F{}".format(Point,feed_speed))
        thread2.pass_command("M400")
        logger.debug("G0 {} F{}".format(Point,feed_speed))
        serialread=str((serial_port.readline()).decode())
        return Response("move to single point {} recieved".format(Point), mimetype='text/plain')

class twoPointmove(Resource):
    """moves between two points"""
    def get(self):
        global feed_speed
        Point1= request.args.get('Point1', None)
        Point2= request.args.get('Point2', None)
        logger.debug("Points from  Rest API ={} {}".format(Point1,Point2))
        thread2.pass_command("M400")
        thread2.pass_command("G0 {} F{}".format(Point1,feed_speed))
        thread2.pass_command("M400")
        thread2.pass_command("G0 {} F{}".format(Point2,feed_speed))
        thread2.pass_command("M400")
        return Response("move between two point {} {} recieved".format(Point1,Point2), mimetype='text/plain')

class home(Resource):
    """do  homing if required"""
    def get(self):
        thread2.pass_command("M400")
        thread2.pass_command("G28 X Y")
        logger.debug("homing gcode rest API")
        return Response("homing done",mimetype='text/plain')


class setAngle(Resource):
    """adjust angle initial and final and save it to csv file:: last saved value is used at startup"""
    def get(self):
        global initial,final,speed
        initial= request.args.get('initial', None)
        final= request.args.get('final', None)
        logger.debug("set Angle initial={} final={} through rest api".format(initial,final))
        fieldnames = ['initial', 'final','feed_rate']
        with open('servo_conf.csv', 'r') as csvfile, open('servo_conf_temp.csv', 'w') as output:
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'initial':initial, 'final': final,'feed_rate':speed})
            shutil.move('servo_conf_temp.csv','servo_conf.csv')
        return Response("setting angle initial ={} final ={} done".format(initial,final),mimetype='text/plain')


class testTap(Resource):
    """tap at current location for just tapping no movement"""
    def get(self):
        global initial,final
        logger.debug("test tap initial={} final={}".format(initial,final))
        thread2.pass_command("M400")
        thread2.pass_command("M280 P0 S{}".format(final))
        thread2.pass_command("M280 P0 S{}".format(initial))
        serialread=str((serial_port.readline()).decode())
        while serialread.find('ok')!=0:
            print(serialread)
            serialread=(str(serial_port.readline().decode()))
        return Response("test tap done initial={} final={}".format(initial,final),mimetype='text/plain')

class speed(Resource):
    """vary the feedrate if required , also saved to csv file"""
    def get(self):
        global initial,final,feed_speed
        speed_value= request.args.get('speed', None)
        logger.debug("speed set {}rest API".format(speed_value))
        fieldnames = ['initial', 'final','feed_rate']
        with open('servo_conf.csv', 'r') as csvfile, open('servo_conf_temp.csv', 'w') as output:
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'initial':initial, 'final': final,'feed_rate':speed_value})
            shutil.move('servo_conf_temp.csv','servo_conf.csv')
        feed_speed=speed_value
        return Response("speed set {}".fromat(speed_value),mimetype='text/plain')

class homepage(Resource):
    def get(self):
        """Present some documentation"""
        content = get_file('smart_tap_home.html')
        return Response(content, mimetype="text/html")



class getcurrentposition(Resource):
    """gets current position"""
    def get(self):
        global initial,final
        logger.debug("get cureent position:")
        thread2.pass_command("M400")
        thread2.pass_command("M114")
        serialread=str((serial_port.readline()).decode())
        while serialread.find('X:')!=0:
            logger_console.info(serialread)
            serialread=(str(serial_port.readline().decode()))
            current_pos=serialread.split(" ")
        logger_console.info(current_pos)
        return Response("current position {} {}".format(current_pos[0],current_pos[1]),mimetype='text/plain')

class setcurrentposition(Resource):
    """set current position to Zero"""
    def get(self):
        global initial,final
        logger.debug("set cureent position:")
        thread2.pass_command("M400")
        thread2.pass_command("G92 X0 Y0")
        return Response("set position 0,0 done ",mimetype='text/plain')

class disableMotor(Resource):
    """set current position to Zero"""
    def get(self):
        global disable_flag
        logger.debug("disable X Y mottors")
        thread2.pass_command("M400")
        if(disable_flag==False):
            thread2.pass_command("M18 X Y")
            disable_flag=True
        else:
            thread2.pass_command("M17")
            disable_flag=False

        return Response("motor disable = {}".format(disable_flag),mimetype='text/plain')

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)

class PrivateResource(Resource):
    """test class to test username and password"""
    @auth.login_required
    def get(self):
        return {"meaning_of_life": 42}

@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password

api.add_resource(swipe, '/swipe')
api.add_resource(tap, '/tap')
api.add_resource(onePointmove,'/opMove')
api.add_resource(twoPointmove,'/tpMove')
api.add_resource(home, '/home')
api.add_resource(setAngle, '/setAngle')
api.add_resource(testTap, '/testTap')
api.add_resource(speed, '/setspeed')
api.add_resource(PrivateResource, '/private')
api.add_resource(homepage, '/')
api.add_resource(getcurrentposition, '/currentpos')
api.add_resource(setcurrentposition, '/setpositionhome')
api.add_resource(disableMotor, '/motorStatus')

if __name__=='__main__':
    logger_console.info('smart tap bot main started')
    thread1=smart_tap_init()
    thread1.start()
    thread2=send_gcode()
    thread2.start()
    time.sleep(2)
    thread2.pass_command("G28 X Y")
    app.run(threaded=True,host='0.0.0.0', port=5000)#threaded flask server at local ip and port
