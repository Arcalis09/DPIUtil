import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import json
import os
import sys
import psutil

CONFIG_FILE = "config.json"
dpi_process = None

# Windows özel bayrak (arka planda başlatmak için)
if os.name == 'nt':
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
else:
    CREATE_NO_WINDOW = 0

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def get_goodbyedpi_path():
    config = load_config()
    return config.get("dpi_path", "")

def choose_exe():
    path = filedialog.askopenfilename(title="Select goodbyedpi.exe", filetypes=[("Executable files", "*.exe")])
    if path and os.path.basename(path).lower() == "goodbyedpi.exe":
        save_config({"dpi_path": path})
        status_label.config(text="Path saved!")
    else:
        messagebox.showerror("Error", "Please select a valid goodbyedpi.exe")

def run_goodbyedpi(args):
    global dpi_process
    exe_path = get_goodbyedpi_path()
    if not exe_path or not os.path.exists(exe_path):
        messagebox.showwarning("No Path", "Please choose a GoodbyeDPI path first.")
        status_label.config(text="Please choose a path")
        return

    if dpi_process and dpi_process.poll() is None:
        messagebox.showinfo("Already running", "GoodbyeDPI is already running.")
        return

    try:
        full_args = [exe_path] + args.split()
        dpi_process = subprocess.Popen(
            full_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW  # <- pencere açılmasını engeller
        )
        status_label.config(text="GoodbyeDPI started.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start: {str(e)}")

def stop_goodbyedpi():
    global dpi_process
    if dpi_process and dpi_process.poll() is None:
        try:
            dpi_process.terminate()
            dpi_process.wait()
            status_label.config(text="GoodbyeDPI stopped.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop: {str(e)}")
    else:
        status_label.config(text="GoodbyeDPI is not running.")

# GUI
root = tk.Tk()
root.title("DPIutil")
root.geometry("320x240")
root.resizable(False, False)

# Arka plan dosyasını PyInstaller ile uyumlu şekilde yükle
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

image_path = os.path.join(base_path, "Space Background.png")
bg_image = Image.open(image_path).resize((320, 240), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Buton stilleri
btn_style = {
    "bg": "black",
    "fg": "white",
    "activebackground": "#222222",
    "activeforeground": "white",
    "font": ("Segoe UI", 10, "bold"),
    "relief": "flat"
}

# Butonlar
tk.Button(root, text="Set GoodbyeDPI Path", command=choose_exe, **btn_style).place(x=90, y=20, width=140)
tk.Button(root, text="Aggressive DPI",
          command=lambda: run_goodbyedpi('-9 --set-ttl 5 --dns-addr 77.88.8.8 --dns-port 1253 '
                                         '--dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253'),
          **btn_style).place(x=90, y=60, width=140)
tk.Button(root, text="Light DPI",
          command=lambda: run_goodbyedpi('-5 --set-ttl 5 --dns-addr 77.88.8.8 --dns-port 1253 '
                                         '--dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253'),
          **btn_style).place(x=90, y=100, width=140)
tk.Button(root, text="Handbrake", command=stop_goodbyedpi, **btn_style).place(x=90, y=140, width=140)

# Status label
status_label = tk.Label(root, text="Welcome to DPIutil", bg="black", fg="lime", font=("Segoe UI", 10))
status_label.place(x=90, y=180, width=140, height=20)

# Download/Upload hız göstergesi
speed_label = tk.Label(root, text="", bg="black", fg="lime", font=("Consolas", 9))
speed_label.place(x=90, y=205, width=140)

# Ağ hızı ölçümü
last_sent = psutil.net_io_counters().bytes_sent
last_recv = psutil.net_io_counters().bytes_recv

def update_speed():
    global last_sent, last_recv
    current = psutil.net_io_counters()
    sent_diff = current.bytes_sent - last_sent
    recv_diff = current.bytes_recv - last_recv
    last_sent = current.bytes_sent
    last_recv = current.bytes_recv

    download_kbps = recv_diff / 1024
    upload_kbps = sent_diff / 1024

    speed_label.config(text=f"↓ {download_kbps:.1f} KB/s\n↑ {upload_kbps:.1f} KB/s")
    root.after(1000, update_speed)

update_speed()
root.mainloop()
