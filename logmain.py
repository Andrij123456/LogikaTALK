import base64
import io
import threading
from socket import socket, AF_INET, SOCK_STREAM

from customtkinter import *
from tkinter import filedialog
from PIL import Image

class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        # Modern window size and style
        self.geometry('500x400')
        self.title("Sigma Chat")
        set_appearance_mode("dark")
        set_default_color_theme("dark-blue")
        self.configure(fg_color="#232946")

        self.username = None
        self.avatar_path = None
        self.avatar_img_40 = None  # For messages
        self.avatar_img_60 = None  # For menu
        self.avatar_img_80 = None  # For dialog

        # Меню
        self.label = None
        self.menu_frame = CTkFrame(self, width=30, height=400, fg_color="#121629", corner_radius=20)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -20
        self.btn = CTkButton(self, text='▶', command=self.toggle_show_menu, width=30, fg_color="#393e46", hover_color="#4ecca3", corner_radius=10)
        self.btn.place(x=0, y=0)

        # Основне поле чату
        self.chat_field = CTkScrollableFrame(self, fg_color="#232946", corner_radius=15)
        self.chat_field.place(x=0, y=0)

        # Поле введення та кнопки
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40, fg_color="#393e46", border_color="#4ecca3", border_width=2, corner_radius=10, text_color="#fff")
        self.message_entry.place(x=0, y=0)
        self.send_button = CTkButton(self, text='➤', width=50, height=40, command=self.send_message, fg_color="#4ecca3", hover_color="#232946", text_color="#232946", corner_radius=10)
        self.send_button.place(x=0, y=0)
        self.open_img_button = CTkButton(self, text='📸', width=50, height=40, command=self.open_image, fg_color="#393e46", hover_color="#4ecca3", corner_radius=10)
        self.open_img_button.place(x=0, y=0)
        self.message_entry.bind('<Return>', lambda e: self.send_message())

        self.adaptive_ui()

        # Показати вікно для введення імені
        self.show_username_dialog()

    def show_username_dialog(self):
        self.username_dialog = CTkToplevel(self)
        self.username_dialog.title("Введіть ваш нік")
        self.username_dialog.geometry("320x260")
        self.username_dialog.grab_set()
        self.username_dialog.configure(fg_color="#232946")
        self.username_dialog.resizable(False, False)

        # Аватар (круг або зображення)
        self.avatar_canvas = CTkCanvas(self.username_dialog, width=80, height=80, bg="#232946", highlightthickness=0)
        self.avatar_canvas.pack(pady=(15, 5))
        self.draw_avatar_circle()

        avatar_btn = CTkButton(self.username_dialog, text="Завантажити аватар", command=self.choose_avatar, fg_color="#393e46", hover_color="#4ecca3", text_color="#fff", corner_radius=10, width=120)
        avatar_btn.pack(pady=(0, 10))

        label = CTkLabel(self.username_dialog, text="Введіть ваш нікнейм", font=("Segoe UI", 18, "bold"), text_color="#4ecca3")
        label.pack(pady=(0, 10))
        self.username_entry = CTkEntry(self.username_dialog, placeholder_text="Ваш нік...", fg_color="#232946", border_color="#4ecca3", border_width=2, corner_radius=10, text_color="#fff")
        self.username_entry.pack(pady=5)
        continue_btn = CTkButton(self.username_dialog, text="Продовжити", command=self.set_username, fg_color="#4ecca3", hover_color="#393e46", text_color="#232946", corner_radius=10)
        continue_btn.pack(pady=10)
        self.username_entry.bind('<Return>', lambda e: self.set_username())

    def draw_avatar_circle(self):
        import random
        self.avatar_canvas.delete("all")
        if self.avatar_img_80:
            self.avatar_canvas.create_oval(0, 0, 80, 80, fill="#232946", outline="")
            self.avatar_canvas.create_image(40, 40, image=self.avatar_img_80)
        else:
            colors = ["#1976d2", "#43a047", "#ffd600", "#8e24aa", "#d32f2f", "#fff", "#111", "#00bcd4"]
            if not hasattr(self, '_avatar_color'):
                self._avatar_color = random.choice(colors)
            self.avatar_canvas.create_oval(0, 0, 80, 80, fill=self._avatar_color, outline="")


    def choose_avatar(self):
        from PIL import ImageTk
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.avatar_path = file_path
            img80 = Image.open(file_path).resize((80, 80)).convert("RGBA")
            img60 = img80.resize((60, 60), Image.LANCZOS)
            img40 = img80.resize((40, 40), Image.LANCZOS)
            import numpy as np
            arr80 = np.array(img80)
            arr60 = np.array(img60)
            arr40 = np.array(img40)
            # Make circular mask for each size
            for arr, size in zip([arr80, arr60, arr40], [80, 60, 40]):
                h, w = arr.shape[:2]
                y, x = np.ogrid[:h, :w]
                mask = (x - w/2)**2 + (y - h/2)**2 > (w/2)**2
                arr[mask] = 0
            from PIL import ImageTk
            self.avatar_img_80 = ImageTk.PhotoImage(Image.fromarray(arr80))
            self.avatar_img_60 = ImageTk.PhotoImage(Image.fromarray(arr60))
            self.avatar_img_40 = ImageTk.PhotoImage(Image.fromarray(arr40))
            if hasattr(self, '_avatar_color'):
                del self._avatar_color
            self.draw_avatar_circle()
            if hasattr(self, 'menu_avatar_canvas'):
                self.draw_menu_avatar()

    def set_username(self):
        name = self.username_entry.get().strip()
        if not name:
            self.username_entry.configure(placeholder_text="Ти тут застряг іза бага")
            return
        self.username = name
        self.username_dialog.destroy()

        # Далі ініціалізуємо чат
        self.add_message("Демонстрація відображення зображення:", CTkImage(Image.open('SigmaCat(2).jpg'), size=(300, 300)))
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався (лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀')
            self.show_menu()

            # --- Аватар у меню ---
            if not hasattr(self, 'menu_avatar_canvas') or not self.menu_avatar_canvas:
                self.menu_avatar_canvas = CTkCanvas(self.menu_frame, width=60, height=60, bg="#121629", highlightthickness=0)
            self.menu_avatar_canvas.pack(pady=(60, 5))
            self.draw_menu_avatar()
            if not hasattr(self, 'menu_avatar_btn') or not self.menu_avatar_btn:
                self.menu_avatar_btn = CTkButton(self.menu_frame, text="Змінити аву", command=self.choose_avatar_from_menu, fg_color="#393e46", hover_color="#4ecca3", text_color="#fff", corner_radius=10, width=90)
            self.menu_avatar_btn.pack(pady=(0, 20))

            # При відкритті меню – додаємо приклад зміни імені
            if not hasattr(self, 'label') or not self.label:
                self.label = CTkLabel(self.menu_frame, text="Ім'я", font=("Segoe UI", 18, "bold"), text_color="#4ecca3")
            self.label.pack(pady=20)

            if not hasattr(self, 'entry') or not self.entry:
                self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...", fg_color="#232946", border_color="#4ecca3", border_width=2, corner_radius=10, text_color="#fff")
            self.entry.pack(pady=10)

            if not hasattr(self, 'save_button') or not self.save_button:
                self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name, fg_color="#4ecca3", hover_color="#393e46", text_color="#232946", corner_radius=10)
                self.save_button.pack(pady=10)

    def draw_menu_avatar(self):
        import random
        self.menu_avatar_canvas.delete("all")
        if self.avatar_img_60:
            self.menu_avatar_canvas.create_oval(0, 0, 60, 60, fill="#121629", outline="")
            self.menu_avatar_canvas.create_image(30, 30, image=self.avatar_img_60)
        else:
            colors = ["#1976d2", "#43a047", "#ffd600", "#8e24aa", "#d32f2f", "#fff", "#111", "#00bcd4"]
            if not hasattr(self, '_avatar_color'):
                self._avatar_color = random.choice(colors)
            self.menu_avatar_canvas.create_oval(0, 0, 60, 60, fill=self._avatar_color, outline="")


    def choose_avatar_from_menu(self):
        from PIL import ImageTk
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.avatar_path = file_path
            img80 = Image.open(file_path).resize((80, 80)).convert("RGBA")
            img60 = img80.resize((60, 60), Image.LANCZOS)
            img40 = img80.resize((40, 40), Image.LANCZOS)
            import numpy as np
            arr80 = np.array(img80)
            arr60 = np.array(img60)
            arr40 = np.array(img40)
            for arr, size in zip([arr80, arr60, arr40], [80, 60, 40]):
                h, w = arr.shape[:2]
                y, x = np.ogrid[:h, :w]
                mask = (x - w/2)**2 + (y - h/2)**2 > (w/2)**2
                arr[mask] = 0
            self.avatar_img_80 = ImageTk.PhotoImage(Image.fromarray(arr80))
            self.avatar_img_60 = ImageTk.PhotoImage(Image.fromarray(arr60))
            self.avatar_img_40 = ImageTk.PhotoImage(Image.fromarray(arr40))
            if hasattr(self, '_avatar_color'):
                del self._avatar_color
            self.draw_menu_avatar()
            self.draw_avatar_circle()

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)

        # Ховаємо/показуємо кнопки та елементи меню залежно від стану
        if self.is_show_menu and self.menu_frame.winfo_width() >= 200:
            # Показати всі елементи меню
            if hasattr(self, 'menu_avatar_canvas') and self.menu_avatar_canvas:
                self.menu_avatar_canvas.pack(pady=(60, 5))
            if hasattr(self, 'menu_avatar_btn') and self.menu_avatar_btn:
                self.menu_avatar_btn.pack(pady=(0, 20))
            if hasattr(self, 'label') and self.label:
                self.label.pack(pady=20)
            if hasattr(self, 'entry') and self.entry:
                self.entry.pack(pady=10)
            if hasattr(self, 'save_button') and self.save_button:
                self.save_button.pack(pady=10)

        elif not self.is_show_menu and self.menu_frame.winfo_width() <= 60:
            # Сховати всі елементи меню
            if hasattr(self, 'menu_avatar_canvas') and self.menu_avatar_canvas:
                self.menu_avatar_canvas.pack_forget()
            if hasattr(self, 'menu_avatar_btn') and self.menu_avatar_btn:
                self.menu_avatar_btn.pack_forget()
            if hasattr(self, 'label') and self.label:
                self.label.pack_forget()
            if hasattr(self, 'entry') and self.entry:
                self.entry.pack_forget()
            if hasattr(self, 'save_button') and self.save_button:
                self.save_button.pack_forget()

        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 60 and not self.is_show_menu:
            self.after(10, self.show_menu)
            # Додатково: знищення елементів якщо меню повністю згорнуте
            if self.label:
                self.label.destroy()
            if getattr(self, "entry", None):
                self.entry.destroy()
            if getattr(self, "save_button", None):
                self.save_button.destroy()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(),
                                y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - 110)
        self.open_img_button.place(x=self.winfo_width()-105, y=self.send_button.winfo_y())

        self.after(50, self.adaptive_ui)

    def add_message(self, message, img=None, author_avatar=None):
        import random
        if not hasattr(self, '_avatar_refs'):
            self._avatar_refs = []
        message_frame = CTkFrame(self.chat_field, fg_color="#393e46", corner_radius=12)
        message_frame.pack(pady=7, anchor='w', padx=10)
        wrapleng_size = self.winfo_width() - self.menu_frame.winfo_width() - 60

        # Аватар над повідомленням
        avatar_canvas = CTkCanvas(message_frame, width=40, height=40, bg="#393e46", highlightthickness=0)
        avatar_canvas.pack(pady=(7, 0))
        avatar_img = None
        if author_avatar:
            avatar_img = author_avatar
        elif self.avatar_img_40:
            avatar_img = self.avatar_img_40
        if avatar_img:
            avatar_canvas.create_oval(0, 0, 40, 40, fill="#393e46", outline="")
            avatar_canvas.create_image(20, 20, image=avatar_img)
            self._avatar_refs.append(avatar_img)
        else:
            colors = ["#1976d2", "#43a047", "#ffd600", "#8e24aa", "#d32f2f", "#fff", "#111", "#00bcd4"]
            if not hasattr(self, '_avatar_color'):
                self._avatar_color = random.choice(colors)
            avatar_canvas.create_oval(0, 0, 40, 40, fill=self._avatar_color, outline="")

        if not img:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size,
                        text_color="#fff", font=("Segoe UI", 14), justify='left', bg_color="#393e46").pack(padx=14, pady=7)
        else:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size,
                    text_color="#fff", font=("Segoe UI", 14), image=img, compound='top',
                    justify='left', bg_color="#393e46").pack(padx=14, pady=7)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}", author_avatar=self.avatar_img_40)
            data= f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
            self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='ignore')

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                    break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("#", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4: 

                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                        img_data = base64.b64decode(b64_img)
                        pil_img = Image.open(io.BytesIO(img_data))
                        ctk_img = CTkImage(pil_img, size=(300, 300))
                        self.add_message(f"{author} надіслав(ла) зображення: {filename}", img=ctk_img)
                except Exception as e:
                        self.add_message(f"Помилка відображення зображення: {e}")
            else:
                self.add_message(line)

    def open_image (self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode())
            self.add_message('', CTkImage(light_image=Image.open(file_name), size=(300, 300)))
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}")

if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()
