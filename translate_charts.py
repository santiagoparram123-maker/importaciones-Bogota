import sys
content = open('analisis_importaciones.py', 'r', encoding='utf-8').read()

replacements = {
    "'Top 15 Bienes Más Importados (por Cantidad)'": "'Top 15 Most Imported Goods (by Quantity)'",
    "'Top 15 Bienes Menos Importados (por Cantidad)'": "'Top 15 Least Imported Goods (by Quantity)'",
    "'Top 10 Productos Más Valiosos (Total USD FOB)'": "'Top 10 Most Valuable Products (Total USD FOB)'",
    "'Top 10 Productos Menos Valiosos (Total USD FOB)'": "'Top 10 Least Valuable Products (Total USD FOB)'",
    "'Top 10 Productos Más Pesados (Kg Netos)'": "'Top 10 Heaviest Products (Net Kg)'",
    "'Top 10 Productos Menos Pesados (Kg Netos)'": "'Top 10 Lightest Products (Net Kg)'",
    "'Más Caros por Kg (Mediana USD/Kg)'": "'Most Expensive per Kg (Median USD/Kg)'",
    "'Más Baratos por Kg (Mediana USD/Kg)'": "'Cheapest per Kg (Median USD/Kg)'",
    "'Top 10 Mayor Costo Unitario (FOB / Cantidad)'": "'Top 10 Highest Unit Cost (FOB / Quantity)'",
    "'Top 10 Menor Costo Unitario (FOB / Cantidad)'": "'Top 10 Lowest Unit Cost (FOB / Quantity)'",
    "'Distribución de USD FOB según Nivel Tecnológico'": "'Distribution of USD FOB by Technological Level'",
    "'Dolares FOB (USD)'": "'FOB Dollars (USD)'",
    "'Nivel Tecnológico'": "'Technological Level'",
    "'Total FOB por Nivel Tecnológico (con %)'": "'Total FOB by Technological Level (with %)'",
    "'Total FOB (USD)'": "'Total FOB (USD)'",
    "'Total Importado (USD FOB) por Uso Económico'": "'Total Imported (USD FOB) by Economic Use'",
    "'🚢 Top 10 Mayor Impacto Logístico (% sobre FOB)'": "'🚢 Top 10 Highest Logistics Impact (% over FOB)'",
    "'✈️ Top 10 Menor Impacto Logístico (% sobre FOB)'": "'✈️ Top 10 Lowest Logistics Impact (% over FOB)'",
    "'🌍 Top 10 Países Proveedores (USD FOB)'": "'🌍 Top 10 Supplier Countries (USD FOB)'",
    "'💸 Top 10 Países con Mayor Costo Logístico (% sobre FOB)'": "'💸 Top 10 Countries with Highest Logistics Cost (% over FOB)'",
    "'Impacto Logístico Promedio (%)'": "'Average Logistics Impact (%)'",
    "'Flujos de Importación: Origen → Uso'": "'Import Flows: Origin → Use'",
    "'Flujos de Importación: Origen → Uso → Tecnología'": "'Import Flows: Origin → Use → Technology'",
    "'Importaciones 2024-2025: Volumen vs Precio '": "'Imports 2024-2025: Volume vs Price '",
    "'Volumen (Kg Netos)'": "'Volume (Net Kg)'",
    "'Precio Unitario (USD/Kg) - Escala Log'": "'Unit Price (USD/Kg) - Log Scale'",
    "title='Importaciones 2024-2025: Volumen vs Precio'": "title='Imports 2024-2025: Volume vs Price'",
    "'Precio Unitario (USD/Kg)'": "'Unit Price (USD/Kg)'"
}

for es_text, en_text in replacements.items():
    content = content.replace(es_text, en_text)

# Save the updated content
open('analisis_importaciones.py', 'w', encoding='utf-8').write(content)
print("Updated analisis_importaciones.py titles successfully!")
