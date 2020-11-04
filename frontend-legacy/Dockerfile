FROM centos:7

ADD frontend-legacy/*.txt /efsearch/

RUN yum -y install epel-release && yum -y install python-pip postgresql && yum -y clean all && \
    pip install -r /efsearch/requirements.txt && \
    rm -rf /root/.cache

EXPOSE 8000

ADD backend/psql-efs                 /usr/local/bin/
ADD frontend-legacy/*                /efsearch/
ADD frontend-legacy/custom/*         /efsearch/custom/
ADD frontend-legacy/languages/*      /efsearch/languages/
ADD frontend-legacy/res/*            /efsearch/res/
ADD frontend-legacy/res/img/*        /efsearch/res/img/
ADD frontend-legacy/res/img/smiles/* /efsearch/res/img/smiles/

WORKDIR /efsearch

CMD ["python", "wsgi.py"]
