import Scripts.ajuste_ventas as ajventas
import Scripts.consolidar_ventas as conventas
import Scripts.descomprimit_archivos as descomprimir
import Scripts.trabajoBD as bdatos
import Scripts.ajustes_universos as universos
import Scripts.ajustes_promos as promos
import Scripts.pi_municipio as pi_muni
import os
import logging
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',    
    handlers=[
#        logging.FileHandler('log_ejecuciones.txt'),
        logging.StreamHandler()
    ]
)
## funcion decoradora para evaluar que los insumos de cada procedimiento esten disponibles 
def validacion_insumos_decorator(func):  
    def wrapper(*args, **kwargs):
        funcion_nombre = func.__name__
        
        insumos = args[0]['listado_insumos'].get(funcion_nombre, [])  # Obtener los insumos de la función del archivo YAML
        faltantes = [archivo for archivo in insumos if not os.path.exists(os.path.join('Insumos', archivo))]        
        if faltantes:
            print(f"Error: Los siguientes insumos faltan en la carpeta 'Insumos': {', '.join(faltantes)}")
        else:
            return func(*args, **kwargs)
    return wrapper


def cargar_configuracion(ruta_config):
    """Cargar el archivo YAML con los insumos necesarios para cada función."""
    with open(ruta_config, 'r') as archivo:
        return yaml.safe_load(archivo)


def descomprimir_zip():
    descomprimir.descomprimir()   
    print('descomprime..')

def validacion_ventas():
    #ruta_yml = os.path.join(os.getcwd(),"Insumos",'config.yml') 
    objetoBaseVentas= conventas.consolidar_df(ruta_config,carpeta,'.csv')
    objetoBaseVentas.validacion('ventas_cop')

@validacion_insumos_decorator
def cargar_ventas(insumos):
    '''
    funcion que ajusta las ventas marcando los materiales PI y marcando los clientes Activos.
    '''
    logging.info('Ingrese los meses con base en los nombre del siguiente listado: \n {}'.format((config['listado_meses'])))
    mes_ventas_metas = input('Escribe el mes de ventas con base en el siguiente listado : \n formato mmmm:').strip().upper()
    mes_calculo_meta = input('Ingrese el mes de la meta : \n formato mmmm:').strip().upper()
    ruta_universos = os.path.join(os.getcwd(),'Insumos',config['listado_insumos']['cargar_ventas'][2])
    if mes_ventas_metas in config['listado_meses']:
        # objeto y metodos para consolidar los archivos csv con las ventas
        objetoBaseVentas= conventas.consolidar_df(ruta_config,carpeta,'.csv')
        base_ventas_directa= objetoBaseVentas.crear_df() # consolida los archivos de ventas de la directa.
        
        
        base_ventas_indirecta= objetoBaseVentas.crear_df(directa=False)
        base_ventas_indirecta = objetoBaseVentas.ajustes_ventas_ind(base_ventas_indirecta,os.path.join(os.getcwd(),'Insumos',config['listado_insumos']['cargar_ventas'][3]))
        objeto_universo = universos.ajuste_universos(ruta_universos,ruta_config)
        
        ruta_driver_po = os.path.join(os.getcwd(),'Insumos',config['listado_insumos']['cargar_ventas'][3])
        base_ventas_indirecta = objeto_universo.Agregar_fuerza_portafolio(ruta_driver_po,base_ventas_indirecta)
        
        
        #base_ventas_indirecta.to_csv('Marcacion_PI_Ind.csv',index=False,decimal=",",sep=";")      
        
        # objeto y metodos para ajustar archivo con las ventas y marca PI
        ruta_pi = os.path.join(os.getcwd(),'Insumos',config['listado_insumos']['cargar_ventas'][1])
        ruta_driver_trans = os.path.join(os.getcwd(),'Insumos',config['listado_insumos']['cargar_ventas'][0])
        ruta_universos = os.path.join(os.getcwd(),'Insumos',config['listado_insumos']['cargar_ventas'][2])
        #ruta_rezonificaciones = os.path.join(os.getcwd(),'Insumos',config['listado_insumos']['cargar_ventas'][2])
        objetoajustesVentas = ajventas.trabajoVentas(base_ventas_directa,base_ventas_indirecta,ruta_config,ruta_pi,ruta_driver_trans,
                                                            ruta_universos,mes_ventas_metas,mes_calculo_meta)
        
        ventas = objetoajustesVentas.ajustes_archivo_ventas()
        #ventas.to_csv('Consolidado.csv',index=False, sep=";", decimal=",")
        logging.info('Se han leido correctamente las ventas, comienza proceso de ingesta de información a la base de datos')
        
        objeto_bd= bdatos.basedatos(ventas)
        objeto_bd.consolidado_info_bd()
        logging.info('Se ha cargados las ventas a la base de datos')
    else:
        logging.info("El mes {} no es valido \n por favor vuelve y ejecuta el programa y escribe un mes valido.".format(mes_ventas_metas))
        exit()  # Salir del programa
         
@validacion_insumos_decorator
def generar_promos(insumos):
    ruta_portafolio = os.path.join(os.getcwd(),'Insumos',config['listado_insumos']['generar_promos'][1])
    ruta_promo = os.path.join(os.getcwd(),'Insumos',config['listado_insumos']['generar_promos'][0])
    hojas = config['hojasPI']
    promos.generar_archivo_promo(ruta_portafolio,ruta_promo,hojas)    
    logging.info("Se exportó archivo con relación de promos exitosamente, revisar carpeta salidas")

    
@validacion_insumos_decorator
def generar_pi_municipio(insumos):
    ruta_pi = os.path.join(os.getcwd(),"Insumos",config['listado_insumos']['generar_pi_municipio'][0])
    pi_muni.consolidaPIformato(ruta_pi)
    logging.info("Se exportó consolidado a  nivel de municipios exitosamente, revisar carpeta salidas")

@validacion_insumos_decorator
def generar_base_socios(insumos):
    print('socios!!')

def menu():
    '''
    funcion principal que ejecuta los scripts en el siguiente orden:
        consolidar ventas (leer modulo)
        ajustes ventas (leer detalle en el modulo internamente leer ajusespi)
    '''  
    insumos = cargar_configuracion(ruta_config)
    #insumos = cargar_configuracion(ruta)
    opciones = {
        "1" : ("Descomprimir archvos de ventas", descomprimir_zip),
        "2" : ("Validación ventas",validacion_ventas),
        "3" : ("Cargar Ventas",cargar_ventas),
        "4" : ("Generar portafolio con promos",generar_promos),
        "5" : ("Generar PI nivel municipio",generar_pi_municipio),
        "6" : ("Generar PI socios",generar_base_socios),        
    }
    logging.info('Bienvenido a la generación de metas para portafolio infaltable')
    logging.info('Escriba en número de segun las siguientees opciones que desea realizar')
    for clave, (nombre, _) in opciones.items():
        print(f"{clave}. {nombre}")

    opcion = input("Seleccione una opción (1-6): ").strip() 
    
    if opcion in opciones:
        _, funcion = opciones[opcion]
        try:
            funcion()
        except:
            funcion(insumos)
    else:
        print("Opción inválida. El programa se cerrará.")
        exit()

'''   
    if opcion == '1':
        a= 1
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
            logging.info('Ingrese los meses con base en los nombre del siguiente listado: \n {}'.format((config['listado_meses'])))
            mes_ventas_metas = input('Escribe el mes de ventas con base en el siguiente listado : \n formato mmmm:').strip().lower()
            mes_calculo_meta = input('Ingrese el mes de la meta : \n formato mmmm:').strip().lower()
            if mes_ventas_metas in config['listado_meses']:
                # objeto y metodos para consolidar los archivos csv con las ventas
                objetoBaseVentas= conventas.consolidar_df(ruta_yml,carpeta,'.csv')
                basevetas= objetoBaseVentas.crear_df() # consolida los archivos de ventas

                # objeto y metodos para ajustar archivo con las ventas y marca PI
                objetoajustesVentas = ajventas.trabajoVentas(basevetas,ruta_yml,ruta_pi,ruta_driver_trans,
                                                            ruta_universos,ruta_rezonificaciones,mes_ventas_metas,mes_calculo_meta)
                ventas = objetoajustesVentas.ajustes_archivo_ventas()
                logging.info('Se han leido correctamente las ventas, comienza proceso de ingesta de informacióna la base de datos')
                objeto_bd= bdatos.basedatos(ventas)
                objeto_bd.consolidado_info_bd()
                logging.info('Se ha cargados las ventas a la base de datos')
            else:
                logging.info("El mes {} no es valido \n por favor vuelve y ejecuta el programa y escribe un mes valido.".format(mes_ventas_metas))
                exit()  # Salir del programa
    # yml= 'Insumos\config.yml'
    ## carpeta = os.path.join(os.getcwd(),'Ventas')
        #objeto = consolidar_df(yml,carpeta,'.csv')
        #objeto.crear_df()

'''

carpeta = os.path.join(os.getcwd(),'Ventas')
ruta_config   =  os.path.join(os.getcwd(),"Insumos",'config.yml') 
#insumos = cargar_configuracion(ruta)  
if __name__=='__main__':
    #ruta   =  os.path.join(os.getcwd(),"Insumos",'config.yml')    
    with open(ruta_config, 'r',encoding='utf-8') as file:
        config = yaml.safe_load(file)   
    menu()
