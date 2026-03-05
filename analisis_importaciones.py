# =============================================================================
# analisis_importaciones.py — Análisis de Importaciones Bogotá
# Autor: Santiago (asistido por IA)
# Genera 12 gráficos profesionales + Reporte HTML interactivo
# =============================================================================

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para evitar problemas
import matplotlib.pyplot as plt
import seaborn as sns
import os
import base64
import warnings
from io import BytesIO
from datetime import datetime

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
ARCHIVO = r'C:\Users\santi\Documents\Santiago\CD\proyectos\Exportaciones e importaciones Colombia\conjunto-importaciones-bogota-21102025.csv'
OUTPUT_DIR = r'C:\Users\santi\Documents\Santiago\CD\proyectos\Exportaciones e importaciones Colombia\graficos_output'
HTML_OUTPUT = r'C:\Users\santi\Documents\Santiago\CD\proyectos\Exportaciones e importaciones Colombia\reporte_importaciones.html'

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

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =============================================================================
# COLECTOR HTML — almacena secciones para el reporte final
# =============================================================================
class ReporteHTML:
    """Acumula secciones HTML y las renderiza al final."""

    def __init__(self):
        self.secciones = []
        self.resumen = {}

    def agregar_seccion(self, titulo, contenido_html, icono='📊'):
        self.secciones.append({'titulo': titulo, 'html': contenido_html, 'icono': icono})

    def fig_a_base64(self, fig) -> str:
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white', dpi=150)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return b64

    def img_tag(self, fig) -> str:
        b64 = self.fig_a_base64(fig)
        return f'<img src="data:image/png;base64,{b64}" style="width:100%;max-width:900px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.12);margin:16px 0;">'

    def tabla_html(self, df, max_rows=15) -> str:
        return df.head(max_rows).to_html(
            index=False, border=0,
            classes='data-table',
            float_format=lambda x: f'{x:,.2f}' if abs(x) > 1 else f'{x:.4f}'
        )

    def generar(self, ruta_salida: str):
        ahora = datetime.now().strftime('%d/%m/%Y %H:%M')
        nav_items = ''.join(
            f'<a href="#seccion-{i}" class="nav-link">{s["icono"]} {s["titulo"]}</a>'
            for i, s in enumerate(self.secciones)
        )
        secciones_html = ''
        for i, s in enumerate(self.secciones):
            secciones_html += f'''
            <section id="seccion-{i}" class="card">
                <h2>{s["icono"]} {s["titulo"]}</h2>
                {s["html"]}
            </section>'''

        resumen_kpi = ''
        if self.resumen:
            cards = ''
            for label, valor in self.resumen.items():
                cards += f'''
                <div class="kpi-card">
                    <div class="kpi-value">{valor}</div>
                    <div class="kpi-label">{label}</div>
                </div>'''
            resumen_kpi = f'<div class="kpi-grid">{cards}</div>'

        html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reporte de Importaciones — Bogotá</title>
<style>
    :root {{
        --bg: #0f172a;
        --surface: #1e293b;
        --surface2: #334155;
        --accent: #38bdf8;
        --accent2: #818cf8;
        --text: #e2e8f0;
        --text-dim: #94a3b8;
        --success: #34d399;
        --warning: #fbbf24;
        --danger: #f87171;
        --radius: 16px;
    }}
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        background: var(--bg);
        color: var(--text);
        line-height: 1.7;
    }}
    /* ── HEADER ── */
    .hero {{
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
        padding: 60px 40px 40px;
        text-align: center;
        border-bottom: 1px solid var(--surface2);
        position: relative;
        overflow: hidden;
    }}
    .hero::before {{
        content: '';
        position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 30% 40%, rgba(56,189,248,.15), transparent 60%),
                    radial-gradient(circle at 70% 60%, rgba(129,140,248,.1), transparent 50%);
    }}
    .hero h1 {{
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        position: relative;
    }}
    .hero .subtitle {{
        color: var(--text-dim);
        font-size: 1rem;
        margin-top: 8px;
        position: relative;
    }}
    /* ── NAV ── */
    .nav {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding: 16px 40px;
        background: var(--surface);
        border-bottom: 1px solid var(--surface2);
        position: sticky; top: 0; z-index: 100;
        backdrop-filter: blur(12px);
    }}
    .nav-link {{
        color: var(--text-dim);
        text-decoration: none;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: .85rem;
        transition: all .2s;
    }}
    .nav-link:hover {{
        background: var(--surface2);
        color: var(--accent);
    }}
    /* ── KPI ── */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        padding: 30px 40px;
    }}
    .kpi-card {{
        background: var(--surface);
        border: 1px solid var(--surface2);
        border-radius: var(--radius);
        padding: 24px;
        text-align: center;
        transition: transform .2s, box-shadow .2s;
    }}
    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(56,189,248,.1);
    }}
    .kpi-value {{
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .kpi-label {{
        color: var(--text-dim);
        font-size: .85rem;
        margin-top: 6px;
    }}
    /* ── CARDS ── */
    .container {{
        max-width: 1100px;
        margin: 0 auto;
        padding: 30px 20px;
    }}
    .card {{
        background: var(--surface);
        border: 1px solid var(--surface2);
        border-radius: var(--radius);
        padding: 32px;
        margin-bottom: 28px;
        transition: box-shadow .3s;
    }}
    .card:hover {{
        box-shadow: 0 4px 24px rgba(0,0,0,.25);
    }}
    .card h2 {{
        font-size: 1.35rem;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--surface2);
        color: var(--accent);
    }}
    .card img {{
        display: block;
        margin: 0 auto;
    }}
    /* ── TABLAS ── */
    .data-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: .88rem;
    }}
    .data-table th {{
        background: var(--surface2);
        color: var(--accent);
        padding: 10px 14px;
        text-align: left;
        font-weight: 600;
        position: sticky; top: 0;
    }}
    .data-table td {{
        padding: 8px 14px;
        border-bottom: 1px solid rgba(255,255,255,.06);
    }}
    .data-table tr:hover td {{
        background: rgba(56,189,248,.05);
    }}
    .data-table tr:nth-child(even) td {{
        background: rgba(255,255,255,.02);
    }}
    /* ── FOOTER ── */
    .footer {{
        text-align: center;
        padding: 40px;
        color: var(--text-dim);
        font-size: .8rem;
        border-top: 1px solid var(--surface2);
    }}
    /* ── SCROLL ── */
    html {{ scroll-behavior: smooth; }}
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg); }}
    ::-webkit-scrollbar-thumb {{ background: var(--surface2); border-radius: 4px; }}
</style>
</head>
<body>
    <div class="hero">
        <h1>📦 Reporte de Importaciones — Bogotá</h1>
        <p class="subtitle">Generado el {ahora} · Análisis de inteligencia comercial</p>
    </div>
    <nav class="nav">{nav_items}</nav>
    {resumen_kpi}
    <div class="container">
        {secciones_html}
    </div>
    <div class="footer">
        Generado automáticamente por <strong>analisis_importaciones.py</strong> · {ahora}
    </div>
</body>
</html>'''
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'\n  🌐 Reporte HTML guardado en: {ruta_salida}')


# Instancia global del reporte
reporte = ReporteHTML()


# =============================================================================
# 1. CARGA
# =============================================================================
def cargar_datos(ruta: str) -> pd.DataFrame:
    print('=' * 60)
    print('  CARGANDO DATOS')
    print('=' * 60)
    try:
        df = pd.read_excel(ruta, engine='calamine')
        print(f'  ✅ Archivo cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas')
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
# UTILIDADES
# =============================================================================
def guardar(fig, nombre: str):
    ruta = os.path.join(OUTPUT_DIR, f'{nombre}.png')
    fig.savefig(ruta, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  💾 {nombre}.png guardado')


def barplot_horizontal(data, x, y, titulo, nombre_archivo, color_palette=PALETTE, fmt=',.0f'):
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
    guardar(fig, nombre_archivo)
    return fig


def barplot_horizontal_fig(data, x, y, titulo, color_palette=PALETTE, fmt=',.0f'):
    """Igual que barplot_horizontal pero retorna el fig sin cerrar."""
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
    return fig


# =============================================================================
# 4. BLOQUE A — PRODUCTOS
# =============================================================================
def bloque_a_productos(df: pd.DataFrame):
    print('\n' + '=' * 60)
    print('  BLOQUE A: ANÁLISIS DE PRODUCTOS')
    print('=' * 60)

    html_partes = []

    # ── Gráfico 1: Top 10 más valiosos ──
    top_fob = (
        df.groupby('Nombre partida', as_index=False)['Dolares FOB']
        .sum().nlargest(TOP_N, 'Dolares FOB').sort_values('Dolares FOB')
    )
    print('\n📊 Top 10 Productos Más Valiosos (USD FOB):')
    print(top_fob.to_string(index=False))

    fig = barplot_horizontal_fig(top_fob, 'Dolares FOB', 'Nombre partida',
                                 'Top 10 Productos Más Valiosos (Total USD FOB)')
    guardar(fig, '01_top10_productos_valiosos')
    # Re-crear para el HTML (guardar cierra el fig)
    fig = barplot_horizontal_fig(top_fob, 'Dolares FOB', 'Nombre partida',
                                 'Top 10 Productos Más Valiosos (Total USD FOB)')
    html_partes.append(f'<h3>1. Top 10 Más Valiosos (FOB)</h3>{reporte.img_tag(fig)}')
    html_partes.append(reporte.tabla_html(top_fob.sort_values('Dolares FOB', ascending=False)))
    plt.close(fig)

    # ── Gráfico 2: Bottom 10 ──
    bottom_fob = (
        df[df['Dolares FOB'] > 0]
        .groupby('Nombre partida', as_index=False)['Dolares FOB']
        .sum().nsmallest(TOP_N, 'Dolares FOB').sort_values('Dolares FOB')
    )
    print('\n📊 Top 10 Productos Menos Valiosos:')
    print(bottom_fob.to_string(index=False))

    fig = barplot_horizontal_fig(bottom_fob, 'Dolares FOB', 'Nombre partida',
                                 'Top 10 Productos Menos Valiosos (Total USD FOB)',
                                 color_palette='rocket')
    guardar(fig, '02_bottom10_productos_valiosos')
    fig = barplot_horizontal_fig(bottom_fob, 'Dolares FOB', 'Nombre partida',
                                 'Top 10 Productos Menos Valiosos (Total USD FOB)',
                                 color_palette='rocket')
    html_partes.append(f'<h3>2. Top 10 Menos Valiosos (FOB &gt; 0)</h3>{reporte.img_tag(fig)}')
    html_partes.append(reporte.tabla_html(bottom_fob.sort_values('Dolares FOB')))
    plt.close(fig)

    # ── Gráfico 3: Peso extremos ──
    peso_grupo = df.groupby('Nombre partida', as_index=False)['Kilogramos netos'].sum()
    top_peso = peso_grupo.nlargest(TOP_N, 'Kilogramos netos').sort_values('Kilogramos netos')
    bottom_peso = peso_grupo[peso_grupo['Kilogramos netos'] > 0].nsmallest(TOP_N, 'Kilogramos netos').sort_values('Kilogramos netos')

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    sns.barplot(data=top_peso, x='Kilogramos netos', y='Nombre partida', palette='mako', ax=axes[0], hue='Nombre partida', legend=False)
    axes[0].set_title('Top 10 Más Pesados (Kg)', fontweight='bold'); axes[0].set_ylabel('')
    sns.barplot(data=bottom_peso, x='Kilogramos netos', y='Nombre partida', palette='flare', ax=axes[1], hue='Nombre partida', legend=False)
    axes[1].set_title('Top 10 Menos Pesados (Kg)', fontweight='bold'); axes[1].set_ylabel('')
    plt.suptitle('Comparativa de Peso: Extremos', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    guardar(fig, '03_peso_extremos')

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    sns.barplot(data=top_peso, x='Kilogramos netos', y='Nombre partida', palette='mako', ax=axes[0], hue='Nombre partida', legend=False)
    axes[0].set_title('Top 10 Más Pesados (Kg)', fontweight='bold'); axes[0].set_ylabel('')
    sns.barplot(data=bottom_peso, x='Kilogramos netos', y='Nombre partida', palette='flare', ax=axes[1], hue='Nombre partida', legend=False)
    axes[1].set_title('Top 10 Menos Pesados (Kg)', fontweight='bold'); axes[1].set_ylabel('')
    plt.suptitle('Comparativa de Peso: Extremos', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    html_partes.append(f'<h3>3. Extremos de Peso (Kg Netos)</h3>{reporte.img_tag(fig)}')
    plt.close(fig)

    # ── Gráfico 4: Diamantes (más caros por kg) ──
    if 'Precio_Unitario_Peso' in df.columns:
        precio_kg = (
            df[df['Precio_Unitario_Peso'].notna()]
            .groupby('Nombre partida', as_index=False)['Precio_Unitario_Peso']
            .median().nlargest(TOP_N, 'Precio_Unitario_Peso').sort_values('Precio_Unitario_Peso')
        )
        print('\n💎 Top 10 Más Caros por Kg:')
        print(precio_kg.to_string(index=False))

        fig = barplot_horizontal_fig(precio_kg, 'Precio_Unitario_Peso', 'Nombre partida',
                                     '💎 Top 10 Más Caros por Kg (Mediana USD/Kg)', fmt=',.2f')
        guardar(fig, '04_top10_diamantes')
        fig = barplot_horizontal_fig(precio_kg, 'Precio_Unitario_Peso', 'Nombre partida',
                                     '💎 Top 10 Más Caros por Kg (Mediana USD/Kg)', fmt=',.2f')
        html_partes.append(f'<h3>4. 💎 "Los Diamantes" — Más Caros por Kg</h3>{reporte.img_tag(fig)}')
        html_partes.append(reporte.tabla_html(precio_kg.sort_values('Precio_Unitario_Peso', ascending=False)))
        plt.close(fig)

    # ── Gráfico 5: Arena (más baratos por kg) ──
    if 'Precio_Unitario_Peso' in df.columns:
        precio_kg_bajo = (
            df[df['Precio_Unitario_Peso'] > 0]
            .groupby('Nombre partida', as_index=False)['Precio_Unitario_Peso']
            .median().nsmallest(TOP_N, 'Precio_Unitario_Peso').sort_values('Precio_Unitario_Peso')
        )
        print('\n🏖️ Top 10 Más Baratos por Kg:')
        print(precio_kg_bajo.to_string(index=False))

        fig = barplot_horizontal_fig(precio_kg_bajo, 'Precio_Unitario_Peso', 'Nombre partida',
                                     '🏖️ Top 10 Más Baratos por Kg (Mediana USD/Kg)',
                                     color_palette='crest', fmt=',.4f')
        guardar(fig, '05_top10_arena')
        fig = barplot_horizontal_fig(precio_kg_bajo, 'Precio_Unitario_Peso', 'Nombre partida',
                                     '🏖️ Top 10 Más Baratos por Kg (Mediana USD/Kg)',
                                     color_palette='crest', fmt=',.4f')
        html_partes.append(f'<h3>5. 🏖️ "La Arena" — Más Baratos por Kg</h3>{reporte.img_tag(fig)}')
        html_partes.append(reporte.tabla_html(precio_kg_bajo.sort_values('Precio_Unitario_Peso')))
        plt.close(fig)

    # ── Gráfico 6: Extremos precio/cantidad ──
    if 'Precio_Unitario_Cant' in df.columns:
        puc = (
            df[df['Precio_Unitario_Cant'].notna() & (df['Precio_Unitario_Cant'] > 0)]
            .groupby('Nombre partida', as_index=False)['Precio_Unitario_Cant'].median()
        )
        top_puc = puc.nlargest(TOP_N, 'Precio_Unitario_Cant').assign(Tipo='Más Caros')
        bottom_puc = puc.nsmallest(TOP_N, 'Precio_Unitario_Cant').assign(Tipo='Más Baratos')
        extremos = pd.concat([top_puc, bottom_puc])

        fig, ax = plt.subplots(figsize=(14, 8))
        sns.barplot(data=extremos, x='Precio_Unitario_Cant', y='Nombre partida',
                    hue='Tipo', palette={'Más Caros': '#e74c3c', 'Más Baratos': '#2ecc71'}, ax=ax)
        ax.set_title('Extremos de Precio por Unidad (Mediana USD/Unidad)', fontweight='bold', pad=15)
        ax.set_xlabel('USD / Unidad'); ax.set_ylabel(''); ax.legend(title='Categoría')
        plt.tight_layout()
        guardar(fig, '06_extremos_precio_cantidad')

        fig, ax = plt.subplots(figsize=(14, 8))
        sns.barplot(data=extremos, x='Precio_Unitario_Cant', y='Nombre partida',
                    hue='Tipo', palette={'Más Caros': '#e74c3c', 'Más Baratos': '#2ecc71'}, ax=ax)
        ax.set_title('Extremos de Precio por Unidad (Mediana USD/Unidad)', fontweight='bold', pad=15)
        ax.set_xlabel('USD / Unidad'); ax.set_ylabel(''); ax.legend(title='Categoría')
        plt.tight_layout()
        html_partes.append(f'<h3>6. Extremos de Precio por Unidad</h3>{reporte.img_tag(fig)}')
        plt.close(fig)

    reporte.agregar_seccion('Bloque A: Análisis de Productos', '\n'.join(html_partes), '📦')


# =============================================================================
# 5. BLOQUE B — CATEGORÍAS ESTRATÉGICAS
# =============================================================================
def bloque_b_categorias(df: pd.DataFrame):
    print('\n' + '=' * 60)
    print('  BLOQUE B: CATEGORÍAS ESTRATÉGICAS')
    print('=' * 60)

    html_partes = []

    # ── Gráfico 7: Boxplot Nivel Tecnológico ──
    if 'Nivel tecnologico' in df.columns:
        df_box = df[df['Dolares FOB'] > 0].copy()
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.boxplot(data=df_box, x='Nivel tecnologico', y='Dolares FOB',
                    palette='Set2', showfliers=False, ax=ax)
        ax.set_title('Distribución de USD FOB según Nivel Tecnológico', fontweight='bold', pad=15)
        ax.set_ylabel('Dolares FOB (USD)'); ax.set_xlabel('Nivel Tecnológico')
        plt.xticks(rotation=30, ha='right'); plt.tight_layout()
        guardar(fig, '07_boxplot_nivel_tecnologico')

        fig, ax = plt.subplots(figsize=(14, 8))
        sns.boxplot(data=df_box, x='Nivel tecnologico', y='Dolares FOB',
                    palette='Set2', showfliers=False, ax=ax)
        ax.set_title('Distribución de USD FOB según Nivel Tecnológico', fontweight='bold', pad=15)
        ax.set_ylabel('Dolares FOB (USD)'); ax.set_xlabel('Nivel Tecnológico')
        plt.xticks(rotation=30, ha='right'); plt.tight_layout()
        html_partes.append(f'<h3>7. Boxplot — Nivel Tecnológico</h3>{reporte.img_tag(fig)}')
        plt.close(fig)

        resumen = df.groupby('Nivel tecnologico')['Dolares FOB'].agg(['sum', 'median', 'count'])
        resumen.columns = ['Total_FOB', 'Mediana_FOB', 'Registros']
        resumen = resumen.sort_values('Total_FOB', ascending=False).reset_index()
        print('\n📊 Resumen por Nivel Tecnológico:')
        print(resumen.to_string(index=False))
        html_partes.append(reporte.tabla_html(resumen))

    # ── Gráfico 8: Uso Económico ──
    if 'Uso economico' in df.columns:
        uso = df.groupby('Uso economico', as_index=False)['Dolares FOB'].sum().sort_values('Dolares FOB')
        print('\n📊 Total por Uso Económico:')
        print(uso.to_string(index=False))

        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(data=uso, x='Dolares FOB', y='Uso economico', palette='coolwarm', ax=ax, hue='Uso economico', legend=False)
        ax.set_title('Total Importado (USD FOB) por Uso Económico', fontweight='bold', pad=15)
        ax.set_xlabel('Dolares FOB (USD)'); ax.set_ylabel('')
        plt.tight_layout()
        guardar(fig, '08_uso_economico')

        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(data=uso, x='Dolares FOB', y='Uso economico', palette='coolwarm', ax=ax, hue='Uso economico', legend=False)
        ax.set_title('Total Importado (USD FOB) por Uso Económico', fontweight='bold', pad=15)
        ax.set_xlabel('Dolares FOB (USD)'); ax.set_ylabel('')
        plt.tight_layout()
        html_partes.append(f'<h3>8. Total FOB por Uso Económico</h3>{reporte.img_tag(fig)}')
        html_partes.append(reporte.tabla_html(uso.sort_values('Dolares FOB', ascending=False)))
        plt.close(fig)

    reporte.agregar_seccion('Bloque B: Categorías Estratégicas', '\n'.join(html_partes), '🏷️')


# =============================================================================
# 6. BLOQUE C — LOGÍSTICA
# =============================================================================
def bloque_c_logistica(df: pd.DataFrame):
    print('\n' + '=' * 60)
    print('  BLOQUE C: ANÁLISIS LOGÍSTICO')
    print('=' * 60)

    if 'Impacto_Logistico_Pct' not in df.columns:
        print('  ❌ Impacto_Logistico_Pct no disponible')
        return

    html_partes = []
    logistica = (
        df[df['Impacto_Logistico_Pct'].notna() & (df['Impacto_Logistico_Pct'] > 0)]
        .groupby('Nombre partida', as_index=False)['Impacto_Logistico_Pct'].median()
    )

    # ── Gráfico 9: Mayor impacto ──
    top_log = logistica.nlargest(TOP_N, 'Impacto_Logistico_Pct').sort_values('Impacto_Logistico_Pct')
    print('\n🚢 Top 10 Mayor Impacto Logístico:')
    print(top_log.to_string(index=False))

    fig = barplot_horizontal_fig(top_log, 'Impacto_Logistico_Pct', 'Nombre partida',
                                 '🚢 Top 10 Mayor Impacto Logístico (% sobre FOB)',
                                 color_palette='Reds_r', fmt='.1f')
    guardar(fig, '09_top10_mayor_impacto_logistico')
    fig = barplot_horizontal_fig(top_log, 'Impacto_Logistico_Pct', 'Nombre partida',
                                 '🚢 Top 10 Mayor Impacto Logístico (% sobre FOB)',
                                 color_palette='Reds_r', fmt='.1f')
    html_partes.append(f'<h3>9. 🚢 Donde el Flete Duele Más</h3>{reporte.img_tag(fig)}')
    html_partes.append(reporte.tabla_html(top_log.sort_values('Impacto_Logistico_Pct', ascending=False)))
    plt.close(fig)

    # ── Gráfico 10: Menor impacto ──
    bot_log = logistica.nsmallest(TOP_N, 'Impacto_Logistico_Pct').sort_values('Impacto_Logistico_Pct')
    print('\n✈️ Top 10 Menor Impacto Logístico:')
    print(bot_log.to_string(index=False))

    fig = barplot_horizontal_fig(bot_log, 'Impacto_Logistico_Pct', 'Nombre partida',
                                 '✈️ Top 10 Menor Impacto Logístico (% sobre FOB)',
                                 color_palette='Greens_r', fmt='.2f')
    guardar(fig, '10_top10_menor_impacto_logistico')
    fig = barplot_horizontal_fig(bot_log, 'Impacto_Logistico_Pct', 'Nombre partida',
                                 '✈️ Top 10 Menor Impacto Logístico (% sobre FOB)',
                                 color_palette='Greens_r', fmt='.2f')
    html_partes.append(f'<h3>10. ✈️ Donde el Flete es Mínimo</h3>{reporte.img_tag(fig)}')
    html_partes.append(reporte.tabla_html(bot_log.sort_values('Impacto_Logistico_Pct')))
    plt.close(fig)

    reporte.agregar_seccion('Bloque C: Análisis Logístico', '\n'.join(html_partes), '🚢')


# =============================================================================
# 7. BLOQUE D — GEOPOLÍTICO
# =============================================================================
def bloque_d_paises(df: pd.DataFrame):
    print('\n' + '=' * 60)
    print('  BLOQUE D: ANÁLISIS GEOPOLÍTICO')
    print('=' * 60)

    if 'Pais de origen' not in df.columns:
        print('  ❌ Columna «Pais de origen» no encontrada')
        return

    html_partes = []

    # ── Gráfico 11: Top 10 países FOB ──
    paises_fob = (
        df.groupby('Pais de origen', as_index=False)['Dolares FOB']
        .sum().nlargest(TOP_N, 'Dolares FOB').sort_values('Dolares FOB')
    )
    print('\n🌍 Top 10 Países Proveedores:')
    print(paises_fob.to_string(index=False))

    fig = barplot_horizontal_fig(paises_fob, 'Dolares FOB', 'Pais de origen',
                                 '🌍 Top 10 Países Proveedores (USD FOB)')
    guardar(fig, '11_top10_paises_fob')
    fig = barplot_horizontal_fig(paises_fob, 'Dolares FOB', 'Pais de origen',
                                 '🌍 Top 10 Países Proveedores (USD FOB)')
    html_partes.append(f'<h3>11. 🌍 Top 10 Países Proveedores</h3>{reporte.img_tag(fig)}')
    html_partes.append(reporte.tabla_html(paises_fob.sort_values('Dolares FOB', ascending=False)))
    plt.close(fig)

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
        guardar(fig, '12_paises_flete_caro')

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
        html_partes.append(f'<h3>12. 💸 Países con Fletes Más Caros</h3>{reporte.img_tag(fig)}')
        html_partes.append(reporte.tabla_html(paises_flete.sort_values('Impacto_Logistico_Pct', ascending=False)))
        plt.close(fig)

    reporte.agregar_seccion('Bloque D: Análisis Geopolítico', '\n'.join(html_partes), '🌍')


# =============================================================================
# 8. RESUMEN EJECUTIVO
# =============================================================================
def resumen_ejecutivo(df: pd.DataFrame):
    print('\n' + '=' * 60)
    print('  📋 RESUMEN EJECUTIVO')
    print('=' * 60)

    registros = f'{len(df):,}'
    productos = f'{df["Nombre partida"].nunique():,}'
    paises = f'{df["Pais de origen"].nunique():,}'
    total_fob = f'USD {df["Dolares FOB"].sum():,.0f}'
    total_cif = f'USD {df["Dolares CIF"].sum():,.0f}'
    costo_log = f'USD {df.get("Costo_Logistico", pd.Series([0])).sum():,.0f}'
    peso_total = f'{df["Kilogramos netos"].sum():,.0f} Kg'

    print(f'  Registros:           {registros}')
    print(f'  Productos únicos:    {productos}')
    print(f'  Países de origen:    {paises}')
    print(f'  Total FOB:           {total_fob}')
    print(f'  Total CIF:           {total_cif}')
    print(f'  Costo logístico:     {costo_log}')
    print(f'  Peso total:          {peso_total}')
    print(f'\n  📁 Gráficos: {OUTPUT_DIR}')
    print('=' * 60)

    # KPIs para el HTML
    reporte.resumen = {
        'Registros': registros,
        'Productos Únicos': productos,
        'Países de Origen': paises,
        'Total FOB': total_fob,
        'Total CIF': total_cif,
        'Costo Logístico': costo_log,
        'Peso Total': peso_total,
    }


# =============================================================================
# MAIN
# =============================================================================
def main():
    df = cargar_datos(ARCHIVO)
    df = limpiar_datos(df)
    df = crear_metricas(df)

    resumen_ejecutivo(df)

    bloque_a_productos(df)
    bloque_b_categorias(df)
    bloque_c_logistica(df)
    bloque_d_paises(df)

    reporte.generar(HTML_OUTPUT)

    print('\n🎉 ¡Análisis completo!')
    print(f'  📁 Gráficos PNG: {OUTPUT_DIR}')
    print(f'  🌐 Reporte HTML: {HTML_OUTPUT}')


if __name__ == '__main__':
    main()
