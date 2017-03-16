"""Script for periodic temperature Json report via MQTT protocol."""
import network
import machine
from simple import MQTTClient
from time import ticks_ms, sleep, sleep_ms
from onewire import OneWire
from ds18x20 import DS18X20
import json

with open('config.json') as config_file:
    config = json.load(config_file)

sta = network.WLAN(network.STA_IF)
sensors = DS18X20(OneWire(machine.Pin(0)))  # wemos pin D3 
mqtt = MQTTClient(config["device_name"], config["mqtt_server"],
                  user=config["mqtt_user"], password=config["mqtt_pass"])


def wifi_connect(timeout=20):
    """Connect to WiFi with timeout [s]."""
    sta.active(True)
    sta.config(dhcp_hostname=config["device_name"])
    sta.ifconfig((config["wifi_ip"], config["wifi_mask"],
                  config["wifi_gateway"], config["wifi_dns"]))
    sta.connect(config["wifi_ssid"], config["wifi_pass"])
    attempt = 0
    print("Connecting to WiFi.", end="")
    while not sta.isconnected():
        sleep(1)
        attempt += 1
        print(".", end="")
        if attempt > timeout:
            sta.disconnect()
            print("\nConnection could NOT be established!")
            break
    if sta.isconnected():
        print("\nConnected to WiFi")


def measure():
    """Perform DS18B20 measurement and return json message to publish."""
    sensors.convert_temp()
    sleep_ms(750)
    temperature = [sensors.read_temp(t) for t in sensors.scan()]
    try:
        print("Temp: " + str(temperature[0]) + chr(176) + "C")
        return json.dumps({'temp': temperature[0]})
    except IndexError:
        print("Sensor Error!")


def mqtt_publish():
    """Connect to MQTT broker, publish message and disconnect again."""
    try:
        mqtt.connect()
        mqtt.publish(config["mqtt_temp_topic"].encode("utf-8"),
                     measure().encode("utf-8"), retain=True)
        mqtt.disconnect()
        print("Message successfully published in topic " +
              config["mqtt_temp_topic"])
    except:
        print("Message NOT published!")


def wifi_disconnect():
    """Disonnect from WiFi."""
    if sta.isconnected():
        sta.disconnect()
    sta.active(False)
    print("WiFi disconnected")


def go_sleep(sleep_minutes):
    """Perform deepsleep to save energy."""
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # ticks_ms is used to make wake up period more consistent
    sleep_seconds = (sleep_minutes * 60) - (ticks_ms() // 1000)
    rtc.alarm(rtc.ALARM0, sleep_seconds * 1000)
    print(str(sleep_seconds // 60) +
          ":" + str(sleep_seconds % 60) +
          " minutes deep sleep NOW!")
    machine.deepsleep()


wifi_connect()
mqtt_publish()
wifi_disconnect()
go_sleep(config["wakeup_period"])
