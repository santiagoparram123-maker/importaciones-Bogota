# 📦 TradeFlow Bogotá 2024-2025: B2B Commercial Intelligence

This project has evolved from a simple Exploratory Data Analysis (EDA) script into a comprehensive **B2B Commercial Intelligence Platform** (TradeFlow Bogotá). It is designed to process, clean, and extract strategic *insights* from the official import records of Bogotá, Colombia, converting raw data into actionable intelligence, ideal for Micro-SaaS modeling.

From a massive dataset of customs transactions, the Python orchestrator builds a completely autonomous **Interactive and Premium HTML Dashboard**, along with an analytical suite of advanced visualizations.

## 🤖 Development Approach & B2B Evolution

Writing AI data mining scripts is an advantage, but creating true data products requires integrating fundamentals of architecture, financial analysis, and commercial user experience (B2B UI/UX).

This tool delegates algorithmic execution and mechanical rendering to automation, allowing strategists to focus on designing **monetizable value architectures**: interactive calculators, geopolitical heat maps, derived *Market Share* metrics, and logistical cost structure analysis at the country and technological sector levels.

## 🚀 Key B2B Innovations

The latest iteration completely transforms static analysis into an immersive analytical tool:

- 🟣 **Global Purple Aesthetic & Dark Mode:** A unified interface with a corporate "deep purple" color palette, designed for high contrast, prolonged reading, and a "premium" executive appearance, featuring fluid animations, *glassmorphism*, and full adaptability between light and dark modes.
- 🧮 **Smart Import Cost Calculator (B2B):** An interactive financial tool (Native Javascript) that predicts freight costs per kilogram based on actual history (Benchmarking), automatically calculates taxes (Tariffs and VAT according to the tariff chapter), and injects the tax burden in real time for precise quotes.
- 📊 **"The Value Row" (Key Metrics):** Financial KPIs in the header:
  - *Market Share* of leading countries.
  - *Benchmarking* of Unit CIF Price per Kilogram (Sand vs. Diamonds).
  - *Freight Trend Analyzer* that exposes percentages of logistics cost increases from the beginning to the end of the year.
- 🗺️ **Advanced Geopolitical Module:** Implementation of dynamic choropleth heat maps (via Plotly) and Sankey diagrams to audit the flows of merchandise from global powers to their economic uses in Colombia.

## 🛠️ Technologies and Decoupled Architecture

The platform maintains strictly separated logic between Backend ETL (Python) and Rendering (Frontend):

- **Backend ETL & Data Science:** `Python 3`, `Pandas` (extraction, cleaning, aggregation, and Unit Economics calculations).
- **Graphics Engines:** `Plotly Express` (Interactive HTML Maps), `Matplotlib`, and `Seaborn` (High-density static PNG charts).
- **File Processing:** `Calamine` (extreme performance for Excel files) and `OpenPyXL`.
- **Frontend App:** Vanilla `HTML/CSS/JS` (Asynchronous loading, Tooltips with native events, Scrollspy for navigation, no heavy external framework dependencies).
- **Interoperability:** Embedded or generated JSON (*dashboard_overview.json*) for fully "stateless" dashboard rehydration on the client.

## ⚙️ Usage Instructions (Local Reproduction)

Due to the size of the customs records, **the original dataset is not included in this repository**.

### 1. Install Dependencies

Make sure to prepare your development environment (`.venv`) and install:

```bash
pip install pandas matplotlib seaborn plotly calamine openpyxl
```

### 2. Obtain the Base Dataset

1. Visit **[Datos Abiertos Colombia - Importaciones Bogotá](https://www.datos.gov.co/dataset/Importaciones-Bogot-/vdw8-sjw6/about_data)**.
2. Download the CSV and save it in the root of this project (e.g., `conjunto-importaciones-bogota-21102025.csv`).

### 3. Configure and Run Backend

Open `analisis_importaciones.py`, check the `ARCHIVO` constant and launch the pipeline:

```bash
python analisis_importaciones.py
```

### 4. View Dashboard

The script will export the data model in JSON, charts to `graficos_output`, and compile the final template.
Open **`index.html`** locally (double click or via a live-server if possible) and explore the dark mode and calculator.

## 📊 Analytical Pipeline Structure

The Backend divides its execution into modular thematic blocks:

- **Dashboard Overview:** Executive comparative summary, grouped CIF/FOB bars month over month with delta calculators.
- **Block A - Products & Unit Prices:** Diamonds vs. Sand.
- **Block B - Economic Use & Technological Levels (High-Tech VS Low-Tech).**
- **Block C - Logistics Impact:** Freight inefficiency identifiers.
- **Block D - Global Suppliers.**
- **Block E - Spatial Strategic Vision:** Interactive flows (Sankey), Price correlations (Scatter Plots), and Sector-Month Heat Maps.
- **Block F - Taxes & Geography:** Distribution of tax burdens and global geopolitical impacts.

## 📄 License

The official dataset upon which these scripts operate is distributed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. The code of this analysis pipeline and the generated HTML/CSS interfaces are for educational and product intelligence purposes.
