import tkinter as tk
from tkinter import messagebox
import random
import math
from tkinter.messagebox import askyesno

def get_european_color(n: int) -> str:
    """
    Возвращает 'red', 'black' или 'green' для числа рулетки.
    Европейская рулетка:
    - 0 — зелёный
    - 1–10 и 19–28: нечётные — красные, чётные — чёрные
    - 11–18 и 29–36: нечётные — чёрные, чётные — красные
    """
    if n == 0:
        return "green"

    if (1 <= n <= 10) or (19 <= n <= 28):
        if n % 2 == 1:
            return "red"
        else:
            return "black"
    else:
        if n % 2 == 1:
            return "black"
        else:
            return "red"


class RouletteGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Казино <<Podpivas>>")
        self.root.geometry("900x550")
        self.root.resizable(False, False)
        self.balance = 1000
        self.bet = 0
        self.selected_color = None
        self.loan_active = False
        self.loan_amount = 0


        self.wheel_numbers = [
            0,
            32, 15, 19, 4, 21, 2, 25, 17, 34,
            6, 27, 13, 36, 11, 30, 8, 23, 10,
            5, 24, 16, 33, 1, 20, 14, 31, 9,
            22, 18, 29, 7, 28, 12, 35, 3, 26
        ]

        self.sectors = [(get_european_color(n), n) for n in self.wheel_numbers]
        self.sector_angle = 360 / len(self.sectors)


        self.current_angle = 0
        self.spin_speed = 0
        self.spinning = False


        main_frame = tk.Frame(root, bg="#1b1b1b")
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(main_frame, bg="#2c2c2c", width=280)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        wheel_frame = tk.Frame(main_frame, bg="#1b1b1b")
        wheel_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


        self.balance_label = tk.Label(
            control_frame,
            text=f"Баланс: ${self.balance}",
            font=("Arial", 16, "bold"),
            bg="#2c2c2c",
            fg="white"
        )
        self.balance_label.pack(pady=15)


        self.loan_label = tk.Label(
            control_frame,
            text="Кредит: нет",
            font=("Arial", 11, "bold"),
            bg="#2c2c2c",
            fg="#ffcc00"
        )
        self.loan_label.pack(pady=(0, 5))

        tk.Label(
            control_frame,
            text="Ставка ($):",
            font=("Arial", 12),
            bg="#2c2c2c",
            fg="white"
        ).pack(pady=(10, 0))

        self.bet_entry = tk.Entry(control_frame, font=("Arial", 14))
        self.bet_entry.pack(pady=5)


        tk.Label(
            control_frame,
            text="Ставка на цвет:",
            font=("Arial", 12),
            bg="#2c2c2c",
            fg="white"
        ).pack(pady=(15, 5))

        color_frame = tk.Frame(control_frame, bg="#2c2c2c")
        color_frame.pack(pady=5)

        self.red_btn = tk.Button(
            color_frame,
            text="Красный",
            bg="red",
            fg="white",
            font=("Arial", 12, "bold"),
            width=10,
            command=lambda: self.select_color("red")
        )
        self.red_btn.pack(side=tk.LEFT, padx=5)

        self.black_btn = tk.Button(
            color_frame,
            text="Чёрный",
            bg="black",
            fg="white",
            font=("Arial", 12, "bold"),
            width=10,
            command=lambda: self.select_color("black")
        )
        self.black_btn.pack(side=tk.LEFT, padx=5)


        self.spin_btn = tk.Button(
            control_frame,
            text="Крутить рулетку!",
            font=("Arial", 14, "bold"),
            bg="#0f9d58",
            fg="white",
            width=22,
            command=self.start_spin
        )
        self.spin_btn.pack(pady=15)


        loan_btn_frame = tk.Frame(control_frame, bg="#2c2c2c")
        loan_btn_frame.pack(pady=(5, 10))

        self.take_loan_btn = tk.Button(
            loan_btn_frame,
            text="Взять кредит 10 000$",
            font=("Arial", 10, "bold"),
            bg="#c62828",
            fg="white",
            command=self.take_loan
        )
        self.take_loan_btn.pack(pady=3, fill=tk.X)

        self.repay_loan_btn = tk.Button(
            loan_btn_frame,
            text="Погасить кредит",
            font=("Arial", 10, "bold"),
            bg="#6a1b9a",
            fg="white",
            command=self.repay_loan
        )
        self.repay_loan_btn.pack(pady=3, fill=tk.X)


        self.give_up_btn = tk.Button(
            control_frame,
            text="Сдаться и уйти",
            font=("Arial", 10, "bold"),
            bg="#555555",
            fg="white",
            command=self.give_up
        )
        self.give_up_btn.pack(pady=5, fill=tk.X)


        self.result_label = tk.Label(
            control_frame,
            text="Выбери цвет и введи ставку",
            font=("Arial", 11),
            bg="#2c2c2c",
            fg="white",
            wraplength=250,
            justify="left"
        )
        self.result_label.pack(pady=10)


        tk.Label(
            control_frame,
            text="Выплата по цвету: 1 к 1\n0 (зелёный) всегда забирает ставку.\n"
                 "Если взял кредит и не вернул —\nколлекторы заберут всё.",
            font=("Arial", 9),
            bg="#2c2c2c",
            fg="#bbbbbb",
            justify="left"
        ).pack(pady=5)


        self.canvas_size = 500
        self.canvas = tk.Canvas(
            wheel_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#1b1b1b",
            highlightthickness=0
        )
        self.canvas.pack(expand=True)

        self.wheel_center = self.canvas_size // 2
        self.wheel_radius = 200


        pointer_size = 20
        cx = self.wheel_center
        cy = self.wheel_center
        self.canvas.create_polygon(
            cx - pointer_size, cy - self.wheel_radius - 15,
            cx + pointer_size, cy - self.wheel_radius - 15,
            cx,               cy - self.wheel_radius - 55,
            fill="gold", outline="black", width=2
        )

        self.draw_wheel(self.current_angle)


    def update_loan_label(self):
        if self.loan_active:
            self.loan_label.config(text=f"Кредит: ${self.loan_amount}", fg="#ffcc00")
        else:
            self.loan_label.config(text="Кредит: нет", fg="#ffcc00")


    def take_loan(self):
        if self.loan_active:
            messagebox.showinfo(
                "Кредит уже есть",
                "Ты уже взял кредит у коллекторов. Верни этот, прежде чем брать новый."
            )
            return

        answer = askyesno(
            "Кредит 10 000$",
            "Ты берёшь кредит 10 000$ у коллекторов.\n"
            "Если не вернёшь — они заберут все твои деньги,\n"
            "и на этом игра закончится.\n\nТочно взять?"
        )
        if not answer:
            return

        self.loan_active = True
        self.loan_amount = 10000
        self.balance += self.loan_amount
        self.balance_label.config(text=f"Баланс: ${self.balance}")
        self.update_loan_label()
        self.result_label.config(
            text="Ты взял кредит 10 000$.\nСтарайся вернуть его, пока не поздно...",
            fg="#ffcc00"
        )


    def repay_loan(self):
        if not self.loan_active:
            messagebox.showinfo("Нет кредита", "У тебя сейчас нет активного кредита.")
            return

        if self.balance < self.loan_amount:
            messagebox.showerror(
                "Недостаточно денег",
                "У тебя недостаточно денег, чтобы погасить кредит."
            )
            return

        answer = askyesno(
            "Погасить кредит",
            f"Погасить кредит {self.loan_amount}$?\n"
            f"С баланса спишется {self.loan_amount}$."
        )
        if not answer:
            return

        self.balance -= self.loan_amount
        self.loan_active = False
        self.loan_amount = 0
        self.balance_label.config(text=f"Баланс: ${self.balance}")
        self.update_loan_label()
        self.result_label.config(
            text="Ты успешно погасил кредит. Коллекторы довольны.",
            fg="#0f9d58"
        )


    def give_up(self):
        if self.loan_active:

            messagebox.showinfo(
                "Коллекторы пришли",
                "Ты ушёл, не вернув кредит.\n"
                "Коллекторы забрали всё.\nИгра окончена."
            )
            self.root.quit()
        else:
            answer = askyesno(
                "Выйти из игры",
                "У тебя нет долгов. Просто выйти из игры?"
            )
            if answer:
                self.root.quit()


    def select_color(self, color):
        if self.spinning:
            return
        self.selected_color = color
        self.red_btn.config(relief="sunken" if color == "red" else "raised")
        self.black_btn.config(relief="sunken" if color == "black" else "raised")


    def start_spin(self):
        if self.spinning:
            return

        try:
            bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введи число для ставки!")
            return

        if bet <= 0:
            messagebox.showerror("Ошибка", "Ставка должна быть > 0!")
            return
        if bet > self.balance:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        if not self.selected_color:
            messagebox.showerror("Ошибка", "Выбери цвет!")
            return

        self.bet = bet
        self.balance -= self.bet
        self.balance_label.config(text=f"Баланс: ${self.balance}")

        self.spin_speed = random.uniform(20, 30)
        self.deceleration = random.uniform(0.05, 0.12)
        self.spinning = True
        self.spin_btn.config(state=tk.DISABLED)
        self.result_label.config(text="Колесо крутится...", fg="white")

        self.animate_spin()


    def animate_spin(self):
        if not self.spinning:
            return

        self.current_angle = (self.current_angle + self.spin_speed) % 360
        if self.spin_speed > 0:
            self.spin_speed -= self.deceleration

        self.draw_wheel(self.current_angle)

        if self.spin_speed <= 0.5:
            self.spinning = False
            self.spin_btn.config(state=tk.NORMAL)
            self.finish_spin()
        else:
            self.root.after(30, self.animate_spin)


    def draw_wheel(self, angle_offset):
        self.canvas.delete("wheel")

        cx = self.wheel_center
        cy = self.wheel_center
        r = self.wheel_radius

        start_angle = angle_offset

        for i, (color, number) in enumerate(self.sectors):
            a1 = start_angle + i * self.sector_angle

            fill_color = "green" if number == 0 else color

            self.canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=a1, extent=self.sector_angle,
                fill=fill_color, outline="white", width=2,
                tags="wheel"
            )

            mid_angle = math.radians(a1 + self.sector_angle / 2)
            text_r = r * 0.72
            tx = cx + text_r * math.cos(mid_angle)
            ty = cy - text_r * math.sin(mid_angle)
            self.canvas.create_text(
                tx, ty,
                text=str(number),
                fill="white",
                font=("Arial", 11, "bold"),
                tags="wheel"
            )

        self.canvas.create_oval(
            cx - 50, cy - 50, cx + 50, cy + 50,
            fill="#222222", outline="white", width=2,
            tags="wheel"
        )


    def finish_spin(self):
        pointer_angle = 90
        base_angle = self.current_angle % 360
        diff = (pointer_angle - base_angle) % 360
        sector_index = int(diff // self.sector_angle) % len(self.sectors)

        result_color, result_number = self.sectors[sector_index]
        result_color_display = (
            "Зелёный" if result_number == 0
            else ("Красный" if result_color == "red" else "Чёрный")
        )

        if result_number == 0:
            text = (
                f"Выпало: {result_number} ({result_color_display})\n"
                f"0 — дом выигрывает, ставка проиграна: ${self.bet}"
            )
            self.result_label.config(text=text, fg="#db4437")
        else:
            if result_color == self.selected_color:
                win = self.bet * 2
                self.balance += win
                text = (
                    f"Выпало: {result_number} ({result_color_display})\n"
                    f"Ты выиграл: ${win}"
                )
                self.result_label.config(text=text, fg="#0f9d58")
            else:
                text = (
                    f"Выпало: {result_number} ({result_color_display})\n"
                    f"Ты проиграл ставку: ${self.bet}"
                )
                self.result_label.config(text=text, fg="#db4437")

        self.balance_label.config(text=f"Баланс: ${self.balance}")
        self.bet_entry.delete(0, tk.END)
        self.selected_color = None
        self.red_btn.config(relief="raised")
        self.black_btn.config(relief="raised")


        if self.balance <= 0:
            if self.loan_active:
                messagebox.showinfo(
                    "Коллекторы пришли",
                    "Ты проиграл все деньги, не вернув кредит.\n"
                    "Коллекторы забрали всё. Игра окончена."
                )
            else:
                messagebox.showinfo("Конец", "Баланс 0! Игра окончена.")
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = RouletteGame(root)
    root.mainloop()