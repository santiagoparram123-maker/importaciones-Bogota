# 📦 Inteligencia Comercial: Análisis de Importaciones en Bogotá

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

### 1. Preparar el Entorno
Clona este repositorio e instala las librerías necesarias:
```bash
pip install pandas matplotlib seaborn calamine openpyxl
### 2. Descargar el Dataset Oficial
1. Ingresa al Portal de Datos Abiertos de Colombia a través de este enlace oficial: **[Importaciones Bogotá - Datos.gov.co](https://www.datos.gov.co/dataset/Importaciones-Bogot-/vdw8-sjw6/about_data)**.
2. Descarga el dataset actualizado.
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

El proyecto ha sido refactorizado para mejorar su escalabilidad, modularidad y experiencia de usuario (UX):
- **Arquitectura Desacoplada:** Separación del motor de procesamiento de datos (`analisis_importaciones.py`) del frontend visual (`dashboard.html`).
- **Mejoras en el Entorno:** Migración a Python 3.12.9 utilizando un entorno virtual (`venv`) estricto para garantizar la reproducibilidad.
- **Nuevos Insights Analíticos:** - Inclusión del Top 15 de bienes más y menos importados por cantidad.
  - Análisis de costo unitario (FOB ÷ Cantidad).
  - Rediseño de los gráficos de peso en distribuciones independientes.
- **Enriquecimiento UI/UX:** Integración de *tooltips* interactivos en los KPIs del dashboard que muestran las definiciones oficiales extraídas de la metadata del gobierno.
- **Optimización Visual:** Inclusión de etiquetas de porcentaje en barras y tablas del Bloque B para una lectura más ejecutiva.

## 📄 Licencia de los Datos

El dataset oficial de *Importaciones Bogotá* referenciado y utilizado para este análisis se distribuye bajo la licencia **[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)**.
