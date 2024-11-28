import pandas as pd
import yaml


class ajustes_pi:

    def __init__(self,ruta_pi,ruta_driver,ruta_yml):
        '''
        ARG: 
            ruta_pi. str ruta donde esta el pi enviado por el equipo de portafolio
            ruta_driver: str donde esta el driver de transformados
            ruta_yml: str ruta donde esta el archivo de configuración.
        '''
        self.ruta_pi = ruta_pi
        self.ruta_driver = ruta_driver
        with open(ruta_yml, 'r',encoding='utf-8') as file:
            self.config = yaml.safe_load(file)    
        #self.config = ruta_yml
    
    def concatenar_hojas(self,excel,hojas,diccio_columnas):     
        '''
        Funcion que lee archivo en excel con hoja determinada
        ARG. EXCEL: archivo excel
            num_hojas: lista con numero de hojas
            diccio_columnas: diccionario con columnas adicionales.
        return DF
        '''
        hojas_concatenadas = pd.DataFrame()      
        for hoja in hojas :
            df1 = excel[hoja]
            df1 = df1[diccio_columnas.keys()]
            hojas_concatenadas = pd.concat([hojas_concatenadas,df1],ignore_index=True)            
            hojas_concatenadas.drop_duplicates(inplace=True)        
        hojas_concatenadas.columns = diccio_columnas.values()    
        return  hojas_concatenadas  # hojas de comercio especializado y bienestar
    
    def merge_driver(self,df,driver,hojas):
        for hoja in hojas:
            driver_tempo =  driver[hoja]
            df = pd.merge(df,driver_tempo, on = hoja, how='left' )
        return df

    def orgarnizar_archivo_pi(self):
        hojas_leer = self.config['hojasPI'] 
        hojas_driver = self.config['hojaDriver']   
        diccionario_columnas_PI = self.config['nombre_col_archivo_pi']       
  
        data_excel = pd.read_excel(self.ruta_pi, sheet_name=hojas_leer,dtype=str)
        driver = pd.read_excel(self.ruta_driver, sheet_name=hojas_driver,dtype=str)

        ## ajustes exclusivos para los canales AU y TD
        piauttd= self.concatenar_hojas(data_excel,[hojas_leer[0],hojas_leer[1]],diccionario_columnas_PI['col_td_Au']) # hojas AU. TD
        ajustespiauttd = self.merge_driver(piauttd,driver,hojas_driver)  
        ajustespiauttd = ajustespiauttd[ajustespiauttd['Excluir_meta']=='No'] # dejar materiales para la meta             
        ajustespiauttd['pi'] = 'si'
        print(self.config)  
        ajustespiauttd = ajustespiauttd[self.config['columnas_driver']]

        ## ajustes exclusivos para los canales CE y BN
        picebn= self.concatenar_hojas(data_excel,[hojas_leer[2],hojas_leer[3]],diccionario_columnas_PI['col_bn_ce']) # hojas CE, B
        ajustespicebn = self.merge_driver(picebn,driver,hojas_driver[0:2])  
        ajustespicebn = ajustespicebn[ajustespicebn['Excluir_meta']=='No']
        ajustespicebn['pi'] = 'si'
        ajustespiauttd = ajustespiauttd[self.config['columnas_driver'][0:4]]


        return ajustespiauttd, ajustespicebn

'''
libro_excel = 'Insumos\PortafolioInfaltable.xlsx'
archivo_yml= 'Insumos\config.yml'
archivo_driver = 'Insumos\drivers_transformados.xlsx'
objeto = ajustes_pi(libro_excel,archivo_driver,archivo_yml)
objeto.orgarnizar_archivo_pi()

'''