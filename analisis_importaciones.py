# =============================================================================
# analisis_importaciones.py — Motor de Datos: Importaciones Bogotá
# Autor: Santiago (asistido por IA)
# Genera 15 gráficos PNG + Sankey HTML + datos JSON para el Dashboard
# =============================================================================

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONFIG — rutas relativas al directorio del script
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(BASE_DIR, 'conjunto-importaciones-bogota-21102025.csv')
CHARTS_DIR = os.path.join(BASE_DIR, 'static', 'charts')
DATA_DIR = os.path.join(BASE_DIR, 'static', 'data')

PALETTE = 'viridis'
TOP_N = 10

# ─────────────────────────────────────────────
# ESTILO SEABORN
# ─────────────────────────────────────────────
sns.set_theme(
    style='whitegrid',
    context='notebook',
    font_scale=1.1,
    palette=PALETTE,
    rc={
        'figure.figsize': (12, 7),
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'figure.dpi': 150,
    }
)


# =============================================================================
# UTILIDADES
# =============================================================================
def setup_dirs():
    """Crea los directorios de salida si no existen."""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f'  📁 Directorio de gráficos: {CHARTS_DIR}')
    print(f'  📁 Directorio de datos:    {DATA_DIR}')


def guardar_chart(fig, nombre: str):
    """Guarda un gráfico PNG en static/charts/ y cierra la figura."""
    ruta = os.path.join(CHARTS_DIR, f'{nombre}.png')
    fig.savefig(ruta, bbox_inches='tight', facecolor='white', dpi=150)
    plt.close(fig)
    print(f'  💾 {nombre}.png guardado')


def guardar_json(data, nombre: str):
    """Guarda un diccionario/lista como JSON en static/data/."""
    ruta = os.path.join(DATA_DIR, f'{nombre}.json')
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'  📄 {nombre}.json guardado')


def df_to_records(df: pd.DataFrame) -> list:
    """Convierte un DataFrame a lista de dicts limpia para JSON."""
    return json.loads(df.to_json(orient='records', force_ascii=False))


def barplot_horizontal(data, x, y, titulo, nombre_archivo, color_palette=PALETTE, fmt=',.0f'):
    """Crea un barplot horizontal, lo guarda como PNG y retorna los datos."""
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(data=data, x=x, y=y, palette=color_palette, ax=ax, hue=y, legend=False)
    ax.set_title(titulo, fontweight='bold', pad=15)
    ax.set_xlabel(x)
    ax.set_ylabel('')
    for bar in ax.patches:
        width = bar.get_width()
        if width > 0:
            ax.text(width, bar.get_y() + bar.get_height() / 2,
                    f'  {width:{fmt}}', va='center', fontsize=9, color='#333')
    plt.tight_layout()
    guardar_chart(fig, nombre_archivo)


# =============================================================================
# 1. CARGA
# =============================================================================
def cargar_datos(ruta: str) -> pd.DataFrame:
    print('=' * 60)
    print('  CARGANDO DATOS')
    print('=' * 60)

    # Intentar con calamine (Excel binario), luego openpyxl, luego CSV
    try:
        try:
            df = pd.read_excel(ruta, engine='calamine')
            print(f'  ✅ Cargado con calamine: {df.shape[0]:,} filas × {df.shape[1]} columnas')
        except Exception:
            try:
                df = pd.read_excel(ruta, engine='openpyxl')
                print(f'  ✅ Cargado con openpyxl: {df.shape[0]:,} filas × {df.shape[1]} columnas')
            except Exception:
                df = pd.read_csv(ruta, encoding='latin-1', sep=';', low_memory=False)
                print(f'  ✅ Cargado como CSV: {df.shape[0]:,} filas × {df.shape[1]} columnas')
    except Exception as e:
        print(f'  ❌ Error al cargar: {e}')
        raise
    return df


# =============================================================================
# 2. LIMPIEZA AVANZADA
# =============================================================================
COLS_NUMERICAS = ['Dolares FOB', 'Dolares CIF', 'Kilogramos netos', 'Cantidad']


def limpiar_columna_numerica(serie: pd.Series) -> pd.Series:
    if serie.dtype == 'object':
        serie = serie.astype(str).str.replace('.', '', regex=False)
        serie = serie.astype(str).str.replace(',', '.', regex=False)
        serie = pd.to_numeric(serie, errors='coerce')
    return serie


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    print('\n' + '=' * 60)
    print('  LIMPIEZA')
    print('=' * 60)
    for col in COLS_NUMERICAS:
        if col in df.columns:
            df[col] = limpiar_columna_numerica(df[col])
            nulos = df[col].isna().sum()
            if nulos > 0:
                print(f'  ⚠️  {col}: {nulos:,} valores no numéricos → NaN')
            else:
                print(f'  ✅ {col}: limpia ({df[col].dtype})')
        else:
            print(f'  ❌ Columna «{col}» no encontrada')

    cols_presentes = [c for c in COLS_NUMERICAS if c in df.columns]
    antes = len(df)
    df = df.dropna(subset=cols_presentes, how='all')
    print(f'  🗑️  Filas eliminadas (todo NaN): {antes - len(df):,}')
    return df


# =============================================================================
# 3. FEATURE ENGINEERING
# =============================================================================
def crear_metricas(df: pd.DataFrame) -> pd.DataFrame:
    print('\n' + '=' * 60)
    print('  FEATURE ENGINEERING')
    print('=' * 60)

    mask_kg = df['Kilogramos netos'] > 0
    df.loc[mask_kg, 'Precio_Unitario_Peso'] = df.loc[mask_kg, 'Dolares FOB'] / df.loc[mask_kg, 'Kilogramos netos']

    if 'Cantidad' in df.columns:
        mask_cant = df['Cantidad'] > 0
        df.loc[mask_cant, 'Precio_Unitario_Cant'] = df.loc[mask_cant, 'Dolares FOB'] / df.loc[mask_cant, 'Cantidad']

    if 'Dolares CIF' in df.columns and 'Dolares FOB' in df.columns:
        df['Costo_Logistico'] = df['Dolares CIF'] - df['Dolares FOB']
        mask_fob = df['Dolares FOB'] > 0
        df.loc[mask_fob, 'Impacto_Logistico_Pct'] = (
            df.loc[mask_fob, 'Costo_Logistico'] / df.loc[mask_fob, 'Dolares FOB']
        ) * 100

    for m in ['Precio_Unitario_Peso', 'Precio_Unitario_Cant', 'Costo_Logistico', 'Impacto_Logistico_Pct']:
        if m in df.columns:
            print(f'  ✅ {m} — mediana: {df[m].median():,.2f}')
    return df


# =============================================================================
# 4. BLOQUE A — PRODUCTOS
# =============================================================================
def bloque_a_productos(df: pd.DataFrame) -> dict:
    print('\n' + '=' * 60)
    print('  BLOQUE A: ANÁLISIS DE PRODUCTOS')
    print('=' * 60)

    tablas = {}
    dataframes = {}  # DataFrames para el reporte de texto
    TOP_N_IMPORT = 15  # Para el análisis de bienes más/menos importados

    # ── Gráfico 0a: Top 15 Bienes Más Importados (por Cantidad) ──
    if 'Cantidad' in df.columns:
        cant_grupo = df.groupby('Nombre partida', as_index=False)['Cantidad'].sum()
        top_importados = cant_grupo.nlargest(TOP_N_IMPORT, 'Cantidad').sort_values('Cantidad')
        print('\n📊 Top 15 Bienes Más Importados (Cantidad):')
        print(top_importados.to_string(index=False))
        barplot_horizontal(top_importados, 'Cantidad', 'Nombre partida',
                           f'Top {TOP_N_IMPORT} Bienes Más Importados (por Cantidad)',
                           '00a_top15_mas_importados', color_palette='viridis')
        tablas['top_importados'] = df_to_records(top_importados.sort_values('Cantidad', ascending=False))
        dataframes[f'Top {TOP_N_IMPORT} Bienes Más Importados (Cantidad)'] = top_importados.sort_values('Cantidad', ascending=False)

    # ── Gráfico 0b: Top 15 Bienes Menos Importados (por Cantidad) ──
    if 'Cantidad' in df.columns:
        bottom_importados = cant_grupo[cant_grupo['Cantidad'] > 0].nsmallest(TOP_N_IMPORT, 'Cantidad').sort_values('Cantidad')
        print(f'\n📊 Top {TOP_N_IMPORT} Bienes Menos Importados (Cantidad):')
        print(bottom_importados.to_string(index=False))
        barplot_horizontal(bottom_importados, 'Cantidad', 'Nombre partida',
                           f'Top {TOP_N_IMPORT} Bienes Menos Importados (por Cantidad)',
                           '00b_top15_menos_importados', color_palette='rocket')
        tablas['bottom_importados'] = df_to_records(bottom_importados.sort_values('Cantidad'))
        dataframes[f'Top {TOP_N_IMPORT} Bienes Menos Importados (Cantidad)'] = bottom_importados.sort_values('Cantidad')

    # ── Gráfico 1: Top 10 más valiosos ──
    top_fob = (
        df.groupby('Nombre partida', as_index=False)['Dolares FOB']
        .sum().nlargest(TOP_N, 'Dolares FOB').sort_values('Dolares FOB')
    )
    print('\n📊 Top 10 Productos Más Valiosos (USD FOB):')
    print(top_fob.to_string(index=False))
    barplot_horizontal(top_fob, 'Dolares FOB', 'Nombre partida',
                       'Top 10 Productos Más Valiosos (Total USD FOB)',
                       '01_top10_productos_valiosos')
    tablas['top_valiosos'] = df_to_records(top_fob.sort_values('Dolares FOB', ascending=False))
    dataframes['Top 10 Productos Más Valiosos (USD FOB)'] = top_fob.sort_values('Dolares FOB', ascending=False)

    # ── Gráfico 2: Bottom 10 ──
    bottom_fob = (
        df[df['Dolares FOB'] > 0]
        .groupby('Nombre partida', as_index=False)['Dolares FOB']
        .sum().nsmallest(TOP_N, 'Dolares FOB').sort_values('Dolares FOB')
    )
    print('\n📊 Top 10 Productos Menos Valiosos:')
    print(bottom_fob.to_string(index=False))
    barplot_horizontal(bottom_fob, 'Dolares FOB', 'Nombre partida',
                       'Top 10 Productos Menos Valiosos (Total USD FOB)',
                       '02_bottom10_productos_valiosos', color_palette='rocket')
    tablas['bottom_valiosos'] = df_to_records(bottom_fob.sort_values('Dolares FOB'))
    dataframes['Top 10 Productos Menos Valiosos (FOB > 0)'] = bottom_fob.sort_values('Dolares FOB')

    # ── Gráfico 3a: Top 10 Más Pesados ──
    peso_grupo = df.groupby('Nombre partida', as_index=False)['Kilogramos netos'].sum()
    top_peso = peso_grupo.nlargest(TOP_N, 'Kilogramos netos').sort_values('Kilogramos netos')
    barplot_horizontal(top_peso, 'Kilogramos netos', 'Nombre partida',
                       'Top 10 Productos Más Pesados (Kg Netos)',
                       '03a_top10_mas_pesados', color_palette='mako')
    tablas['top_pesados'] = df_to_records(top_peso.sort_values('Kilogramos netos', ascending=False))
    dataframes['Top 10 Más Pesados (Kg)'] = top_peso.sort_values('Kilogramos netos', ascending=False)

    # ── Gráfico 3b: Top 10 Menos Pesados ──
    bottom_peso = peso_grupo[peso_grupo['Kilogramos netos'] > 0].nsmallest(TOP_N, 'Kilogramos netos').sort_values('Kilogramos netos')
    barplot_horizontal(bottom_peso, 'Kilogramos netos', 'Nombre partida',
                       'Top 10 Productos Menos Pesados (Kg Netos)',
                       '03b_top10_menos_pesados', color_palette='flare')
    tablas['bottom_pesados'] = df_to_records(bottom_peso.sort_values('Kilogramos netos'))
    dataframes['Top 10 Menos Pesados (Kg)'] = bottom_peso.sort_values('Kilogramos netos')

    # ── Gráfico 4: Diamantes (más caros por kg) ──
    if 'Precio_Unitario_Peso' in df.columns:
        precio_kg = (
            df[df['Precio_Unitario_Peso'].notna()]
            .groupby('Nombre partida', as_index=False)['Precio_Unitario_Peso']
            .median().nlargest(TOP_N, 'Precio_Unitario_Peso').sort_values('Precio_Unitario_Peso')
        )
        print('\nTop 10 Más Caros por Kg:')
        print(precio_kg.to_string(index=False))
        barplot_horizontal(precio_kg, 'Precio_Unitario_Peso', 'Nombre partida',
                           'Más Caros por Kg (Mediana USD/Kg)',
                           '04_top10_diamantes', fmt=',.2f')
        tablas['diamantes'] = df_to_records(precio_kg.sort_values('Precio_Unitario_Peso', ascending=False))
        dataframes['Más Caros por Kg (Mediana USD/Kg)'] = precio_kg.sort_values('Precio_Unitario_Peso', ascending=False)

    # ── Gráfico 5: Arena (más baratos por kg) ──
    if 'Precio_Unitario_Peso' in df.columns:
        precio_kg_bajo = (
            df[df['Precio_Unitario_Peso'] > 0]
            .groupby('Nombre partida', as_index=False)['Precio_Unitario_Peso']
            .median().nsmallest(TOP_N, 'Precio_Unitario_Peso').sort_values('Precio_Unitario_Peso')
        )
        print('\nTop 10 Más Baratos por Kg:')
        print(precio_kg_bajo.to_string(index=False))
        barplot_horizontal(precio_kg_bajo, 'Precio_Unitario_Peso', 'Nombre partida',
                           'Más Baratos por Kg (Mediana USD/Kg)',
                           '05_top10_arena', color_palette='crest', fmt=',.4f')
        tablas['arena'] = df_to_records(precio_kg_bajo.sort_values('Precio_Unitario_Peso'))
        dataframes['Más Baratos por Kg (Mediana USD/Kg)'] = precio_kg_bajo.sort_values('Precio_Unitario_Peso')



    # ── Gráfico 7: Costo Unitario por Cantidad (FOB / Cantidad) ──
    if 'Precio_Unitario_Cant' in df.columns:
        cuc = (
            df[df['Precio_Unitario_Cant'].notna() & (df['Precio_Unitario_Cant'] > 0)]
            .groupby('Nombre partida', as_index=False)['Precio_Unitario_Cant'].median()
        )
        top_cuc = cuc.nlargest(TOP_N, 'Precio_Unitario_Cant').sort_values('Precio_Unitario_Cant')
        bottom_cuc = cuc.nsmallest(TOP_N, 'Precio_Unitario_Cant').sort_values('Precio_Unitario_Cant')

        print('\n💲 Top 10 Mayor Costo Unitario por Cantidad:')
        print(top_cuc.to_string(index=False))
        barplot_horizontal(top_cuc, 'Precio_Unitario_Cant', 'Nombre partida',
                           'Top 10 Mayor Costo Unitario (FOB / Cantidad)',
                           '07a_costo_unitario_alto', fmt=',.0f')

        print('\n💲 Top 10 Menor Costo Unitario por Cantidad:')
        print(bottom_cuc.to_string(index=False))
        barplot_horizontal(bottom_cuc, 'Precio_Unitario_Cant', 'Nombre partida',
                           'Top 10 Menor Costo Unitario (FOB / Cantidad)',
                           '07b_costo_unitario_bajo', color_palette='crest', fmt=',.4f')

        tablas['costo_unitario_alto'] = df_to_records(top_cuc.sort_values('Precio_Unitario_Cant', ascending=False))
        tablas['costo_unitario_bajo'] = df_to_records(bottom_cuc.sort_values('Precio_Unitario_Cant'))
        dataframes['Top 10 Mayor Costo Unitario (FOB/Cantidad)'] = top_cuc.sort_values('Precio_Unitario_Cant', ascending=False)
        dataframes['Top 10 Menor Costo Unitario (FOB/Cantidad)'] = bottom_cuc.sort_values('Precio_Unitario_Cant')

    guardar_json(tablas, 'bloque_a_productos')
    return dataframes


# =============================================================================
# 5. BLOQUE B — CATEGORÍAS ESTRATÉGICAS
# =============================================================================
def bloque_b_categorias(df: pd.DataFrame) -> dict:
    print('\n' + '=' * 60)
    print('  BLOQUE B: CATEGORÍAS ESTRATÉGICAS')
    print('=' * 60)

    tablas = {}
    dataframes = {}

    # ── Gráfico 8: Nivel Tecnológico con % ──
    if 'Nivel tecnologico' in df.columns:
        df_box = df[df['Dolares FOB'] > 0].copy()
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.boxplot(data=df_box, x='Nivel tecnologico', y='Dolares FOB',
                    palette='Set2', showfliers=False, ax=ax)
        ax.set_title('Distribución de USD FOB según Nivel Tecnológico', fontweight='bold', pad=15)
        ax.set_ylabel('Dolares FOB (USD)'); ax.set_xlabel('Nivel Tecnológico')
        plt.xticks(rotation=30, ha='right'); plt.tight_layout()
        guardar_chart(fig, '08_boxplot_nivel_tecnologico')

        resumen = df.groupby('Nivel tecnologico')['Dolares FOB'].agg(['sum', 'median', 'count'])
        resumen.columns = ['Total_FOB', 'Mediana_FOB', 'Registros']
        resumen = resumen.sort_values('Total_FOB', ascending=False).reset_index()
        total_fob_sum = resumen['Total_FOB'].sum()
        resumen['Pct_Total'] = (resumen['Total_FOB'] / total_fob_sum * 100).round(1)

        # Barplot horizontal con etiquetas de %
        fig2, ax2 = plt.subplots(figsize=(12, 7))
        resumen_sorted = resumen.sort_values('Total_FOB')
        sns.barplot(data=resumen_sorted, x='Total_FOB', y='Nivel tecnologico',
                    palette='Set2', ax=ax2, hue='Nivel tecnologico', legend=False)
        ax2.set_title('Total FOB por Nivel Tecnológico (con %)', fontweight='bold', pad=15)
        ax2.set_xlabel('Total FOB (USD)'); ax2.set_ylabel('')
        for i, bar in enumerate(ax2.patches):
            w = bar.get_width()
            if w > 0:
                pct = resumen_sorted.iloc[i]['Pct_Total']
                ax2.text(w, bar.get_y() + bar.get_height() / 2,
                         f'  {pct:.1f}%', va='center', fontsize=10, fontweight='bold', color='#333')
        plt.tight_layout()
        guardar_chart(fig2, '08b_nivel_tecnologico_pct')

        print('\n📊 Resumen por Nivel Tecnológico:')
        print(resumen.to_string(index=False))
        tablas['nivel_tecnologico'] = df_to_records(resumen)
        dataframes['Resumen por Nivel Tecnológico'] = resumen

    # ── Gráfico 9: Uso Económico con % ──
    if 'Uso economico' in df.columns:
        uso = df.groupby('Uso economico', as_index=False)['Dolares FOB'].sum().sort_values('Dolares FOB')
        total_uso_sum = uso['Dolares FOB'].sum()
        uso['Pct_Total'] = (uso['Dolares FOB'] / total_uso_sum * 100).round(1)
        print('\n📊 Total por Uso Económico:')
        print(uso.to_string(index=False))

        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(data=uso, x='Dolares FOB', y='Uso economico', palette='coolwarm', ax=ax, hue='Uso economico', legend=False)
        ax.set_title('Total Importado (USD FOB) por Uso Económico', fontweight='bold', pad=15)
        ax.set_xlabel('Dolares FOB (USD)'); ax.set_ylabel('')
        for i, bar in enumerate(ax.patches):
            w = bar.get_width()
            if w > 0:
                pct = uso.iloc[i]['Pct_Total']
                ax.text(w, bar.get_y() + bar.get_height() / 2,
                         f'  {pct:.1f}%', va='center', fontsize=10, fontweight='bold', color='#333')
        plt.tight_layout()
        guardar_chart(fig, '09_uso_economico')
        tablas['uso_economico'] = df_to_records(uso.sort_values('Dolares FOB', ascending=False))
        dataframes['Total Importado por Uso Económico'] = uso.sort_values('Dolares FOB', ascending=False)

    guardar_json(tablas, 'bloque_b_categorias')
    return dataframes


# =============================================================================
# 6. BLOQUE C — LOGÍSTICA
# =============================================================================
def bloque_c_logistica(df: pd.DataFrame) -> dict:
    print('\n' + '=' * 60)
    print('  BLOQUE C: ANÁLISIS LOGÍSTICO')
    print('=' * 60)

    if 'Impacto_Logistico_Pct' not in df.columns:
        print('  ❌ Impacto_Logistico_Pct no disponible')
        return {}

    tablas = {}
    dataframes = {}
    logistica = (
        df[df['Impacto_Logistico_Pct'].notna() & (df['Impacto_Logistico_Pct'] > 0)]
        .groupby('Nombre partida', as_index=False)['Impacto_Logistico_Pct'].median()
    )

    # ── Gráfico 9: Mayor impacto ──
    top_log = logistica.nlargest(TOP_N, 'Impacto_Logistico_Pct').sort_values('Impacto_Logistico_Pct')
    print('\n🚢 Top 10 Mayor Impacto Logístico:')
    print(top_log.to_string(index=False))
    barplot_horizontal(top_log, 'Impacto_Logistico_Pct', 'Nombre partida',
                       '🚢 Top 10 Mayor Impacto Logístico (% sobre FOB)',
                       '10_top10_mayor_impacto_logistico', color_palette='Reds_r', fmt='.1f')
    tablas['mayor_impacto'] = df_to_records(top_log.sort_values('Impacto_Logistico_Pct', ascending=False))
    dataframes['🚢 Top 10 Mayor Impacto Logístico (% sobre FOB)'] = top_log.sort_values('Impacto_Logistico_Pct', ascending=False)

    # ── Gráfico 10: Menor impacto ──
    bot_log = logistica.nsmallest(TOP_N, 'Impacto_Logistico_Pct').sort_values('Impacto_Logistico_Pct')
    print('\n✈️ Top 10 Menor Impacto Logístico:')
    print(bot_log.to_string(index=False))
    barplot_horizontal(bot_log, 'Impacto_Logistico_Pct', 'Nombre partida',
                       '✈️ Top 10 Menor Impacto Logístico (% sobre FOB)',
                       '11_top10_menor_impacto_logistico', color_palette='Greens_r', fmt='.2f')
    tablas['menor_impacto'] = df_to_records(bot_log.sort_values('Impacto_Logistico_Pct'))
    dataframes['✈️ Top 10 Menor Impacto Logístico (% sobre FOB)'] = bot_log.sort_values('Impacto_Logistico_Pct')

    guardar_json(tablas, 'bloque_c_logistica')
    return dataframes


# =============================================================================
# 7. BLOQUE D — GEOPOLÍTICO
# =============================================================================
def bloque_d_paises(df: pd.DataFrame) -> dict:
    print('\n' + '=' * 60)
    print('  BLOQUE D: ANÁLISIS GEOPOLÍTICO')
    print('=' * 60)

    if 'Pais de origen' not in df.columns:
        print('  ❌ Columna «Pais de origen» no encontrada')
        return {}

    tablas = {}
    dataframes = {}

    # ── Gráfico 11: Top 10 países FOB ──
    paises_fob = (
        df.groupby('Pais de origen', as_index=False)['Dolares FOB']
        .sum().nlargest(TOP_N, 'Dolares FOB').sort_values('Dolares FOB')
    )
    print('\n🌍 Top 10 Países Proveedores:')
    print(paises_fob.to_string(index=False))
    barplot_horizontal(paises_fob, 'Dolares FOB', 'Pais de origen',
                       '🌍 Top 10 Países Proveedores (USD FOB)',
                       '12_top10_paises_fob')
    tablas['paises_fob'] = df_to_records(paises_fob.sort_values('Dolares FOB', ascending=False))
    dataframes['🌍 Top 10 Países Proveedores (USD FOB)'] = paises_fob.sort_values('Dolares FOB', ascending=False)

    # ── Gráfico 12: Países flete caro ──
    if 'Impacto_Logistico_Pct' in df.columns:
        paises_flete = (
            df[df['Impacto_Logistico_Pct'].notna() & (df['Impacto_Logistico_Pct'] > 0)]
            .groupby('Pais de origen', as_index=False)['Impacto_Logistico_Pct']
            .mean().nlargest(TOP_N, 'Impacto_Logistico_Pct')
            .sort_values('Impacto_Logistico_Pct', ascending=True)
        )
        print('\n💸 Top 10 Países Flete Más Caro:')
        print(paises_flete.to_string(index=False))

        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(data=paises_flete, x='Impacto_Logistico_Pct', y='Pais de origen',
                    palette='OrRd', ax=ax, hue='Pais de origen', legend=False)
        ax.set_title('💸 Top 10 Países con Mayor Costo Logístico (% sobre FOB)', fontweight='bold', pad=15)
        ax.set_xlabel('Impacto Logístico Promedio (%)'); ax.set_ylabel('')
        for bar in ax.patches:
            w = bar.get_width()
            if w > 0:
                ax.text(w, bar.get_y() + bar.get_height() / 2, f'  {w:.1f}%', va='center', fontsize=9, color='#333')
        plt.tight_layout()
        guardar_chart(fig, '13_paises_flete_caro')
        tablas['paises_flete_caro'] = df_to_records(paises_flete.sort_values('Impacto_Logistico_Pct', ascending=False))
        dataframes['💸 Top 10 Países Flete Más Caro (% sobre FOB)'] = paises_flete.sort_values('Impacto_Logistico_Pct', ascending=False)

    guardar_json(tablas, 'bloque_d_paises')
    return dataframes


# =============================================================================
# 8. RESUMEN EJECUTIVO → KPIs JSON
# =============================================================================
def resumen_ejecutivo(df: pd.DataFrame) -> dict:
    print('\n' + '=' * 60)
    print('  📋 RESUMEN EJECUTIVO')
    print('=' * 60)

    kpis = {
        'registros': f'{len(df):,}',
        'productos_unicos': f'{df["Nombre partida"].nunique():,}',
        'paises_origen': f'{df["Pais de origen"].nunique():,}',
        'total_fob': f'USD {df["Dolares FOB"].sum():,.0f}',
        'total_cif': f'USD {df["Dolares CIF"].sum():,.0f}',
        'costo_logistico': f'USD {df.get("Costo_Logistico", pd.Series([0])).sum():,.0f}',
        'peso_total': f'{df["Kilogramos netos"].sum():,.0f} Kg',
        'generado': datetime.now().strftime('%d/%m/%Y %H:%M'),
    }

    print(f'  Registros:           {kpis["registros"]}')
    print(f'  Productos únicos:    {kpis["productos_unicos"]}')
    print(f'  Países de origen:    {kpis["paises_origen"]}')
    print(f'  Total FOB:           {kpis["total_fob"]}')
    print(f'  Total CIF:           {kpis["total_cif"]}')
    print(f'  Costo logístico:     {kpis["costo_logistico"]}')
    print(f'  Peso total:          {kpis["peso_total"]}')
    print('=' * 60)

    guardar_json(kpis, 'kpis')
    return kpis


# =============================================================================
# 8a-2. DASHBOARD OVERVIEW → Datos para el panel interactivo
# =============================================================================
def generar_dashboard_overview(df: pd.DataFrame) -> dict:
    """Genera datos para el dashboard overview didáctico al inicio de la página."""
    print('\n' + '=' * 60)
    print('  📊 DASHBOARD OVERVIEW')
    print('=' * 60)

    overview = {}

    # ── Totales generales ──
    total_cif = float(df['Dolares CIF'].sum())
    total_fob = float(df['Dolares FOB'].sum())
    total_logistico = total_cif - total_fob
    total_registros = len(df)

    overview['totales'] = {
        'total_cif': round(total_cif, 0),
        'total_fob': round(total_fob, 0),
        'total_logistico': round(total_logistico, 0),
        'total_registros': total_registros,
        'pct_logistico': round((total_logistico / total_fob * 100) if total_fob > 0 else 0, 1),
    }

    # ── Datos mensuales para mini bar chart ──
    if 'Mes' in df.columns:
        mensual = df.groupby('Mes').agg({
            'Dolares CIF': 'sum',
            'Dolares FOB': 'sum',
        }).reset_index()
        mensual = mensual.sort_values('Mes')
        overview['mensual'] = {
            'meses': mensual['Mes'].tolist(),
            'cif': [round(v, 0) for v in mensual['Dolares CIF'].tolist()],
            'fob': [round(v, 0) for v in mensual['Dolares FOB'].tolist()],
        }
        print(f'  ✅ Datos mensuales: {len(mensual)} meses')

    # ── Distribución por Uso Económico (donut) ──
    if 'Uso economico' in df.columns:
        uso_dist = df.groupby('Uso economico')['Dolares CIF'].sum().sort_values(ascending=False)
        uso_dist = uso_dist[uso_dist > 0]
        total = uso_dist.sum()
        uso_data = []
        for nombre, valor in uso_dist.items():
            uso_data.append({
                'nombre': str(nombre),
                'valor': round(float(valor), 0),
                'pct': round(float(valor) / total * 100, 1),
            })
        overview['uso_economico'] = uso_data
        print(f'  ✅ Uso económico: {len(uso_data)} categorías')

    # ── Top 5 Países (barra de progreso) ──
    if 'Pais de origen' in df.columns:
        pais_top = df.groupby('Pais de origen').agg({
            'Dolares CIF': 'sum',
            'Dolares FOB': 'sum',
        }).nlargest(5, 'Dolares CIF')
        max_cif = pais_top['Dolares CIF'].max()
        paises_data = []
        for pais, row in pais_top.iterrows():
            paises_data.append({
                'nombre': str(pais),
                'cif': round(float(row['Dolares CIF']), 0),
                'fob': round(float(row['Dolares FOB']), 0),
                'pct_bar': round(float(row['Dolares CIF']) / max_cif * 100, 1),
            })
        overview['top_paises'] = paises_data
        print(f'  ✅ Top 5 países exportados')

    # ── Top 5 Productos más importados ──
    if 'Nombre partida' in df.columns:
        prod_top = df.groupby('Nombre partida').agg({
            'Dolares CIF': 'sum',
            'Cantidad': 'sum',
        }).nlargest(5, 'Dolares CIF')
        productos_data = []
        for prod, row in prod_top.iterrows():
            nombre = str(prod)
            if len(nombre) > 45:
                nombre = nombre[:45] + '...'
            productos_data.append({
                'nombre': nombre,
                'cif': round(float(row['Dolares CIF']), 0),
                'cantidad': round(float(row['Cantidad']), 0),
            })
        overview['top_productos'] = productos_data
        print(f'  ✅ Top 5 productos exportados')

    # ── Nivel Tecnológico (mini resumen) ──
    if 'Nivel tecnologico' in df.columns:
        nivel_dist = df.groupby('Nivel tecnologico')['Dolares CIF'].sum().sort_values(ascending=False)
        nivel_dist = nivel_dist[nivel_dist > 0]
        total_nivel = nivel_dist.sum()
        nivel_data = []
        for nombre, valor in nivel_dist.items():
            nivel_data.append({
                'nombre': str(nombre),
                'valor': round(float(valor), 0),
                'pct': round(float(valor) / total_nivel * 100, 1),
            })
        overview['nivel_tecnologico'] = nivel_data
        print(f'  ✅ Nivel tecnológico: {len(nivel_data)} niveles')

    guardar_json(overview, 'dashboard_overview')
    print(f'  📦 dashboard_overview.json exportado')
    return overview


# =============================================================================
# 8b. VALUE ROW → Métricas financieras avanzadas
# =============================================================================
def calcular_value_row(df: pd.DataFrame) -> dict:
    print('\n' + '=' * 60)
    print('  📊 VALUE ROW: MÉTRICAS FINANCIERAS AVANZADAS')
    print('=' * 60)

    value_row = {}

    # ── Market Share por País (en CIF) ──
    if 'Pais de origen' in df.columns and 'Dolares CIF' in df.columns:
        pais_cif = df.groupby('Pais de origen')['Dolares CIF'].sum()
        total_cif = pais_cif.sum()
        pais_lider = pais_cif.idxmax()
        pais_lider_valor = pais_cif.max()
        pais_lider_pct = (pais_lider_valor / total_cif * 100) if total_cif > 0 else 0

        value_row['market_share_pais'] = pais_lider
        value_row['market_share_valor'] = f'USD {pais_lider_valor:,.0f}'
        value_row['market_share_pct'] = f'{pais_lider_pct:.1f}%'
        print(f'  🏆 Market Share: {pais_lider} → {pais_lider_pct:.1f}% del CIF total')

    # ── Costo Unitario CIF Promedio Global ──
    if 'Dolares CIF' in df.columns and 'Cantidad' in df.columns:
        total_cif = df['Dolares CIF'].sum()
        total_cant = df[df['Cantidad'] > 0]['Cantidad'].sum()
        costo_unitario_cif = total_cif / total_cant if total_cant > 0 else 0

        value_row['costo_unitario_cif'] = f'USD {costo_unitario_cif:,.2f}'
        value_row['costo_unitario_cif_raw'] = round(costo_unitario_cif, 2)
        print(f'  💲 Costo Unitario CIF Global: USD {costo_unitario_cif:,.2f}')

    # ── Tendencia de Fletes ──
    if 'Costo_Logistico' in df.columns and 'Mes' in df.columns:
        flete_por_mes = df.groupby('Mes')['Costo_Logistico'].sum().sort_index()
        if len(flete_por_mes) >= 2:
            primer_mes = flete_por_mes.index[0]
            ultimo_mes = flete_por_mes.index[-1]
            val_primer = flete_por_mes.iloc[0]
            val_ultimo = flete_por_mes.iloc[-1]
            cambio_pct = ((val_ultimo - val_primer) / val_primer * 100) if val_primer > 0 else 0

            value_row['fletes_primer_mes'] = int(primer_mes)
            value_row['fletes_ultimo_mes'] = int(ultimo_mes)
            value_row['fletes_val_primer'] = f'USD {val_primer:,.0f}'
            value_row['fletes_val_ultimo'] = f'USD {val_ultimo:,.0f}'
            value_row['fletes_cambio_pct'] = f'{cambio_pct:+.1f}%'
            value_row['fletes_tendencia'] = 'up' if cambio_pct > 0 else 'down'
            print(f'  📈 Tendencia Fletes: Mes {primer_mes} ({val_primer:,.0f}) → Mes {ultimo_mes} ({val_ultimo:,.0f}) = {cambio_pct:+.1f}%')

    guardar_json(value_row, 'value_row')
    print('  ✅ value_row.json exportado')
    return value_row


# =============================================================================
# 8c. BLOQUE E — VISUALIZACIONES ESTRATÉGICAS
# =============================================================================
def bloque_e_estrategico(df: pd.DataFrame) -> dict:
    print('\n' + '=' * 60)
    print('  BLOQUE E: VISUALIZACIONES ESTRATÉGICAS')
    print('=' * 60)

    tablas = {}
    dataframes = {}

    # ── Gráfico 14: Sankey (Plotly) ──
    # Flujo: País de origen (Top 5) → Uso económico → Nivel tecnológico
    cols_sankey = ['Pais de origen', 'Uso economico', 'Nivel tecnologico', 'Dolares CIF']
    if all(c in df.columns for c in cols_sankey):
        print('\n🔀 Generando Diagrama Sankey...')
        df_sankey = df[df['Dolares CIF'] > 0].copy()

        # Top 5 países por CIF
        top5_paises = df_sankey.groupby('Pais de origen')['Dolares CIF'].sum().nlargest(5).index.tolist()
        df_sankey = df_sankey[df_sankey['Pais de origen'].isin(top5_paises)]

        # Nodos: países, usos económicos, niveles tecnológicos
        paises = df_sankey['Pais de origen'].unique().tolist()
        usos = df_sankey['Uso economico'].dropna().unique().tolist()
        niveles = df_sankey['Nivel tecnologico'].dropna().unique().tolist()

        all_nodes = paises + usos + niveles
        node_idx = {name: i for i, name in enumerate(all_nodes)}

        # Links: País → Uso económico
        link_pu = df_sankey.groupby(['Pais de origen', 'Uso economico'])['Dolares CIF'].sum().reset_index()
        link_pu = link_pu[link_pu['Dolares CIF'] > 0]

        # Links: Uso económico → Nivel tecnológico
        link_un = df_sankey.groupby(['Uso economico', 'Nivel tecnologico'])['Dolares CIF'].sum().reset_index()
        link_un = link_un[link_un['Dolares CIF'] > 0]

        sources, targets, values = [], [], []

        for _, row in link_pu.iterrows():
            if row['Pais de origen'] in node_idx and row['Uso economico'] in node_idx:
                sources.append(node_idx[row['Pais de origen']])
                targets.append(node_idx[row['Uso economico']])
                values.append(row['Dolares CIF'])

        for _, row in link_un.iterrows():
            if row['Uso economico'] in node_idx and row['Nivel tecnologico'] in node_idx:
                sources.append(node_idx[row['Uso economico']])
                targets.append(node_idx[row['Nivel tecnologico']])
                values.append(row['Dolares CIF'])

        # Colores por tipo de nodo
        node_colors = []
        for node in all_nodes:
            if node in paises:
                node_colors.append('rgba(79, 70, 229, 0.8)')   # Índigo
            elif node in usos:
                node_colors.append('rgba(16, 185, 129, 0.8)')  # Esmeralda
            else:
                node_colors.append('rgba(139, 92, 246, 0.8)')  # Violeta

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=25,
                line=dict(color='rgba(0,0,0,0.15)', width=0.5),
                label=all_nodes,
                color=node_colors,
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color='rgba(200, 200, 220, 0.3)',
            )
        )])

        fig_sankey.update_layout(
            title_text='Flujo de Valor CIF: País de Origen → Uso Económico → Nivel Tecnológico',
            font=dict(family='Inter, sans-serif', size=13),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=550,
            margin=dict(l=20, r=20, t=60, b=20),
        )

        sankey_path = os.path.join(CHARTS_DIR, 'sankey_flow.html')
        fig_sankey.write_html(
            sankey_path,
            full_html=True,
            include_plotlyjs='cdn',
            config={'responsive': True, 'displayModeBar': False}
        )
        print(f'  💾 sankey_flow.html guardado')

        # Datos para tabla
        sankey_table = link_pu.sort_values('Dolares CIF', ascending=False).head(15)
        tablas['sankey_flows'] = df_to_records(sankey_table)
        dataframes['Flujos Sankey (País → Uso Económico)'] = sankey_table

    # ── Gráfico 15: Heatmap de Crecimiento por Sector ──
    if 'Mes' in df.columns and 'Nombre capitulo' in df.columns:
        print('\n🔥 Generando Heatmap de Sectores...')

        # Top 10 sectores por FOB total
        top10_sectores = (
            df.groupby('Nombre capitulo')['Dolares FOB'].sum()
            .nlargest(10).index.tolist()
        )
        df_heat = df[df['Nombre capitulo'].isin(top10_sectores)].copy()
        pivot = df_heat.pivot_table(
            values='Dolares FOB', index='Nombre capitulo', columns='Mes',
            aggfunc='sum', fill_value=0
        )
        # Truncar nombres largos para el eje Y
        pivot.index = [n[:45] + '...' if len(n) > 45 else n for n in pivot.index]

        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(
            pivot, annot=True, fmt=',.0f', cmap='YlOrRd',
            linewidths=0.5, linecolor='white',
            cbar_kws={'label': 'USD FOB'},
            ax=ax
        )
        ax.set_title('Mapa de Calor: FOB por Sector × Mes', fontweight='bold', pad=15)
        ax.set_xlabel('Mes')
        ax.set_ylabel('')
        plt.xticks(rotation=0)
        plt.yticks(rotation=0, fontsize=8)
        plt.tight_layout()
        guardar_chart(fig, '14_heatmap_sectores')

        tablas['heatmap_sectores'] = df_to_records(
            pivot.reset_index().rename(columns={'Nombre capitulo': 'Sector'})
        )
        dataframes['Heatmap Sectores × Mes'] = pivot.reset_index()

    # ── Gráfico 16: Scatter Benchmarking ──
    cols_scatter = ['Nombre partida', 'Kilogramos netos', 'Dolares CIF', 'Cantidad']
    if all(c in df.columns for c in cols_scatter):
        print('\n📊 Generando Scatter Benchmarking...')

        # Top 30 productos por CIF total
        top30 = df.groupby('Nombre partida').agg({
            'Kilogramos netos': 'sum',
            'Dolares CIF': 'sum',
            'Cantidad': 'sum'
        }).nlargest(30, 'Dolares CIF').reset_index()

        # Costo unitario CIF = CIF / Cantidad
        top30 = top30[top30['Cantidad'] > 0].copy()
        top30['Costo_Unitario_CIF'] = top30['Dolares CIF'] / top30['Cantidad']

        fig, ax = plt.subplots(figsize=(14, 9))

        # Normalizar tamaño de burbujas
        sizes = top30['Dolares CIF'] / top30['Dolares CIF'].max() * 1500 + 50

        scatter = ax.scatter(
            top30['Kilogramos netos'],
            top30['Costo_Unitario_CIF'],
            s=sizes,
            alpha=0.6,
            c=top30['Dolares CIF'],
            cmap='viridis',
            edgecolors='white',
            linewidth=0.8,
        )

        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title('Benchmarking: Top 30 Productos — Volumen vs Precio Unitario CIF',
                     fontweight='bold', pad=15)
        ax.set_xlabel('Volumen (Kg Netos) — escala log')
        ax.set_ylabel('Costo Unitario CIF (USD/Unidad) — escala log')

        cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
        cbar.set_label('Total CIF (USD)')

        # Anotar top 5 productos
        for _, row in top30.nlargest(5, 'Dolares CIF').iterrows():
            nombre_corto = row['Nombre partida'][:30] + '...' if len(row['Nombre partida']) > 30 else row['Nombre partida']
            ax.annotate(
                nombre_corto,
                (row['Kilogramos netos'], row['Costo_Unitario_CIF']),
                fontsize=7, alpha=0.85,
                xytext=(10, 10), textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color='gray', lw=0.5)
            )

        plt.tight_layout()
        guardar_chart(fig, '15_scatter_benchmarking')

        # Datos para tabla
        scatter_data = top30[['Nombre partida', 'Kilogramos netos', 'Costo_Unitario_CIF', 'Dolares CIF']].copy()
        scatter_data = scatter_data.sort_values('Dolares CIF', ascending=False)
        tablas['scatter_benchmarking'] = df_to_records(scatter_data)
        dataframes['Scatter Benchmarking Top 30'] = scatter_data

    guardar_json(tablas, 'bloque_e_estrategico')
    return dataframes


# =============================================================================
# 8d. BLOQUE F — MAPA GEOGRÁFICO + CALCULADORA INTELIGENTE
# =============================================================================
# Mapeo de nombres de países español → inglés para plotly choropleth
PAIS_MAP_ES_EN = {
    'China': 'China', 'Estados Unidos': 'United States', 'Mexico': 'Mexico',
    'México': 'Mexico', 'Alemania': 'Germany', 'Brasil': 'Brazil',
    'Japón': 'Japan', 'Japon': 'Japan', 'Corea del Sur': 'South Korea',
    'Corea': 'South Korea', 'Francia': 'France', 'Italia': 'Italy',
    'Reino Unido': 'United Kingdom', 'España': 'Spain', 'India': 'India',
    'Canadá': 'Canada', 'Canada': 'Canada', 'Colombia': 'Colombia',
    'Argentina': 'Argentina', 'Chile': 'Chile', 'Perú': 'Peru', 'Peru': 'Peru',
    'Ecuador': 'Ecuador', 'Turquía': 'Turkey', 'Turquia': 'Turkey',
    'Tailandia': 'Thailand', 'Taiwan': 'Taiwan', 'Taiwán': 'Taiwan',
    'Suiza': 'Switzerland', 'Países Bajos': 'Netherlands', 'Paises Bajos': 'Netherlands',
    'Holanda': 'Netherlands', 'Bélgica': 'Belgium', 'Belgica': 'Belgium',
    'Suecia': 'Sweden', 'Austria': 'Austria', 'Polonia': 'Poland',
    'Noruega': 'Norway', 'Dinamarca': 'Denmark', 'Finlandia': 'Finland',
    'Portugal': 'Portugal', 'Irlanda': 'Ireland', 'Rusia': 'Russia',
    'Federacion de Rusia': 'Russia', 'Israel': 'Israel',
    'Sudafrica': 'South Africa', 'Sudáfrica': 'South Africa',
    'Australia': 'Australia', 'Nueva Zelanda': 'New Zealand',
    'Indonesia': 'Indonesia', 'Malasia': 'Malaysia', 'Filipinas': 'Philippines',
    'Vietnam': 'Vietnam', 'Viet Nam': 'Vietnam', 'Singapur': 'Singapore',
    'Emiratos Arabes Unidos': 'United Arab Emirates',
    'Arabia Saudita': 'Saudi Arabia', 'Egipto': 'Egypt',
    'Venezuela': 'Venezuela', 'Paraguay': 'Paraguay', 'Uruguay': 'Uruguay',
    'Bolivia': 'Bolivia', 'Panamá': 'Panama', 'Panama': 'Panama',
    'Costa Rica': 'Costa Rica', 'Guatemala': 'Guatemala',
    'Honduras': 'Honduras', 'El Salvador': 'El Salvador',
    'República Dominicana': 'Dominican Republic',
    'Puerto Rico': 'Puerto Rico', 'Cuba': 'Cuba', 'Trinidad y Tobago': 'Trinidad and Tobago',
    'Jamaica': 'Jamaica', 'Nicaragua': 'Nicaragua',
    'República Checa': 'Czech Republic', 'Republica Checa': 'Czech Republic',
    'Hungría': 'Hungary', 'Hungria': 'Hungary', 'Rumania': 'Romania',
    'Grecia': 'Greece', 'Pakistán': 'Pakistan', 'Pakistan': 'Pakistan',
    'Bangladesh': 'Bangladesh', 'Sri Lanka': 'Sri Lanka',
    'Marruecos': 'Morocco', 'Túnez': 'Tunisia', 'Nigeria': 'Nigeria',
    'Kenia': 'Kenya', 'Ghana': 'Ghana', 'Etiopía': 'Ethiopia',
    'Hong Kong': 'Hong Kong',
}


def bloque_f_mapas(df: pd.DataFrame) -> dict:
    print('\n' + '=' * 60)
    print('  BLOQUE F: MAPA GEOGRÁFICO + CALCULADORA INTELIGENTE')
    print('=' * 60)

    tablas = {}
    dataframes = {}

    # ── Gráfico 17: Mapa Geográfico Coroplético (Plotly) ──
    if 'Pais de origen' in df.columns and 'Dolares CIF' in df.columns:
        print('\n🌍 Generando Mapa Geográfico...')

        pais_cif = df.groupby('Pais de origen')['Dolares CIF'].sum().reset_index()
        pais_cif.columns = ['Pais', 'Total_CIF']
        pais_cif = pais_cif[pais_cif['Total_CIF'] > 0].sort_values('Total_CIF', ascending=False)

        # Mapear nombres al inglés para plotly
        pais_cif['Country'] = pais_cif['Pais'].map(PAIS_MAP_ES_EN).fillna(pais_cif['Pais'])

        fig_map = px.choropleth(
            pais_cif,
            locations='Country',
            locationmode='country names',
            color='Total_CIF',
            hover_name='Pais',
            hover_data={'Total_CIF': ':,.0f', 'Country': False},
            color_continuous_scale='YlOrRd',
            labels={'Total_CIF': 'USD CIF'},
            title='Mapa de Calor Geográfico: Importaciones por País de Origen (USD CIF)',
        )

        fig_map.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor='rgba(100,100,100,0.3)',
                projection_type='natural earth',
                landcolor='rgba(240,240,240,1)',
                showland=True,
                showcountries=True,
                countrycolor='rgba(200,200,200,0.5)',
            ),
            font=dict(family='Inter, sans-serif', size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=550,
            margin=dict(l=10, r=10, t=60, b=10),
            coloraxis_colorbar=dict(
                title='USD CIF',
                tickformat=',',
            ),
        )

        map_path = os.path.join(CHARTS_DIR, 'mapa_importaciones.html')
        fig_map.write_html(
            map_path,
            full_html=True,
            include_plotlyjs='cdn',
            config={'responsive': True, 'displayModeBar': False}
        )
        print(f'  💾 mapa_importaciones.html guardado')

        # Datos para tabla
        map_table = pais_cif[['Pais', 'Total_CIF']].head(20)
        tablas['mapa_paises'] = df_to_records(map_table)
        dataframes['Mapa: Top 20 Países por CIF'] = map_table

    # ── Gráfico 18: Top 15 Productos con Mayor Carga Impositiva (Costo Logístico) ──
    if 'Impacto_Logistico_Pct' in df.columns and 'Nombre capitulo' in df.columns:
        print('\n💸 Generando gráfico de carga impositiva por sector...')

        carga_sector = (
            df[df['Impacto_Logistico_Pct'].notna() & (df['Impacto_Logistico_Pct'] > 0)]
            .groupby('Nombre capitulo').agg({
                'Impacto_Logistico_Pct': 'median',
                'Costo_Logistico': 'sum',
                'Dolares CIF': 'sum'
            }).reset_index()
        )
        carga_sector.columns = ['Sector', 'Impacto_Logistico_Mediana', 'Costo_Logistico_Total', 'Total_CIF']
        carga_top = carga_sector.nlargest(15, 'Impacto_Logistico_Mediana').sort_values('Impacto_Logistico_Mediana')

        # Truncar nombres para el eje
        top_labels = [s[:40] + '...' if len(s) > 40 else s for s in carga_top['Sector']]

        fig, ax = plt.subplots(figsize=(14, 9))
        bars = ax.barh(
            range(len(carga_top)),
            carga_top['Impacto_Logistico_Mediana'],
            color=plt.cm.Reds(np.linspace(0.3, 0.9, len(carga_top))),
            edgecolor='white',
            linewidth=0.5,
        )
        ax.set_yticks(range(len(carga_top)))
        ax.set_yticklabels(top_labels, fontsize=8)
        ax.set_title('Top 15 Sectores con Mayor Carga de Costo Logístico (% sobre FOB)',
                     fontweight='bold', pad=15)
        ax.set_xlabel('Impacto Logístico Mediano (%)')

        for i, bar in enumerate(bars):
            w = bar.get_width()
            costo = carga_top.iloc[i]['Costo_Logistico_Total']
            ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2,
                    f'{w:.1f}% (USD {costo:,.0f})',
                    va='center', fontsize=8, color='#333')

        plt.tight_layout()
        guardar_chart(fig, '16_carga_impositiva_sectores')

        tablas['carga_impositiva'] = df_to_records(
            carga_top.sort_values('Impacto_Logistico_Mediana', ascending=False)
        )
        dataframes['Top 15 Sectores Mayor Carga Impositiva'] = carga_top.sort_values(
            'Impacto_Logistico_Mediana', ascending=False
        )

    # ── Datos para Calculadora Inteligente (Lookup por Capítulo × País) ──
    if all(c in df.columns for c in ['Nombre capitulo', 'Pais de origen', 'Impacto_Logistico_Pct', 'Dolares CIF']):
        print('\n🧮 Generando datos para calculadora inteligente...')

        # Impacto logístico mediano por sector
        sector_impacto = (
            df[df['Impacto_Logistico_Pct'].notna() & (df['Impacto_Logistico_Pct'] > 0)]
            .groupby('Nombre capitulo')['Impacto_Logistico_Pct'].median()
            .round(2).to_dict()
        )

        # Impacto logístico mediano por país
        pais_impacto = (
            df[df['Impacto_Logistico_Pct'].notna() & (df['Impacto_Logistico_Pct'] > 0)]
            .groupby('Pais de origen')['Impacto_Logistico_Pct'].median()
            .round(2).to_dict()
        )

        # CIF promedio por sector (para pre-llenar el valor CIF)
        sector_cif_promedio = (
            df[df['Dolares CIF'] > 0]
            .groupby('Nombre capitulo')['Dolares CIF'].median()
            .round(0).to_dict()
        )

        # Lista de sectores y países ordenados por frecuencia
        sectores_list = (
            df.groupby('Nombre capitulo')['Dolares CIF'].sum()
            .sort_values(ascending=False).index.tolist()
        )
        paises_list = (
            df.groupby('Pais de origen')['Dolares CIF'].sum()
            .sort_values(ascending=False).index.tolist()
        )

        calc_data = {
            'sectores': sectores_list,
            'paises': paises_list,
            'sector_impacto': sector_impacto,
            'pais_impacto': pais_impacto,
            'sector_cif_promedio': {k: int(v) for k, v in sector_cif_promedio.items()},
        }

        guardar_json(calc_data, 'calculadora_data')
        print(f'  ✅ calculadora_data.json exportado ({len(sectores_list)} sectores, {len(paises_list)} países)')

    guardar_json(tablas, 'bloque_f_mapas')
    return dataframes


# =============================================================================
# 9. REPORTE DE TEXTO — Exporta todos los DataFrames a .txt
# =============================================================================
def generar_reporte_texto(kpis: dict, bloques: dict):
    """Genera un archivo de texto con todos los resultados tabulares."""
    ruta = os.path.join(DATA_DIR, 'resultados_completos.txt')
    ahora = datetime.now().strftime('%d/%m/%Y %H:%M')

    with open(ruta, 'w', encoding='utf-8') as f:
        f.write('=' * 80 + '\n')
        f.write('  REPORTE COMPLETO DE IMPORTACIONES — BOGOTÁ\n')
        f.write(f'  Generado: {ahora}\n')
        f.write('=' * 80 + '\n\n')

        # ── KPIs ──
        f.write('─' * 80 + '\n')
        f.write('  📋 RESUMEN EJECUTIVO (KPIs)\n')
        f.write('─' * 80 + '\n')
        labels = {
            'registros': 'Registros totales',
            'productos_unicos': 'Productos únicos',
            'paises_origen': 'Países de origen',
            'total_fob': 'Total FOB',
            'total_cif': 'Total CIF',
            'costo_logistico': 'Costo logístico total',
            'peso_total': 'Peso total',
        }
        for key, label in labels.items():
            f.write(f'  {label:.<30} {kpis.get(key, "N/A")}\n')
        f.write('\n')

        # ── Cada bloque ──
        bloque_nombres = {
            'A': '📦 BLOQUE A: ANÁLISIS DE PRODUCTOS',
            'B': '🏷️ BLOQUE B: CATEGORÍAS ESTRATÉGICAS',
            'C': '🚢 BLOQUE C: ANÁLISIS LOGÍSTICO',
            'D': '🌍 BLOQUE D: ANÁLISIS GEOPOLÍTICO',
            'E': '🔬 BLOQUE E: VISUALIZACIONES ESTRATÉGICAS',
            'F': '🌎 BLOQUE F: MAPA GEOGRÁFICO + CALCULADORA',
        }

        for bloque_id, titulo in bloque_nombres.items():
            dfs = bloques.get(bloque_id, {})
            if not dfs:
                continue

            f.write('\n' + '=' * 80 + '\n')
            f.write(f'  {titulo}\n')
            f.write('=' * 80 + '\n')

            for nombre_tabla, df in dfs.items():
                f.write('\n' + '─' * 80 + '\n')
                f.write(f'  {nombre_tabla}\n')
                f.write('─' * 80 + '\n')
                f.write(df.to_string(index=False) + '\n')

        f.write('\n' + '=' * 80 + '\n')
        f.write(f'  FIN DEL REPORTE · {ahora}\n')
        f.write('=' * 80 + '\n')

    print(f'  📝 resultados_completos.txt guardado')


# =============================================================================
# MAIN
# =============================================================================
def main():
    setup_dirs()

    # Detección automática del archivo (csv o xlsx)
    archivo = ARCHIVO
    if not os.path.exists(archivo):
        # Buscar alternativa xlsx
        alt = archivo.replace('.csv', '.xlsx')
        if os.path.exists(alt):
            archivo = alt
        else:
            alt2 = archivo.replace('.csv', ' - copia.xlsx')
            if os.path.exists(alt2):
                archivo = alt2
            else:
                print(f'  ❌ No se encontró el dataset en: {archivo}')
                print('  💡 Descárgalo de: https://www.datos.gov.co/dataset/Importaciones-Bogot-/vdw8-sjw6/about_data')
                return

    df = cargar_datos(archivo)
    df = limpiar_datos(df)
    df = crear_metricas(df)

    kpis = resumen_ejecutivo(df)
    dashboard_ov = generar_dashboard_overview(df)
    value_row = calcular_value_row(df)

    bloques = {
        'A': bloque_a_productos(df),
        'B': bloque_b_categorias(df),
        'C': bloque_c_logistica(df),
        'D': bloque_d_paises(df),
        'E': bloque_e_estrategico(df),
        'F': bloque_f_mapas(df),
    }

    # Generar reporte de texto con todos los DataFrames
    generar_reporte_texto(kpis, bloques)

    print('\n🎉 ¡Análisis completo!')
    print(f'  📁 Gráficos PNG: {CHARTS_DIR}')
    print(f'  📄 Datos JSON:   {DATA_DIR}')
    print(f'  📝 Reporte TXT:  {os.path.join(DATA_DIR, "resultados_completos.txt")}')
    print(f'  🌐 Abre index.html en tu navegador para ver el reporte')
    print(f'\n  💡 Tip: Para servir localmente, ejecuta:')
    print(f'     python -m http.server 8000')
    print(f'     y abre http://localhost:8000/index.html')


if __name__ == '__main__':
    main()
