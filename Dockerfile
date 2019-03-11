FROM registry.gitlab.com/sysbio-aging/mitoage:base

WORKDIR /srv/www

COPY . .

RUN rm -rf database_files || echo "no database files found. good" && \
    rm -rf static_collected_files || echo "no static collected files found. good" && \
    mkdir -p /etc/services.d/django /var/log/mitoage && \
    cp config_files/run_app /etc/services.d/django/run

EXPOSE 5000

ENTRYPOINT ["/init"]

CMD []
