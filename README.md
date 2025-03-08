# Развёртывание бота с использованием Docker
## Описание
Этот проект представляет собой бота, развёртываемого с помощью Docker Compose.
## Установка и запуск
Для развертывания бота выполните следующие шаги:
### 1. Установите Docker
```sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
### 2. Клонируйте репозиторий
```git clone --branch docker https://github.com/RybiyGlaz/MyFirstPT_bot.git
cd MyFirstPT_bot
```
### 3. Запустите контейнеры с помощью Docker Compose
```sudo systemctl restart docker
docker compose up --build -d
docker ps
```
