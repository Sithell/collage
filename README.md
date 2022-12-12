# collage
Generate collages in telegram

Telegram бот, генерирующий всевозможные коллажи из заданного набора фотографий и выдающий результат в виде zip архива. Для ускорения используется параллельная обработка в несколько воркеров.

## Setup

1. Для работы нужно [установить beanstalkd](https://beanstalkd.github.io/download.html) и запустить его:
```bash
sudo systemctl start beanstalkd.service
```

2. Установить зависимости
```bash
pip install -r requirements.txt
```

3. Получить у [BotFather](https://t.me/BotFather) токен для бота

4. Заполнить конфиги, в т.ч. токен в `config/telegram.py`
```bash
cp config/beanstalk.py.dist config/beanstalk.py
cp config/telegram.py.dist config/telegram.py  
```

5. Создать папку `temp`
```bash
mkdir temp
```

6. Запустить бота
```bash
python main.py
```

7. Параллельно запустить воркер(ы)
```bash
python worker/collage_worker.py
```

8. Готово.

