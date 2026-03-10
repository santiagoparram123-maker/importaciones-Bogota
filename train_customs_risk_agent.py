import pandas as pd
import numpy as np
import json
import os
import logging
from sklearn.ensemble import IsolationForest

# Configuración básica de logging para llevar trazabilidad de la ejecución del Agente/Script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cargar_y_limpiar_datos(ruta_archivo: str) -> pd.DataFrame:
    """
    1. Carga y Limpieza:
    Lee el archivo CSV histórico. Aplica manejo de valores nulos y asegura 
    tipos de datos precisos para evitar caídas en producción.
    Maneja el riesgo matemático de división por cero descartando pesos nulos.
    """
    logging.info(f"Iniciando carga de datos desde {ruta_archivo}...")
    
    # Manejo de error si el archivo fuente no existe
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo {ruta_archivo} no se encuentra originado en el directorio actual.")
        
    try:
        try:
            df = pd.read_excel(ruta_archivo, engine='calamine')
        except Exception:
            try:
                df = pd.read_excel(ruta_archivo, engine='openpyxl')
            except Exception:
                df = pd.read_csv(ruta_archivo, encoding='latin1', sep=';', low_memory=False)
    except Exception as e:
        raise ValueError(f"No se pudo leer el archivo de origen: {e}")
    
    # Seleccionar solo las columnas clave exigidas
    columnas_requeridas = ['Codigo partida', 'Dolares FOB', 'Kilogramos netos']
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: '{col}' en el origen de datos.")
            
    # Garantizar que trabajamos solo con columnas requeridas para ahorrar memoria
    df = df[columnas_requeridas].copy()
    
    # Eliminar valores nulos antes del tipado fuerte
    df.dropna(subset=columnas_requeridas, inplace=True)
    
    # Conversión segura de tipos de datos a lo esperado
    df['Codigo partida'] = df['Codigo partida'].astype(str).str.strip()
    df['Dolares FOB'] = pd.to_numeric(df['Dolares FOB'], errors='coerce')
    df['Kilogramos netos'] = pd.to_numeric(df['Kilogramos netos'], errors='coerce')
    
    # Eliminar cualquier nulo provocado por strings defectuosas durante la conversión
    df.dropna(subset=['Dolares FOB', 'Kilogramos netos'], inplace=True)
    
    # Regla de Negocio Crítica: Evitar ZeroDivisionError y lógica corrupta.
    # El peso debe ser mayor a 0 y el valor monetario debe ser al menos 0.
    df = df[(df['Kilogramos netos'] > 0) & (df['Dolares FOB'] >= 0)]
    
    logging.info(f"Carga y limpieza completadas. Registros válidos tras el filtro: {len(df)}")
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    2. Ingeniería de Características (Feature Engineering):
    Calcula el precio unitario base sobre el cual giran las auditorías de aduanas.
    """
    logging.info("Tansformando variables (Feature Engineering)...")
    df['precio_fob_por_kg'] = df['Dolares FOB'] / df['Kilogramos netos']
    return df

def calcular_estadisticas_y_modelo(df: pd.DataFrame) -> dict:
    """
    3 y 4. Agrupación Estadística y Detección de Anomalías (Modelo Base):
    Agrupa por 'Codigo partida' usando pandas para calcular media, mediana y desviación estándar.
    Utiliza el enfoque estadístico (Z-score) emparejado con Machine Learning (Isolation Forest)
    para determinar un umbral lógico y robusto por cada código HS.
    """
    logging.info("Calculando perfiles estadísticos (Z-score) y fronteras de decisión (Isolation Forest)...")
    resultados = {}
    
    # Agrupamos eficientemente por partida arancelaria
    grupos = df.groupby('Codigo partida')
    
    for partida, datos_partida in grupos:
        precios = datos_partida['precio_fob_por_kg'].values
        
        # 3. Agrupación y descriptiva estadística
        media = np.mean(precios)
        mediana = np.median(precios)
        std = np.std(precios) if len(precios) > 1 else 0.0
        
        # --- Modelo Iteración 1: Z-Score (Detección Estadística Clásica) ---
        # Definimos "Anormalmente Bajo" a 2 desviaciones estándar debajo del promedio histórico.
        umbral_zscore = media - (2 * std)
        
        # Si la varianza histórica es exagerada (ej. mala calidad de datos), el umbral colapsa a números negativos.
        # Fallback defensivo: usar el 60% de la mediana del mercado para esa métrica en particular.
        if umbral_zscore <= 0:
            umbral_zscore = mediana * 0.6 
            
        # --- Modelo Iteración 2: Isolation Forest de Scikit-Learn ---
        umbral_iforest = umbral_zscore 
        
        # Requiere mínimo 20 filas históricas para que el algoritmo no sobreadapte
        if len(precios) >= 20: 
            X = precios.reshape(-1, 1)
            # Contamination=0.05 significa que asumimos un ~5% histórico de anomalías ya existentes en los datos.
            iso_forest = IsolationForest(contamination=0.05, random_state=42)
            iso_forest.fit(X)
            
            # Recreamos un espectro continuo de valores entre el mínimo registrado y la media
            # para identificar exactamente en qué punto el algoritmo marca la transición a "Anomalía (-1)".
            espacio_busqueda = np.linspace(X.min(), media, 1000).reshape(-1, 1)
            predicciones = iso_forest.predict(espacio_busqueda)
            
            # Encontramos el mínimo precio que sigue considerándose "Normal (1)" según el ML
            puntos_normales = espacio_busqueda[predicciones == 1]
            if len(puntos_normales) > 0:
                umbral_iforest = float(puntos_normales.min())
                
        # 4. Determinación del umbral exacto combinando la matemática y el ML.
        # Tomamos el mínimo entre ML y Z-score para evitar asfixiar importaciones levemente baratas
        # (Priorizamos exactitud contra Falsos Positivos de subfacturación).
        umbral_final_riesgo = min(umbral_zscore, umbral_iforest)
        # Seguro extra: La aduana nunca permitiría valores de 0 USD. Un mínimo razonable para la alerta.
        umbral_final_riesgo = max(umbral_final_riesgo, 0.05) 

        # Se agrupan los resultados tal y cual se demandan en la salida JSON del frontend
        resultados[str(partida)] = {
            "precio_medio_hist_usd": round(float(media), 2),
            "mediana_usd": round(float(mediana), 2),
            "desviacion_estandar_usd": round(float(std), 2),
            "umbral_riesgo_usd": round(float(umbral_final_riesgo), 2),
            "muestras_entrenamiento": int(len(precios))
        }
        
    logging.info(f"Ingesta e Inferencia exitosa. Modelados {len(resultados)} códigos arancelarios.")
    return resultados

def exportar_resultados(resultados: dict, archivo_salida: str = "risk_baselines.json"):
    """
    5. Exportación para el Frontend:
    Convierte todo el análisis complejo a un archivo ligero (.json), ideal
    para ser mapeado a velocidad luz por JS en el Dashboard.
    """
    logging.info(f"Escribiendo red neuronal base/estadísticas al disco local: {archivo_salida} ...")
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        # indent=4 provee buena indentación humana para el portafolio, ensure_ascii=False soporta Ñ.
        json.dump(resultados, f, indent=4, ensure_ascii=False)
    logging.info("¡Pipeline de Agente de IA ejecutado y finalizado correctamente!")

def main():
    """ 
    Función orquestadora principal. Ejecución paso a paso del pipeline. 
    """
    archivo_csv = "conjunto-importaciones-bogota-21102025.csv"
    archivo_json = "risk_baselines.json"
    
    try:
        # Paso 1
        df_limpio = cargar_y_limpiar_datos(archivo_csv)
        
        # Paso 2
        df_transformado = feature_engineering(df_limpio)
        
        # Paso 3 y 4
        baselines = calcular_estadisticas_y_modelo(df_transformado)
        
        # Paso 5
        exportar_resultados(baselines, archivo_json)
        
    except FileNotFoundError as e:
        logging.error(f"Error Crítico (No se encontraron datos): {e}")
        logging.error("Asegúrate de colocar 'conjunto-importaciones-bogota-21102025.csv' en la misma carpeta que este script.")
    except KeyError as e:
        logging.error(f"Error de Estructura: Revise que el CSV contenga las columnas correctas. Falla en: {e}")
    except Exception as e:
        # Este Catch-all previene corrupciones silenciosas del programa.
        logging.error(f"Excepción general no detectada durante el ciclo de vida del agente: {e}")

# Punto de entrada de Python
if __name__ == "__main__":
    main()
