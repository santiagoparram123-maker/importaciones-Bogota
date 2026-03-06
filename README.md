# 📦 Importaciones Bogotá 2024-2025: Inteligencia Comercial y Análisis

Este proyecto es una herramienta automatizada de Análisis Exploratorio de Datos (EDA) e Inteligencia Comercial, diseñada para procesar y extraer *insights* estratégicos del registro de importaciones de la ciudad de Bogotá, Colombia.

A partir de datos crudos, el script limpia, procesa y genera un **Dashboard interactivo en HTML** junto con **12 visualizaciones clave** sobre productos, logística, geopolítica y niveles tecnológicos.
## 🤖 Enfoque de Desarrollo: Productividad y Criterio Técnico

Escribir scripts con IA es una gran ventaja competitiva, pero la IA no entiende el contexto del mundo real por sí sola. Para que un análisis no colapse al enfrentarse a un dataset sucio de aduanas, hace falta aplicar fundamentos de ciencia de datos.

Este proyecto refleja mi forma de trabajar: **uso la inteligencia artificial para acelerar el desarrollo**, mientras aplico mi propio criterio técnico para guiar la herramienta. Al delegar la escritura mecánica del código, puedo centrarme en estructurar soluciones robustas y escalables, pensadas para generar valor real en entornos B2B. Es el balance perfecto entre velocidad automatizada y dirección humana.
## 🚀 Características Principales

El pipeline de datos (`analisis_importaciones.py`) ejecuta de forma automática:
- **Limpieza de Datos:** Estandarización de formatos numéricos colombianos y eliminación de valores atípicos/nulos.
- **Feature Engineering:** Cálculo de métricas personalizadas como *Precio Unitario por Kg*, *Precio Unitario por Cantidad* y *Porcentaje de Impacto Logístico* (Costo de flete vs. Valor FOB).
- **Generación de Reportes:** Creación de un archivo `reporte_importaciones.html` estructurado y estilizado para lectura ejecutiva.
- **Exportación de Gráficos:** 12 gráficos en formato PNG listos para presentaciones, divididos en 4 bloques estratégicos:
  - 📦 **Bloque A - Productos:** Top de valor, extremos de peso y análisis de precios unitarios ("Diamantes" vs. "Arena").
  - 🏷️ **Bloque B - Categorías:** Distribución por nivel tecnológico y uso económico.
  - 🚢 **Bloque C - Logística:** Identificación de las partidas con mayor y menor impacto en costos de flete.
  - 🌍 **Bloque D - Geopolítica:** Análisis de países proveedores y costos logísticos asociados por región.

## 🛠️ Tecnologías Utilizadas

- **Python 3**
- **Pandas:** Procesamiento y estructuración de datos.
- **Matplotlib & Seaborn:** Visualización de datos y diseño de paletas de colores (`viridis`, `rocket`, `crest`).
- **Calamine:** Motor de alto rendimiento para la lectura de archivos de Excel binarios y antiguos.
- **Base64 / HTML / CSS:** Renderizado nativo del dashboard sin dependencias de servidores externos.

## ⚙️ Instrucciones de Uso (Reproducción Local)

Debido al tamaño de los registros, **el dataset original no está incluido en este repositorio**. Para ejecutar este proyecto en tu máquina local, sigue estos pasos:

### ⚙️ 1. Instalación de Dependencias

Asegúrate de tener activo tu entorno virtual y ejecuta el siguiente comando en tu terminal para instalar las librerías necesarias para el análisis y visualización:

```bash
pip install pandas matplotlib seaborn calamine openpyxl
```

### 📥 2. Obtención del Dataset Oficial

Para que el pipeline de datos funcione, necesitas la fuente de información cruda:

1. Ingresa al portal oficial del gobierno: **[Datos Abiertos Colombia - Importaciones Bogotá](https://www.datos.gov.co/dataset/Importaciones-Bogot-/vdw8-sjw6/about_data)**.
2. Descarga el archivo y guárdalo en la misma carpeta del proyecto (asegúrate de que el nombre coincida con el que lee el script `analisis_importaciones.py`).
3. Coloca el archivo descargado en la carpeta raíz de este proyecto.

### 3. Configurar las Rutas
Abre el archivo `analisis_importaciones.py` y actualiza la sección de configuración (`CONFIG`) con las rutas correspondientes a tu máquina local:

```python
ARCHIVO = r'ruta/local/hacia/el/dataset_descargado.csv'
OUTPUT_DIR = r'ruta/local/para/guardar/graficos_output'
HTML_OUTPUT = r'ruta/local/para/guardar/reporte_importaciones.html'
### 4. Ejecutar el Análisis
Una vez configurado, ejecuta el script desde la terminal:
```bash
python analisis_importaciones.py
```
### 5. Visualizar los Resultados
Al finalizar la ejecución, encontrarás:
- **12 archivos PNG** en la carpeta `graficos_output`.
- Un **dashboard interactivo** en `reporte_importaciones.html`, listo para abrir en cualquier navegador web.
[![Ver Dashboard](https://img.shields.io/badge/Ver_Dashboard-En_Vivo-2ea44f?style=for-the-badge&logo=google-analytics)](https://santiagoparram123-maker.github.io/importaciones-Bogota/)

## 📊 Estructura del Análisis

El script genera un análisis segmentado en 4 bloques temáticos para facilitar la toma de decisiones:

### Bloque A: Productos
- Top 10 productos por valor importado.
- Productos con mayor y menor peso.
- Análisis de precios unitarios (identificación de productos de alto valor vs. commodities).

### Bloque B: Categorías
- Distribución de importaciones por nivel tecnológico (Alta, Media, Baja).
- Clasificación por uso económico (Bienes de Consumo, Intermedios, Capital).

### Bloque C: Logística
- Partidas con mayor impacto en costos de flete (FOB vs. CIF).
- Partidas con menor impacto logístico.

### Bloque D: Geopolítica
- Principales países proveedores.
- Comparativa de costos logísticos por región de origen.

## 🆕 Novedades (Última Actualización)

El proyecto ha evolucionado a **TradeFlow Bogotá**, con una refactorización completa orientada a escalar y ofrecer una experiencia B2B premium:
- **Rediseño Premium UI/UX (SaaS B2B):** Migración a un diseño moderno y claro (esquema "slate") con tarjetas blancas elegantes, sombras sutiles, bordes redondeados y una nueva paleta de colores corporativa (acentos en índigo y esmeralda).
- **Sistema de Tooltips Interactivo en KPIs:** Implementación de *tooltips* interactivos dinámicos para la metadata de cada KPI. Eliminamos los atributos nativos HTML obsoletos, integrando cuadros oscuros flotantes orientados por eventos (JS) que aparecen con transiciones de desvanecimiento ultra fluidas (0.3s) por encima del contenido inferior.
- **Arquitectura Desacoplada y Organizada:** Separación más clara de los scripts de minería/limpieza de datos (`analisis_importaciones.py`) del template final visual (`index.html`).
- **Insights Analíticos Extendidos:** 
  - Identificación del Top 15 de bienes más y menos importados por cantidad global.
  - Segmentaciones de costo unitario ponderado (Valor FOB ÷ Unidad).
- **Mejoras Estructurales:** Nueva navegación adhesiva inteligente (*Sticky Nav*) con acabado tipo cristal opaco (*frosted glass effect*), animaciones fluidas (fade in / up) a medida que carga cada tarjeta y un refinado **hero banner** interactivo.

## 📄 Licencia de los Datos

El dataset oficial de *Importaciones Bogotá* referenciado y utilizado para este análisis se distribuye bajo la licencia **[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)**.
