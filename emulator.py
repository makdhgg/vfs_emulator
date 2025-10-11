import tkinter as tk
from tkinter import scrolledtext, Entry, Button, Frame
import os
import socket


class VFSEmulator:
    def __init__(self, root):
        self.root = root
        self.command_history = []
        self.current_directory = "/"
        self.setup_gui()

    def setup_gui(self):
        # Заголовок окна с именем VFS
        self.root.title("VFS - Virtual File System")
        self.root.geometry("800x600")

        # Основная область вывода
        self.output_area = scrolledtext.ScrolledText(
            self.root,
            height=20,
            width=80,
            bg='black',
            fg='white',
            font=('Courier New', 12)
        )
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.output_area.config(state=tk.DISABLED)

        # Фрейм для ввода команды
        input_frame = Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)

        # Метка приглашения к вводу
        username = os.getlogin()
        hostname = socket.gethostname()
        self.prompt_label = tk.Label(
            input_frame,
            text=f"{username}@{hostname}:~$ ",
            bg='black',
            fg='green',
            font=('Courier New', 12)
        )
        self.prompt_label.pack(side=tk.LEFT)

        # Поле ввода команды
        self.command_entry = Entry(
            input_frame,
            bg='black',
            fg='white',
            font=('Courier New', 12),
            insertbackground='white'
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind('<Return>', self.execute_command)
        self.command_entry.focus()

        # Кнопка выполнения
        execute_button = Button(
            input_frame,
            text="Выполнить",
            command=self.execute_command,
            font=('Courier New', 10)
        )
        execute_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Вывод начального сообщения
        self.print_output("Добро пожаловать в VFS - Virtual File System")
        self.print_output("Доступные команды: ls, cd, exit")
        self.print_output("Для справки введите: help")
        self.print_output("")

    def print_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def expand_environment_variables(self, arg):
        """Раскрывает переменные окружения в аргументе"""
        if arg.startswith('$'):
            env_var = arg[1:]
            env_value = os.getenv(env_var)
            if env_value is not None:
                return env_value
            else:
                raise ValueError(f"Переменная окружения '{env_var}' не найдена")
        return arg

    def parse_command(self, command_input):
        """Парсер команд с поддержкой раскрытия переменных окружения"""
        try:
            parts = command_input.strip().split()
            if not parts:
                return "", []

            command = parts[0]
            args = parts[1:]

            # Раскрываем переменные окружения в аргументах
            processed_args = []
            for arg in args:
                # Обрабатываем аргументы, которые могут содержать $VAR
                expanded_arg = ""
                i = 0
                while i < len(arg):
                    if arg[i] == '$' and (i == 0 or arg[i - 1] != '\\'):
                        # Нашли начало переменной
                        j = i + 1
                        while j < len(arg) and (arg[j].isalnum() or arg[j] == '_'):
                            j += 1
                        var_name = arg[i + 1:j]
                        var_value = os.getenv(var_name)
                        if var_value is not None:
                            expanded_arg += var_value
                        else:
                            # Если переменная не найдена, оставляем как есть
                            expanded_arg += arg[i:j]
                        i = j
                    else:
                        if arg[i] == '\\' and i + 1 < len(arg) and arg[i + 1] == '$':
                            # Экранированный $
                            expanded_arg += '$'
                            i += 2
                        else:
                            expanded_arg += arg[i]
                            i += 1

                processed_args.append(expanded_arg)

            return command, processed_args

        except Exception as e:
            self.print_output(f"Ошибка парсера: {e}")
            return "", []

    def execute_command(self, event=None):
        command_input = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)

        if not command_input:
            return

        # Выводим введенную команду
        username = os.getlogin()
        hostname = socket.gethostname()
        self.print_output(f"{username}@{hostname}:~$ {command_input}")

        # Парсим команду
        command, args = self.parse_command(command_input)

        # Обрабатываем команды
        if command == "exit":
            self.root.quit()

        elif command == "ls":
            # Команда-заглушка ls
            self.print_output(f"ls: вывод содержимого директории '{self.current_directory}'")
            if args:
                self.print_output(f"Аргументы: {' '.join(args)}")
            self.print_output("file1.txt  file2.txt  directory/  document.pdf")

        elif command == "cd":
            # Команда-заглушка cd
            if len(args) == 0:
                self.print_output("cd: ошибка - не указана целевая директория")
                self.print_output("Использование: cd <директория>")
            elif len(args) > 1:
                self.print_output("cd: ошибка - слишком много аргументов")
                self.print_output("Использование: cd <директория>")
            else:
                target_dir = args[0]
                self.print_output(f"cd: смена директории на '{target_dir}'")
                self.current_directory = target_dir
                self.print_output(f"Текущая директория: {self.current_directory}")

        elif command == "help":
            self.print_output("Доступные команды:")
            self.print_output("  ls - вывод содержимого директории (заглушка)")
            self.print_output("  cd <директория> - смена директории (заглушка)")
            self.print_output("  exit - выход из VFS")
            self.print_output("  help - эта справка")
            self.print_output("")
            self.print_output("Поддерживается раскрытие переменных окружения:")
            self.print_output("  cd $HOME/documents  # Перейдет в /home/user/documents")

        elif command:
            self.print_output(f"Ошибка: неизвестная команда '{command}'")
            self.print_output("Введите 'help' для списка команд")

        self.print_output("")


def main():
    print("VFS - Virtual File System")
    print("Этап 1: REPL прототип")
    root = tk.Tk()
    app = VFSEmulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()