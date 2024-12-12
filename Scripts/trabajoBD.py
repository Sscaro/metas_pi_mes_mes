import pandas as pd
import sqlite3
'''
modulo exlcusivo para trabajo con la base de datos
ingreso de datos
ejecución de querys

'''

class basedatos:
    '''
    constructor: arg: df data frmae
    '''
    def __init__(self,df):
        self.df = df

    def consolidado_info_bd(self):
        conexion = sqlite3.connect('Salidas\BaseDatos_PI.db')
        self.df.to_sql("ventas",conexion, if_exists="append")
        conexion.close()

query = '''
SELECT tipo_venta, oficina_ventas, clave_Agente, Agente, Canal_trans, Sub_canal_trans, tipologia, segmento_vital, clave_grupo_cte_5, 
COD_CLIENTE, representante_ventas,clave_representante_ventas ,codigo_vendedor, estrato,
SUM(ventas) as Ventas_totales, 
sum(CASE WHEN PI = 'si' THEN ventas ELSE 0 END) AS ventas_totales_PI,
COUNT(DISTINCT clave_material) AS Numero_materiales_comprados_totales,
COUNT(DISTINCT CASE WHEN PI = 'si' THEN clave_material  END) AS Nume_materiales_PI_Comprados
FROM ventas
WHERE 
Mes_ventas = 'junio' and Canal_trans in ('Tradicional','Autoservicios','Bienestar','Comercio Especializa') and Estado = 'Activo'
GROUP BY 
tipo_venta, oficina_ventas, clave_Agente, Agente, Canal_trans, Sub_canal_trans, tipologia, segmento_vital, clave_grupo_cte_5, 
COD_CLIENTE, representante_ventas ,clave_representante_ventas ,codigo_vendedor, estrato
'''