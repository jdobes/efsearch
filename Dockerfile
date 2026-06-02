FROM registry.access.redhat.com/ubi10/ubi-minimal:10.2-1780413072@sha256:39c5de8723ad21c6a34e15cfba75f096d6a7191de98481b870b3dba575d65302

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
