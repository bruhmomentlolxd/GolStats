"""Inicia GolStats como una aplicación de escritorio.

Lo usa iniciar.bat (doble clic). Arranca el servidor y abre la app en su propia ventana.
Variables opcionales:
  GOLSTATS_LAN=1        permite entrar desde otros dispositivos de la misma red WiFi (ej. el celular)
  GOLSTATS_NO_BROWSER=1 no abre la ventana automáticamente
"""
import os
import socket
import subprocess
import threading
import webbrowser

from app import app

BROWSERS_WINDOWS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def free_port(host, start=5000, end=5030):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    raise RuntimeError("No hay puertos libres entre 5000 y 5030.")


def local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))  # no envía nada: solo averigua qué IP usaría esta PC
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def open_window(url):
    """Abre la app en una ventana propia (sin barra de pestañas) usando Edge o Chrome."""
    for exe in BROWSERS_WINDOWS:
        if os.path.exists(exe):
            subprocess.Popen([exe, f"--app={url}", "--window-size=1200,860"])
            return
    webbrowser.open(url)


def main():
    lan = os.environ.get("GOLSTATS_LAN") == "1"
    host = "0.0.0.0" if lan else "127.0.0.1"
    port = free_port(host)
    url = f"http://127.0.0.1:{port}"

    print("=" * 56)
    print("  GolStats funcionando")
    print(f"  En esta PC:  {url}")
    if lan:
        print(f"  En el celular (mismo WiFi):  http://{local_ip()}:{port}")
    print("  Para cerrar la app: cerra esta ventana negra.")
    print("=" * 56)

    if os.environ.get("GOLSTATS_NO_BROWSER") != "1":
        threading.Timer(1.5, open_window, args=(url,)).start()

    try:
        from waitress import serve
        serve(app, host=host, port=port, threads=4)
    except ImportError:  # sin waitress: servidor de Flask (también sirve)
        app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
