import pandas as pd
import numpy as np
#sys.path.append(os.getcwd())
import yaml
import Scripts.ajustesbasePI as basePI
import Scripts.ajustes_universos as universos
"""
Modulo para realizar ajustes sobre la tabla consldiad de ventas
Nota: proceso previo: "Consolidar ventas"
    1. agrupar las ventas para tener un consolidado cliente, material, vendedor mensual
    2. marcar si el material comprado por un cliente hace parte o no del Portafolio infaltble
    3. marcar si el cliente esta en los universos de cliente (dir e ind) si esta lo marca como Activo.
    (en la directa no tiene en cuenta algunos codigos de bloqueo)
    4. concatena el cod_crm con el agente comercial y crea la columna COD_CLIENTE
"""
class trabajoVentas:
    def __init__(self,ventas,ventasInd, ruta_yml,ruta_pi,ruta_driver,ruta_universos,mes_ventas,mes_meta):

        '''
        ARG: ventas: df con la información de ventas consolidada
            ruta_yml: str ruta archivo de configuración
            ruta_pi: str ruta del portafolio infaltable
            ruta_driver: str ruta driver de transformados. 
            ruta_universos: ruta str, con dirección de archivo .xlsx con universo
            ruta_rezonificaciones: ruta str. con dirección de archivo . xlsx con rezonificaciones
            mes_ventas: str con el nombre del mes de ventas
            mes_meta: str con nombre mes de calculo de la meta.
        '''
        self.archivo_ventas = ventas # df ventas
        self.archivo_ventas_ind = ventasInd
        self.ruta_pi= ruta_pi # ruta archivo excel pi
        self.ruta_driver = ruta_driver # ruta transformados
        self.ruta_yml= ruta_yml # ruta archivo configuración
        self.ruta_universos = ruta_universos # ruta universos excel
        self.mes_ventas = mes_ventas
        self.mes_meta = mes_meta
        with open(ruta_yml, 'r',encoding='utf-8') as file:
            self.config = yaml.safe_load(file)    

    def ajustes_archivo_ventas(self):
        '''
        metodo para realizar los cruces entre las ventas y los materiales que hacen parte del PI, es decir hace la marcación de materiales 
        que hacen parte del PI 
        '''
        ventas = self.archivo_ventas.copy()

        ##Unión archivo con marcación de PI con universo de mes en curso (directa e  indirecta)
        objeto_universos = universos.ajuste_universos(self.ruta_universos,self.ruta_yml)
        universodir = objeto_universos.limpieza_universos_dir()        
        ventas = pd.merge(ventas,universodir, on ='clave_cliente',how='left')
        ventas = pd.concat([ventas,self.archivo_ventas_ind],ignore_index=True)
       
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

        driver_transformados = pd.read_excel(self.ruta_driver,sheet_name='tipologia',usecols=['clave_tipologia','Canal_trans','Sub_canal_trans'],dtype=str)
        ventas = pd.merge(ventas,driver_transformados, on = 'clave_tipologia',how='left')
        ventas.fillna({'Canal_trans':"sin asginar"},inplace=True)
        ventas.fillna({'Sub_canal_trans':"sin asginar"},inplace=True)
       
        ventas = ventas.drop(columns=["pi_AU", "pi_BN"])
        ventas["PI"] = ventas["PI"].fillna("NO")    
        ventas['Mes_ventas'] = self.mes_ventas 
        ventas['Mes_meta']= self.mes_meta
        
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