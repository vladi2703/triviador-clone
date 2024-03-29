# Triviador Clone

Тривиадор е игра базирана на ходове. Всеки играч трябва да завладее първата си територия. След това за всяка друга може да я завладее по два начина: 

- Ако територията е свободна, превзема я
- Ако територията е заета, трябва да атакува притежателя ѝ

Атаката се състои в задаване на въпрос до двамата играчи - нападателя и защитника. Който отговори правилно печели територията. Ако и двамата отговорят правилно - по-бързият печели. 

Цел на играта: 

Играчът, завладял целия “свят” печели.

## Структура на проекта

```
├── README.md
├── client.py
├── gameutils
│   ├── database.py
│   ├── game.py
│   ├── playboard.py
│   └── question.py
├── main.py
├── messagingutils
│   ├── messageq.py
│   └── messaging.py
├── resources
│   └── players.txt
├── server.py
├── test
│   ├── test_game.py
│   ├── test_messageq.py
│   ├── test_messaging.py
│   └── test_question.py
└── venv
```

Сървърът се стартира с изпълнение на файла *main.py,* всеки от играчите трябва да стартира файлът *client.py* като по този начин се свързва със сървъра. Броят играчи е фиксиран - 3ма. 

## Пакетът *`gameutils`*

Съдържа модули, които повишават нивото на абстракция на програмата и са полезни за лесна работа в сървъра. 

### Database.py

Съдържа клас `PlayerDatabase`, който съдържа информация за играчите. Записва прогресът от текущата игра във файл в паметта, и при стартиране на нова игра - при наличен файл с архивирана игра я зарежда и продължава от където е спряла. 

### Game.py

Съдържа клас `Game`, който пази текущия въпрос и се грижи за обработката на съобщенията получени от клиента и сървъра. 

### Playboard.by

Съдържа клас `Board` който паси текущото състояние на игралната дъска. Пази информация като: 

- Кой играч е на ход
- Коя територия от кого е завладяна

Класовете `BoardDisplay`и `QuestionDisplay` са помощни класове, използващи библиотеката `tkinter` с цел визуализация на дъската, и обработка на потребителския вход (напр. какъв отговор е даден на някой въпрос, коя територия иска да превземе) 

### Question.py

Клас, представляващ въпрос. Съдържа въпроса, верния отговор и грешните отговори.
Може да извлече въпрос от API по дадени параметри. Може да бъде сериализиран до json. 

## Пакетът `messagingutils`

Пакетът отговаря за комуникацията между клиента и сървъра. Тъй като по време на изпълнение на програмата се използват множество съобщения е нужно те да бъдат форматирани и изпращани по подходящ начин, с цел по-лесната им обработка. Протоколът за комуникация между клиент и сървър е следната:

Всяко съобщение съдържа:

- **Header**
    - Дължина на тялото *(body)*
    - Тип на съобщението, което изразява очакваната реакция и обработка от отсрещната страна. Например:
        - `DISCONNECT`
        - `GET_QUESTION`
        - `CORRECT_ANSWER`
- ********Body (тяло)********
    - речник от обекти в json формат

### Messaging.py

Модулът съдържа класът, отговорен за съобщенията `Message`, имплементира функциите `to_bytes` и `from_bytes` . С цел по-оптимална комуникация между сървъра и клиента, те си комуникират използвайки съобщения в байтов формат, които при получаване декодират до текст, четим от човек. 

### Messageq.py

Модулът съдържа имплементация на структурата от данни опашка - FIFO. Тя работи само с обекти от тип съобщение (`Message`) 

## Сървърът

Сървърът е ядрото на играта. Той трябва да поддържа връзка с множество клиенти, за тази цел използвайки селектор. Стартира се с метода `start` , което го привежда в режим готов за приемане на връзки. В зависимост от дошлата заявка изпълнява една от двете функции:

- `accept_wrapper` - ако заявката е за приемане на входящ сокет
- `service_connection` - ако заявката е за обработка на вече съществуваща връзка.

`accept_wrapper` 

 Когато се приеме нов клиент, той се добавя в базата данни. Към момента всеки играч се идентифицира с порта си. В бъдеще може да се създаде въпрос преди влизане на клиент за име, с което желае да се идентифицира. За всеки клиент се създава опашка от съобщения които трябва да му бъдат изпратени. Пазят се в речник от тип **клиент : опашка.** Когато се включат трима играчи играта стартира. Създава се карта за игра. Тя също може да бъде сериализирана до json, което прави възможно изпращането ѝ до всички клиенти. При всяка промяна на картата, обновената ѝ версия бива изпратена до клиентите. Всеки клиент съдържа обект от тип `BoardDisplay` с помощта, на който визуализира картата. Сървърът изпраща на клиента, с който току що е установил връзка потвърдително съобщеине. 

`service_connection`

В зависимост от маската - текущата връзка е готова за четене или писане се изпълняват две действия:

- Ако е заявка за писане - изпращаме най-старото съобщение в опашката за клиента
- Ако заявката е за четене - прочита съобщението и с помощен метод от класа `Game` подготвя отговор, който трябва да бъде изпратен на клиента.

## Клиентът

При пускане на клиентът се изпълняват две нишки. Едната прочита и отговаря на заявки от сървъра, а другата изпълнява *repl - read-eval-print loop -* прочита команди от потребителя и ги изпраща на сървъра. За момента служи само с цел разработка на софтуера. Втората нишка прочита съобщението, изпратено от сървъра, обработва го по подходящ начин, обновява картата, ако е необходимо и отново чака за съобщение от сървъра. 

## Бъдещо развитие

Проектът е в начален стадий на развитие. Ето и няколко функционалности, които могат да се иплементират в бъдеще: 

- Жокери на въпросите
- Повече паралелни игри
- Добавяне на обратно броене при въпросите
- Подобряване на графиките
- Разбъркване на възможните отговори
- Модифициране на аргументите за стартиране - host, port
    
    

## Как да стартираме проекта

- Изпълнете `sudo apt-get install python3-tk` 
- Изпълнете `python3 main.py` за стартиране на сървъра
- Изпълнете пъти `python3 client.py` за стартиране на клиент (играч)
- След като 3 клиента са стартирали и успешно са се свързали към сървъра - играта започва.

Приятна игра 🎮

## Използвани материали

- [https://realpython.com/python-sockets/#application-client-and-server](https://realpython.com/python-sockets/#application-client-and-server)
