import csv

def limpiar_archivo(archivo_entrada, archivo_salida):
  """
  Limpia el archivo de conciertos.

  Args:
    archivo_entrada: El archivo de entrada.
    archivo_salida: El archivo de salida.
  """

  with open(archivo_entrada, "r") as f_entrada:
    with open(archivo_salida, "w", newline="") as f_salida:
      reader = csv.reader(f_entrada, delimiter=",")
      writer = csv.writer(f_salida, delimiter=",")
      
      writer.writerow(next(reader)) # write the first row without checking the if statement
      for row in reader:
        # Obtener el país y la información extra.
        if not row[5].isdigit():
          pais = row[4]
          extra = row[5]

          # Unir la información.
          pais_nuevo = f"{extra} {pais}"

          # Eliminar el caracter extra del país.
          pais_nuevo = pais_nuevo[1:-1]

          del row[5]

          # Actualizar el país con la nueva información.
          row[4] = pais_nuevo

        writer.writerow(row)

archivo_entrada = "./datosRaw/conciertos_1.dump"
archivo_salida = "./datosLimpios/conciertos_1_limpio.dump"

limpiar_archivo(archivo_entrada, archivo_salida)