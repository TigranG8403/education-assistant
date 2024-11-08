# Education Assistant
### Введение
Прототип разработан с фокусом на демонстрацию основных функций, описанных нами в презентации. Он отображает ключевые моменты интерфейса и функциональности, однако некоторые элементы представлены в упрощенном виде для экономии времени. Следует учитывать, что текущая версия прототипа не в точности соответствует представленному в презентации описанию: часть деталей была упрощена, чтобы сконцентрироваться на ключевых аспектах. Важно понимать, что это именно прототип, демонстрирующий общую логику работы приложения и базовый функционал, которые ещё предстоит доработать и уточнить.

### Шаги для установки клиента:
1. Скачивание и разархивирование папки client;
2. Импорт полученной папки (как проекта) в среду разработки (PyCharm, VS Code) и установка в неё виртуального окружения Python 3.12;
3. В терминале выполните команду: `pip install kivy pydantic requests SpeechRecognition pyaudio pydub moviepy fitz python-docx python-pptx` или переместите requirements.txt во вложенную папку Scripts папки виртуального окружения и в cmd выполните команды: 1) `cd путь_к_разархивированной_папке_репозитория\папка_вирт_окруж\Scripts`, 2) `pip install -r requirements.txt`
4. Запуск client.py через среду разработки.

### Если вы хотите развернуть серверную часть на своём устройстве (продвинутый уровень):
1. Скачивание и разархивирование папки server;
2. Импорт полученной папки (как проекта) в среду разработки (PyCharm, VS Code) и установка в неё виртуального окружения Python 3.11;
3. В терминале выполните команду: `pip install fastapi uvicorn pytubefix pydub SpeechRecognition html transformers bert_punctuation torch>=1.1.0 pytorch_pretrained_bert==0.6.2 pymorphy2==0.8 sacremoses` или переместите requirements.txt во вложенную папку Scripts папки виртуального окружения и в cmd выполните команды: 1) `cd путь_к_разархивированной_папке_репозитория\папка_вирт_окруж\Scripts`, 2) `pip install -r requirements.txt`
4. [Скачивание архива с весами BERT](https://drive.google.com/file/d/190dLqhRjqgNJLKBqz0OxQ3TzxSm5Qbfx) в папку server;
5. Редактирование кода: в среде разработки нажимаем Ctrl-F: 1) server.py: uvicorn.run("server:app", reload=True, host = "192.168.3.10", port=1234) и заменяем в этой строке данные: "host = "ваш_локальный_ip", port=ваш_порт";
                                                            2) client.py: "http://176.56.54.46:1234" и заменяем все экземпляры на "http://ваш_стат_или_локал_ip:ваш_порт";
6. Работа с брандмауэром системы и роутера: 1) Брандмауэр: создание разрешающих правил входящего и исходящего подключений для вашего порта;
                                            2) Роутер: Безопасность -> Службы NAT -> Переадресация портов -> Ваш порт и устройство (путь может отличаться в зависимости от производителя и модели оборудования).
7. Установка и настройка клиента Lantern и программы nekoray для обхода замедления YouTube: 1) Установка Lantern;
                                                                                            2) Настройки Lantern: Управление системными прокси: вкл;
                                                                                            3) Установка nekoray;
                                                                                            4) Настройка nekoray: ПКМ по списку серверов: Новый профиль -> имя: произвольное; -> тип: http; -> адрес и порт: см. настройки Lantern для HTTP(S); -> ОК;
                    ->Настройки -> Настройки маршрутов -> Базовые маршруты -> см. таблицу: строка "Домен", колонка "Прокси" - вводим "geosite:youtube" -> ОК.
                                                                                            -> Режим TUN: вкл; Режим системного прокси: вкл; -> ПКМ по созданному серверу: Запустить. (Если не работает, то выполнить пункт 6 с соответствующими параметрами);

### Текущее состояние\планы на будущее проекта: 
1. Установленная на данный момент костыльная русско-англо-русская модель суммаризации будет изменена на BART, дообученный сразу сокращать тексты на русском;
2. Серверная часть запущена 24/7 на DELL POWEREDGE R720 (2 x Xeon E5-2680 v2; 384 GB оперативной памяти), который установлен дома (со статическим IP). Cуммаризация происходит довольно медленно: на сервере нет мощного GPU (просим проявить терпение)...;
3. Есть проблема с доставкой длинного суммаризированного текста в приложение: на сервере суммаризированный текст отображается, а в приложении - ошибка 500. Поэтому убедительная просьба: разбивайте длинные тексты, видео на части (это ведь ещё прототип);
4. Из-за нехватки времени приложение пока не оптимизировано под мобильные платформы, что мы обязательно исправим;
5. Возникнут вопросы - пишите капитану.

     ## Мы были честными, Ваши COPY-PASTE!
