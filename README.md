# 📦 TradeFlow Bogotá 2024-2025: Inteligencia Comercial B2B

Este proyecto ha evolucionado de un simple script de Análisis Exploratorio de Datos (EDA) a una completa **Plataforma de Inteligencia Comercial B2B** (TradeFlow Bogotá). Está diseñada para procesar, limpiar y extraer *insights* estratégicos del registro oficial de importaciones de la ciudad de Bogotá, Colombia, convirtiendo datos crudos en inteligencia accionable, ideal para el modelado de Micro-SaaS.

A partir de un conjunto masivo de transacciones aduaneras, el orquestador en Python construye un **Dashboard Interactivo y Premium en HTML** completamente autónomo, junto con una suite analítica de visualizaciones avanzadas.

## 🤖 Enfoque de Desarrollo y Evolución B2B

Escribir scripts de minería de datos con IA es una ventaja, pero crear verdaderos productos de datos requiere integrar fundamentos de arquitectura, análisis financiero y experiencia de usuario comercial (B2B UI/UX). 

Esta herramienta delega la ejecución algorítmica y el renderizado mecánico a la automatización, permitiendo a los estrategas centrarse en el diseño de **arquitecturas de valor monetizables**: calculadoras interactivas, mapas de calor geopolíticos, métricas de *Market Share* derivadas y análisis de estructuras de costos logísticos a nivel país y sector tecnológico.

## 🚀 Innovaciones B2B Destacadas

La última iteración transforma por completo el análisis estático en una herramienta analítica inmersiva:

- 🟣 **Global Purple Aesthetic & Dark Mode:** Una interfaz unificada con una paleta de colores corporativa "deep purple", diseñada para altos contrastes, lectura prolongada y una apariencia ejecutiva "premium", con animaciones fluidas, *glassmorphism* y total adaptabilidad entre modos de luz.
- 🧮 **Calculadora Inteligente de Costos de Importación (B2B):** Una herramienta financiera interactiva (Javascript Nativo) que predice costos de flete por kilogramo basándose en el historial real (Benchmarking), calcula automáticamente impuestos (Aranceles e IVA según el capítulo arancelario) e inyecta la carga tributaria en tiempo real para cotizaciones precisas.
- 📊 **"The Value Row" (Métricas Clave):** KPIs financieros en la cabecera:
  - *Market Share* de los países líderes.
  - *Benchmarking* del Unit CIF Price por Kilogramo (Arena vs. Diamantes).
  - *Freight Trend Analyzer* que expone porcentajes de encarecimiento logístico de principio a fin de año.
- 🗺️ **Módulo Geopolítico Avanzado:** Implementación de mapas coropléticos de calor dinámicos (via Plotly) e diagramas Sankey para auditar los flujos de mercancía desde las potencias globales hacia sus usos económicos en Colombia.

## 🛠️ Tecnologías y Arquitectura Desacoplada

La plataforma mantiene una lógica estrictamente separada entre Backend ETL (Python) y Rendering (Frontend):

- **Backend ETL & Data Science:** `Python 3`, `Pandas` (extracción, limpieza, agregación y cálculos de Unit Economics).
- **Motores Gráficos:** `Plotly Express` (Mapas HTML interactivos), `Matplotlib`, y `Seaborn` (Gráficos estáticos PNG alta densidad).
- **Procesamiento de Archivos:** `Calamine` (rendimiento extremo para archivos Excel) y `OpenPyXL`.
- **Frontend App:** Vanilla `HTML/CSS/JS` (Carga asíncrona, Tooltips con eventos nativos, Scrollspy para navegación, sin dependencias de frameworks externos pesados).
- **Interoperabilidad:** JSON embebido o generado (*dashboard_overview.json*) para una rehidratación del dashboard totalmente "stateless" en el cliente.

## ⚙️ Instrucciones de Uso (Reproducción Local)

Debido al tamaño de los registros aduaneros, **el dataset original no está incluido en este repositorio**.

### 1. Instalación de Dependencias

Asegúrate de preparar tu entorno de desarrollo (`.venv`) e instalar:

```bash
pip install pandas matplotlib seaborn plotly calamine openpyxl
```

### 2. Obtención del Dataset Base

1. Ingresa a **[Datos Abiertos Colombia - Importaciones Bogotá](https://www.datos.gov.co/dataset/Importaciones-Bogot-/vdw8-sjw6/about_data)**.
2. Descarga el CSV y guárdalo en la raíz de este proyecto (ej. `conjunto-importaciones-bogota-21102025.csv`).

### 3. Configurar y Ejecutar Backend

Abre `analisis_importaciones.py`, verifica la constante `ARCHIVO` y lanza la canalización:

```bash
python analisis_importaciones.py
```

### 4. Visualización del Dashboard

El script exportará el modelo de datos en JSON, gráficos en `graficos_output` y compilará la plantilla final.
Abre **`index.html`** localmente (doble clic o mediante un live-server si es posible) y explora el modo oscuro y la calculadora.

## 📊 Estructura Analítica del Pipeline

El Backend divide su ejecución en bloques temáticos modulares:

- **Dashboard Overview:** Resumen ejecutivo comparativo, barras agrupadas CIF/FOB mes tras mes con calculadoras delta.
- **Bloque A - Productos & Precios Unitarios:** Diamantes vs. Arena.
- **Bloque B - Uso Económico & Niveles Tecnológicos (High-Tech VS Low-Tech).**
- **Bloque C - Impacto Logístico:** Identificadores de ineficiencia de flete.
- **Bloque D - Proveedores Globales.**
- **Bloque E - Visión Estratégica Espacial:** Flujos interactivos (Sankey), Correlaciones de precios (Scatter Plots) y Mapas de Calor Sector-Mes.
- **Bloque F - Impuestos & Geografía:** Distribución de cargas tributarias e impactos geopolíticos mundiales.

## 📄 Licencia

El dataset oficial sobre el que operan estos scripts se distribuye bajo **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. El código de este pipeline de análisis y las interfaces HTML/CSS generadas son para fines educativos y de inteligencia de producto.
