FROM postgres:latest

RUN apt-get update && apt-get install -y gettext-base

COPY init.sql /docker-entrypoint-initdb.d/init.sql.raw

RUN mkdir -p /oracle/pg_data/archive/ /var/log/postgresql/ /etc/postgresql/ && \
    chown postgres:postgres /oracle/pg_data/archive/ /var/log/postgresql/

ENTRYPOINT ["bash", "-c", "\
    envsubst < /docker-entrypoint-initdb.d/init.sql.raw > /docker-entrypoint-initdb.d/init.sql && \
    echo \"listen_addresses = '*'\" > /etc/postgresql/postgresql.conf && \
    echo \"port = '${DB_PORT}'\" >> /etc/postgresql/postgresql.conf && \
    echo \"log_destination = 'stderr'\" >> /etc/postgresql/postgresql.conf && \
    echo \"logging_collector = 'on'\" >> /etc/postgresql/postgresql.conf && \
    echo \"log_directory = '/var/log/postgresql/'\" >> /etc/postgresql/postgresql.conf && \
    echo \"log_filename = 'postgresql.log'\" >> /etc/postgresql/postgresql.conf && \
    echo \"archive_mode = 'on'\" >> /etc/postgresql/postgresql.conf && \
    echo \"archive_command = 'cp %p /oracle/pg_data/archive/%f'\" >> /etc/postgresql/postgresql.conf && \
    echo \"max_wal_senders = '10'\" >> /etc/postgresql/postgresql.conf && \
    echo \"wal_level = 'replica'\" >> /etc/postgresql/postgresql.conf && \
    echo \"wal_log_hints = 'on'\" >> /etc/postgresql/postgresql.conf && \
    echo \"log_replication_commands = 'on'\" >> /etc/postgresql/postgresql.conf && \
    echo \"local all ${DB_USER} peer\" > /etc/postgresql/pg_hba.conf && \
    echo \"host all all 0.0.0.0/0 md5\" >> /etc/postgresql/pg_hba.conf && \
    echo \"host replication ${DB_REPL_USER} 0.0.0.0/0 trust\" >> /etc/postgresql/pg_hba.conf && \
    docker-entrypoint.sh \"$@\""]

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf", "-c", "hba_file=/etc/postgresql/pg_hba.conf"]
