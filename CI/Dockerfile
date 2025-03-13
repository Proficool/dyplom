FROM jenkins/jenkins:2.492.1-jdk17

# Переходим на пользователя root для установки необходимых пакетов и настроек
USER root

# Обновляем пакеты и устанавливаем lsb-release и curl
RUN apt-get update && apt-get install -y lsb-release curl

# Добавляем официальный GPG-ключ Docker
RUN curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc \
  https://download.docker.com/linux/debian/gpg

# Добавляем Docker-репозиторий
RUN echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
  https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list

# Устанавливаем Docker CLI
RUN apt-get update && apt-get install -y docker-ce-cli

USER root