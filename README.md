# Monitoreo Sismográfico Volcánico — Análisis Espectral y Filtrado Digital

**Curso:** Percepción Computacional — Sesión 09 / 10  
**Caso de Estudio:** *El Misterio del Sismógrafo Corrupto*  
**Repositorio Remoto:** https://github.com/FSFR192/S9_PERECEPCION.git

---

## 🌋 Descripción del Proyecto

Sistema de monitoreo, análisis espectral y depuración de señales sísmicas contaminadas por ruido ambiental, vehicular y electromagnético en una estación de vigilancia volcánica.

El proyecto implementa el flujo completo de percepción computacional:
1. **Adquisición / Generación de la señal temporal**: Frecuencia de muestreo $f_s = 200\text{ Hz}$.
2. **Identificación de Componentes (Gráfica 1 - Señales Superpuestas)**:
   - 🔵 **Actividad volcánica (1.2 y 3.5 Hz)**: Microtemblores precursores de baja frecuencia ($0.5 - 5\text{ Hz}$).
   - 🟠 **Ruido de tránsito (12 Hz)**: Interferencia mecánica industrial (Amplitud = 1.40).
   - 🟣 **Ruido eléctrico (60 Hz)**: Interferencia electromagnética de red (Amplitud = 2.20, **Mayor amplitud**).
   - ⚪ **Ruido aleatorio blanco**: Ruido gaussiano $\mathcal{N}(0, 1)$ con amplitud 0.90.
3. **Análisis Espectral por Transformada Rápida de Fourier (FFT)**: Identificación de picos dominantes en escala logarítmica.
4. **Diseño de Filtro Digital**: Filtro pasa-banda Butterworth de 4to orden con fase cero (`sosfiltfilt`) entre **0.5 Hz y 5.0 Hz**.
5. **Depuración y Filtrado (Gráfica 2)**: Comparación antes vs después del filtrado.
6. **Métricas de Calidad y Alerta**:
   - $\text{SNR}_{\text{antes}} = -9.95\text{ dB}$ (señal sumergida en ruido)
   - $\text{SNR}_{\text{después}} = 8.94\text{ dB}$ (señal recuperada)
   - **Mejora de SNR**: $+18.89\text{ dB}$
   - **RMS en banda volcánica**: $0.673$ (Supera el umbral de $0.500 \rightarrow$ **ALERTA VOLCÁNICA ACTIVADA**)

7. **🔊 Sonificación Sísmica**: Transposición acústica (infrasonido a espectro audible) mediante la Web Audio API y exportación WAV, permitiendo *escuchar* directamente la señal corrupta con el zumbido eléctrico frente a la señal depurada y limpia.

---

## 📁 Estructura del Repositorio

- **[`index.html`](index.html)**: Punto de entrada para despliegue en Vercel con el panel completo y sonificación sísmica.
- **[`dashboard_interactivo.html`](dashboard_interactivo.html)**: Panel de control web interactivo con diseño tipo sala de control, simulación en vivo, barra de audio, sliders en tiempo real y vista adaptable (*Modo 4 Gráficas* y *Enfoque del Profesor: 2 Gráficas Grandes*).
- **[`caso_sismografo_s09_(1).py`](caso_sismografo_s09_(1).py)**: Script principal con todo el procesamiento numérico, las gráficas solicitadas por el docente y exportación de audios WAV.
- **[`interfaz_sismografo_gui.py`](interfaz_sismografo_gui.py)**: Aplicación de escritorio nativa Python (Tkinter + Matplotlib) con visualización en vivo.
- **[`servidor_dashboard.py`](servidor_dashboard.py)**: Servidor HTTP local para servir el dashboard web fácilmente.

---

## 🚀 Cómo Ejecutar

### 1. Dashboard Web Interactivo
Simplemente abre `dashboard_interactivo.html` en cualquier navegador (Google Chrome, Edge, Firefox, etc.) haciendo doble clic sobre el archivo, o mediante Python:
```bash
python servidor_dashboard.py
```

### 2. Script de Análisis y Gráficas del Docente
```bash
python "caso_sismografo_s09_(1).py"
```

### 3. Interfaz de Escritorio (Tkinter)
```bash
python interfaz_sismografo_gui.py
```

