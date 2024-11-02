from datetime import datetime


def hello_user():
    """ Функция формирует приветствие в зависимости от текущего времени суток """
    current_time = datetime.now().strftime("%H:%M:%S")

    if "06:00:00" <= current_time <= "11:59:59":
        return "Доброе утро!"
    elif "12:00:00" <= current_time <= "17:59:59":
        return "Добрый день!"
    elif "18:00:00" <= current_time <= "20:59:59":
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


if __name__ == "__main__":
    print(hello_user())
