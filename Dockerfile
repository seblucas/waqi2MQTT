FROM seblucas/alpine-python3:latest
LABEL maintainer="Sebastien Lucas <sebastien@slucas.fr>"
LABEL Description="waqi2MQTT image"

COPY waqi2MQTT.py /usr/bin/waqi2MQTT.py
COPY runCron.sh /bin/runCron.sh

RUN chmod +x /usr/bin/waqi2MQTT.py && \
    chmod +x /bin/runCron.sh

ENTRYPOINT ["runCron.sh"]
    
