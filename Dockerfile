FROM seblucas/alpine-python3:latest
LABEL maintainer="Sebastien Lucas <sebastien@slucas.fr>"
LABEL Description="waqi2MQTT image"

COPY waqi2MQTT.py /usr/bin/waqi2MQTT.py
ADD https://gist.github.com/seblucas/0668844f2ef247993ff605f10014c1ed/raw/070321575dc656eee16ee6bfeb3f19aea56a4ac0/runCron.sh /bin/runCron.sh

RUN chmod +x /usr/bin/waqi2MQTT.py && \
    chmod +x /bin/runCron.sh

ENTRYPOINT ["runCron.sh"]
    
