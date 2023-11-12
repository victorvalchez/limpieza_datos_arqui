import pandas as pd
import re
import csv
# ----------------------------------------------------- #
# ----------------- Limpieza de datos ----------------- #
# ----------------------------------------------------- #

# ----------------------INTERPRETES---------------------- #
# Lee el dataset de un archivo CSV, indicando que la primera fila es el header
df = pd.read_csv("./datosRaw/interpretes.dump", header=0)

# Definir una función personalizada para limpiar los valores en la columna 'cese' quitar el espacio
def limpiar_cese(valor):
    if pd.isna(valor):
        return ' '  # Si el valor es NaN, reemplazarlo con un solo espacio
    else:
        return valor # Si el valor no es NaN, devolverlo sin cambios

# Aplicar la función personalizada a la columna 'cese'
df['cese'] = df['cese'].apply(limpiar_cese)

# Reemplazar múltiples espacios en blanco por un solo espacio en la columna 'cese'
df['cese'] = df['cese'].str.replace(r'\s+', '', regex=True)

# Elimina las filas con datos `\N` en cualquier columna excepto la de `cese`
df = df.loc[(~df.eq(r"\N")).all(axis=1)]

# Crea una nueva columna que contenga una combinación del interprete_o_banda y el pasaporte
df["interprete_o_banda_pasaporte"] = df["interprete_o_banda"] + df["pasaporte"]

# Elimina las filas duplicadas
df = df.drop_duplicates(subset="interprete_o_banda_pasaporte")

# Borra la nueva columna   
del df["interprete_o_banda_pasaporte"]

# Para limpiar los datos en la columna rol y traducirlos al español
df['rol'] = df['rol'].replace({'SOLIST': 'Solista'}, regex=True) # Verifica si la columna 'rol' contiene el valor 'SOLIST' y reemplázalo con 'Solista'
df['rol'] = df['rol'].replace({'Percusi?n': 'Percusion'}, regex=False)
df['rol'] = df['rol'].replace({'Percussion': 'Percusion'}, regex=True)
df['rol'] = df['rol'].replace({'Bass': 'Bajo'}, regex=True)
df['rol'] = df['rol'].replace({'Guitar': 'Guitarra'}, regex=False)
df['rol'] = df['rol'].replace({'Voice': 'Voz'}, regex=True)
df['rol'] = df['rol'].replace({'Keyboards': 'Teclados'}, regex=True)
df['rol'] = df['rol'].replace({'Woodwinds': 'Viento_Madera'}, regex=True)
df['rol'] = df['rol'].replace({'Strings': 'Cuerda'}, regex=True)

# Limpiar columna nacionalidad_registro y nacionalidad
df['nacionalidad_registro'] = df['nacionalidad_registro'].replace({'Swede': 'Swedish'}, regex=True)
df['nacionalidad'] = df['nacionalidad'].replace({'Swede': 'Swedish'}, regex=True)

# Lista de nombres de columnas que contienen fechas
columnas_fechas = ['incorporacion', 'cese', 'fecha_nacimiento']

# Convertir las columnas al formato dd/mm/yyyy
for columna in columnas_fechas:
    # Convertir las fechas al formato datetime
    df[columna] = pd.to_datetime(df[columna], errors='coerce', format='%d/%m/%y')
    
    # Ajustar las fechas con años mayores que el año actual
    df.loc[df[columna].dt.year > pd.Timestamp.now().year, columna] -= pd.DateOffset(years=100)

    # Formatear las fechas al formato dd/mm/yyyy
    df[columna] = df[columna].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

# Función para verificar el formato y eliminar filas que no cumplan
expresion_regular = r'^[A-Z]{2}>>\d{10}$'
def check_pass(fila):
    if re.match(expresion_regular, str(fila['pasaporte'])):
        return True
    else:
        return False
    
# Aplicar la función a cada fila del DataFrame
df = df[df.apply(check_pass, axis=1)]

df['nacionalidad'] = df['nacionalidad'].str.strip()

# Guarda el dataset limpio en un archivo CSV
df.to_csv("./datosLimpios/interpretes_limpio.dump", index=None)


# ----------------------TEMAS---------------------- #
# Lee el dataset de un archivo CSV, indicando que la primera fila es el header
df = pd.read_csv("./datosRaw/temas.dump", header=0)

# Elimina las filas con datos vacíos
df = df.loc[~df.isna().any(axis=1)]

# Reemplaza los espacios mal formateados entre las comillas
df["autor"] = df["autor"].str.replace("\" ", "\"").str.replace(" \"", "\"")

# Función para verificar el formato y eliminar filas que no cumplan
expresion_regular = r'^[A-Z]{2}>>\d{10}$'
def check_pass(fila):
    if re.match(expresion_regular, str(fila['pasaporte_autor'])):
        return True
    else:
        return False

# Crea una nueva columna que contenga una combinación del título y el pasaporte
df["titulo_pasaporte"] = df["titulo"] + df["pasaporte_autor"]

# Elimina las filas duplicadas en las que el título y el pasaporte son iguales, pero el autor es diferente
df = df.drop_duplicates(subset="titulo_pasaporte", keep=False)

# Borra la nueva columna
del df["titulo_pasaporte"]

# Aplicar la función a cada fila del DataFrame
df = df[df.apply(check_pass, axis=1)]

# Guarda el dataset limpio en un archivo CSV
df.to_csv("./datosLimpios/temas_limpio.dump", index=None)

# ----------------------CONCIERTOS---------------------- #
# Lee el dataset de un archivo CSV, indicando que la primera fila es el header
def limpiar_archivo(archivo_entrada, archivo_salida):
    with open(archivo_entrada, "r") as f_entrada:
        with open(archivo_salida, "w", newline="") as f_salida:
            reader = csv.reader(f_entrada, delimiter=",")
            writer = csv.writer(f_salida, delimiter=",")
            
            writer.writerow(next(reader)) # write the first row without checking the if statement
            for row in reader:
                if not row[5].isdigit():
                    pais = row[4]
                    extra = row[5]

                    pais_nuevo = f"{extra} {pais}"
                    pais_nuevo = pais_nuevo[1:-1]
                    del row[5]
                    row[4] = pais_nuevo

                writer.writerow(row)

def limpiar_fecha(df):
    columnas_fechas = ['fecha']
    for columna in columnas_fechas:
        df[columna] = pd.to_datetime(df[columna], errors='coerce', format='%d/%m/%y')
        df.loc[df[columna].dt.year > pd.Timestamp.now().year, columna] -= pd.DateOffset(years=100)
        df[columna] = df[columna].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def check_pass(fila):
    if re.match(expresion_regular, str(fila['pasaporte_autor'])):
        return True
    else:
        return False

expresion_regular = r'^[A-Z]{2}>>\d{10}$'

# Aplicar funciones a los 5 archivos
for i in range(1, 6):
    archivo_entrada = f"./datosRaw/conciertos_{i}.dump"
    archivo_salida = f"./datosLimpios/conciertos_{i}_limpio.dump"

    # Limpieza del archivo
    limpiar_archivo(archivo_entrada, archivo_salida)

    # Leer el DataFrame limpio
    df = pd.read_csv(archivo_salida, header=0)

    # Limpieza de la fecha
    limpiar_fecha(df)

    # Filtrar según la expresión regular
    df = df[df.apply(check_pass, axis=1)]

    # Guardar el DataFrame limpio en un nuevo archivo CSV
    df.to_csv(f"./datosLimpios/conciertos_{i}_limpio.dump", index=None)