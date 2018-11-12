
# Описание

Микросервис, предназначенный для чтения, записи и доставки сообщений от Kafka любым приложениям по протоколу HTTP.

Используемый стек: ```python3.7```, ```aiohttp3.4```

# Установка

1. Создать и активировать виртуальную среду

    ```$ virtualenv -p python3.7 venv```

    ```$ source venv/bin/activate```

2. Установить зависимости
    ```$ pip install -r requirements.txt```

3. Задать настройки приложения
	
В папке ```config``` находятся заготовка ```dev.yaml.example```. Для локального запуска необходимо создать файл ```dev.yaml``` и задать требуемые параметры. 

Секция ```kafka``` содержит параметры ```host``` и ```port```, где необходимо указать хост и порт брокера Kafka, а также параметр ```topics``` - поддерживаемые топики, сообщения которых будут "слушаться", "читаться", а также "отправляться".

Секция ```consumers``` содержит список приложений-клиентов, который будут получать сообщения. Параметры ```host```, ```port```, и ```protocol```, где задаются параметры приложения-клиента, которое будет получать и отправлять сообщения, а также ```url``` - callback url, на которой будут отправляться приходящие сообщения. 

БД конфигурируется в разделе ```mysql``` (опускаю описание очевидных параметров),  ```minsize``` и ```maxsize``` задают минимальное и максимальное количество соединений в пулле.

Настройки почты конфигурируется в разделе ```email``` (опускаю описание очевидных параметров),  ```auth_required``` указывает на то, нужна ли аутентификация, и если да, то берет данные из ```username```, ```password```.  ```email_to_notify``` - адрес почты администратора, куда будут направяться сообщения об ошибках в системе.

Параметры внизу файла конфигурации ```host``` и ```port``` отвечают за хост и порт самого приложения. ```debug``` - параметр сигнализирует о статусе запуска, аналогично параметру ```DEBUG``` в ```django```. ```period_to_resend``` - время в секундах, через которое будет проверяться наличие недоставленных сообщений. ```resend_limit``` - количество попыток отправки недоставленных сообщений. ```token``` - авторизационный токен.

4. Подготовка БД 

Необходимо создать таблицу в БД, запустив вспомогательный скрипт ```init_db.py```.
Скрипт может принимать в параметрах наименование конфигурационного файла  - ```init_db.py --config=test```. По-умолчанию используется файл настроек ```dev.yaml```

# Запуск приложения

Приложение можно запускать в двух различных вариантов, а именно:

- С помощью встроенного сервера

    ```$ python run.py --config=<config_name> ```
    Параметр ```--config``` можно пропустить, в таком случае по-умолчанию будет использован файл ```config/dev.yaml```

- С помощью Gunicorn

    ```$ gunicorn 'app.main:wsgi("<config_name>")' -b 0.0.0.0:<port> -k aiohttp.GunicornWebWorker -w <workers>```,  где ```<config_name>``` - имя конфигурационного файла (**внимание**, в данном способе запуска указывать кофнигурационный файл обязательно, по-умолчанию значение не подставляется), ```<port>``` - TCP-порт, по которому будет доступно приложение, ```<workers>``` - количество "воркеров".


**...планиурется добавить возможность контейнеризации приложения...**