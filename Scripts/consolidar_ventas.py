import pandas as pd
import os
import yaml
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',    
    handlers=[
#        logging.FileHandler('log_ejecuciones.txt'),
        logging.StreamHandler()
    ]
)

'''
modulo exclusivo para ajustar las ventas descargadas,
lo que hace este modulo es: 
    1. consilidar los diferentes archivos de la carpeta ventas y en una sola tabla
    2. devuelve como resultado un tabla agrupada por mes y un archivo .xlsx con la suma de las ventasy el nombre del archivo

    
'''

class consolidar_df:

    def __init__(self,ruta_yml, carpeta,tipo_archivo):
        '''
        ARG: ruta_yml: str: ruta con archivo de configuración
            carpeta: str.  carpeta donde esta las ventas
            tipo_archivo str. tipo de archivo que se va a consolidar (.csv, .excel, .txt, etc...) precedidas de un .
        '''
        self.carpeta = carpeta       
        with open(ruta_yml, 'r',encoding='utf-8') as file:
            self.config = yaml.safe_load(file) 
        self.tipo_archivo = tipo_archivo

    def crear_df(self):

        dataframes = []
        #lista_validacion =[]
        for archivo in os.listdir(self.carpeta):# lista los archivos de una carpeta
            if archivo.endswith(self.tipo_archivo): # tendra en cuenta solo los archivos con extesión qu se parametrizaron
            # Cargar cada archivo como DataFrame
                try:
                    df = pd.read_csv(os.path.join(self.carpeta, archivo), header=0,sep =",", thousands=",", names=self.config['nombre_col_ventas'].keys(),dtype=self.config['nombre_col_ventas'])
                except:
                    df = pd.read_csv(os.path.join(self.carpeta, archivo), header=0,sep =",",thousands="." , names=self.config['nombre_col_ventas'].keys(),dtype=self.config['nombre_col_ventas'])
                
            
                dataframes.append(df)
        
                logging.info('se ha leido archivo {} '.format(archivo))

        df_concatenado = pd.concat(dataframes, ignore_index=True)
        #df_validacion = pd.DataFrame(lista_validacion)
        #df_validacion.to_excel('Salidas\ResultadoxArchivo.xlsx',index=False)
        
        # Identificar columnas categóricas (excluyendo la columna 'Ventas')
        columnas_categoricas = df_concatenado.select_dtypes(exclude=["number"]).columns
        resultado = df_concatenado.groupby(list(columnas_categoricas))["ventas"].sum().reset_index()
        #resultado.to_csv('ventas_agrupadas.csv',index=False)
     
        logging.info('Se ha consolidado toda la información de los archivos de ventas \n espera... ')
        return resultado
    
    def validacion(self):
        lista_validacion =[]
        for archivo in os.listdir(self.carpeta):# lista los archivos de una carpeta
            if archivo.endswith(self.tipo_archivo): # tendra en cuenta solo los archivos con extesión qu se parametrizaron
            # Cargar cada archivo como DataFrame
                try:
                    df = pd.read_csv(os.path.join(self.carpeta, archivo), header=0,sep =",", thousands=",", names=self.config['nombre_col_ventas'].keys(),dtype=self.config['nombre_col_ventas'])
                except:
                    df = pd.read_csv(os.path.join(self.carpeta, archivo), header=0,sep =",",thousands="." , names=self.config['nombre_col_ventas'].keys(),dtype=self.config['nombre_col_ventas'])
            
            suma_validacion = df['ventas'].sum()
            lista_validacion.append({"Nombre_archivo": archivo, "Ventas_totales": suma_validacion})
                
            logging.info('se ha leido archivo {} '.format(archivo))
        
        df_validacion = pd.DataFrame(lista_validacion)
        
        df_validacion.to_excel('Salidas\ResultadoxArchivo.xlsx',index=False)
        
        return logging.info('se exportó archivo de validacion ResultadoxArchivo.xlsx carpeta salidas')

'''
yml= 'Insumos\config.yml'
carpeta = os.path.join(os.getcwd(),'Ventas')
objeto = consolidar_df(yml,carpeta,'.csv')
objeto.crear_df()
'''