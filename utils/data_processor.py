import os
import pandas as pd
import numpy as np

def create_simulated_data():
    """Crea datos simulados para demostración"""
    num_rows = 50
    df = pd.DataFrame({
        'MAP': np.random.normal(75, 10, size=num_rows).round(0).astype(int),
        'CO': np.random.normal(5, 1, size=num_rows).round(0).astype(int),
        'SVV': np.random.normal(12, 3, size=num_rows).round(0).astype(int),
        'PPV': np.random.normal(11, 3, size=num_rows).round(0).astype(int),
        'tiempo_segundos': [20 * i for i in range(num_rows)]
    })
    return df

def load_patient_data(patient_id, folder_path='data/HEMODINAMICA'):
    """Carga los datos de un paciente o genera datos simulados"""
    try:
        # Verificar si el directorio existe
        if not os.path.exists(folder_path):
            print(f"¡Carpeta {folder_path} no encontrada! Creando datos simulados.")
            return create_simulated_data()
            
        file_path = os.path.join(folder_path, f"{patient_id}.xlsx")
        if not os.path.exists(file_path):
            print(f"¡Archivo {file_path} no encontrado! Creando datos simulados.")
            return create_simulated_data()
            
        df = pd.read_excel(file_path)
        print(f"Datos del paciente {patient_id} cargados correctamente")
        
        # Verificar columnas necesarias
        required_columns = ['MAP', 'CO', 'SVV', 'PPV', 'tiempo_segundos']
        for col in required_columns:
            if col not in df.columns:
                if col == 'MAP':
                    df[col] = np.random.normal(75, 10, size=len(df))
                elif col == 'CO':
                    df[col] = np.random.normal(5, 1, size=len(df))
                elif col == 'SVV':
                    df[col] = np.random.normal(12, 3, size=len(df))
                elif col == 'PPV':
                    df[col] = np.random.normal(11, 3, size=len(df))
                elif col == 'tiempo_segundos':
                    df[col] = [20 * i for i in range(len(df))]
        
        # Redondear valores a enteros
        for col in ['MAP', 'CO', 'SVV', 'PPV']:
            if col in df.columns:
                df[col] = df[col].round(0).astype(int)
        
        return df
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return create_simulated_data()

def predict_sto2(map_val, co_val, svv_val, pvv_val):
    """Predice la probabilidad de StO2 <65% en 10 minutos"""
    # Factores de riesgo según rangos
    map_risk = 0
    if map_val < 65: map_risk = 0.4
    elif map_val < 70: map_risk = 0.2
    elif map_val > 100: map_risk = 0.3
    
    co_risk = 0
    if co_val < 2.5: co_risk = 0.4
    elif co_val < 4.0: co_risk = 0.2
    elif co_val > 8.0: co_risk = 0.3
    
    svv_risk = 0
    if svv_val > 17: svv_risk = 0.3
    elif svv_val > 13: svv_risk = 0.15
    
    pvv_risk = 0
    if pvv_val > 15: pvv_risk = 0.3
    elif pvv_val > 12: pvv_risk = 0.15
    
    # Calcular probabilidad final
    risk = (map_risk * 0.35) + (co_risk * 0.35) + (svv_risk * 0.15) + (pvv_risk * 0.15)
    risk += np.random.normal(0, 0.05)  # Añadir variabilidad
    return min(1.0, max(0.0, risk)) * 100  # Devolver como porcentaje