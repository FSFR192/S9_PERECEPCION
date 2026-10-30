# -*- coding: utf-8 -*-
"""
Servidor local para el Dashboard de Monitoreo Sismográfico Volcánico.
Utiliza únicamente la librería estándar de Python (no requiere instalaciones adicionales).

Uso:
    python servidor_dashboard.py
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PUERTO = 8050
DIRECTORIO = os.path.dirname(os.path.abspath(__file__))

class ManejadorArchivos(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORIO, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

def main():
    os.chdir(DIRECTORIO)
    url = f"http://localhost:{PUERTO}/dashboard_interactivo.html"
    
    print("=" * 65)
    print("  🌋 CENTRO DE MONITOREO SISMOGRÁFICO VOLCÁNICO")
    print("=" * 65)
    print(f"-> Servidor iniciado en: {url}")
    print(f"-> Abriendo navegador automáticamente...")
    print("-> Presione Ctrl + C para detener el servidor.")
    print("=" * 65)

    webbrowser.open(url)

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PUERTO), ManejadorArchivos) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"\nAviso al iniciar servidor en puerto {PUERTO}: {e}")
        print("Abriendo archivo HTML directamente de forma local...")
        webbrowser.open(os.path.join(DIRECTORIO, "dashboard_interactivo.html"))

if __name__ == "__main__":
    main()

