FROM registry.access.redhat.com/ubi10/ubi-minimal:10.1-1774228210@sha256:c858c2eb5bd336d8c400f6ee976a9d731beccf3351fa7a6f485dced24ae4af17

ENV TZ=UTC

ADD requirements.txt         /efsearch/

RUN microdnf install -y --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        python3 python3-pip && \
    microdnf clean all && \
    pip3 install -r /efsearch/requirements.txt && \
    rm -rf /root/.cache

EXPOSE 8000

ADD *.sh                      /efsearch/
ADD backend/*.py              /efsearch/backend/
ADD backend/common/*.py       /efsearch/backend/common/
ADD backend/db_admin/*.py     /efsearch/backend/db_admin/
ADD backend/fetcher/*.py      /efsearch/backend/fetcher/
ADD backend/scheduler/*.py    /efsearch/backend/scheduler/
ADD frontend/*                /efsearch/frontend/
ADD frontend/custom/*         /efsearch/frontend/custom/
ADD frontend/languages/*      /efsearch/frontend/languages/
ADD frontend/res/*            /efsearch/frontend/res/
ADD frontend/res/css/*        /efsearch/frontend/res/css/
ADD frontend/res/img/*        /efsearch/frontend/res/img/
ADD frontend/res/img/smiles/* /efsearch/frontend/res/img/smiles/

WORKDIR /efsearch
