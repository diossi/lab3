import time
import tkinter as tk
from tkinter import messagebox, ttk


def format_time(seconds: float) -> str:
    total_cs = int(round(max(0.0, seconds) * 100))
    hours, rem = divmod(total_cs, 360000)
    minutes, rem = divmod(rem, 6000)
    secs, cs = divmod(rem, 100)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{cs:02d}"


class Stopwatch:
    def __init__(self) -> None:
        self.is_running = False
        self.start_time = 0.0
        self.elapsed = 0.0
        self.last_lap = 0.0
        self.laps: list[tuple[int, float, float]] = []

    def start(self) -> None:
        if not self.is_running:
            self.start_time = time.perf_counter()
            self.is_running = True

    def pause(self) -> None:
        if self.is_running:
            self.elapsed += time.perf_counter() - self.start_time
            self.is_running = False

    def reset(self) -> None:
        self.is_running = False
        self.start_time = self.elapsed = self.last_lap = 0.0
        self.laps.clear()

    def get_time(self) -> float:
        if self.is_running:
            return self.elapsed + (time.perf_counter() - self.start_time)
        return self.elapsed

    def add_lap(self) -> tuple[int, float, float]:
        if not self.is_running:
            raise RuntimeError("Сначала запустите секундомер, чтобы записать круг.")
        total = self.get_time()
        record = (len(self.laps) + 1, total - self.last_lap, total)
        self.last_lap = total
        self.laps.append(record)
        return record


class CountdownTimer:
    def __init__(self) -> None:
        self.is_running = False
        self.total_seconds = 0.0
        self.remaining = 0.0
        self.end_time = 0.0

    def set_time(self, hours: int, minutes: int, seconds: int) -> None:
        if not (0 <= hours <= 99):
            raise ValueError("Часы должны быть целым числом от 0 до 99.")
        if not (0 <= minutes <= 59):
            raise ValueError("Минуты должны быть целым числом от 0 до 59.")
        if not (0 <= seconds <= 59):
            raise ValueError("Секунды должны быть целым числом от 0 до 59.")

        duration = float(hours * 3600 + minutes * 60 + seconds)
        if duration <= 0:
            raise ValueError("Укажите время таймера больше 0 секунд.")

        self.is_running = False
        self.total_seconds = self.remaining = duration

    def start(self) -> None:
        if self.remaining <= 0:
            raise ValueError("Задайте время таймера перед запуском.")
        if not self.is_running:
            self.end_time = time.perf_counter() + self.remaining
            self.is_running = True

    def pause(self) -> None:
        if self.is_running:
            self.remaining = max(0.0, self.end_time - time.perf_counter())
            self.is_running = False

    def reset(self) -> None:
        self.is_running = False
        self.remaining = self.total_seconds

    def get_time(self) -> tuple[float, bool]:
        if not self.is_running:
            return self.remaining, False
        rem = self.end_time - time.perf_counter()
        if rem <= 0:
            self.remaining = 0.0
            self.is_running = False
            return 0.0, True
        return rem, False


class TimerStopwatchApp(tk.Tk):

    BG_DARK, BG_PANEL, BG_ENTRY = "#1E1E2E", "#2A2A3D", "#313244"
    TEXT_LIGHT, TEXT_GRAY = "#CDD6F4", "#A6ADC8"
    BLUE, GREEN, YELLOW, RED = "#89B4FA", "#A6E3A1", "#F9E2AF", "#F38BA8"

    def __init__(self) -> None:
        super().__init__()
        self.stopwatch = Stopwatch()
        self.timer = CountdownTimer()
        self.mode = "stopwatch"

        self.resizable_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Готов к работе")
        self.hours_var = tk.StringVar(value="00")
        self.minutes_var = tk.StringVar(value="05")
        self.seconds_var = tk.StringVar(value="00")

        self.title("Таймер-секундомер")
        self.geometry("500x580")
        self.minsize(400, 460)
        self.configure(bg=self.BG_DARK)

        self._create_menu()
        self._create_widgets()

        self.timer.set_time(0, 5, 0)
        self._update_screen()
        self.after(30, self._tick)

    def report_callback_exception(self, exc, val, tb) -> None:
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n{val}")

    def _create_menu(self) -> None:
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Сбросить", command=self._on_reset)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.destroy)
        menubar.add_cascade(label="Файл", menu=file_menu)

        mode_menu = tk.Menu(menubar, tearoff=0)
        mode_menu.add_command(
            label="Секундомер", command=lambda: self._switch_mode("stopwatch")
        )
        mode_menu.add_command(
            label="Таймер", command=lambda: self._switch_mode("timer")
        )
        menubar.add_cascade(label="Режим", menu=mode_menu)

        window_menu = tk.Menu(menubar, tearoff=0)
        for label, w, h in [
            ("Компактный (420×480)", 420, 480),
            ("Стандартный (500×580)", 500, 580),
            ("Крупный (660×720)", 660, 720),
        ]:
            window_menu.add_command(
                label=label, command=lambda ww=w, hh=h: self._set_window_size(ww, hh)
            )
        window_menu.add_separator()
        window_menu.add_checkbutton(
            label="Разрешить изменение размеров",
            variable=self.resizable_var,
            command=self._toggle_resizable,
        )
        menubar.add_cascade(label="Окно", menu=window_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="О программе",
            command=lambda: messagebox.showinfo(
                "О программе", "Программа «Таймер-секундомер» (Python + Tkinter)."
            ),
        )
        menubar.add_cascade(label="Справка", menu=help_menu)
        self.config(menu=menubar)

    def _create_widgets(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview", background=self.BG_PANEL, foreground=self.TEXT_LIGHT,
            fieldbackground=self.BG_PANEL, borderwidth=0, rowheight=25,
            font=("Consolas", 10),
        )
        style.configure(
            "Treeview.Heading", background=self.BG_ENTRY,
            foreground=self.TEXT_LIGHT, font=("Segoe UI", 10, "bold"),
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        top_bar = tk.Frame(self, bg=self.BG_DARK)
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 6))
        top_bar.columnconfigure((0, 1), weight=1)

        self.btn_sw_mode = tk.Button(
            top_bar, text="Секундомер", font=("Segoe UI", 11, "bold"),
            bg=self.BLUE, fg="#11111B", bd=0, pady=8, cursor="hand2",
            command=lambda: self._switch_mode("stopwatch"),
        )
        self.btn_sw_mode.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_tm_mode = tk.Button(
            top_bar, text="Таймер", font=("Segoe UI", 11, "bold"),
            bg=self.BG_PANEL, fg=self.TEXT_GRAY, bd=0, pady=8, cursor="hand2",
            command=lambda: self._switch_mode("timer"),
        )
        self.btn_tm_mode.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        
        display_box = tk.Frame(self, bg=self.BG_PANEL, padx=15, pady=18)
        display_box.grid(row=1, column=0, sticky="ew", padx=15, pady=6)
        display_box.columnconfigure(0, weight=1)

        self.mode_label = tk.Label(
            display_box, text="СЕКУНДОМЕР", bg=self.BG_PANEL,
            fg=self.TEXT_GRAY, font=("Segoe UI", 9, "bold"),
        )
        self.mode_label.grid(row=0, column=0)

        self.time_label = tk.Label(
            display_box, text="00:00:00.00", bg=self.BG_PANEL,
            fg=self.TEXT_LIGHT, font=("Consolas", 38, "bold"),
        )
        self.time_label.grid(row=1, column=0, pady=6)

        self.workspace = tk.Frame(self, bg=self.BG_DARK)
        self.workspace.grid(row=2, column=0, sticky="nsew", padx=15, pady=6)
        self.workspace.columnconfigure(0, weight=1)
        self.workspace.rowconfigure(0, weight=1)

        self.sw_frame = tk.Frame(self.workspace, bg=self.BG_PANEL)
        self.sw_frame.grid(row=0, column=0, sticky="nsew")
        self.sw_frame.columnconfigure(0, weight=1)
        self.sw_frame.rowconfigure(0, weight=1)

        self.laps_table = ttk.Treeview(
            self.sw_frame, columns=("num", "lap", "total"), show="headings"
        )
        for col, title, width in (
            ("num", "Круг №", 75),
            ("lap", "Время круга", 150),
            ("total", "Общее время", 150),
        ):
            self.laps_table.heading(col, text=title)
            self.laps_table.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(
            self.sw_frame, orient="vertical", command=self.laps_table.yview
        )
        self.laps_table.configure(yscrollcommand=scrollbar.set)
        self.laps_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tm_frame = tk.Frame(self.workspace, bg=self.BG_PANEL, padx=15, pady=20)
        self.tm_frame.grid(row=0, column=0, sticky="nsew")
        self.tm_frame.columnconfigure((0, 1, 2), weight=1)

        tk.Label(
            self.tm_frame, text="Введите время (ЧЧ : ММ : СС)",
            bg=self.BG_PANEL, fg=self.TEXT_LIGHT, font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, columnspan=3, pady=(0, 12))

        for col, (title, var) in enumerate((
            ("Часы (0–99)", self.hours_var),
            ("Минуты (0–59)", self.minutes_var),
            ("Секунды (0–59)", self.seconds_var),
        )):
            tk.Label(
                self.tm_frame, text=title, bg=self.BG_PANEL,
                fg=self.TEXT_GRAY, font=("Segoe UI", 9),
            ).grid(row=1, column=col, pady=(0, 4))
            tk.Entry(
                self.tm_frame, textvariable=var, justify="center", width=5,
                font=("Consolas", 18, "bold"), bg=self.BG_ENTRY,
                fg=self.TEXT_LIGHT, insertbackground=self.TEXT_LIGHT, relief="flat",
            ).grid(row=2, column=col, padx=6, ipady=6)

        self.tm_frame.grid_remove()

        self.btn_bar = tk.Frame(self, bg=self.BG_DARK)
        self.btn_bar.grid(row=3, column=0, sticky="ew", padx=15, pady=(6, 10))

        self.btn_start = tk.Button(
            self.btn_bar, text="Старт", font=("Segoe UI", 11, "bold"),
            bg=self.GREEN, fg="#11111B", bd=0, pady=10, cursor="hand2",
            command=self._on_start_pause,
        )
        self.btn_lap = tk.Button(
            self.btn_bar, text="Круг", font=("Segoe UI", 11, "bold"),
            bg=self.BLUE, fg="#11111B", bd=0, pady=10, cursor="hand2",
            command=self._on_lap,
        )
        self.btn_reset = tk.Button(
            self.btn_bar, text="Сброс", font=("Segoe UI", 11, "bold"),
            bg=self.RED, fg="#11111B", bd=0, pady=10, cursor="hand2",
            command=self._on_reset,
        )
        self._place_buttons(is_stopwatch=True)

        tk.Label(
            self, textvariable=self.status_var, bg=self.BG_PANEL,
            fg=self.TEXT_GRAY, anchor="w", padx=12, pady=5, font=("Segoe UI", 9),
        ).grid(row=4, column=0, sticky="ew")

        self.bind("<Configure>", self._on_window_resize)

    def _place_buttons(self, is_stopwatch: bool) -> None:
        for btn in (self.btn_start, self.btn_lap, self.btn_reset):
            btn.grid_forget()

        if is_stopwatch:
            self.btn_bar.columnconfigure((0, 1, 2), weight=1, uniform="btns")
            self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            self.btn_lap.grid(row=0, column=1, sticky="ew", padx=5)
            self.btn_reset.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        else:
            self.btn_bar.columnconfigure(2, weight=0, uniform="")
            self.btn_bar.columnconfigure((0, 1), weight=1, uniform="btns")
            self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            self.btn_reset.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def _switch_mode(self, new_mode: str) -> None:
        if self.mode == new_mode:
            return
        self.mode = new_mode
        is_sw = new_mode == "stopwatch"

        if is_sw:
            self.tm_frame.grid_remove()
            self.sw_frame.grid()
            self.mode_label.config(text="СЕКУНДОМЕР")
            self.btn_sw_mode.config(bg=self.BLUE, fg="#11111B")
            self.btn_tm_mode.config(bg=self.BG_PANEL, fg=self.TEXT_GRAY)
            self.status_var.set("Режим: Секундомер")
        else:
            self.sw_frame.grid_remove()
            self.tm_frame.grid()
            self.mode_label.config(text="ТАЙМЕР ОБРАТНОГО ОТСЧЁТА")
            self.btn_tm_mode.config(bg=self.BLUE, fg="#11111B")
            self.btn_sw_mode.config(bg=self.BG_PANEL, fg=self.TEXT_GRAY)
            self.status_var.set("Режим: Таймер")

        self._place_buttons(is_sw)
        self._update_start_button()
        self._update_screen()

    def _read_timer_inputs(self) -> None:
        raw_values = [
            self.hours_var.get().strip(),
            self.minutes_var.get().strip(),
            self.seconds_var.get().strip(),
        ]
        if not all(raw_values):
            raise ValueError("Заполните все поля времени (часы, минуты, секунды).")
        try:
            hours, minutes, seconds = map(int, raw_values)
        except ValueError as err:
            raise ValueError("В полях времени допускаются только целые числа.") from err

        self.timer.set_time(hours, minutes, seconds)
        self.hours_var.set(f"{hours:02d}")
        self.minutes_var.set(f"{minutes:02d}")
        self.seconds_var.set(f"{seconds:02d}")

    def _on_start_pause(self) -> None:
        try:
            if self.mode == "stopwatch":
                if self.stopwatch.is_running:
                    self.stopwatch.pause()
                    self.status_var.set("Секундомер на паузе")
                else:
                    self.stopwatch.start()
                    self.status_var.set("Секундомер запущен")
            else:
                if self.timer.is_running:
                    self.timer.pause()
                    self.status_var.set("Таймер на паузе")
                else:
                    if self.timer.remaining in (0.0, self.timer.total_seconds):
                        self._read_timer_inputs()
                    self.timer.start()
                    self.status_var.set("Таймер запущен")
        except ValueError as err:
            messagebox.showwarning("Некорректный ввод", str(err))
            self.status_var.set(f"Ошибка: {err}")

        self._update_start_button()
        self._update_screen()

    def _on_lap(self) -> None:
        try:
            num, lap_sec, total_sec = self.stopwatch.add_lap()
            self.laps_table.insert(
                "", 0,
                values=(f"#{num:02d}", format_time(lap_sec), format_time(total_sec)),
            )
            self.status_var.set(f"Записан круг #{num}")
        except RuntimeError as err:
            messagebox.showinfo("Внимание", str(err))

    def _on_reset(self) -> None:
        if self.mode == "stopwatch":
            self.stopwatch.reset()
            self.laps_table.delete(*self.laps_table.get_children())
            self.status_var.set("Секундомер сброшен")
        else:
            try:
                self._read_timer_inputs()
            except ValueError as err:
                self.timer.reset()
                messagebox.showwarning("Некорректный ввод", str(err))
            self.status_var.set("Таймер сброшен")

        self._update_start_button()
        self._update_screen()

    def _update_start_button(self) -> None:
        if self.mode == "stopwatch":
            running = self.stopwatch.is_running
            started = self.stopwatch.elapsed > 0
        else:
            running = self.timer.is_running
            started = 0 < self.timer.remaining < self.timer.total_seconds

        if running:
            self.btn_start.config(text="Пауза", bg=self.YELLOW)
        elif started:
            self.btn_start.config(text="Продолжить", bg=self.GREEN)
        else:
            self.btn_start.config(text="Старт", bg=self.GREEN)

    def _update_screen(self) -> None:
        if self.mode == "stopwatch":
            self.time_label.config(
                text=format_time(self.stopwatch.get_time()), fg=self.TEXT_LIGHT
            )
        else:
            rem, finished = self.timer.get_time()
            warn = 0 < rem <= 10 and self.timer.is_running
            self.time_label.config(
                text=format_time(rem), fg=self.RED if warn else self.TEXT_LIGHT
            )
            if finished:
                self._update_start_button()
                self.status_var.set("Время вышло!")
                self.bell()
                messagebox.showinfo("Таймер", "Время вышло!")

    def _tick(self) -> None:
        self._update_screen()
        self.after(30, self._tick)

    def _set_window_size(self, width: int, height: int) -> None:
        self.geometry(f"{width}x{height}")
        self.status_var.set(f"Размер окна: {width}×{height}")

    def _toggle_resizable(self) -> None:
        allowed = self.resizable_var.get()
        self.resizable(allowed, allowed)
        self.status_var.set(
            f"Изменение размера окна: {'разрешено' if allowed else 'запрещено'}"
        )

    def _on_window_resize(self, event) -> None:
        if event.widget is self:
            font_size = max(26, min(64, event.width // 12))
            self.time_label.config(font=("Consolas", font_size, "bold"))


if __name__ == "__main__":
    app = TimerStopwatchApp()
    app.mainloop()