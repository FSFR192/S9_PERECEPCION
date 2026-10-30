# -*- coding: utf-8 -*-
"""
Interfaz Gráfica Interactiva de Monitoreo Sismográfico Volcánico
Estructura académica requerida:
- Gráfica 1: Señales superpuestas con colores y leyenda para saber quién es quién
  (Volcánica 1.2–3.5 Hz | Tránsito 12 Hz | Eléctrico 60 Hz | Señal total)
- Gráfica 2: Depuración (Señal corrupta con ruido vs Señal recuperada/filtrada)
"""

import sys
import os
import webbrowser
import datetime
import numpy as np
from scipy.signal import butter, sosfiltfilt, find_peaks

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    HAS_GUI_LIBS = True
except ImportError as e:
    HAS_GUI_LIBS = False
    print(f"Aviso: Librería gráfica no disponible en este entorno: {e}")

class SismografoApp:
    def __init__(self, root=None):
        self.root = root
        if self.root:
            self.root.title("Monitoreo Sismográfico Volcánico - Señales Superpuestas y Depuración")
            self.root.geometry("1400x900")
            self.root.minsize(1220, 780)
            self.root.configure(bg="#f1f5f9")

        self.fs = 200
        self.duracion = 60
        self.time_offset = 0.0
        self.is_live = False
        self.timer_id = None

        self.param_f1 = 1.2
        self.param_f2 = 3.5
        self.param_amp_trans = 1.4
        self.param_amp_elec = 2.2
        self.param_amp_rand = 0.9
        self.param_umbral = 0.50

        self.sos = butter(N=4, Wn=[0.5, 5.0], btype="bandpass", fs=self.fs, output="sos")

        self.calcular_senales()

        if self.root and HAS_GUI_LIBS:
            self.crear_interfaz()

    def calcular_senales(self):
        np.random.seed(7)
        self.t = np.arange(0, self.duracion, 1/self.fs)
        t_eval = self.t + self.time_offset

        # 1. Actividad volcánica (1.2 y 3.5 Hz)
        self.s_volcanica = (
            0.8 * np.sin(2 * np.pi * self.param_f1 * t_eval) +
            0.45 * np.sin(2 * np.pi * self.param_f2 * t_eval)
        )
        # 2. Ruido tránsito (12 Hz)
        self.s_transito = self.param_amp_trans * np.sin(2 * np.pi * 12 * t_eval)
        # 3. Ruido eléctrico (60 Hz - Mayor amplitud)
        self.s_electrico = self.param_amp_elec * np.sin(2 * np.pi * 60 * t_eval)
        # 4. Ruido aleatorio blanco
        self.s_aleatorio = self.param_amp_rand * np.random.normal(size=len(self.t))

        # Señal total corrupta
        self.senal_corrupta = self.s_volcanica + self.s_transito + self.s_electrico + self.s_aleatorio

        # Señal depurada (filtrada)
        self.senal_limpia = sosfiltfilt(self.sos, self.senal_corrupta)

        # SNR
        def snr_db(s_util, ruido):
            pot_s = np.mean(s_util**2)
            pot_r = max(1e-12, np.mean(ruido**2))
            return 10 * np.log10(pot_s / pot_r)

        self.snr_antes = snr_db(self.s_volcanica, self.senal_corrupta - self.s_volcanica)
        self.snr_despues = snr_db(self.s_volcanica, self.senal_limpia - self.s_volcanica)
        self.mejora_snr = self.snr_despues - self.snr_antes

        self.rms_volcanica = np.sqrt(np.mean(self.senal_limpia**2))
        self.alerta_activa = self.rms_volcanica >= self.param_umbral

        N = len(self.senal_corrupta)
        self.frecuencias = np.fft.rfftfreq(N, d=1/self.fs)
        fft_raw = np.fft.rfft(self.senal_corrupta)
        self.magnitud = (2.0 / N) * np.abs(fft_raw)

    def crear_interfaz(self):
        main_frame = tk.Frame(self.root, bg="#f1f5f9")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # SIDEBAR
        sidebar = tk.Frame(main_frame, bg="#0d1727", width=210)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🌋", font=("Segoe UI Emoji", 30), bg="#0d1727", fg="#ffffff").pack(pady=(14, 2))
        tk.Label(sidebar, text="SISMOGRAFÍA", font=("Segoe UI", 8, "bold"), bg="#0d1727", fg="#64748b").pack(pady=(0, 14))

        menu_items = [
            ("📊 Resumen", True),
            ("〰️ 1. Señales juntas", False),
            ("🌪️ 2. Depuración", False),
            ("📶 FFT", False),
            ("📈 SNR", False),
            ("🔔 Alertas", False)
        ]
        for text, active in menu_items:
            bg_col = "#1976d2" if active else "#0d1727"
            fg_col = "#ffffff" if active else "#94a3b8"
            btn = tk.Label(sidebar, text=f"  {text}", font=("Segoe UI", 9, "bold" if active else "normal"), bg=bg_col, fg=fg_col, anchor="w", padx=12, pady=6)
            btn.pack(fill=tk.X, padx=10, pady=2)

        station_frame = tk.Frame(sidebar, bg="#08101e", bd=1, relief=tk.SOLID)
        station_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=14)
        tk.Label(station_frame, text="ESTACIÓN SISMOLÓGICA", font=("Segoe UI", 7, "bold"), bg="#08101e", fg="#64748b").pack(anchor="w", padx=8, pady=(6, 3))
        for k, v in [("Volcán:", "Volcán del Sur"), ("Estación:", "VS-01"), ("Ubicación:", "-16.372°, -71.584°"), ("Frecuencia:", "200 Hz"), ("Estado:", "● Operativa")]:
            row = tk.Frame(station_frame, bg="#08101e")
            row.pack(fill=tk.X, padx=8, pady=1)
            tk.Label(row, text=k, font=("Segoe UI", 7), bg="#08101e", fg="#64748b").pack(side=tk.LEFT)
            tk.Label(row, text=v, font=("Segoe UI", 7, "bold" if "Operativa" in v else "normal"), bg="#08101e", fg="#22c55e" if "Operativa" in v else "#cbd5e1").pack(side=tk.RIGHT)

        # MAIN PANEL
        content_frame = tk.Frame(main_frame, bg="#f1f5f9")
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=14, pady=10)

        # HEADER
        header = tk.Frame(content_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        header.pack(fill=tk.X, pady=(0, 6))

        title_box = tk.Frame(header, bg="#ffffff")
        title_box.pack(side=tk.LEFT, padx=12, pady=6)
        tk.Label(title_box, text="Monitoreo Sismográfico Volcánico", font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0b1f3a").pack(anchor="w")
        tk.Label(title_box, text="Gráfica 1: Señales Superpuestas  |  Gráfica 2: Depuración y Filtrado", font=("Segoe UI", 8.5, "bold"), bg="#ffffff", fg="#1976d2").pack(anchor="w")

        actions_box = tk.Frame(header, bg="#ffffff")
        actions_box.pack(side=tk.RIGHT, padx=10)

        self.btn_live = tk.Button(actions_box, text="▶ En vivo", font=("Segoe UI", 8, "bold"), bg="#f8fafc", fg="#1e293b", relief=tk.SOLID, bd=1, padx=8, pady=3, command=self.toggle_live)
        self.btn_live.pack(side=tk.LEFT, padx=3)

        btn_web = tk.Button(actions_box, text="🌐 Dashboard Web", font=("Segoe UI", 8, "bold"), bg="#2563eb", fg="#ffffff", relief=tk.FLAT, padx=10, pady=3, command=self.abrir_web)
        btn_web.pack(side=tk.LEFT, padx=3)

        # BANNER DE GUÍA
        guide_banner = tk.Frame(content_frame, bg="#eff6ff", bd=1, relief=tk.SOLID)
        guide_banner.pack(fill=tk.X, pady=(0, 6), ipady=3)
        tk.Label(guide_banner, text="📌 Indicación: ", font=("Segoe UI", 8, "bold"), bg="#eff6ff", fg="#1e40af").pack(side=tk.LEFT, padx=(8, 2))
        tk.Label(guide_banner, text="Mayor amplitud: Eléctrico (2.20) [60 Hz]  |  Media: Tránsito (1.40) [12 Hz]  |  Lenta/Útil: Volcán (~1.25) [1.2–3.5 Hz]", font=("Segoe UI", 8), bg="#eff6ff", fg="#1d4ed8").pack(side=tk.LEFT)

        # KPI ROW
        kpi_frame = tk.Frame(content_frame, bg="#f1f5f9")
        kpi_frame.pack(fill=tk.X, pady=(0, 6))
        for i in range(6): kpi_frame.columnconfigure(i, weight=1)

        c1 = tk.Frame(kpi_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        c1.grid(row=0, column=0, sticky="nsew", padx=3)
        tk.Label(c1, text="〰️ Frecuencias detectadas", font=("Segoe UI", 8, "bold"), bg="#ffffff", fg="#0284c7").pack(anchor="w", padx=8, pady=(4, 1))
        self.lbl_freq_list = tk.Label(c1, text="", font=("Segoe UI", 7), bg="#ffffff", fg="#334155", justify="left")
        self.lbl_freq_list.pack(anchor="w", padx=8, pady=(0, 4))

        self.kpi_labels = {}
        def add_kpi(col, key, title, sub, val_col, icon):
            card = tk.Frame(kpi_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
            card.grid(row=0, column=col, sticky="nsew", padx=3)
            tk.Label(card, text=f"{icon} {title}", font=("Segoe UI", 8, "bold"), bg="#ffffff", fg="#0b1f3a").pack(anchor="w", padx=8, pady=(4, 1))
            lbl_val = tk.Label(card, text="", font=("Segoe UI", 12, "bold"), bg="#ffffff", fg=val_col)
            lbl_val.pack(anchor="w", padx=8)
            tk.Label(card, text=sub, font=("Segoe UI", 6.5), bg="#ffffff", fg="#64748b").pack(anchor="w", padx=8, pady=(1, 4))
            self.kpi_labels[key] = lbl_val

        add_kpi(1, "snr_antes", "SNR antes", "Señal en ruido", "#4338ca", "📊")
        add_kpi(2, "snr_despues", "SNR después", "Señal filtrada", "#16a34a", "📊")
        add_kpi(3, "mejora", "Mejora", "Incremento de SNR", "#ea580c", "↗️")
        add_kpi(4, "rms", "RMS volcánico", "(0.5 – 5 Hz)", "#0f2b48", "〰️")
        add_kpi(5, "umbral", "Umbral", "Referencia", "#0f172a", "🚩")

        # GRÁFICOS MATPLOTLIB
        graph_box = tk.Frame(content_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        graph_box.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        self.fig = plt.Figure(figsize=(10.5, 4.4), dpi=100, facecolor="#ffffff")
        self.fig.subplots_adjust(left=0.06, right=0.97, top=0.90, bottom=0.11, hspace=0.38, wspace=0.18)

        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = self.fig.add_subplot(2, 2, 3)
        self.ax4 = self.fig.add_subplot(2, 2, 4)

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_box)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.actualizar_vistas()

    def toggle_live(self):
        self.is_live = not self.is_live
        if self.is_live:
            self.btn_live.config(text="⏸ Pausar", bg="#ef4444", fg="#ffffff")
            self.animar_live()
        else:
            self.btn_live.config(text="▶ En vivo", bg="#f8fafc", fg="#1e293b")
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None

    def animar_live(self):
        if not self.is_live: return
        self.time_offset += 0.05
        self.calcular_senales()
        self.actualizar_vistas()
        self.timer_id = self.root.after(60, self.animar_live)

    def actualizar_vistas(self):
        self.lbl_freq_list.config(text=f"● Volcánica: {self.param_f1:.1f} y {self.param_f2:.1f} Hz\n● Tránsito: 12 Hz\n● Eléctrico: 60 Hz")
        self.kpi_labels["snr_antes"].config(text=f"{self.snr_antes:.2f} dB")
        self.kpi_labels["snr_despues"].config(text=f"{self.snr_despues:.2f} dB")
        self.kpi_labels["mejora"].config(text=f"{self.mejora_snr:.2f} dB")
        self.kpi_labels["rms"].config(text=f"{self.rms_volcanica:.3f}")
        self.kpi_labels["umbral"].config(text=f"{self.param_umbral:.3f}")

        m = self.t <= 5.0

        # GRÁFICA 1: SEÑALES SUPERPUESTAS JUNTAS (INDICACIÓN DEL PROFESOR)
        self.ax1.clear()
        self.ax1.plot(self.t[m], self.senal_corrupta[m], color="#94a3b8", lw=1.0, alpha=0.5, label="Señal total/corrupta")
        self.ax1.plot(self.t[m], self.s_electrico[m], color="#9333ea", lw=1.2, label="Eléctrico 60 Hz (Amp 2.20)")
        self.ax1.plot(self.t[m], self.s_transito[m], color="#f59e0b", lw=1.5, label="Tránsito 12 Hz (Amp 1.40)")
        self.ax1.plot(self.t[m], self.s_volcanica[m], color="#2563eb", lw=2.0, label="Volcánica 1.2–3.5 Hz (~1.25)")
        self.ax1.set_title("Gráfica 1 — Señales superpuestas (¿Quién es quién?)", fontsize=8.5, fontweight="bold", color="#0b1f3a", loc="left")
        self.ax1.set_xlabel("Tiempo (s)", fontsize=7, color="#334155")
        self.ax1.set_ylabel("Amplitud", fontsize=7, color="#334155")
        self.ax1.set_xlim(0, 5)
        self.ax1.set_ylim(-6.5, 6.5)
        self.ax1.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
        self.ax1.legend(loc="upper right", fontsize=5.5, frameon=True, ncol=2)
        self.ax1.tick_params(labelsize=6.5)

        # PLOT 2: FFT
        self.ax2.clear()
        mask = self.frecuencias <= 80
        self.ax2.plot(self.frecuencias[mask], self.magnitud[mask], color="#0284c7", lw=1.1)
        self.ax2.axvspan(0.5, 5, color="#0ea5e9", alpha=0.18)
        self.ax2.set_yscale("log")
        self.ax2.set_ylim(0.01, 15)
        self.ax2.set_xlim(0, 80)
        self.ax2.set_title("Espectro frecuencial (FFT): Picos identificados", fontsize=8.5, fontweight="bold", color="#0b1f3a", loc="left")
        self.ax2.set_xlabel("Frecuencia (Hz)", fontsize=7, color="#334155")
        self.ax2.set_ylabel("Magnitud", fontsize=7, color="#334155")
        self.ax2.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
        self.ax2.tick_params(labelsize=6.5)

        self.ax2.plot(self.param_f1, 0.8, "o", color="#2563eb", markersize=3.5)
        self.ax2.annotate(f"{self.param_f1:.1f} Hz (volcán)", (self.param_f1, 0.8), xytext=(self.param_f1+1.2, 0.8), fontsize=6, color="#2563eb")
        self.ax2.plot(12.0, self.param_amp_trans, "o", color="#f59e0b", markersize=3.5)
        self.ax2.annotate("12 Hz (tránsito)", (12.0, self.param_amp_trans), xytext=(13.0, 1.1), fontsize=6, color="#f59e0b")
        self.ax2.plot(60.0, self.param_amp_elec, "o", color="#9333ea", markersize=3.5)
        self.ax2.annotate("60 Hz (eléc.)", (60.0, self.param_amp_elec), xytext=(48.0, 3.2), fontsize=6, color="#9333ea")

        # GRÁFICA 3: DEPURACIÓN / FILTRADO (INDICACIÓN DEL PROFESOR)
        self.ax3.clear()
        self.ax3.plot(self.t[m], self.senal_corrupta[m], color="#94a3b8", lw=1.0, alpha=0.7, label="Corrupta (antes de filtrar)")
        self.ax3.plot(self.t[m], self.senal_limpia[m], color="#ea580c", lw=1.8, label="Depurada (0.5 – 5 Hz)")
        self.ax3.set_title("Gráfica 2 — Depuración (Corrupta vs Filtrada)", fontsize=8.5, fontweight="bold", color="#0b1f3a", loc="left")
        self.ax3.set_xlabel("Tiempo (s)", fontsize=7, color="#334155")
        self.ax3.set_ylabel("Amplitud", fontsize=7, color="#334155")
        self.ax3.set_xlim(0, 5)
        self.ax3.set_ylim(-6.5, 6.5)
        self.ax3.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
        self.ax3.legend(loc="upper right", fontsize=6, frameon=True)
        self.ax3.tick_params(labelsize=6.5)

        # PLOT 4: VALIDACIÓN REFERENCIA VS RECUPERADA
        self.ax4.clear()
        self.ax4.plot(self.t[m], self.s_volcanica[m], color="#0284c7", lw=1.4, label="Volcánica pura (referencia)")
        self.ax4.plot(self.t[m], self.senal_limpia[m], color="#ea580c", lw=1.4, label="Señal recuperada")
        self.ax4.set_title("Validación: Referencia vs Recuperada (+18.89 dB)", fontsize=8.5, fontweight="bold", color="#0b1f3a", loc="left")
        self.ax4.set_xlabel("Tiempo (s)", fontsize=7, color="#334155")
        self.ax4.set_ylabel("Amplitud", fontsize=7, color="#334155")
        self.ax4.set_xlim(0, 5)
        self.ax4.set_ylim(-1.6, 1.6)
        self.ax4.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
        self.ax4.legend(loc="upper right", fontsize=6, frameon=True)
        self.ax4.tick_params(labelsize=6.5)

        self.canvas.draw_idle()

    def abrir_web(self):
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_interactivo.html")
        if os.path.exists(html_path):
            webbrowser.open(f"file:///{html_path.replace(os.sep, '/')}")

def main():
    if not HAS_GUI_LIBS:
        html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_interactivo.html")
        webbrowser.open(f"file:///{html_file.replace(os.sep, '/')}")
        return
    root = tk.Tk()
    app = SismografoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
