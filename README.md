Установка и запуск
Для развертывания бота выполните следующие шаги:

1. Установите Docker
удар
Копировать
Редактировать
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
2. Клонируйте репозиторий
удар
Копировать
Редактировать
git clone --branch docker https://github.com/RybiyGlaz/MyFirstPT_bot.git
cd MyFirstPT_bot
3. Запустите контейнеры с помощью Docker Compose
удар
Копировать
Редактировать
sudo systemctl restart docker
docker compose up --build -d
docker ps
Структура проекта
bot/ — директория с кодом бота.
config/ — конфигурационные файлы.
logs/ — директория с логами работы бота.
docker-compose.yml — конфигурация Docker Compose.
Конфигурация
Бот использует переменные окружения, описанные в docker-compose.yml:

Переменная	Значение по умолчанию	Описание
БОТ_ТОКЕН	(указать токен)	Токен для Telegram-бота
DB_HOST	дб	Хо
DB_PORT	5432	Порт базы данных
ИМЯ_БД	bot_db	Имя базы данных
DB_USER	пользователь	Пользователь базы данных
DB_PASSWORD	Пароль	Пароль БД
