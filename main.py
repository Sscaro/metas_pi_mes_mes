import Scripts.ajuste_ventas as ajventas
import Scripts.consolidar_ventas as conventas
import Scripts.descomprimit_archivos as descomprimir
import os
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

def run():
    '''
    funcion principal que ejecuta los scripts en el siguiente orden:
        consolidar ventas (leer modulo)
        ajustes ventas (leer detalle en el modulo internamente leer ajusespi)

    '''  
    logging.info('Bienvenido a la generación de metas para portafolio infaltable')
    logging.info('Selecciona proceso que desea ralizar: ')
    logging.info('1.    Descomprimir archvos de ventas:')
    logging.info('2.    Validación ventas')
    logging.info('3.    Cargar Ventas')


    
    opcion = input('Escribe alguna de las opciones anteriores: \n  ')
    carpeta = os.path.join(os.getcwd(),'Ventas')
    if opcion == '1':
        descomprimir.descomprimir()   
    else:
        ### primer modulo consolida las ventas en un solo data frame
        #insumos (algunos insumos pueden ser usados en instancias para otros objetos.)
        ruta_yml = os.path.join(os.getcwd(),'Insumos','config.yml') # archivo yml
        ruta_driver_trans = os.path.join(os.getcwd(),'Insumos','drivers_transformados.xlsx') # archivo transformados
        ruta_pi = os.path.join(os.getcwd(),'Insumos','PortafolioInfaltable.xlsx') # archivos Portafolio
        ruta_universos = os.path.join(os.getcwd(),'Insumos','Clientes_activos_Dir_Ind.xlsx') # archivo ultimo universo
        ruta_rezonificaciones = os.path.join(os.getcwd(),'Insumos','RezonifacionesIND.xlsx') # ruta rezonificaciones    
        
        if opcion =='2':

            objetoBaseVentas= conventas.consolidar_df(ruta_yml,carpeta,'.csv')
            objetoBaseVentas.validacion()

        else:
            mes_ventas_metas = input('Ingrese el mes de las ventas a cargar: \n formato mmmm:')   
            mes_calculo_meta = input('Ingrese el mes de la meta : \n formato mmmm:')      
            # objeto y metodos para consolidar los archivos csv con las ventas
            objetoBaseVentas= conventas.consolidar_df(ruta_yml,carpeta,'.csv')
            basevetas= objetoBaseVentas.crear_df() # consolida los archivos de ventas

            # objeto y metodos para ajustar archivo con las ventas y marca PI
            objetoajustesVentas = ajventas.trabajoVentas(basevetas,ruta_yml,ruta_pi,ruta_driver_trans,
                                                         ruta_universos,ruta_rezonificaciones,mes_ventas_metas,mes_calculo_meta)
            objetoajustesVentas.ajustes_archivo_ventas()

    # yml= 'Insumos\config.yml'
    ## carpeta = os.path.join(os.getcwd(),'Ventas')
        #objeto = consolidar_df(yml,carpeta,'.csv')
        #objeto.crear_df()


if __name__=='__main__':
    run()
