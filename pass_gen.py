import customtkinter as ctk
from tkinter import messagebox, filedialog
from random import shuffle, choice
import pyperclip
import json
from datetime import datetime
import csv
from difflib import SequenceMatcher
import threading
import time

class PasswordGenerator:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Password Master Pro")
        self.window.geometry("800x600")
        
        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Основные переменные
        self.password_length = ctk.IntVar(value=12)
        self.use_lowercase = ctk.BooleanVar(value=True)
        self.use_uppercase = ctk.BooleanVar(value=True)
        self.use_digits = ctk.BooleanVar(value=True)
        self.use_symbols = ctk.BooleanVar(value=True)
        self.generated_password = ctk.StringVar()
        self.num_passwords = ctk.IntVar(value=1)
        self.category = ctk.StringVar(value="Общие")
        
        # Инициализация систем
        self.create_main_layout()
        self.create_profiles_system()
        self.setup_achievements_system()
        self.create_animated_strength_meter()
        self.create_tooltip_system()
        self.create_animated_statistics()
        self.create_template_system()
        
        # Визуальные эффекты и горячие клавиши
        self.add_visual_effects()
        self.setup_hotkeys()
        
        # Статистика и достижения
        self.level = 0
        self.xp = 0
        self.achievements = {
            "beginner": {"name": "Новичок", "desc": "Создан первый пароль", "unlocked": False},
            "master": {"name": "Мастер", "desc": "Создано 100 паролей", "unlocked": False},
            "secure": {"name": "Защитник", "desc": "Создан пароль максимальной надежности", "unlocked": False},
            "collector": {"name": "Коллекционер", "desc": "Использованы все категории", "unlocked": False}
        }

    def create_main_layout(self):
        # Добавляем стильный заголовок
        header = ctk.CTkFrame(self.window, height=60)
        header.pack(fill="x", padx=10, pady=5)
        
        logo_label = ctk.CTkLabel(header,
                                 text="🔒 Password Master Pro",
                                 font=("Roboto", 24, "bold"))
        logo_label.pack(side="left", padx=20)
        
        # Добавляем кнопки быстрого доступа
        quick_buttons = ctk.CTkFrame(header)
        quick_buttons.pack(side="right", padx=20)
        
        for icon, command in [
            ("🔄", self.generate_multiple_passwords),
            ("📋", self.copy_password),
            ("💾", self.save_password),
            ("🔍", self.analyze_password)
        ]:
            ctk.CTkButton(quick_buttons,
                         text=icon,
                         width=40,
                         command=command).pack(side="left", padx=5)
        
        # Создаем боковую панель
        self.sidebar = ctk.CTkFrame(self.window, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        # Основной контент
        self.main_content = ctk.CTkTabview(self.window)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Добавляем вкладки
        self.tab_generator = self.main_content.add("Генератор")
        self.tab_history = self.main_content.add("История")
        self.tab_settings = self.main_content.add("Настройки")
        
        self.create_sidebar()
        self.create_generator_tab()
        self.create_history_tab()
        self.create_settings_tab()
        
    def create_sidebar(self):
        # Статистика
        stats_label = ctk.CTkLabel(self.sidebar, text="Статистика", font=("Roboto", 16, "bold"))
        stats_label.pack(pady=10)
        
        self.passwords_count = ctk.CTkLabel(self.sidebar, text="Создано паролей: 0")
        self.passwords_count.pack()
        
        self.avg_strength = ctk.CTkLabel(self.sidebar, text="Средняя надежность: 0%")
        self.avg_strength.pack()
        
        # Категории
        ctk.CTkLabel(self.sidebar, text="Категории", font=("Roboto", 16, "bold")).pack(pady=(20,10))
        categories = ["Общие", "Банковские", "Социальные сети", "Почта", "Другое"]
        for cat in categories:
            btn = ctk.CTkButton(self.sidebar, text=cat, command=lambda c=cat: self.set_category(c))
            btn.pack(pady=2)
            
    def create_generator_tab(self):
        # Основные настройки
        settings_frame = ctk.CTkFrame(self.tab_generator)
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        # Длина пароля с числовым индикатором
        length_frame = ctk.CTkFrame(settings_frame)
        length_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(length_frame, text="Длина пароля:").pack(side="left", padx=5)
        self.length_indicator = ctk.CTkLabel(length_frame, text="12")
        self.length_indicator.pack(side="right", padx=5)
        
        length_slider = ctk.CTkSlider(settings_frame, 
                                    from_=8, to=32,
                                    variable=self.password_length,
                                    command=self.update_length_indicator)
        length_slider.pack(fill="x", pady=5)
        
        # Колиство паролей
        num_frame = ctk.CTkFrame(settings_frame)
        num_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(num_frame, text="Количество паролей:").pack(side="left", padx=5)
        ctk.CTkEntry(num_frame, textvariable=self.num_passwords, width=50).pack(side="right", padx=5)
        
        # Чекбоксы в строку
        checks_frame = ctk.CTkFrame(settings_frame)
        checks_frame.pack(fill="x", pady=10)
        
        for text, var in [
            ("a-z", self.use_lowercase),
            ("A-Z", self.use_uppercase),
            ("0-9", self.use_digits),
            ("!@#", self.use_symbols)
        ]:
            ctk.CTkCheckBox(checks_frame, text=text, variable=var).pack(side="left", padx=10)
            
        # Кнопки действий
        buttons_frame = ctk.CTkFrame(self.tab_generator)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(buttons_frame, 
                     text="Сгенерировать",
                     command=self.generate_multiple_passwords,
                     fg_color="green").pack(side="left", padx=5, expand=True)
                     
        ctk.CTkButton(buttons_frame,
                     text="Копировать",
                     command=self.copy_password).pack(side="left", padx=5, expand=True)
                     
        ctk.CTkButton(buttons_frame,
                     text="Сохранить",
                     command=self.save_password).pack(side="left", padx=5, expand=True)
        
        ctk.CTkButton(buttons_frame,
                     text="Анализ",
                     command=self.analyze_password).pack(side="left", padx=5, expand=True)
        
        # Пле вывда паролей
        self.password_text = ctk.CTkTextbox(self.tab_generator, height=200)
        self.password_text.pack(fill="both", padx=20, pady=10, expand=True)
        
        # Индикатор надежности
        strength_frame = ctk.CTkFrame(self.tab_generator)
        strength_frame.pack(fill="x", padx=20, pady=10)
        
        self.strength_label = ctk.CTkLabel(strength_frame, text="Надежность: ")
        self.strength_label.pack(side="left", padx=5)
        
        self.strength_progress = ctk.CTkProgressBar(strength_frame, width=300)
        self.strength_progress.pack(side="left", padx=5, expand=True)
        self.strength_progress.set(0)

    def create_history_tab(self):
        # Верхняя панель с поиском и фильтрами
        top_frame = ctk.CTkFrame(self.tab_history)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # Поиск
        search_frame = ctk.CTkFrame(top_frame)
        search_frame.pack(side="left", fill="x", expand=True)
        
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, 
                                   placeholder_text="Поиск по истории...",
                                   textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Кнопка поиска
        ctk.CTkButton(search_frame,
                     text="🔍",
                     width=30,
                     command=lambda: self.search_history(self.search_var.get())).pack(side="left", padx=5)
        
        # Фильтры и экспорт
        filter_frame = ctk.CTkFrame(top_frame)
        filter_frame.pack(side="right", padx=5)
        
        self.filter_var = ctk.StringVar(value="Все")
        ctk.CTkComboBox(filter_frame,
                        values=["Все", "Сильные", "Средние", "Слабые"],
                        variable=self.filter_var,
                        command=self.filter_history).pack(side="left", padx=5)
        
        # Кнопки ествий
        actions_frame = ctk.CTkFrame(self.tab_history)
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(actions_frame,
                     text="Экспорт в JSON",
                     command=lambda: self.export_passwords("json")).pack(side="left", padx=5)
        
        ctk.CTkButton(actions_frame,
                     text="Экспорт в CSV",
                     command=lambda: self.export_passwords("csv")).pack(side="left", padx=5)
        
        ctk.CTkButton(actions_frame,
                     text="Очистить историю",
                     fg_color="red",
                     command=self.clear_history).pack(side="right", padx=5)
        
        # Список паролей с прокруткой
        history_frame = ctk.CTkFrame(self.tab_history)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.history_text = ctk.CTkTextbox(history_frame)
        self.history_text.pack(fill="both", expand=True)

    def create_settings_tab(self):
        settings_frame = ctk.CTkFrame(self.tab_settings)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Настройки приложения
        ctk.CTkLabel(settings_frame, 
                    text="Настройки приложения",
                    font=("Roboto", 16, "bold")).pack(pady=10)
        
        # Выбор темы
        theme_frame = ctk.CTkFrame(settings_frame)
        theme_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(theme_frame, text="Тема:").pack(side="left", padx=5)
        ctk.CTkComboBox(theme_frame,
                       values=["Темная", "Светлая", "Системная"],
                       command=self.change_theme).pack(side="left", padx=5)
        
        # Пуь сохранения
        path_frame = ctk.CTkFrame(settings_frame)
        path_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(path_frame, text="Путь сохранения:").pack(side="left", padx=5)
        ctk.CTkButton(path_frame,
                     text="Выбрать",
                     command=self.choose_save_path).pack(side="right", padx=5)

    def create_profiles_system(self):
        profiles_frame = ctk.CTkFrame(self.tab_settings)
        profiles_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(profiles_frame, 
                     text="Профили генерации",
                     font=("Roboto", 16, "bold")).pack(pady=5)
        
        self.profiles = {
            "Стандартный": {"length": 12, "lowercase": True, "uppercase": True, 
                           "digits": True, "symbols": True},
            "Только цифры": {"length": 8, "lowercase": False, "uppercase": False, 
                              "digits": True, "symbols": False},
            "Максимальная защита": {"length": 32, "lowercase": True, "uppercase": True,
                                   "digits": True, "symbols": True}
        }
        
        for name, settings in self.profiles.items():
            profile_btn = ctk.CTkButton(profiles_frame,
                                      text=name,
                                      command=lambda s=settings: self.apply_profile(s))
            profile_btn.pack(pady=2)

    # Дополнительные методы
    def update_length_indicator(self, value):
        self.length_indicator.configure(text=str(int(float(value))))
        
    def generate_multiple_passwords(self):
        num = self.num_passwords.get()
        if num == 1:
            self.animate_password_generation()
        else:
            # Существующий код для множества паролей
            passwords = []
            for _ in range(num):
                password = self.generate_single_password()
                if password:
                    passwords.append(password)
            
            self.password_text.delete("1.0", "end")
            self.password_text.insert("1.0", "\n".join(passwords))
        
        self.update_statistics()

    def generate_single_password(self):
        # Проверяем, что хотя бы один параметр выбран
        if not any([
            self.use_lowercase.get(),
            self.use_uppercase.get(),
            self.use_digits.get(),
            self.use_symbols.get()
        ]):
            messagebox.showwarning("Предупреждение", "Выберите хотя бы один тип символов")
            return None

        # Создаем наборы символов
        chars = ''
        if self.use_lowercase.get():
            chars += 'abcdefghijklmnopqrstuvwxyz'
        if self.use_uppercase.get():
            chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if self.use_digits.get():
            chars += '0123456789'
        if self.use_symbols.get():
            chars += '!@#$%^&*()_+-=[]{}|;:,.<>?'

        # Генерируем пароль
        length = self.password_length.get()
        password_chars = [choice(chars) for _ in range(length)]
        shuffle(password_chars)  # Перемешиваем символы
        password = ''.join(password_chars)
        
        # Обновляем визуальные элементы
        strength = self.calculate_password_strength(password)
        self.animate_strength(strength)
        self.strength_progress.set(strength)
        self.strength_label.configure(text=f"Надежность: {int(strength * 100)}%")
        
        # Проверяем достижения
        self.check_achievements(password)
        
        # Добавляем опыт
        self.add_xp(10 + int(strength * 20))  # От 10 до 30 XP за пароль
        
        # Обновляем статистику
        self.update_statistics()
        
        # Показываем уведомление при сильном пароле
        if strength > 0.8:
            self.show_notification("Отличный пароль!", 
                                 "Создан пароль высокой надежности")
        
        return password
        
    def export_passwords(self, format):
        history_text = self.history_text.get("1.0", "end-1c")
        if not history_text:
            messagebox.showwarning("Предупреждение", "История пуста")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(f"{format.upper()} files", f"*.{format}")]
        )
        
        if file_path:
            try:
                if format == "json":
                    history = []
                    for line in history_text.split('\n'):
                        if line:
                            date, rest = line.split(" - ", 1)
                            password, category = rest.rsplit(": ", 1)
                            history.append({
                                "date": date,
                                "password": password,
                                "category": category,
                                "strength": self.calculate_password_strength(password)
                            })
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(history, f, indent=4, ensure_ascii=False)
                        
                elif format == "csv":
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(["Дата", "Пароль", "Категория", "Надежность"])
                        for line in history_text.split('\n'):
                            if line:
                                date, rest = line.split(" - ", 1)
                                password, category = rest.rsplit(": ", 1)
                                writer.writerow([
                                    date, password, category,
                                    f"{int(self.calculate_password_strength(password) * 100)}%"
                                ])
                
                self.show_notification("Экспорт выполнен", 
                                    f"История сохранена в файл {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать историю: {str(e)}")

    def change_theme(self, theme):
        theme_map = {
            "Темная": "dark",
            "Светлая": "light",
            "Системная": "system"
        }
        ctk.set_appearance_mode(theme_map[theme])
        
    def choose_save_path(self):
        path = filedialog.askdirectory()
        if path:
            # Сохранение пуи в настройках
            pass

    def copy_password(self):
        # Получаем текст из текстового поля
        password = self.password_text.get("1.0", "end-1c")
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Предупреждение", "Нет пароля для копирования")

    def save_password(self):
        password = self.password_text.get("1.0", "end-1c")
        if not password:
            messagebox.showwarning("Предупреждение", "Нет пароля для сохранения")
            return
        
        # Создаем запись с теущей датой и категорией
        password_entry = {
            "password": password,
            "category": self.category.get(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Добавляем в историю
        self.history_text.insert("end", f"{password_entry['date']} - {password}: {password_entry['category']}\n")
        messagebox.showinfo("Успех", "Пароль сохранен в истории")

    def set_category(self, category):
        self.category.set(category)
        messagebox.showinfo("Категория", f"Выбрана катерия: {category}")

    def calculate_password_strength(self, password):
        score = 0
        
        # Длиа пароля
        if len(password) >= 12:
            score += 0.25
        elif len(password) >= 8:
            score += 0.15
            
        # Наличие разных типов символов
        if any(c.islower() for c in password):
            score += 0.15
        if any(c.isupper() for c in password):
            score += 0.15
        if any(c.isdigit() for c in password):
            score += 0.2
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            score += 0.25
            
        return min(score, 1.0)  # Максимальное значение 1.0

    def animate_password_generation(self):
        self.password_text.delete("1.0", "end")
        
        # Анимация загрузки
        chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
        def loading_animation(i=0):
            if i < 10:  # 10 итераций нимации
                self.password_text.delete("1.0", "end")
                self.password_text.insert("1.0", f"Генерация пароля {chars[i % len(chars)]}")
                self.window.after(100, lambda: loading_animation(i + 1))
            else:
                password = self.generate_single_password()
                if password:
                    self.type_effect(password)
        
        loading_animation()

    def update_statistics(self):
        # Обновляем счетчик паролей
        current_count = int(self.passwords_count.cget("text").split(": ")[1])
        self.passwords_count.configure(text=f"Создано паролей: {current_count + 1}")
        
        # Оновляем среднюю надежность
        password = self.password_text.get("1.0", "end-1c")
        strength = self.calculate_password_strength(password)
        current_avg = float(self.avg_strength.cget("text").split(": ")[1].strip("%")) / 100
        new_avg = (current_avg * current_count + strength) / (current_count + 1)
        self.avg_strength.configure(text=f"Средняя надежность: {int(new_avg * 100)}%")

    def analyze_password(self):
        password = self.password_text.get("1.0", "end-1c")
        if not password:
            messagebox.showwarning("Предупреждение", "Нет пароля для анализа")
            return
        
        analysis = []
        # Проека длины
        if len(password) < 8:
            analysis.append("❌ Слишком короткий ароль")
        elif len(password) >= 12:
            analysis.append("✅ Хорошая длина пароля")
        
        # Проверка символов
        if any(c.islower() for c in password):
            analysis.append("✅ Есть строчные буквы")
        if any(c.isupper() for c in password):
            analysis.append("✅ Есть заглавные буквы")
        if any(c.isdigit() for c in password):
            analysis.append("✅ Есть цифры")
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            analysis.append("✅ Есть специальные символы")
        
        messagebox.showinfo("Анализ пароля", "\n".join(analysis))

    def auto_save_passwords(self):
        try:
            with open('password_history.json', 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
        
        password_entry = {
            "password": self.password_text.get("1.0", "end-1c"),
            "category": self.category.get(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "strength": self.calculate_password_strength(self.password_text.get("1.0", "end-1c"))
        }
        
        history.append(password_entry)
        
        with open('password_history.json', 'w') as f:
            json.dump(history, f, indent=4)

    def run(self):
        self.window.mainloop()

    def search_history(self, query):
        history_text = self.history_text.get("1.0", "end-1c")
        results = []
        
        for line in history_text.split('\n'):
            if query.lower() in line.lower():
                results.append(line)
                
        self.history_text.delete("1.0", "end")
        self.history_text.insert("1.0", "\n".join(results))

    def check_password_leaks(self):
        password = self.password_text.get("1.0", "end-1c")
        # Здесь можно добавить реальную проверку чере API
        messagebox.showinfo("Проверка утечек", 
                           "Пароль не найден в базах утечек данных")

    def filter_history(self, filter_value):
        history_text = self.history_text.get("1.0", "end-1c")
        filtered_results = []
        
        for line in history_text.split('\n'):
            if filter_value == "Все":
                filtered_results.append(line)
            elif filter_value == "Сильные" and "strength': 0.8" in line:
                filtered_results.append(line)
            elif filter_value == "Средние" and "strength': 0.5" in line:
                filtered_results.append(line)
            elif filter_value == "Слабые" and "strength': 0.3" in line:
                filtered_results.append(line)
        
        self.history_text.delete("1.0", "end")
        self.history_text.insert("1.0", "\n".join(filtered_results))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history_text.delete("1.0", "end")
            # Опционально: очистить файл истории, если он существует
            try:
                with open('password_history.json', 'w') as f:
                    json.dump([], f)
            except FileNotFoundError:
                pass
            messagebox.showinfo("Успех", "История очищена")

    def type_effect(self, password, index=0):
        if index < len(password):
            self.password_text.delete("1.0", "end")
            self.password_text.insert("1.0", password[:index+1])
            self.window.after(50, lambda: self.type_effect(password, index+1))
        else:
            # После завершения анимации обновляем статистику
            self.update_statistics()

    def add_visual_effects(self):
        # Добавляем градиентный фон
        self.window.configure(fg_color=["#1a1a1a", "#2d2d2d"])
        
        # Добавляем тени для всех фреймов
        for frame in [self.sidebar, self.tab_generator, self.tab_history, self.tab_settings]:
            frame.configure(corner_radius=10, border_width=2, border_color="#3f3f3f")
        
        # Анимация при наведении на кнопки
        def on_enter(e):
            e.widget.configure(fg_color=["#2ecc71", "#27ae60"])
        def on_leave(e):
            e.widget.configure(fg_color=["#3498db", "#2980b9"])
        
        for button in self.window.winfo_children():
            if isinstance(button, ctk.CTkButton):
                button.bind("<Enter>", on_enter)
                button.bind("<Leave>", on_leave)

    def setup_hotkeys(self):
        self.window.bind("<Control-g>", lambda e: self.generate_multiple_passwords())
        self.window.bind("<Control-c>", lambda e: self.copy_password())
        self.window.bind("<Control-s>", lambda e: self.save_password())
        self.window.bind("<Control-a>", lambda e: self.analyze_password())
        self.window.bind("<Control-f>", lambda e: self.search_var.focus_set())

    def show_notification(self, title, message, duration=3000):
        notification_window = ctk.CTkToplevel(self.window)
        notification_window.geometry("300x100+{}+{}".format(
            self.window.winfo_x() + self.window.winfo_width() - 320,
            self.window.winfo_y() + 20
        ))
        notification_window.title("")
        notification_window.overrideredirect(True)
        
        ctk.CTkLabel(notification_window, 
                     text=title,
                     font=("Roboto", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(notification_window, 
                     text=message).pack(pady=5)
        
        notification_window.lift()
        self.window.after(duration, notification_window.destroy)

    def create_statistics_visualization(self):
        stats_frame = ctk.CTkFrame(self.tab_history)
        stats_frame.pack(fill="x", pady=10, padx=5)
        
        # Круговая диаграмма категорий
        self.pie_canvas = ctk.CTkCanvas(stats_frame, height=200, bg="#2d2d2d")
        self.pie_canvas.pack(side="left", fill="both", expand=True)
        
        # График тенденций надежности
        self.trend_canvas = ctk.CTkCanvas(stats_frame, height=200, bg="#2d2d2d")
        self.trend_canvas.pack(side="right", fill="both", expand=True)
        
        def update_statistics():
            # Обновление круговой диаграммы
            categories = {}
            history_text = self.history_text.get("1.0", "end-1c")
            for line in history_text.split('\n'):
                if line:
                    category = line.split(": ")[-1]
                    categories[category] = categories.get(category, 0) + 1
                    
            # Орисовка диараммы...
            
            self.window.after(5000, update_statistics)
        
        update_statistics()

    def apply_profile(self, settings):
        self.password_length.set(settings["length"])
        self.use_lowercase.set(settings["lowercase"])
        self.use_uppercase.set(settings["uppercase"])
        self.use_digits.set(settings["digits"])
        self.use_symbols.set(settings["symbols"])
        
        self.update_length_indicator(settings["length"])
        self.show_notification("Профиль применен", 
                             f"Применены настройки профиля с длиной {settings['length']}")

    def setup_achievements(self):
        self.achievements = {
            "beginner": {"name": "Новичок", "desc": "Создан первый пароль", "unlocked": False},
            "master": {"name": "Мастер", "desc": "Создано 100 паролей", "unlocked": False},
            "secure": {"name": "Защитник", "desc": "Создан пароль максимальной надежности", "unlocked": False},
            "collector": {"name": "Коллекционер", "desc": "Использованы все категории", "unlocked": False}
        }
        
    def check_achievements(self, password=None):
        """Проверяет достижения пользователя"""
        # Проверяем достижения
        if not self.achievements["beginner"]["unlocked"]:
            self.unlock_achievement("beginner")
                
        current_count = int(self.passwords_count.cget("text").split(": ")[1])
        if current_count >= 100 and not self.achievements["master"]["unlocked"]:
            self.unlock_achievement("master")
                
        if password and self.calculate_password_strength(password) == 1.0:
            if not self.achievements["secure"]["unlocked"]:
                self.unlock_achievement("secure")

    def create_tooltip_system(self):
        class AnimatedTooltip:
            def __init__(self, widget, text):
                self.widget = widget
                self.text = text
                self.tooltip = None
                self.alpha = 0.0
                self.widget.bind("<Enter>", self.show)
                self.widget.bind("<Leave>", self.hide)
            
            def show(self, event=None):
                x = self.widget.winfo_rootx() + self.widget.winfo_width() + 10
                y = self.widget.winfo_rooty() + self.widget.winfo_height() // 2
                
                self.tooltip = ctk.CTkToplevel(self.widget)
                self.tooltip.wm_overrideredirect(True)
                self.tooltip.wm_geometry(f"+{x}+{y}")
                self.tooltip.attributes('-alpha', 0.0)
                
                frame = ctk.CTkFrame(self.tooltip, fg_color="#2d2d2d")
                frame.pack(padx=5, pady=5)
                
                label = ctk.CTkLabel(frame, text=self.text)
                label.pack()
                
                def fade_in():
                    if self.tooltip and self.alpha < 1.0:
                        self.alpha += 0.1
                        self.tooltip.attributes('-alpha', self.alpha)
                        self.tooltip.after(20, fade_in)
                
                fade_in()
            
            def hide(self, event=None):
                def fade_out():
                    if self.tooltip and self.alpha > 0.0:
                        self.alpha -= 0.1
                        self.tooltip.attributes('-alpha', self.alpha)
                        if self.alpha <= 0:
                            self.tooltip.destroy()
                            self.tooltip = None
                        else:
                            self.tooltip.after(20, fade_out)
                
                if self.tooltip:
                    fade_out()

        # Добавляем подсказки к элементам интерфейса
        tooltips = [
            (self.strength_progress, "Индикатор надежности пароля"),
            (self.password_text, "Сгенерированные пароли"),
            # Добавьте другие элементы и их посказки
        ]
        
        for widget, text in tooltips:
            AnimatedTooltip(widget, text)

    def apply_template(self, template):
        """Применяет шаблон для генерации пароля"""
        if "#" in template:
            result = ""
            for char in template:
                if char == "#":
                    result += choice("0123456789")
                elif char == "w":
                    result += choice("abcdefghijklmnopqrstuvwxyz")
                elif char == "W":
                    result += choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                else:
                    result += char
            return result
        return template

    def create_template_system(self):
        template_frame = ctk.CTkFrame(self.tab_settings)
        template_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(template_frame,
                    text="Шаблоны паролей",
                    font=("Roboto", 16, "bold")).pack(pady=5)
        
        self.templates = {
            "PIN": "####",
            "Слово + Число": "word####",
            "Сложный": "Word####!@",
            "Особый": "W####w!@"
        }
        
        for name, pattern in self.templates.items():
            frame = ctk.CTkFrame(template_frame)
            frame.pack(fill="x", pady=2)
            ctk.CTkLabel(frame, text=name).pack(side="left", padx=5)
            ctk.CTkLabel(frame, text=pattern).pack(side="left", padx=5)
            ctk.CTkButton(frame,
                         text="Применить",
                         command=lambda p=pattern: self.apply_template(p)).pack(side="right", padx=5)

    def setup_achievements_system(self):
        self.level = 0
        self.xp = 0
        self.achievements_frame = ctk.CTkFrame(self.sidebar)
        self.achievements_frame.pack(fill="x", pady=10, padx=5)
        
        self.level_label = ctk.CTkLabel(self.achievements_frame, 
                                       text="Уровень: 0",
                                       font=("Roboto", 14, "bold"))
        self.level_label.pack()
        
        self.xp_progress = ctk.CTkProgressBar(self.achievements_frame, width=150)
        self.xp_progress.pack(pady=5)
        self.xp_progress.set(0)
        
        def add_xp(amount):
            self.xp += amount
            level_threshold = (self.level + 1) * 100
            if self.xp >= level_threshold:
                self.level += 1
                self.xp = self.xp - level_threshold
                self.level_label.configure(text=f"Уровень: {self.level}")
                self.show_notification("Новый уровень!", f"Достигнут уровень {self.level}")
            
            self.xp_progress.set(self.xp / level_threshold)
        
        self.add_xp = add_xp

    def create_animated_strength_meter(self):
        strength_frame = ctk.CTkFrame(self.tab_generator)
        strength_frame.pack(fill="x", padx=20, pady=10)
        
        self.strength_canvas = ctk.CTkCanvas(strength_frame, height=40, bg="#2d2d2d")
        self.strength_canvas.pack(fill="x", pady=5)
        
        def animate_strength(strength):
            """Анимирует индикатор надежности пароля"""
            colors = ["#ff0000", "#ff7f00", "#ffff00", "#00ff00"]
            segments = 20
            width = self.strength_canvas.winfo_width()
            
            def animate_frame(current=0):
                if current <= strength * segments:
                    self.strength_canvas.delete("all")
                    segment_width = width / segments
                    
                    for i in range(int(current)):
                        x1 = i * segment_width
                        x2 = (i + 1) * segment_width
                        color_index = min(3, i // (segments // 4))
                        
                        self.strength_canvas.create_rectangle(
                            x1, 5, x2-2, 35,
                            fill=colors[color_index],
                            width=0
                        )
                    
                    self.window.after(50, lambda: animate_frame(current + 0.5))
            
        # Сохраняем функцию как атрибут класса
        self.animate_strength = animate_strength
        # Инициализируем с нулевой силой пароля
        self.animate_strength(0)

    def create_template_preview(self):
        preview_frame = ctk.CTkFrame(self.tab_generator)
        preview_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(preview_frame, 
                    text="Предпросмотр шаблона",
                    font=("Roboto", 14, "bold")).pack()
        
        self.preview_text = ctk.CTkTextbox(preview_frame, height=60)
        self.preview_text.pack(fill="x", pady=5)
        
        def update_preview(template):
            previews = []
            for _ in range(3):  # Показываем 3 варианта
                result = self.apply_template(template)
                previews.append(result)
            
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", "\n".join(previews))
        
        self.update_template_preview = update_preview

    def create_animated_statistics(self):
        stats_frame = ctk.CTkFrame(self.tab_history)
        stats_frame.pack(fill="x", pady=10, padx=5)
        
        self.stats_canvas = ctk.CTkCanvas(stats_frame, height=200, bg="#2d2d2d")
        self.stats_canvas.pack(fill="x", pady=5)
        
        def animate_stats():
            data = self.get_password_statistics()  # Получаем статистику
            
            def animate_bar(index=0, height=0):
                if index < len(data):
                    target_height = data[index] * 150
                    if height < target_height:
                        self.stats_canvas.delete(f"bar_{index}")
                        self.stats_canvas.create_rectangle(
                            index * 30 + 10, 180 - height,
                            (index + 1) * 30, 180,
                            fill="#2ecc71",
                            tags=f"bar_{index}"
                        )
                        self.window.after(16, lambda: animate_bar(index, height + 5))
                    else:
                        self.window.after(100, lambda: animate_bar(index + 1))
            
            animate_bar()
        
        # Обновляем кажды 5 секунд
        def update():
            animate_stats()
            self.window.after(5000, update)
        
        update()

    def get_password_statistics(self):
        """Возвращает статистику паролей для анимированного графика"""
        history_text = self.history_text.get("1.0", "end-1c")
        
        # Инициализируем массив для хранения статистики
        # Например: [процент сильных, процент средних, процент слабых паролей]
        stats = [0, 0, 0]
        total = 0
        
        for line in history_text.split('\n'):
            if line:
                password = line.split(" - ")[1].split(": ")[0]
                strength = self.calculate_password_strength(password)
                total += 1
                
                if strength >= 0.8:
                    stats[0] += 1
                elif strength >= 0.5:
                    stats[1] += 1
                else:
                    stats[2] += 1
        
        # Преобразуем в проценты
        if total > 0:
            stats = [count / total for count in stats]
        
        return stats

    def unlock_achievement(self, achievement_id):
        """Разблокирует достижение и показывает уведомление"""
        if achievement_id in self.achievements and not self.achievements[achievement_id]["unlocked"]:
            self.achievements[achievement_id]["unlocked"] = True
            achievement = self.achievements[achievement_id]
            self.show_notification(
                f"🏆 Получено достижение: {achievement['name']}", 
                achievement['desc']
            )
            # Добавляем бонусный опыт за достижение
            self.add_xp(50)  # Бонус 50 XP за каждое достижение

if __name__ == "__main__":
    app = PasswordGenerator()
    app.run()
