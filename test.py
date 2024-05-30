import tkinter as tk
from tkinter import scrolledtext
from pywinauto import Desktop


class TaskbarMonitorApp:

    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.title("Taskbar Monitor")
        self.main_window.configure(bg='#2e2e2e')

        self.text_area = scrolledtext.ScrolledText(main_window,
                                                   wrap=tk.WORD,
                                                   width=100,
                                                   height=30,
                                                   bg='#1e1e1e',
                                                   fg='white',
                                                   font=("Helvetica", 10))
        self.text_area.pack(pady=10)

        self.start_button = tk.Button(main_window,
                                      text="Start Monitoring",
                                      command=self.start_monitoring,
                                      bg='#444444',
                                      fg='white',
                                      font=("Helvetica", 12))
        self.start_button.pack(pady=10)

        self.whitelist = ['Program Manager', 'Панель задач', 'Taskbar Monitor']

        self.stop_monitoring = False

    def get_taskbar_windows(self, wtype: str) -> list:
        all_windows = Desktop(backend="uia").windows()
        taskbar_windows = []
        for window in all_windows:
            if wtype == 'all':
                if window.is_visible():
                    taskbar_windows.append({
                        'title': window.window_text(),
                        'handle': window.handle
                    })
            elif wtype == 'current':
                if window.is_active():
                    taskbar_windows.append({
                        'title': window.window_text(),
                        'handle': window.handle
                    })
        return taskbar_windows

    def start_monitoring(self):
        self.start_button.config(state=tk.DISABLED)
        self.main_window.iconify()
        self.main_window.after(2000, self.add_current_to_whitelist)

    def add_current_to_whitelist(self):
        current_window = self.get_taskbar_windows(wtype='current')
        if current_window:
            self.whitelist.append(current_window[0]['title'])
        self.monitor_taskbar()

    def monitor_taskbar(self):
        self.update_taskbar_windows()
        if not self.stop_monitoring:
            self.main_window.after(2000, self.monitor_taskbar)

    def update_taskbar_windows(self):
        taskbar_windows = self.get_taskbar_windows(wtype='all')
        self.text_area.delete(1.0, tk.END)

        if taskbar_windows:
            self.text_area.insert(tk.END, "Открытые окна на панели задач:\n")
            for idx, window in enumerate(taskbar_windows):
                self.text_area.insert(
                    tk.END, f"{idx + 1}. "
                    f"Заголовок: {window['title']}, "
                    f"Хэндл: {window['handle']}\n")

                if window['title'] not in self.whitelist:
                    self.text_area.insert(
                        tk.END, f"Закрытие окна: {window['title']}\n")

                    app = Desktop(backend="uia").window(
                        handle=window['handle'])
                    app.close()
        else:
            self.text_area.insert(tk.END,
                                  "Нет открытых окон на панели задач.\n")

        self.main_window.update()

    def on_closing(self):
        self.stop_monitoring = True
        self.main_window.destroy()


if __name__ == "__main__":
    main_interface = tk.Tk()
    taskbar_monitor = TaskbarMonitorApp(main_interface)
    main_interface.protocol("WM_DELETE_WINDOW", taskbar_monitor.on_closing)
    main_interface.mainloop()
