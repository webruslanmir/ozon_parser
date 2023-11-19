# Начните с базового образа Ubuntu
FROM ubuntu:latest

# Обновите пакеты Ubuntu
RUN apt-get update && apt-get upgrade -y

# Установите зависимости для Playwright
RUN apt-get install -y curl python3 python3-pip xvfb unzip libnss3 libasound2 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb-dev

# Установите Playwright
RUN curl -L https://playwright.azureedge.net/sdk/1.14.2/playwright-python.zip -o playwright-python.zip && \
    unzip playwright-python.zip && rm playwright-python.zip && \
    cd playwright-python-1.14.2 && \
    python3 install.py

# Установите зависимости вашего проекта
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Копируйте весь проект внутрь контейнера
COPY . .

# Установите переменные окружения
ENV DISPLAY=:99

# Запустите Xvfb перед запуском вашего приложения
CMD ["bash", "-c", "Xvfb :99 -ac -screen 0 1024x768x24 > /dev/null 2>&1 & python3 ozon_main.py"]
