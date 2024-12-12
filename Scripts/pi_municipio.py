#Documento para enviar al equipo de pedido infaltable
# este documento realiza la consoldicación de todo el portafolio eviando por el equipo de Portafolio
# se debe correr una vez al mes para que el equipo de data puede enviar este formato a servicios nutresa
# y se cargue a las maquinas de los vendedores
import pandas as pd
import os

def rutainsumos(nombrearhvo): 
    rutacompleta = os.path.join(os.getcwd(),"insumos",nombrearhvo)
    return rutacompleta

def eliminarcolumnas(df,eliminar):
    columnas = df.columns.to_list()
    for i in columnas:
        if i in eliminar:
            del df[i]
    return df

class concatenarportafolio:
    def __init__(self,archivo):
        self.archivo = archivo
        self.diccionario =  {"Material":str,
                "Material Aj":str} 

    def concatenadohojas(self,hojas):
        total = pd.DataFrame()
        for i in hojas:
            hoja = pd.read_excel(self.archivo,sheet_name=i, dtype =str)
            total = pd.concat([total,hoja],axis=0)
        return total
    
#import modulos.portacompleto as pt # modulo para desplegegar el portafolio a nivel segmento vital.

def consolidaPIformato(nombrearhivo):
    ruta_pi = rutainsumos(nombrearhivo)
    bases = concatenarportafolio(ruta_pi)
    hojasAUYD = ["Infaltable TD","Infaltable AU"]
    baseAUTD = bases.concatenadohojas(hojasAUYD)
    columnasAUTDEliminar = ["Material","Nombre Material","Excluir de Meta","Innovación"]
    baseAUTD = eliminarcolumnas(baseAUTD,columnasAUTDEliminar)
    baseAUTD.rename(columns={'Material Aj':'Material','Nombre Material Aj':'Nombre Material'},inplace=True)
    baseAUTD.drop_duplicates(inplace=True,keep='first')
    hojasBCE = ["Infaltable B","Infaltable CE"]
    baseBCE = bases.concatenadohojas(hojasBCE)    
    baseBCE = eliminarcolumnas(baseBCE,columnasAUTDEliminar)
    baseBCE.rename(columns={'Material Aj':'Material','Nombre Material Aj':'Nombre Material'},inplace=True)
    baseBCE.drop_duplicates(inplace=True,keep='first')
    writer = pd.ExcelWriter('Salidas\consolidadopi.xlsx')
    baseAUTD.to_excel(writer, sheet_name="PI No Municipio", index=False)
    baseBCE.to_excel(writer, sheet_name="PI Comer Esp y Bienestar", index=False)
    #writer.save()
    writer.close()

#pt.concatenararhivos(pt.rutainsumos(nombrearhivo))   
#consolidaPIformato(nombrearhivo)