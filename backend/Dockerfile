FROM centos:8

ADD backend/*.txt /efsearch/

RUN dnf -y install python3 python3-devel shadow-utils postgresql gcc && dnf -y clean all && \
    pip3 install -r /efsearch/requirements.txt && \
    rm -rf /root/.cache

RUN adduser --gid 0 -d /efsearch --no-create-home -c 'efsearch user' efsearch

USER efsearch

EXPOSE 8000

ADD backend/psql-efs        /usr/local/bin/
ADD backend/*.sh            /efsearch/
ADD backend/common/*.py     /efsearch/common/
ADD backend/db_admin/*.py   /efsearch/db_admin/
ADD backend/fetcher/*.py    /efsearch/fetcher/
ADD backend/scheduler/*.py  /efsearch/scheduler/
