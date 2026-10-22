FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv \
        chromium chromium-driver \
        git curl \
 && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV SE_OFFLINE=false

RUN git config --system --add safe.directory '*'

RUN jenkins-plugin-cli --plugins \
        configuration-as-code \
        workflow-aggregator \
        git \
        junit \
        job-dsl \
        htmlpublisher \
        timestamper

COPY casc.yaml /var/jenkins_home/casc.yaml
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc.yaml
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dhudson.model.DownloadService.noSignatureCheck=true -Dhudson.plugins.git.GitSCM.ALLOW_LOCAL_CHECKOUT=true"

USER jenkins

