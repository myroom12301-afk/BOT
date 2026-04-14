# Используем базовый образ с Python
FROM python:3.12

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл requirements.txt
COPY requirements.txt /app/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта из локального контекста сборки в контейнер
COPY . /app/

# Запускаем ваш бот
CMD ["python", "main.py"]