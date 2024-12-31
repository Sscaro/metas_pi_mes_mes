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
   
    def limpieza_universos_dir(self):
        
        universoDirecta = self.lectura_excel('directa','directa')
        universoDirecta.columns = ['clave_cliente','CODIGO_BLOQUEO']
        universoDirecta = universoDirecta[~universoDirecta['CODIGO_BLOQUEO'].isin(self.config['codigos_bloqueo'])]
       
        del universoDirecta['CODIGO_BLOQUEO']
        #pd_universos = pd.concat([universoDirecta,universoIndirecta])
        universoDirecta['Estado'] = 'Activo'
        #print(pd_universos.info())
 
        return  universoDirecta
    
    def limpieza_universos_ind(self):
         universoInd = self.lectura_excel('indirecta','indirecta')
         universoInd = universoInd.drop_duplicates(keep='first')
         universo_cliente = universoInd[['Cod_CRM','r_id_vendedor']].drop_duplicates(subset='Cod_CRM')
         universo_cliente = universo_cliente.rename(columns={'Cod_CRM':'clave_cliente'})
         
         listado_columas = self.config['columnas_usar_universos']['indirecta']
         # se crea un data frame para saber cual es la fuerza del portafolio más reprensentativa a nivel Agente - vendedor
         # listado_columas orden: 0: agente, 1: Cod Crm 2: cod_vendedor, 3:fuerza
         
         fuerza_vendedor = universoInd[[listado_columas[0],listado_columas[2],listado_columas[3]]].dropna()
         num_clientes_vendedor = fuerza_vendedor.value_counts().reset_index().sort_values(by=[listado_columas[2],'count'],ascending=False)
         # data frame imputaciones para completar los vendedores sin fuerza portafolio
         imputaciones = num_clientes_vendedor.drop_duplicates(subset=[listado_columas[0],listado_columas[2]], keep='first')
         universoInd = universoInd.merge(imputaciones[[listado_columas[0], listado_columas[2],listado_columas[3]]], on=[listado_columas[0], listado_columas[2]], how='left', suffixes=('', '_imputado'))
        # se imputan valores nulos para aquellos vendedores que no tienen fuerza
         universoInd[listado_columas[3]] = universoInd[listado_columas[3]].fillna(universoInd[listado_columas[3]+'_imputado']) 
         universoInd[listado_columas[3]] = universoInd[listado_columas[3]].fillna(self.config['columnas_usar_universos']['imputacion_fuerza'])
         universoInd[['Codigo_Fuerza', 'Descripcion_Fuerza']] = universoInd[listado_columas[3]].str.split(' - ', expand=True)
         universoInd = universoInd.sort_values(by=[listado_columas[0], listado_columas[1], 'Descripcion_Fuerza'], ascending=True)
         universoInd = universoInd.drop_duplicates(subset=listado_columas[0:3],keep='first')
         universoInd = universoInd.drop(columns=[listado_columas[3],'Fuerzas en el rutero_imputado'],)
         universoactivo = universoInd[['r_id_agente_comercial','Cod_CRM']].drop_duplicates(subset=['r_id_agente_comercial','Cod_CRM'], keep='first')
         universoactivo['Estado'] = 'Activo'
      
         
         return universoInd, universoactivo, universo_cliente
    
    def Agregar_fuerza_portafolio(self,ruta_driver_portafolio,ventas):
        universoAjuste, universoactivo, universo_cliente_vende =self.limpieza_universos_ind() 
        universoactivo.columns = ['clave_Agente','clave_cliente','Estado']
        universoAjuste.columns = ['clave_Agente','cod_vendedor','clave_cliente','Codigo_Fuerza','Nombre_fuerza']
        
        #ventas = pd.read_csv('Marcacion_PI_Ind.csv',sep=";",dtype=str)
        ventas = pd.merge(ventas,universoactivo, on = ['clave_Agente','clave_cliente'], how='left')
        print('primer_info')
        print(ventas.info())
        driver_fuerzas = pd.read_excel(ruta_driver_portafolio, sheet_name='driver_fuerza', dtype=str)       
        data_expandida = pd.merge(universoAjuste,driver_fuerzas,on='Codigo_Fuerza',how='left')
        print('segundo_info')
        print(data_expandida.info())
        data_expandida = data_expandida.drop_duplicates(subset=['clave_cliente','Cod_portafolio'],keep='first')
     
      
        
        ventas = pd.merge(ventas,data_expandida, on=['clave_Agente','clave_cliente','Cod_portafolio'], how = 'left', )
        # col eliminar
        ventas['clave_vendedor'] = ventas['cod_vendedor']
        col_eliminar = ['Cod_portafolio','Codigo_Fuerza','Nombre_fuerza','cod_vendedor']
        for col in col_eliminar:
            del ventas[col]
        print('tercer_info')
        print(ventas.info())
        #ventas.to_csv('resultado.csv',index=False, sep=";", decimal=",")
        reultado_ventas = self.__imputacion_nulos(ventas,universo_cliente_vende)
        reultado_ventas.to_csv('resultado3.csv',index=False, sep=";", decimal=",")
        return reultado_ventas
    
    def __imputacion_nulos(self, df,universo_cliente_vende):
        ###Metodo para imputar vendedores con codigo nulo
        cliente_vendedor = (
        df.groupby(['clave_cliente', 'clave_vendedor'], dropna=True)['ventas_cop']
        .sum()
        .reset_index()
        .sort_values(by=['clave_cliente', 'ventas_cop'], ascending=[True, False])
        .drop_duplicates(subset=['clave_cliente'], keep='first')
        .rename(columns={'clave_vendedor': 'Imputed_vendedor_cliente'}))
        
        df = df.merge(cliente_vendedor[['clave_cliente', 'Imputed_vendedor_cliente']], 
              on='clave_cliente', 
              how='left')
        df['clave_vendedor'] = df['clave_vendedor'].fillna(df['Imputed_vendedor_cliente'])

        ## paso imputar vendedor con primer vendedor que encuentre en el universo
        if df['clave_vendedor'].isnull().any():
            df = df.merge(universo_cliente_vende, on = 'clave_cliente',how='left')
            df['clave_vendedor'] = df['clave_vendedor'].fillna(df['r_id_vendedor'])
        
        # Paso 2: Identificar si aún quedan valores nulos
        if df['clave_vendedor'].isnull().any():
            agente_vendedor = (
            df.groupby(['clave_Agente', 'clave_vendedor'], dropna=True)['ventas_cop']
            .sum()
            .reset_index()
            .sort_values(by=['clave_Agente', 'ventas_cop'], ascending=[True, False])
            .drop_duplicates(subset=['clave_Agente'], keep='first')
            .rename(columns={'clave_vendedor': 'Imputed_vendedor_agente'}))
                # Añadir al DataFrame los Cod_vendedor imputados por agente
            df = df.merge(agente_vendedor[['clave_Agente', 'Imputed_vendedor_agente']], 
                  on='clave_Agente', 
                  how='left')
            df['clave_vendedor'] = df['clave_vendedor'].fillna(df['Imputed_vendedor_agente'])
        df = df.drop(columns=['Imputed_vendedor_cliente', 'Imputed_vendedor_agente','r_id_vendedor'], errors='ignore')
        return df
'''

universo = os.path.join(os.getcwd(),'Insumos','Clientes_activos_Dir_Ind.xlsx')
yml = os.path.join(os.getcwd(),'Insumos','config.yml')
objeto = ajuste_universos(universo,yml)
objeto.limpieza_universos()
'''
