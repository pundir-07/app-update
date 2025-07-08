# app.py
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("My Python App")
    root.geometry("300x150")

    label = tk.Label(root, text="Hello, this is my app!")
    label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
