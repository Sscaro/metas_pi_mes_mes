import pandas as pd
import yaml
class ajuste_universos:

    def __init__(self,ruta,ruta_yml):
        '''
        arg: ruta: str con ruta de con los universos
        ruta_yml: str ruta yml
        '''
        self.ruta = ruta        
        with open(ruta_yml, 'r',encoding='utf-8') as file:
            self.config = yaml.safe_load(file)

    def lectura_excel(self,hoja, columnas,tipo=str):
         
         '''
         metodo que lee un archivo .xslx 
         ARG  hoja: str, con el nombre de la hoja del archivo
            columnas: lista con los nombres de las columnas a usar        
            tipo: diccionario con el tipo de dato que debe tener la columna
         '''
         datos = pd.read_excel(self.ruta, sheet_name = hoja , usecols= self.config['columnas_usar_universos'][columnas], dtype=tipo)
         datos = datos.drop_duplicates(keep='first')    
         
         return datos
   
    def limpieza_universos(self):
        
        universoDirecta = self.lectura_excel('directa','directa')
        universoDirecta.columns = ['COD_CLIENTE','CODIGO_BLOQUEO']
        universoDirecta = universoDirecta[~universoDirecta['CODIGO_BLOQUEO'].isin(self.config['codigos_bloqueo'])]
       
        del universoDirecta['CODIGO_BLOQUEO']      
        universoIndirecta = self.lectura_excel('indirecta','indirecta')
        universoIndirecta.columns = ['COD_AGENTE','COD_CLIENTE']
        universoIndirecta['COD_CLIENTE'] = universoIndirecta['COD_AGENTE'] + '-' +universoIndirecta['COD_CLIENTE']                     
        del universoIndirecta['COD_AGENTE']      
        
        
        pd_universos = pd.concat([universoDirecta,universoIndirecta])
        pd_universos['Estado'] = 'Activo'
        #print(pd_universos.info())
 
        return   pd_universos
         
'''
universo = os.path.join(os.getcwd(),'Insumos','Clientes_activos_Dir_Ind.xlsx')
yml = os.path.join(os.getcwd(),'Insumos','config.yml')
objeto = ajuste_universos(universo,yml)
objeto.limpieza_universos()
'''
