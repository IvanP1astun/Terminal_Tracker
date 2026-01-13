import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class PyMonday:
    def __init__(self, data_file="pymonday_data.json"):
        """Инициализация системы PyMonday"""
        self.data_file = data_file
        self.users = {}
        self.boards = {}
        self.current_user = None
        self.load_data()

    def save_data(self):
        """Сохранение данных в JSON файл"""
        data = {
            "users": self.users,
            "boards": self.boards
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get("users", {})
                    self.boards = data.get("boards", {})
            except:
                print("Ошибка загрузки данных. Начинаем с чистого листа.")

    def register_user(self):
        """Регистрация нового пользователя"""
        print("\n=== РЕГИСТРАЦИЯ ===")
        email = input("Email: ").strip()

        if email in self.users:
            print("Пользователь с таким email уже существует!")
            return

        name = input("Имя: ").strip()
        password = input("Пароль: ").strip()

        self.users[email] = {
            "name": name,
            "password": password,
            "created_at": datetime.now().isoformat()
        }
        self.save_data()
        print(f"Пользователь {name} успешно зарегистрирован!")

    def login(self):
        """Вход в систему"""
        print("\n=== ВХОД ===")
        email = input("Email: ").strip()
        password = input("Пароль: ").strip()

        if email in self.users and self.users[email]["password"] == password:
            self.current_user = email
            print(f"Добро пожаловать, {self.users[email]['name']}!")
            return True
        else:
            print("Неверный email или пароль!")
            return False

    def logout(self):
        """Выход из системы"""
        self.current_user = None
        print("Вы вышли из системы.")

    def create_board(self):
        """Создание новой доски"""
        if not self.current_user:
            print("Сначала войдите в систему!")
            return

        print("\n=== СОЗДАНИЕ ДОСКИ ===")
        board_name = input("Название доски: ").strip()
        board_id = f"board_{len(self.boards) + 1}"

        self.boards[board_id] = {
            "id": board_id,
            "name": board_name,
            "owner": self.current_user,
            "created_at": datetime.now().isoformat(),
            "columns": ["To Do", "In Progress", "Review", "Done"],  # Стандартные колонки
            "items": {},  # Элементы на доске
            "members": [self.current_user]  # Участники доски
        }
        self.save_data()
        print(f"Доска '{board_name}' создана!")

    def list_boards(self):
        """Показать все доски пользователя"""
        if not self.current_user:
            print("Сначала войдите в систему!")
            return

        print("\n=== ВАШИ ДОСКИ ===")
        user_boards = []

        for board_id, board in self.boards.items():
            if self.current_user in board["members"]:
                user_boards.append(board)

        if not user_boards:
            print("У вас нет досок. Создайте первую!")
            return

        for i, board in enumerate(user_boards, 1):
            items_count = len(board["items"])
            print(f"{i}. {board['name']} (ID: {board['id']})")
            print(f"   Элементов: {items_count}, Участников: {len(board['members'])}")
            print(f"   Создана: {board['created_at'][:10]}")

    def add_item_to_board(self):
        """Добавление элемента на доску"""
        if not self.current_user:
            print("Сначала войдите в систему!")
            return

        self.list_boards()
        board_num = input("\nВыберите номер доски: ").strip()

        user_boards = [b for b in self.boards.values() 
                      if self.current_user in b["members"]]

        try:
            board_index = int(board_num) - 1
            if 0 <= board_index < len(user_boards):
                board = user_boards[board_index]
                board_id = board["id"]

                print(f"\nДобавление элемента в доску '{board['name']}'")
                item_name = input("Название элемента: ").strip()
                item_desc = input("Описание: ").strip()

                print("Доступные колонки:")
                for i, col in enumerate(board["columns"], 1):
                    print(f"{i}. {col}")

                col_choice = input("Выберите колонку (номер): ").strip()

                try:
                    col_index = int(col_choice) - 1
                    if 0 <= col_index < len(board["columns"]):
                        status = board["columns"][col_index]
                        item_id = f"item_{len(board['items']) + 1}"

                        board["items"][item_id] = {
                            "id": item_id,
                            "name": item_name,
                            "description": item_desc,
                            "status": status,
                            "created_by": self.current_user,
                            "created_at": datetime.now().isoformat(),
                            "assigned_to": self.current_user,
                            "comments": []
                        }
                        self.save_data()
                        print(f"Элемент '{item_name}' добавлен в колонку '{status}'!")
                    else:
                        print("Неверный номер колонки!")
                except ValueError:
                    print("Введите номер колонки!")
            else:
                print("Неверный номер доски!")
        except ValueError:
            print("Введите номер!")

    def view_board(self):
        """Просмотр содержимого доски"""
        if not self.current_user:
            print("Сначала войдите в систему!")
            return

        self.list_boards()
        board_num = input("\nВыберите номер доски для просмотра: ").strip()

        user_boards = [b for b in self.boards.values() 
                      if self.current_user in b["members"]]

        try:
            board_index = int(board_num) - 1
            if 0 <= board_index < len(user_boards):
                board = user_boards[board_index]

                print(f"\n=== ДОСКА: {board['name']} ===")
                print(f"Владелец: {self.users[board['owner']]['name']}")
                print(f"Участники: {', '.join([self.users[m]['name'] for m in board['members']])}")

                # Группируем элементы по колонкам
                items_by_column = {col: [] for col in board["columns"]}

                for item_id, item in board["items"].items():
                    items_by_column[item["status"]].append(item)

                # Выводим колонки с элементами
                for column in board["columns"]:
                    print(f"\n--- {column} ---")
                    items = items_by_column[column]

                    if not items:
                        print("  (пусто)")
                    else:
                        for item in items:
                            assigned_name = self.users[item["assigned_to"]]["name"]
                            print(f"  • {item['name']}")
                            print(f"    ID: {item['id']}, Назначено: {assigned_name}")
                            if item["description"]:
                                print(f"    Описание: {item['description'][:50]}...")
                            print(f"    Создано: {item['created_at'][:10]}")

                # Меню действий с доской
                while True:
                    print("\nДействия с доской:")
                    print("1. Добавить элемент")
                    print("2. Переместить элемент")
                    print("3. Добавить комментарий")
                    print("4. Вернуться в главное меню")

                    action = input("Выберите действие: ").strip()

                    if action == "1":
                        self._add_item_to_specific_board(board["id"])
                    elif action == "2":
                        self._move_item(board["id"])
                    elif action == "3":
                        self._add_comment(board["id"])
                    elif action == "4":
                        break
                    else:
                        print("Неверный выбор!")
        except ValueError:
            print("Введите номер!")

    def _add_item_to_specific_board(self, board_id):
        """Добавить элемент в конкретную доску"""
        board = self.boards[board_id]

        print(f"\nДобавление элемента в доску '{board['name']}'")
        item_name = input("Название элемента: ").strip()
        item_desc = input("Описание: ").strip()

        print("Доступные колонки:")
        for i, col in enumerate(board["columns"], 1):
            print(f"{i}. {col}")

        col_choice = input("Выберите колонку (номер): ").strip()

        try:
            col_index = int(col_choice) - 1
            if 0 <= col_index < len(board["columns"]):
                status = board["columns"][col_index]
                item_id = f"item_{len(board['items']) + 1}"

                board["items"][item_id] = {
                    "id": item_id,
                    "name": item_name,
                    "description": item_desc,
                    "status": status,
                    "created_by": self.current_user,
                    "created_at": datetime.now().isoformat(),
                    "assigned_to": self.current_user,
                    "comments": []
                }
                self.save_data()
                print(f"Элемент '{item_name}' добавлен в колонку '{status}'!")
            else:
                print("Неверный номер колонки!")
        except ValueError:
            print("Введите номер колонки!")

    def _move_item(self, board_id):
        """Переместить элемент между колонками"""
        board = self.boards[board_id]

        if not board["items"]:
            print("На доске нет элементов!")
            return

        print("\nДоступные элементы:")
        items_list = list(board["items"].values())
        for i, item in enumerate(items_list, 1):
            print(f"{i}. {item['name']} (текущий статус: {item['status']})")

        try:
            item_choice = int(input("Выберите элемент (номер): ").strip()) - 1
            if 0 <= item_choice < len(items_list):
                item_id = items_list[item_choice]["id"]

                print("\nДоступные колонки:")
                for i, col in enumerate(board["columns"], 1):
                    print(f"{i}. {col}")

                col_choice = int(input("Выберите новую колонку (номер): ").strip()) - 1

                if 0 <= col_choice < len(board["columns"]):
                    new_status = board["columns"][col_choice]
                    board["items"][item_id]["status"] = new_status
                    self.save_data()
                    print(f"Элемент перемещен в колонку '{new_status}'!")
                else:
                    print("Неверный номер колонки!")
            else:
                print("Неверный номер элемента!")
        except ValueError:
            print("Введите номер!")

    def _add_comment(self, board_id):
        """Добавить комментарий к элементу"""
        board = self.boards[board_id]

        if not board["items"]:
            print("На доске нет элементов!")
            return

        print("\nДоступные элементы:")
        items_list = list(board["items"].values())
        for i, item in enumerate(items_list, 1):
            print(f"{i}. {item['name']}")

        try:
            item_choice = int(input("Выберите элемент (номер): ").strip()) - 1
            if 0 <= item_choice < len(items_list):
                item_id = items_list[item_choice]["id"]
                comment_text = input("Введите комментарий: ").strip()

                comment = {
                    "text": comment_text,
                    "author": self.current_user,
                    "created_at": datetime.now().isoformat()
                }

                board["items"][item_id]["comments"].append(comment)
                self.save_data()
                print("Комментарий добавлен!")
            else:
                print("Неверный номер элемента!")
        except ValueError:
            print("Введите номер!")

    def search_items(self):
        """Поиск элементов по названию"""
        if not self.current_user:
            print("Сначала войдите в систему!")
            return

        search_term = input("Введите текст для поиска: ").strip().lower()
        found_items = []

        for board_id, board in self.boards.items():
            if self.current_user in board["members"]:
                for item_id, item in board["items"].items():
                    if search_term in item["name"].lower() or search_term in item["description"].lower():
                        found_items.append({
                            "board": board["name"],
                            "item": item
                        })

        print(f"\n=== РЕЗУЛЬТАТЫ ПОИСКА: '{search_term}' ===")
        if found_items:
            for result in found_items:
                item = result["item"]
                print(f"Доска: {result['board']}")
                print(f"Элемент: {item['name']}")
                print(f"Статус: {item['status']}")
                print(f"Описание: {item['description'][:100]}...")
                print("-" * 40)
        else:
            print("Ничего не найдено.")

    def dashboard(self):
        """Панель управления с общей статистикой"""
        if not self.current_user:
            print("Сначала войдите в систему!")
            return

        print("\n=== ПАНЕЛЬ УПРАВЛЕНИЯ ===")

        # Статистика
        user_boards = [b for b in self.boards.values() 
                      if self.current_user in b["members"]]

        total_items = 0
        items_by_status = {}

        for board in user_boards:
            total_items += len(board["items"])
            for item in board["items"].values():
                status = item["status"]
                items_by_status[status] = items_by_status.get(status, 0) + 1

        print(f"Количество досок: {len(user_boards)}")
        print(f"Всего элементов: {total_items}")
        print("\nЭлементы по статусам:")
        for status, count in items_by_status.items():
            print(f"  {status}: {count}")

        # Недавние элементы
        print("\n=== ПОСЛЕДНИЕ ЭЛЕМЕНТЫ ===")
        all_items = []

        for board in user_boards:
            for item in board["items"].values():
                all_items.append({
                    "board": board["name"],
                    "item": item
                })

        # Сортируем по дате создания
        all_items.sort(key=lambda x: x["item"]["created_at"], reverse=True)

        for i, entry in enumerate(all_items[:5], 1):
            item = entry["item"]
            print(f"{i}. {item['name']} (Доска: {entry['board']})")
            print(f"   Статус: {item['status']}, Создано: {item['created_at'][:10]}")

    def main_menu(self):
        """Главное меню системы"""
        while True:
            print("\n" + "="*50)
            print("PYMONDAY - Система управления задачами")
            print("="*50)

            if self.current_user:
                user_name = self.users[self.current_user]["name"]
                print(f"Вы вошли как: {user_name}")
                print("\nГлавное меню:")
                print("1. Просмотреть все доски")
                print("2. Создать новую доску")
                print("3. Просмотреть доску")
                print("4. Поиск элементов")
                print("5. Панель управления (Dashboard)")
                print("6. Выйти из системы")
                print("0. Выход из программы")
            else:
                print("\n1. Вход в систему")
                print("2. Регистрация")
                print("0. Выход")

            choice = input("\nВыберите действие: ").strip()

            if not self.current_user:
                # Меню для неавторизованного пользователя
                if choice == "1":
                    if self.login():
                        continue
                elif choice == "2":
                    self.register_user()
                elif choice == "0":
                    print("До свидания!")
                    break
                else:
                    print("Неверный выбор!")

            else:
                # Меню для авторизованного пользователя
                if choice == "1":
                    self.list_boards()
                elif choice == "2":
                    self.create_board()
                elif choice == "3":
                    self.view_board()
                elif choice == "4":
                    self.search_items()
                elif choice == "5":
                    self.dashboard()
                elif choice == "6":
                    self.logout()
                elif choice == "0":
                    print("До свидания!")
                    break
                else:
                    print("Неверный выбор!")


def main():
    """Основная функция запуска программы"""
    app = PyMonday()

    # Создадим тестовые данные, если система пустая
    if not app.users and not app.boards:
        print("Добро пожаловать в PyMonday!")
        print("Похоже, это ваш первый запуск.")
        print("Давайте создадим тестовые данные для демонстрации...")

        # Создаем тестового пользователя
        test_email = "demo@example.com"
        app.users[test_email] = {
            "name": "Демо Пользователь",
            "password": "demo123",
            "created_at": datetime.now().isoformat()
        }

        # Создаем тестовую доску
        board_id = "board_1"
        app.boards[board_id] = {
            "id": board_id,
            "name": "Мой первый проект",
            "owner": test_email,
            "created_at": datetime.now().isoformat(),
            "columns": ["To Do", "In Progress", "Review", "Done"],
            "items": {
                "item_1": {
                    "id": "item_1",
                    "name": "Изучить Python",
                    "description": "Пройти курс по основам Python",
                    "status": "In Progress",
                    "created_by": test_email,
                    "created_at": datetime.now().isoformat(),
                    "assigned_to": test_email,
                    "comments": [
                        {
                            "text": "Начал изучение!",
                            "author": test_email,
                            "created_at": datetime.now().isoformat()
                        }
                    ]
                },
                "item_2": {
                    "id": "item_2",
                    "name": "Создать проект",
                    "description": "Разработать консольное приложение",
                    "status": "To Do",
                    "created_by": test_email,
                    "created_at": datetime.now().isoformat(),
                    "assigned_to": test_email,
                    "comments": []
                }
            },
            "members": [test_email]
        }

        app.save_data()
        print("\nТестовые данные созданы!")
        print("Вы можете войти с email: demo@example.com, пароль: demo123")

    # Запускаем главное меню
    app.main_menu()


if __name__ == "__main__":
    main()
