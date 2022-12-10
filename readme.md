# Парсер уровней сигнала для модема Vodafone k5161h

Сценарий python считывает данные и строит графики уровней **RSRP**, **RSRQ**, **SINR** и **RSSI** с указанием номера базовой станции.

## Варианты
**lte_api.py** - Получение данных через API и отображение графиков через сохранение изображений.  
**lte_api_draw.py** - Получение данных через API и отображение графиков в окне.  
**lte_chrome.py** - Получение данных через парсинг страницы и отображение графиков через сохранение изображений.

## Установка на примере Ubuntu

1. Создайте и перейдите в каталог, например **lte**  
`mkdir lte`  
`cd lte`

2. Скопируйте в созданный каталог файлы из репозитория

3. Установите **chromium** для варианта **lte_chrome.py**  
`sudo apt install chromium`

4. Установите **python3-pip** и **python3-venv**  
`sudo apt install python3-pip python3-venv`

5. Создайте и активируйте окружение, например **python_env**  
`python3 -m venv python_env`  
`source python_env/bin/activate`

6. Установите библиотеку **matplotlib**  
`pip install matplotlib`

7. Установите библиотеку **selenium** для варианта **lte_chrome.py**  
`pip install selenium`

8. Проверьте параметры в начале файла **lte.py**  

## Запуск

Запустите сценарий **lte.py**  
`python3 lte.py`  

Для запуска сценария без активации окружения  
`python_env/bin/python3 lte.py`

В каталоге появится файл **png** с именем, содержащим время запуска сценария.  
Файл будет обновляться автоматически после каждого считывания данных.  

## Примечание

[Описание характеристик сигнала](https://wiki.teltonika-networks.com/view/Mobile_Signal_Strength_Recommendations)
[API](https://www.lewuathe.com/querying-huawei-4g-router-to-get-the-devices.html)

## Пример

<img src="https://github.com/demonlibra/Vodafone-k5161h_Signal/blob/main/example_1.png" width="400"> <img src="https://github.com/demonlibra/Vodafone-k5161h_Signal/blob/main/example_2.png" width="400">