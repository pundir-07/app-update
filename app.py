# app.py
import tkinter as tk
from updater import main as check_for_updates
def main():
    root = tk.Tk()
    root.title("My Python App Version Updated")
    root.geometry("300x150")
    check_for_updates()
    label = tk.Label(root, text="Hello, this is my app!")
    label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
