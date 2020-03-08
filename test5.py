import tkinter as tk
from PIL import Image, ImageTk


class MainWindow(tk.Tk):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.overrideredirect(True)
        self.frame = tk.Frame(self, relief="flat", bd=0)

        self.label = tk.Label()

    def mainloop(self, n=0):
        while self.winfo_exists():
            background = Image.frombytes("RGB", ..., ...)
            tk_backkground = ImageTk.PhotoImage(background)

            self.label.config(image=tk_backkground)
            self.update()
            self.update_idletasks()


if __name__ == '__main__':
    root = MainWindow()
    root.mainloop()
