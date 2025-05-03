import os, json, sys, re, datetime

script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
session_file = os.path.join(script_dir, f"session\\client.session")

def read_config():
    with open(f'{script_dir}\\config.json', 'r') as f:
        data = f.read()
        config = json.loads(data)
    return config

def save_config(config):
    with open(f'{script_dir}\\config.json', 'w') as f:
        data = f.write(json.dumps(config))
        config = json.dumps(data)


def program_over():
    print("\nВыполнение окончено.")
    while True:
        pass


def save_usernames_to_file(usernames, group_name):
    """Сохраняет список юзернеймов в файл с названием группы."""
    safe_group_name = re.sub(r'[<>:"/\\|?*]', '_', group_name)
    filename = f"usernames_{safe_group_name}.txt"
    try:
        with open(f'{script_dir}\\result\\{filename}', "w", encoding="utf-8") as file:
            for username in usernames:
                file.write(f"@{username}\n")
        print(f"Юзернеймы успешно сохранены в файл: {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении юзернеймов в файл: {e}")


class ProgressBar:
    def __init__(self, total, length=40, fill='█', empty='-', prefix=f'{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} Прогресс'):
        """
        :param total: Общее количество шагов
        :param length: Длина прогресс-бара в символах
        :param fill: Символ заполнения
        :param empty: Символ пустого места
        :param prefix: Текст перед прогресс-баром
        :param suffix: Текст после прогресс-бара
        """
        self.total = total
        self.length = length
        self.fill = fill
        self.empty = empty
        self.prefix = prefix
        self.current = 0

    def next(self, string=None):
        """
        Увеличивает прогресс на 1 шаг и обновляет отображение.
        :param string: Дополнительный текст, отображаемый перед прогресс-баром
        """
        self.current += 1
        self._print_bar(string)

    def end(self, string=None):
        """Завершает прогресс-бар."""
        self.current = self.total
        self._print_bar(string)

    def _print_bar(self, string=None):
        percent = self.current / self.total
        filled_length = int(self.length * percent)
        bar = self.fill * filled_length + self.empty * (self.length - filled_length)
        text = f'\r{self.prefix}: |{bar}| {int(percent * 100)}%'
        if string:
            text += f' - {string}'
        sys.stdout.write(text)
        sys.stdout.flush()

        if self.current == self.total:
            print()

    def reset(self):
        """Сбрасывает прогресс."""
        self.current = 0