FROM centos:7

RUN yum -y install gcc
RUN yum -y install gcc-c++
RUN yum -y install make
RUN yum -y install swig
RUN yum -y install python-devel
RUN yum -y install git
RUN yum -y install openssl-devel
RUN yum -y install expat-devel
