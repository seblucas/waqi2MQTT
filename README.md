# waqi2MQTT
Get the air quality from http://aqicn.org/ (waqi) and send it to your MQTT broker 

# Why ?

I did not find anything as simple as sending the data to a MQTT broker so I had to build it with python.

# Usage

## Prerequisite

You simply need Python3 (never tested with Python2.7) and the only dependencies are `requests` (to access the api) and `paho-mqtt` (for MQTT broker interaction) so this line should be enough  :

```bash
pip3 install paho-mqtt requests
```

## Getting your API token

First you'll have to get tour [API Key](http://aqicn.org/data-platform/token/#/). Then you can use the demo to find the city's ID you're interested in.

## Using the script

Easy, first try a dry-run command :

```bash
./waqi2MQTT.py -c '<CITY_ID>' -a '<API_KEY>' -n -v
```

and then a real command to add to your crontab :

```bash
./waqi2MQTT.py -c '<CITY_ID>' -a '<CLIENT_SECRET>'
```

The secrets can also be set with environment variables, see the help for more detail.

## Other things to know

I personaly use cron to start this program so as I want to keep the latest timestamp received from the API, I store it by default in `/tmp/waqi_last` (you can change it through a command line parameter).

## Docker

I added a sample Dockerfile, I personaly use it with a `docker-compose.yml` like this one :

```yml
version: '3'

services:
  waqi:
    build: .
    image: waqi2mqtt-python3-cron:latest
    restart: always
    environment:
      WAQI_API_KEY: YOUR_API_KEY
      WAQI_CITY_ID: "YOUR_CITY_ID_WITH_THE_@"
      CRON_STRINGS: "09 * * * * waqi2MQTT.py -m localhost -v"
      CRON_LOG_LEVEL: 8
```

# Limits

None, I hope at least ;). I had to adjust the timestamp provided, it seems to fit with my locale (France) but it may need some additional work. 

# License

This program is licenced with GNU GENERAL PUBLIC LICENSE version 2 by Free Software Foundation, Inc.
