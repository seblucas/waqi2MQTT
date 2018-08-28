#!/bin/sh

CRON_LOG_LEVEL="${CRON_LOG_LEVEL:-7}"

[ ! -z "$CRON_STRINGS" ] && echo -e "$CRON_STRINGS\n" >> /var/spool/cron/crontabs/root

crond -l $CRON_LOG_LEVEL -f
