ARG python=python:3.9.13-slim-bullseye

FROM ${python}

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>


# add and install python requirements
RUN pip install --upgrade pip --no-cache-dir
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir


# # setup user and group ids
ARG USER_ID=1001
ENV USER_ID $USER_ID
ARG GROUP_ID=1001
ENV GROUP_ID $GROUP_ID
ARG USER_NAME=appuser


ARG APP_DIR=/usr/src/app
# Setup app directory and copy files
RUN mkdir -p $APP_DIR

# Copy app files to container
WORKDIR $APP_DIR
COPY ./app .
COPY ./download_data.sh .

# Download data file for US wildfire analysis
ARG HOME=/home/$USER_NAME
RUN mkdir -p $HOME/.kaggle 
COPY ./kaggle.json $HOME/.kaggle
RUN chmod 600 $HOME/.kaggle/kaggle.json 
RUN ./download_data.sh

# # add non-root user and give permissions to workdir

RUN groupadd --gid $GROUP_ID $USER_NAME && \
          adduser $USER_NAME --ingroup $USER_NAME --gecos '' --disabled-password --uid $USER_ID && \
          chown -R $USER_NAME:$USER_NAME $APP_DIR && \
          chown -R $USER_NAME:$USER_NAME $HOME



# #switch user
USER $USER_NAME

# To download nltk lexicons upfront before starting streamlit app
# RUN python ./__init__.py

# CMD streamlit run --server.port 80 main.py