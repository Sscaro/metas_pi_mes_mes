import os
import zipfile

## directorio Ventas

def descomprimir():
    directorio = os.path.join(os.getcwd(),'Ventas')
    archivos = os.listdir(directorio)
    for archivo in archivos:
        if archivo.endswith('.zip'):
            nueva_carpeta = os.path.splitext(archivo)[0] # separa la extensión de achivo
            ruta_zip = os.path.join(directorio, archivo) # crea una carpeta con el nombre de la descargar
            directorio_destino = os.path.join(directorio, nueva_carpeta)
            os.makedirs(directorio_destino, exist_ok=True)
                    # Extraer el contenido del archivo ZIP
            with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
                zip_ref.extractall(directorio_destino)
            
            for root, dirs, files in os.walk(directorio_destino):
                for file in files:
                    if file.endswith('.csv'):
                        # Crear la ruta completa del archivo CSV
                        ruta_csv = os.path.join(root, file)
                        
                        # Renombrar y mover el archivo CSV al directorio principal
                        nuevo_nombre_csv = os.path.join(directorio, f'{nueva_carpeta}.csv')
                        os.rename(ruta_csv, nuevo_nombre_csv)
            
            # Eliminar la carpeta extraída después de mover el archivo CSV      
            os.rmdir(directorio_destino)
            os.remove(os.path.join(os.getcwd(),'Ventas',archivo))
    return print("Terminao proceso de descomprimir archivos")