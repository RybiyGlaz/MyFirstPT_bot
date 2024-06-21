1. Создать три машины
2. На каждой из них создать нового пользователя ansible
3. И также на каждой машине предоставить права данному пользователю ansible ALL=(ALL:ALL) NOPASSWD:ALL (чтобы войти в файл sudoers написать sudo visudo)
4. Установить на хостовой машине ansible (
sudo apt-get install python3
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 2
sudo apt install python3-pip
sudo apt install ansible
export PATH=$PATH:/home/user/.local/bin
ansible --version)
5. Создать директории и конфигурационные файлы как в данном репозитории или перенести их на сволю мамашину данной векти данного репозитория с помощью git clone --branch ansible https://github.com/RybiyGlaz/MyFirstPT_bot.git
6. ansible-playbook playboot-tg-bot.yaml
