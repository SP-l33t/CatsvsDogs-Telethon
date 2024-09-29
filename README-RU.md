[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+jJhUfsfFCn4zZDk0)      [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/catsdogs_game_bot/join?startapp=525256526)


## Рекомендации по использованию

# 🔥🔥 Версия PYTHON должна быть 3.10 🔥🔥🔥

> 🇪🇳 README in english available [here](README)

## Функционал  
|          Функционал           | Поддерживается |
|:-----------------------------:|:--------------:|
|        Многопоточность        |       ✅        |
|   Привязка прокси к сессии    |       ✅        |
| Привязка User-Agent к сессии  |       ✅        |
|      Регистрация в боте       |       ✅        |
|          Автозадачи           |       ✅        |
|   Ежедневные вознаграждения   |       ✅        |
|  Поддержка telethon .session  |       ✅        |


## [Настройки](https://github.com/GravelFire/MajorBot/blob/main/.env-example/)
|        Настройки        |                                                                                                                              Описание                                                                                                                               |
|:-----------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|  **API_ID / API_HASH**  |                                                                                         Данные платформы, с которой будет запущена сессия Telegram (по умолчанию - android)                                                                                         |
| **GLOBAL_CONFIG_PATH**  | Определяет глобальный путь для accounts_config, proxies, sessions. <br/>Укажите абсолютный путь или используйте переменную окружения (по умолчанию - переменная окружения: **TG_FARM**)<br/> Если переменной окружения не существует, использует директорию скрипта |
|     **SLEEP_TIME**      |                                                                                                    Задержка перед следующим кругом (by default - [7200, 10800])                                                                                                     |
| **SESSION_START_DELAY** |                                                                        Задержка для старта каждой сессии от 1 до установленного значения (по умолчанию : **30**, задержка в интервале 1..30)                                                                        |
|      **AUTO_TASK**      |                                                                                                        Автоматическое виполнение заданий ( **True** / False)                                                                                                        |
|    **JOIN_CHANNELS**    |                                                                                                 Автоматически подписываться на телеграм каналы ( **True** / False )                                                                                                 |
|    **CLAIM_REWARD**     |                                                                                                                     Собирать ежедневную награду                                                                                                                     |
|       **REF_ID**        |                                                                                               Ваш идентификатор реферала после startapp= (Ваш идентификатор telegram)                                                                                               |
| **SESSIONS_PER_PROXY**  |                                                                                           Количество сессий, которые могут использовать один прокси (По умолчанию **1** )                                                                                           |
| **USE_PROXY_FROM_FILE** |                                                                                             Использовать ли прокси из файла `bot/config/proxies.txt` (**True** / False)                                                                                             |
|    **DEVICE_PARAMS**    |                                                                                  Вводить параметры устройства, чтобы сделать сессию более похожую, на реальную  (True / **False**)                                                                                  |
|    **DEBUG_LOGGING**    |                                                                                               Включить логирование трейсбэков ошибок в папку /logs (True / **False**)                                                                                               |

## Быстрый старт 📚

Для быстрой установки и последующего запуска - запустите файл run.bat на Windows или run.sh на Линукс

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) **версии 3.10**

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/SP-l33t/CatsvsDogs) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
git clone https://github.com/SP-l33t/CatsvsDogs.git
cd MajorBot
```

Затем для автоматической установки введите:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/CatsvsDogs-Telethon >>> python3 main.py --action (1/2)
# Or
~/CatsvsDogs-Telethon >>> python3 main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```


# Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/CatsvsDogs-Telethon >>> python main.py --action (1/2)
# Или
~/CatsvsDogs-Telethon >>> python main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```
