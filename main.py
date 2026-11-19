import time
import tkinter as tk
from tkinter import messagebox, ttk


def format_time(seconds: float) -> str:
    # Переводим секунды в формат ЧЧ:ММ:СС.сс
    total_cs = int(round(max(0.0, seconds) * 100))
    hours, rem = divmod(total_cs, 360000)
    minutes, rem = divmod(rem, 6000)
    secs, cs = divmod(rem, 100)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{cs:02d}"


class Stopwatch:
    """Логика секундомера."""

    def __init__(self) -> None:
        self.is_running = False
        self.start_time = 0.0
        self.elapsed = 0.0
        self.last_lap = 0.0
        self.laps: list[tuple[int, float, float]] = []

    def start(self) -> None:
        if not self.is_running:
            # Используем perf_counter, чтобы время не плыло при лагах интерфейса
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
    """Логика таймера обратного отсчёта."""

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
    """Главное окно приложения."""

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

    def report_callback_exception(self, exc, val, tb) -> None:
        # Перехватываем любые непредвиденные ошибки Tkinter, чтобы окно не закрывалось
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n{val}")

    def _create_menu(self) -> None:
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.destroy)
        menubar.add_cascade(label="Файл", menu=file_menu)

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

        # Верхние вкладки переключения режимов
        top_bar = tk.Frame(self, bg=self.BG_DARK)
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 6))
        top_bar.columnconfigure((0, 1), weight=1)

        self.btn_sw_mode = tk.Button(
            top_bar, text="Секундомер", font=("Segoe UI", 11, "bold"),
            bg=self.BLUE, fg="#11111B", bd=0, pady=8, cursor="hand2",
        )
        self.btn_sw_mode.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_tm_mode = tk.Button(
            top_bar, text="Таймер", font=("Segoe UI", 11, "bold"),
            bg=self.BG_PANEL, fg=self.TEXT_GRAY, bd=0, pady=8, cursor="hand2",
        )
        self.btn_tm_mode.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Табло времени
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

        # Рабочая область (таблица кругов или ввод интервала таймера)
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

        # Нижняя панель кнопок
        self.btn_bar = tk.Frame(self, bg=self.BG_DARK)
        self.btn_bar.grid(row=3, column=0, sticky="ew", padx=15, pady=(6, 10))

        self.btn_start = tk.Button(
            self.btn_bar, text="Старт", font=("Segoe UI", 11, "bold"),
            bg=self.GREEN, fg="#11111B", bd=0, pady=10, cursor="hand2",
        )
        self.btn_lap = tk.Button(
            self.btn_bar, text="Круг", font=("Segoe UI", 11, "bold"),
            bg=self.BLUE, fg="#11111B", bd=0, pady=10, cursor="hand2",
        )
        self.btn_reset = tk.Button(
            self.btn_bar, text="Сброс", font=("Segoe UI", 11, "bold"),
            bg=self.RED, fg="#11111B", bd=0, pady=10, cursor="hand2",
        )
        self._place_buttons(is_stopwatch=True)

        tk.Label(
            self, textvariable=self.status_var, bg=self.BG_PANEL,
            fg=self.TEXT_GRAY, anchor="w", padx=12, pady=5, font=("Segoe UI", 9),
        ).grid(row=4, column=0, sticky="ew")

    def _place_buttons(self, is_stopwatch: bool) -> None:
        # В секундомере 3 кнопки (Старт, Круг, Сброс), в таймере — 2 (Старт, Сброс)
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

    def _set_window_size(self, width: int, height: int) -> None:
        self.geometry(f"{width}x{height}")
        self.status_var.set(f"Размер окна: {width}×{height}")

    def _toggle_resizable(self) -> None:
        allowed = self.resizable_var.get()
        self.resizable(allowed, allowed)
        self.status_var.set(
            f"Изменение размера окна: {'разрешено' if allowed else 'запрещено'}"
        )


if __name__ == "__main__":
    app = TimerStopwatchApp()
    app.mainloop()