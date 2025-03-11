# cronjob.sh

# Este cron job se ejecutará cada minuto
* * * * * root python /app/main.py >> /var/log/cron.log 2>&1