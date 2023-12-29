FROM registry.access.redhat.com/ubi8/ubi-minimal

ENV TZ=UTC

ADD requirements.txt         /efsearch/

# install postgresql from centos if not building on RHSM system
RUN FULL_RHEL=$(microdnf repolist --enabled | grep rhel-8) ; \
    if [ -z "$FULL_RHEL" ] ; then \
        rpm -Uvh http://mirror.centos.org/centos/8-stream/BaseOS/x86_64/os/Packages/centos-stream-repos-8-4.el8.noarch.rpm \
                 http://mirror.centos.org/centos/8-stream/BaseOS/x86_64/os/Packages/centos-gpg-keys-8-4.el8.noarch.rpm && \
        sed -i 's/^\(enabled.*\)/\1\npriority=200/;' /etc/yum.repos.d/CentOS*.repo ; \
    fi

RUN microdnf module enable postgresql:13 && \
    microdnf install --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        python39 python39-pip python39-devel python39-setuptools shadow-utils gcc postgresql postgresql-devel util-linux && \
    microdnf clean all && \
    pip3 install -r /efsearch/requirements.txt && \
    rm -rf /root/.cache

RUN adduser --gid 0 -d /efsearch --no-create-home -c 'efsearch user' efsearch

USER efsearch

EXPOSE 8000

ADD psql-efs                         /usr/local/bin/
ADD *.sh                             /efsearch/
ADD backend/*.py                     /efsearch/backend/
ADD backend/common/*.py              /efsearch/backend/common/
ADD backend/db_admin/*.py            /efsearch/backend/db_admin/
ADD backend/fetcher/*.py             /efsearch/backend/fetcher/
ADD backend/scheduler/*.py           /efsearch/backend/scheduler/
ADD frontend-legacy/*                /efsearch/frontend/
ADD frontend-legacy/custom/*         /efsearch/frontend/custom/
ADD frontend-legacy/languages/*      /efsearch/frontend/languages/
ADD frontend-legacy/res/*            /efsearch/frontend/res/
ADD frontend-legacy/res/css/*        /efsearch/frontend/res/css/
ADD frontend-legacy/res/img/*        /efsearch/frontend/res/img/
ADD frontend-legacy/res/img/smiles/* /efsearch/frontend/res/img/smiles/

WORKDIR /efsearch
