1. Установить докер (
sudo apt-get install ca-certificates curl 
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
)
2. Создать необходимые директории и конфигурационные файлы с содержимым как на данном репозитории или клонируем содержимое даннной ветки данного репозитория себе на машину (git clone --branch docker https://github.com/RybiyGlaz/MyFirstPT_bot.git)
3. В директории, в которй у нас находятся файлы из пункта 2, прописываем:
1) sudo systemctl restart docker 
2)  docker compose up --build -d
3)  docker ps
