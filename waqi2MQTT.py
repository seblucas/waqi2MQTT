#!/usr/bin/env python3
#
#  waqi2MQTT.py
#
#  Copyright 2016~2018 Sébastien Lucas <sebastien@slucas.fr>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# Sample data returned by the API
# {
#    "status":"ok",
#    "data":{
#       "aqi":161,
#       "idx":6973,
#       "attributions":[
#          {
#             "url":"http://www.irceline.be/en/",
#             "name":"IRCEL-CELINE - Belgian Interregional Environment Agency"
#          }
#       ],
#       "city":{
#          "geo":[
#             50.7934690465272,
#             3.10964187480641
#          ],
#          "name":"Menen",
#          "url":"http://aqicn.org/city/belgium/fla/menen/"
#       },
#       "dominentpol":"pm25",
#       "iaqi":{
#          "h":{
#             "v":86
#          },
#          "p":{
#             "v":1020
#          },
#          "pm10":{
#             "v":66
#          },
#          "pm25":{
#             "v":161
#          },
#          "t":{
#             "v":-0.1
#          }
#       },
#       "time":{
#          "s":"2017-02-10 14:00:00",
#          "tz":"+01:00",
#          "v":1486735200
#       }
#    }
# }


import os, re, time, json, argparse
import requests                     # pip install requests
import paho.mqtt.publish as publish # pip install paho-mqtt

verbose = False
WAQI_URL = 'https://api.waqi.info/feed/{0}/?token={1}'

def debug(msg):
  if verbose:
    print (msg + "\n")
    
def environ_or_required(key):
  if os.environ.get(key):
      return {'default': os.environ.get(key)}
  else:
    return {'required': True}

def getWaqi(city, apiKey):
  tstamp = int(time.time())
  waqiUrl = WAQI_URL.format(city, apiKey)
  debug ("Trying to get data from {0}".format(waqiUrl))
  try:
    r = requests.get(waqiUrl)
    data = r.json()
    if not 'status' in data:
      return (False, {"time": tstamp, "message": "WAQI data not well formed", "data": data})
    if data['status'] != 'ok':
      return (False, {"time": tstamp, "message": "WAQI internal API Error", "data": data})
    if (not 'h' in data['data']['iaqi'] or
       not 't' in data['data']['iaqi'] or
       not 'p' in data['data']['iaqi'] or
       not 'pm10' in data['data']['iaqi'] or
       not 'pm25' in data['data']['iaqi']):
      return (False, {"time": tstamp, "message": "WAQI's response incomplete", "data": data})
    tz = data['data']['time']['tz']
    diff = int(tz[1:3]) * 3600
    if tz[0] == "+":
      diff *= -1
    newObject = {"time": data['data']['time']['v']+diff, "temp": data['data']['iaqi']['t']['v'],
                                                    "hum": data['data']['iaqi']['h']['v'],
                                                    "pm10": data['data']['iaqi']['pm10']['v'],
                                                    "pm25": data['data']['iaqi']['pm25']['v'],
                                                    "pres": data['data']['iaqi']['p']['v']}
    return (True, newObject)
  except requests.exceptions.RequestException as e:
    return (False, {"time": tstamp, "message": "WAQI not available : " + str(e)})


parser = argparse.ArgumentParser(description='Read current air quality, temperature and humidity from waqi.info and send them to a MQTT broker.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-a', '--waqi-api-key', dest='waqiApiKey', action="store",
                   help='WAQI API Key.',
                   **environ_or_required('WAQI_API_KEY'))
parser.add_argument('-c', '--city', dest='city', action="store",
                   help='WAQI city ID.',
                   **environ_or_required('WAQI_CITY_ID'))
parser.add_argument('-m', '--mqtt-host', dest='host', action="store", default="127.0.0.1",
                   help='Specify the MQTT host to connect to.')
parser.add_argument('-n', '--dry-run', dest='dryRun', action="store_true", default=False,
                   help='No data will be sent to the MQTT broker.')
parser.add_argument('-o', '--last-time', dest='previousFilename', action="store", default="/tmp/waqi_last",
                   help='The file where the last timestamp coming from WAQI API will be saved')
parser.add_argument('-t', '--topic', dest='topic', action="store", default="sensor/outdoor",
                   help='The MQTT topic on which to publish the message (if it was a success).')
parser.add_argument('-T', '--topic-error', dest='topicError', action="store", default="error/sensor/outdoor", metavar="TOPIC",
                   help='The MQTT topic on which to publish the message (if it wasn\'t a success).')
parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,
                   help='Enable debug messages.')


args = parser.parse_args()
verbose = args.verbose;

maxRetry = 3
while maxRetry > 0:
  status, data = getWaqi(args.city, args.waqiApiKey)
  if status:
    break
  time.sleep(7)
  debug ("Retrying ...")
  maxRetry -= 1

jsonString = json.dumps(data)
if status:
  debug("Success with message <{0}>".format(jsonString))
  if os.path.isfile(args.previousFilename):
    oldTimestamp = open(args.previousFilename).read(10);
    if int(oldTimestamp) >= data["time"]:
      print ("No new data found")
      exit(0)

  # save the last timestamp in a file
  with open(args.previousFilename, 'w') as f:
    f.write(str(data["time"]))
  if not args.dryRun:
    publish.single(args.topic, jsonString, hostname=args.host)
else:
  print("Failure with message <{0}>".format(jsonString))
  if not args.dryRun:
    publish.single(args.topicError, jsonString, hostname=args.host)


