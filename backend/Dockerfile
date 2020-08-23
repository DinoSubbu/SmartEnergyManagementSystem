FROM ubuntu:latest

# Environmental variables for Gurobi
ENV GUROBI_HOME="/opt/gurobi901/linux64"
ENV PATH="$PATH:$GUROBI_HOME/bin"
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$GUROBI_HOME/lib"
ENV GUROBI_LICENSE="e3445096-6167-11ea-b82c-020d093b5256"

COPY . /

EXPOSE 8081

RUN cat /etc/resolv.conf

# Set the locale
RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository universe && apt-get install -y locales locales-all \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen
ENV LANG en_US.UTF-8 
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install python3 and pip3
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils \
    && apt-get -y install python3-dev python3-pip \
    && pip3 install --upgrade pip

# Install system libraries needed for python dependencies
RUN apt-get -y install libffi-dev python-dev curl wget

# Setup Gurobi solver
#RUN wget https://packages.gurobi.com/9.0/gurobi9.0.1_linux64.tar.gz \
   #&& tar xvfz gurobi9.0.1_linux64.tar.gz --directory /opt/ 
#RUN cd $GUROBI_HOME && python3 setup.py install
#RUN grbgetkey $GUROBI_LICENSE && gurobi.sh

# Install Python3 dependencies
RUN cat requirements.txt | xargs -n 1 pip3 install --no-cache-dir
