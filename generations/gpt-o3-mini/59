from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Crear una sesión Spark
spark = SparkSession.builder.appName("EscrituraParquetADL2").getOrCreate()

# Ejemplo: Los datos provienen de una API y no se conoce su estructura de antemano.
# Primero, se realizan las peticiones a la API para obtener y analizar los datos.
import requests

# Reemplaza esta URL con la dirección real de tu API
api_url = "https://api.example.com/data"
response = requests.get(api_url)

if response.status_code == 200:
    json_data = response.json()
else:
    raise Exception("Error al obtener datos de la API. Código de estado: {}".format(response.status_code))

# Imprimir los datos obtenidos para analizarlos
print("Datos obtenidos de la API:")
print(json_data)

# Suponiendo que json_data es una lista de diccionarios, se crea el DataFrame
df = spark.createDataFrame(json_data)
df.printSchema()

# Configurar la conexión a ADL2 usando la identidad de Microsoft ID
# No es necesario proporcionar credenciales explícitamente en un notebook de Synapse
# Spark utilizará la identidad administrada del notebook para autenticarse.

# Especificar la ruta al contenedor y la carpeta en ADL2
container_name = "<your_container_name>"  # Reemplazar con el nombre de tu contenedor
folder_path = "<your_folder_path>"  # Reemplazar con la ruta a la carpeta dentro del contenedor
adl2_path = f"abfss://{container_name}@{<your_storage_account_name>}.dfs.core.windows.net/{folder_path}"

# Escribir el DataFrame en formato parquet en ADL2
df.write.parquet(adl2_path, mode="overwrite")

# Opcional: leer el archivo parquet para verificar
df_leido = spark.read.parquet(adl2_path)
df_leido.show()

# Detener la sesión Spark
spark.stop()
