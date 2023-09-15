import board
import busio
import PM2_5
import aq
import time
import adafruit_dht
import digitalio
from random import randint
from secrets import secrets

from adafruit_wiznet5k.adafruit_wiznet5k import *
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket

import adafruit_minimqtt.adafruit_minimqtt as MQTT

#Add PM2.5
PM_test = PM2_5.PM2_5(board.GP4, board.GP5)

#Add air quality
air_q = aq.air_quality(board.GP0, board.GP1)

#Add DHT22
dhtDevice = adafruit_dht.DHT22(board.GP2)

#Add Fan
fan = digitalio.DigitalInOut(board.GP6)
fan.direction = digitalio.Direction.OUTPUT

#SPI
SPI0_SCK = board.GP18
SPI0_TX = board.GP19
SPI0_RX = board.GP16
SPI0_CSn = board.GP17

#Reset
W5x00_RSTn = board.GP20

print("Wiznet5k Adafruit Up&Down Link Test (DHCP)")
# Setup your network configuration below
# random MAC, later should change this value on your vendor ID
MY_MAC = (0x00, 0x01, 0x02, 0x03, 0x04, 0x05)
IP_ADDRESS = (192, 168, 1, 100)
SUBNET_MASK = (255, 255, 255, 0)
GATEWAY_ADDRESS = (192, 168, 1, 1)
DNS_SERVER = (8, 8, 8, 8)


ethernetRst = digitalio.DigitalInOut(W5x00_RSTn)
ethernetRst.direction = digitalio.Direction.OUTPUT

# For Adafruit Ethernet FeatherWing
cs = digitalio.DigitalInOut(SPI0_CSn)
# For Particle Ethernet FeatherWing
# cs = digitalio.DigitalInOut(board.D5)

spi_bus = busio.SPI(SPI0_SCK, MOSI=SPI0_TX, MISO=SPI0_RX)

# Reset W5x00 first
ethernetRst.value = False
time.sleep(1)
ethernetRst.value = True

# # Initialize ethernet interface without DHCP
# eth = WIZNET5K(spi_bus, cs, is_dhcp=False, mac=MY_MAC, debug=False)
# # Set network configuration
# eth.ifconfig = (IP_ADDRESS, SUBNET_MASK, GATEWAY_ ADDRESS, DNS_SERVER)

# Initialize ethernet interface with DHCP
eth = WIZNET5K(spi_bus, cs, is_dhcp=True, mac=MY_MAC, debug=False)

print("Chip Version:", eth.chip)
print("MAC Address:", [hex(i) for i in eth.mac_address])
print("My IP address is:", eth.pretty_ip(eth.ip_address))

# MQTT Topic
# Use this topic if you'd like to connect to a standard MQTT broker
mqtt_topic = secrets["Beebotte_channel"]
mqtt_temp = "/temp"
mqtt_hum = "/hum"
mqtt_pm1 = "/pm1"
mqtt_pm25 = "/pm25"
mqtt_pm10 = "/pm10"
mqtt_tvoc = "/tvoc"
mqtt_cho2 = "/ch02"
mqtt_co2 = "/c02"
mqtt_fan = "/fan"
# Adafruit IO-style Topic
# Use this topic if you'd like to connect to io.adafruit.com
# mqtt_topic = 'aio_user/feeds/temperature'

### Code ###


# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connect(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")
    print("Flags: {0}\n RC: {1}".format(flags, rc))


def disconnect(client, userdata, rc):
    # This method is called when the client disconnects
    # from the broker.
    print("Disconnected from MQTT Broker!")


def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

def unsubscribe(client, userdata, topic, pid):
    # This method is called when the client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(client, userdata, topic, pid):
    # This method is called when the client publishes data to a feed.
    print("Published to {0} with PID {1}".format(topic, pid))
    
def message(client, topic, message):
    # Method callled when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))
    if message != None:
        fan.value = 1
        

# Initialize MQTT interface with the ethernet interface
MQTT.set_socket(socket, eth)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="mqtt.beebotte.com",
    username=secrets["Beebotte_user"],
    password= "",
    client_id= "",
    is_ssl=False,
)

# Connect callback handlers to client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish
mqtt_client.on_message = message

print("Attempting to connect to %s" % mqtt_client.broker)
mqtt_client.connect()

print("Subscribing to %s" % mqtt_topic + mqtt_fan)
mqtt_client.subscribe(mqtt_topic + mqtt_fan)

while True:
    mqtt_client.loop()
    try:
        # Print the values to the serial port
        temperature_c = int(dhtDevice.temperature)
        print("Publishing to %s" % mqtt_topic)
        mqtt_client.publish(mqtt_topic+mqtt_temp, '{"data": '+ '{}'.format(temperature_c) + ', "write": true}')
        humidity = int(dhtDevice.humidity)       
        mqtt_client.publish(mqtt_topic+mqtt_hum, '{"data": '+ '{}'.format(humidity) + ', "write": true}')
        print(
            "Temp:  {:.1f} C    Humidity: {}% ".format(temperature_c, humidity)
        )
        TV0C,CH02,C02 = air_q.collect_data()
        mqtt_client.publish(mqtt_topic+mqtt_tvoc, '{"data": '+ '{}'.format(TV0C) + ', "write": true}')
        mqtt_client.publish(mqtt_topic+mqtt_cho2, '{"data": '+ '{}'.format(CH02) + ', "write": true}')
        mqtt_client.publish(mqtt_topic+mqtt_co2, '{"data": '+ '{}'.format(C02) + ', "write": true}')
        print ("TV0C value = {} ug/m3".format(TV0C))
        print ("CH02 value = {} ug/m3".format(CH02))
        print ("C02 value = {} PPM".format(C02))
        PM1,PM25,PM10 = PM_test.collect_data()
        mqtt_client.publish(mqtt_topic+mqtt_pm1, '{"data": '+ '{}'.format(PM1) + ', "write": true}')
        mqtt_client.publish(mqtt_topic+mqtt_pm25, '{"data": '+ '{}'.format(PM25) + ', "write": true}')
        mqtt_client.publish(mqtt_topic+mqtt_pm10, '{"data": '+ '{}'.format(PM10) + ', "write": true}')        
        print ("PM1.0 value = {} ug/m3".format(PM1))
        print ("PM2.5 value = {} ug/m3".format(PM25))
        print ("PM10 value = {} ug/m3".format(PM10))

        time.sleep (0.5)

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except SyntaxError as error:
        print (error)
        time.sleep(2.0)
        continue
    except TypeError as error:
        time.sleep(0.1)
        continue
    except ValueError as error:
        time.sleep(0.1)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)
    