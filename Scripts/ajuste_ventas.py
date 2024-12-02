import pandas as pd
import os
#sys.path.append(os.getcwd())
import yaml
import Scripts.ajustesbasePI as basePI

class trabajoVentas:
    def __init__(self,ventas, ruta_yml,ruta_pi,ruta_driver):

        '''
        ARG: ventas: df con la información de ventas consolidada
            ruta_yml: str ruta archivo de configuración
            ruta_pi: str ruta del portafolio infaltable
            ruta_driver: str ruta driver de transformados. 
        '''
        self.archivo_ventas = ventas
        self.ruta_pi= ruta_pi
        self.ruta_driver = ruta_driver
        self.ruta_yml= ruta_yml
        with open(ruta_yml, 'r',encoding='utf-8') as file:
            self.config = yaml.safe_load(file)    

    def ajustes_archivo_ventas(self):
        '''
        metodo para realizar los cruces entre las ventas y los materiales que hacen parte del PI, es decir hace la marcación de materiales 
        que hacen parte del PI 
        '''
        ventas = self.archivo_ventas.copy()
        
        #Esta parte realiza reemplazos que se parametrizan en el archivo de configuración
        for replacement in self.config['reemplazos']:
            columna = replacement['columnas_condicion']
            valor_viejo = replacement['valores']
            valor_nuevo = replacement['valor_nuevo']
    
            if columna in self.archivo_ventas.columns:
                ventas[columna] = ventas[columna].replace(valor_viejo, valor_nuevo)


        ###luego de los reemplazos en esta parte se realiza el merge para marcar si el material es PI
        objeto_ajustesPI  = basePI.ajustes_pi(self.ruta_pi,self.ruta_driver,self.ruta_yml)
        Pi_TD_AU, pi_ce_bn = objeto_ajustesPI.orgarnizar_archivo_pi()
 
        ventas = pd.merge(ventas,Pi_TD_AU, on =self.config['uniones']['unionesau_td'],how='left')
        ventas = pd.merge(ventas,pi_ce_bn, on =self.config['uniones']['unionesce_bn'],how='left',suffixes=('_AU','_BN'))
        ventas["PI"] = ventas["pi_AU"].combine_first(ventas["pi_BN"])
        ventas = ventas.drop(columns=["pi_AU", "pi_BN"])
        ventas["PI"] = ventas["PI"].fillna("NO")
        ventas.to_csv('prueba_ventas.csv',index=False)
        return ventas

'''
rutaventas = os.path.join(os.getcwd(),'Ventas','Extracción_información_AGCO_D-I_-_Generación_Metas___96632318.csv')
rutayml= os.path.join(os.getcwd(),'Insumos','config.yml')
#rutayml = "Documents\3.TrabajoExtra\Desarrollo_Metas_PI\Insumos\config.yml"
archivo_driver = 'Insumos\drivers_transformados.xlsx'
libro_excel = 'Insumos\PortafolioInfaltable.xlsx'

objeto = trabajoVentas(rutaventas,rutayml,libro_excel,archivo_driver)
objeto.ajustes_archivo_ventas()

'''