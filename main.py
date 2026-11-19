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