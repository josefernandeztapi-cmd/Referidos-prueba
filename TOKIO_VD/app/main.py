import streamlit as st
import pandas as pd
from pandas.errors import EmptyDataError, ParserError
import warnings
from PIL import Image
import custom_style as cs
from environment import FILE_NAME_TO_DOWNLOAD
from logic.download import generate_download_data
from pipeline import proceso_segmentacion
from pipeline import mapa_calor
import datetime
###from logic.migi_api import load_send_files
from unidecode import unidecode
warnings.filterwarnings("ignore")
import os
# Load area icon
area_image = Image.open("static/img/analytics_migi.ico")
st.set_page_config(page_title="TOKIO DIGITALES", layout="wide", page_icon=area_image)

# Set custom style
st.markdown(cs.running_gif, unsafe_allow_html =True)
st.markdown(cs.gif_labels, unsafe_allow_html  = True)
st.markdown(cs.footer_style, unsafe_allow_html=True)
st.markdown(cs.proof, unsafe_allow_html=True)
background_color = cs.page_background_color

# Page distribution
title_container = st.container()
develop_container = st.container()

# State variables
mark_button_status = False

with st.sidebar:
    st.image("static/img/company_logo.png")

    # Change sidebar name and sidebar options
    st.title("Menú de Navegación")
    options = st.sidebar.radio(" ", options = ["Cargar bases de datos","Resumen Por Colaborador", "Resumen Por Clasificación", "Resultados"])


with title_container:
    logo, title = st.columns([1,3])
    
    with logo:
        # Customer logo
        st.image("static/img/logo.png")

    with title:
        # Strategy name
        st.markdown(cs.strategy_name, unsafe_allow_html=True)

with develop_container:
    # Views logic
    if options == "Cargar bases de datos":

        ##st.markdown("<h4 style='text-align: left; color: #002855;'>Ingrese Otras Campanas</h4>", unsafe_allow_html=True)

        input_data_column_1, show_data = st.columns([1,3])

        # Input data to mark
        with input_data_column_1:


##st.title("Concatenación de Archivos Excel")

            st.markdown("<h4 style='text-align: left; color: #002855;'>Ingrese Archivos Efectividad</h4>", unsafe_allow_html=True)
            ##st.markdown("Concatenación de Archivos Excel")

        # Configuración: nombre de la hoja y columnas a seleccionar
            nombre_hoja = 'Productividad Día'
            columnas = ['Campaña', 'Codigo', 'CÉDULA', 'UsuarioSIP', 'LÍDER', 
                        'Ventas por cédula', 'Ventas por producto', 'Gestión', 'RPC']

            # Permitir subir múltiples archivos Excel
            archivos_excel = st.file_uploader(" ", type="xlsx", accept_multiple_files=True)

            if archivos_excel:
                
                st.success("Primero debes concatenar la base de datos de efectividad.",icon="⚠️")
                if st.button("Concatenar Archivos"):
                    df_list = []
                    for archivo in archivos_excel:
                        # Leer el archivo, omitiendo las primeras 20 filas
                        df = pd.read_excel(archivo, sheet_name=nombre_hoja, usecols=columnas, skiprows=20)
                        # Agregar una columna con el nombre del archivo
                        df['Archivo'] = os.path.basename(archivo.name)
                        df_list.append(df)
                    # Concatenar todos los DataFrames en uno solo
                    df_concatenado = pd.concat(df_list, ignore_index=True)
                    st.session_state.df_concatenado = df_concatenado
                    
                    st.success("¡Archivos concatenados exitosamente!",icon="✅")
                    st.dataframe(df_concatenado.head())
    # Verificar si ya se ha concatenado la base de efectividad
        if 'df_concatenado' in st.session_state:
            base_efectividad=st.session_state.df_concatenado 
            

        st.write('')
        st.write('')
        input_data_column, show_data = st.columns([1,3])

        # Input data to mark
        with input_data_column:
            st.markdown("<h4 style='text-align: left; color: #002855;'>Ingrese Archivo de Ventas</h4>", unsafe_allow_html=True)

             # Cargar el archivo de Excel
            input_data = st.file_uploader("Carga tu archivo de Excel", type=["xlsx"])

            if input_data is not None:
                # Llamar a la función con el archivo cargado
                resultado = proceso_segmentacion.cargar_y_procesar_excel(input_data)

                if resultado:
                    # Extraer los valores retornados de la función
                    data = resultado[0]  # DataFrame concatenado
                    valor_ordenar = resultado[1]  # Variable de interés seleccionada
                    productos = resultado[2]  # Lista de productos seleccionados

               

        col1, col2 = st.columns([1, 4])  # Ajusta las proporciones según el espacio deseado

        with col1:  # Columna izquierda
            st.markdown("<h4 style='text-align: left; color: #002855;'>Ingrese Valor a Analizar</h4>", unsafe_allow_html=True)
            valor_monetario = st.selectbox(
                label="Selecciona el valor",
                options=['Desembolsos', 'Ventas']
            )


        with col1:  # Columna izquierda
            st.markdown("<h4 style='text-align: left; color: #002855;'>Ingrese Valor a Ranquear</h4>", unsafe_allow_html=True)
            variable_ranquear = st.selectbox(
                label="Selecciona variable",
                options=['cantidad_ventas', 'monto_total', 'ticket_promedio']
            )
            

        mark_button_status = st.button('Segmentar Agentes')


            
        # Display some data.
        with show_data:
      
            if (mark_button_status):

                base_tokio=proceso_segmentacion.procesar_tokio_digitales(data,valor_ordenar,productos,valor_monetario,variable_ranquear)
                efectividad_asesores=proceso_segmentacion.efectividad_por_asesor(base_efectividad)
                antiguedad=proceso_segmentacion.antiguedad_colaborador(data)
                base_final=proceso_segmentacion.concatenar_resultados(base_tokio,efectividad_asesores,antiguedad)

                print('Se realizan los cruces')

                #Save result into the ram
                st.session_state['depuracion'] = base_final
                
                #Message to user.
                st.write('')
                st.write('')
                import streamlit as st

# Mensaje con tamaño personalizado
                st.markdown(
                    "<h3 style='color: green;'>🔀 Agentes segmentados correctamente</h3>",
                    unsafe_allow_html=True
                )

                #st.success('Agentes segmentados correctamente', icon="🔀")
                
                ###print('Fin proceso mark_button_status')
                print("Fin proceso mark_button_status:", datetime.datetime.now())
                
                
    if (options == "Resumen Por Colaborador") and ('depuracion' in st.session_state):

        st.write('')
        st.write('')
        st.write('')
        st.write('') 

        inference_db = st.session_state.depuracion
        ##show_results(inference_db)
        fig=mapa_calor.resumen_grafico(inference_db)
        # fig = resumen_grafico(df)
        st.pyplot(fig)
# plt.show()  # O en Streamlit: st.pyplot(fig)
        
        ##st.download_button(label="Descargar", data=csv,file_name = FILE_NAME_TO_DOWNLOAD, mime='text/csv')


    if (options == "Resumen Por Clasificación") and ('depuracion' in st.session_state):

            st.write('')
            st.write('')
            st.write('')
            st.write('') 

            inference_db = st.session_state.depuracion
            ##show_results(inference_db)
            mapa_calor.graficar_clasificacion_2(inference_db)
            # fig = resumen_grafico(df)
            ###st.write(result)
    # plt.show()  # O en Streamlit: st.pyplot(fig)
            
            ##st.download_button(label="Descargar", data=csv,file_name = FILE_NAME_TO_DOWNLOAD, mime='text/csv')

    

    if (options == "Resultados") and ('depuracion' in st.session_state):

        st.write('')
        st.write('')
        st.write('')
        st.write('') 

        inference_db = st.session_state.depuracion
        ##show_results(inference_db)
        csv = generate_download_data(inference_db)
        
        st.download_button(label="Descargar", data=csv,file_name = FILE_NAME_TO_DOWNLOAD, mime='text/csv')

