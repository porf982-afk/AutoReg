import requests
import random
import string
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui
import json
import os
from datetime import datetime
from pynput import mouse, keyboard
import sys

class PasswordGenerator:
    SPECIAL_CHARS = '!@#$%'

    @staticmethod
    def generate(length=8):
        uppercase = random.choice(string.ascii_uppercase)
        lowercase = random.choice(string.ascii_lowercase)
        digit = random.choice(string.digits)
        special = random.choice(PasswordGenerator.SPECIAL_CHARS)

        remaining = ''.join(random.choices(string.ascii_letters + string.digits, k=4))

        password = list(uppercase + lowercase + digit + special + remaining)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_strong(length=10):
        uppercase = random.choice(string.ascii_uppercase)
        lowercase = random.choice(string.ascii_lowercase)
        digit = random.choice(string.digits)
        special = random.choice(PasswordGenerator.SPECIAL_CHARS)
        special2 = random.choice(PasswordGenerator.SPECIAL_CHARS)

        remaining = ''.join(random.choices(string.ascii_letters + string.digits, k=length-5))

        password = list(uppercase + lowercase + digit + special + special2 + remaining)
        random.shuffle(password)

        return ''.join(password)

class UsernameManager:
    def __init__(self, filename="database.txt"):
        self.filename = filename
        self.available_usernames = []
        self.used_usernames = []
        self.used_file = "used_usernames.txt"

        self.load_usernames()
        self.load_used()

    def load_usernames(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.available_usernames = [line.strip() for line in f if line.strip()]

            self.available_usernames = [u for u in self.available_usernames
                                      if u not in self.used_usernames]

            print(f"Загружено {len(self.available_usernames)} name")

        except Exception as e:
            print(f"Ошибка загрузки БД: {e}")
            self.available_usernames = self._generate_fallback_usernames()

    def load_used(self):
        try:
            if os.path.exists(self.used_file):
                with open(self.used_file, 'r', encoding='utf-8') as f:
                    self.used_usernames = [line.strip() for line in f if line.strip()]
        except:
            self.used_usernames = []

    def save_used(self, username):
        self.used_usernames.append(username)
        with open(self.used_file, 'a', encoding='utf-8') as f:
            f.write(f"{username}\n")

    def get_random_username(self):
        if not self.available_usernames:
            print("Username закончились")
            return self._generate_fallback_username()

        username = random.choice(self.available_usernames)
        self.available_usernames.remove(username)
        self.save_used(username)

        name = username.split('.')[0].capitalize()
        print(f"Использованно name с БД: {username} → Имя: {name}")
        print(f"Осталось в БД: {len(self.available_usernames)}")

        return name, username

    def _generate_fallback_username(self):
        first_names = ['james', 'john', 'robert', 'michael', 'william', 'david']
        last_names = ['smith', 'johnson', 'williams', 'brown', 'jones', 'miller']

        first = random.choice(first_names)
        last = random.choice(last_names)
        username = f"{first}.{last}{random.randint(1, 999)}"
        name = first.capitalize()

        self.save_used(username)
        return name, username

    def _generate_fallback_usernames(self):
        usernames = []
        first_names = ['james', 'john', 'RobertosBibka', 'MichailoX', 'william', 'david']
        last_names = ['smith', 'johnson', 'williams', 'brown', 'Jansina', 'miller']

        for first in first_names:
            for last in last_names:
                usernames.append(f"{first}.{last}")
                for i in range(1, 10):
                    usernames.append(f"{first}.{last}{i}")
        return usernames

    def get_stats(self):
        return {
            'available': len(self.available_usernames),
            'used': len(self.used_usernames)
        }

class MailTM:
    def __init__(self):
        self.base_url = "https://api.mail.tm"
        self.session = requests.Session()
        self.email = None
        self.password = None

    def create_account(self):
        try:
            response = self.session.get(f"{self.base_url}/domains")
            domain = response.json()['hydra:member'][0]['domain']

            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            self.email = f"{username}@{domain}"
            self.password = PasswordGenerator.generate(8)

            data = {"address": self.email, "password": self.password}
            response = self.session.post(f"{self.base_url}/accounts", json=data)

            if response.status_code == 201:
                print(f"Почта: {self.email}")
                print(f"Пароль: {self.password}")
                return True

        except Exception as e:
            print(f"Ошибка: {e}")

        self.email = f"user{random.randint(1000,9999)}@mail.ru"
        self.password = PasswordGenerator.generate(8)
        print(f"Почта: {self.email}")
        print(f"Пароль: {self.password}")
        return True

class SimpleActionRecorder:
    def __init__(self):
        self.clicks = []
        self.is_recording = False
        self.mouse_listener = None
        self.keyboard_listener = None
        self.click_count = 0
        self.recording_file = "clicks_record.json"

    def start_recording(self):
        self.clicks = []
        self.click_count = 0
        self.is_recording = True

        print("\n=== Запись ===")
        print("Процесс:")
        print("1. Поле имени")
        print("2. Поле email")
        print("3. Поле пароля")
        print("4. Поле повтора пароля")
        print("5. Кнопка регистрации")
        print("\nESC - по завершению процесса\n")

        def on_click(x, y, button, pressed):
            if pressed and self.is_recording:
                self.click_count += 1
                self.clicks.append({
                    'order': self.click_count,
                    'x': x,
                    'y': y,
                    'timestamp': time.time()
                })
                print(f"Клик {self.click_count}: ({x}, {y})")

        def on_press(key):
            if key == keyboard.Key.esc and self.is_recording:
                print("Запись остановлена")
                self.stop_recording()
                return False

        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.keyboard_listener = keyboard.Listener(on_press=on_press)

        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_recording(self):
        self.is_recording = False

        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        record_data = {
            'total_clicks': len(self.clicks),
            'clicks': self.clicks,
            'recorded_at': datetime.now().isoformat(),
        }

        with open(self.recording_file, 'w', encoding='utf-8') as f:
            json.dump(record_data, f, indent=2)

        print(f"\nЗаписано {len(self.clicks)} пресетов")

class RegistrationBot:
    def __init__(self, target_url="https://google.com"):
        self.driver = None
        self.recorder = SimpleActionRecorder()
        self.target_url = target_url
        self.mail = None
        self.username_manager = UsernameManager()
        self.clicks_data = None

        self.browser_width = 800
        self.browser_height = 700
        self.browser_x = 0
        self.browser_y = 0

        self.load_clicks()

    def load_clicks(self):
        try:
            with open("clicks_record.json", 'r', encoding='utf-8') as f:
                self.clicks_data = json.load(f)
            print(f"Загружено {len(self.clicks_data['clicks'])} пресетов")
            print(" ")
            return True
        except:
            self.clicks_data = None
            return False

    def create_browser(self):
        chrome_options = Options()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument(f'--window-size={self.browser_width},{self.browser_height}')
        chrome_options.add_argument(f'--window-position={self.browser_x},{self.browser_y}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def close_browser(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def show_ascii_animation(self, seconds):
        frames = [
            "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
        ]

        start_time = time.time()
        frame_idx = 0

        while time.time() - start_time < seconds:
            remaining = int(seconds - (time.time() - start_time))

            bar_length = 20
            progress = (seconds - remaining) / seconds
            filled = int(bar_length * progress)
            bar = '█' * filled + '░' * (bar_length - filled)

            sys.stdout.write(f'\r{frames[frame_idx % len(frames)]} [{bar}] {remaining:2d} сек')
            sys.stdout.flush()

            frame_idx += 1
            time.sleep(0.1)

        sys.stdout.write('\r [████████████████████] Готово!    \n')
        sys.stdout.flush()

    def record_mode(self):
        print("\n=== Режим записи ===")
        print(f"Целевой сайт: {self.target_url}")
        print("Инфа дня: размер браузера не трогать")
        print("Инфа дня: командную строку расположите правее от браузера для...")
        print("Инфа дня: комфорта и слежки процесса")

        self.driver = self.create_browser()
        self.driver.get(self.target_url)
        time.sleep(3)

        self.recorder.start_recording()

        try:
            while self.recorder.is_recording:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.recorder.stop_recording()

        self.load_clicks()

    def execute_single_registration(self, account_number, total):
        print(f"\n{'='*50}")
        print(f"         Прогресс {account_number}/{total}")
        print(f"{'='*50}")

        name, username = self.username_manager.get_random_username()
        self.mail = MailTM()
        self.mail.create_account()

        email = self.mail.email
        password = self.mail.password

        print(f"Имя: {name}")
        print(f"Email: {email}")
        print(f"Пароль: {password}")

        self.driver = self.create_browser()
        self.driver.get(self.target_url)
        time.sleep(3)

        try:
            input_data = {1: name, 2: email, 3: password, 4: password}

            for click in self.clicks_data['clicks']:
                x = click['x']
                y = click['y']
                order = click['order']

                pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.4))
                time.sleep(0.1)
                pyautogui.click()
                time.sleep(0.3)

                if order in input_data:
                    text = input_data[order]
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.1)
                    pyautogui.press('delete')
                    for char in text:
                        pyautogui.write(char, interval=random.uniform(0.02, 0.06))
                    time.sleep(0.5)

            with open('accounts.txt', 'a', encoding='utf-8') as f:
                f.write(f"{email}:{password}:{name}:{username}\n")

            self.close_browser()
            return True

        except Exception as e:
            print(f"✗ Ошибка: {e}")
            self.close_browser()
            return False

    def automation_mode(self, count=1):
        print("\n=== Запуск процесса ===")
        print(f"Целевой сайт: {self.target_url}")

        if not self.clicks_data:
            print("Нет записей")
            return

        stats = self.username_manager.get_stats()
        print(f"В базе доступно {stats['available']} username")

        successful = 0

        for i in range(1, count + 1):
            if self.execute_single_registration(i, count):
                successful += 1

            if i < count:
                wait_time = random.randint(10, 15)
                print(f"\nОжидание:")
                self.show_ascii_animation(wait_time)

        print(f"\n{'='*50}")
        print(f"         Итог: {successful}/{count} успешно")
        print(f"{'='*50}")

def main():
    print("""
    ╔═══════════════════════════════════════╗
    ║             AutoReg v2.0              ║
    ╚═══════════════════════════════════════╝
    """)

    target_url = input(" Введите URL сайта для регистрации: ").strip()

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    print(f"\n Целевой сайт: {target_url}\n")

    print(" Режим:")
    print("   1.  Запись кликов")
    print("   2.  Автоматическая регистрация")

    choice = input("\n Режим: ").strip()
    print(" ")

    bot = RegistrationBot(target_url)

    try:
        if choice == '1':
            bot.record_mode()
            print("\n Запись завершена.")

        elif choice == '2':
            if not os.path.exists("clicks_record.json"):
                print(" Требуются записи")
                return

            count = input(" Количество аккаунтов: ").strip()
            count = int(count) if count.isdigit() else 1
            bot.automation_mode(count)

    except KeyboardInterrupt:
        print("\n Прервано пользователем")
    except Exception as e:
        print(f" Ошибка: {e}")
    finally:
        bot.close_browser()
        print("\n Процесс завершен")

if __name__ == "__main__":
    main()