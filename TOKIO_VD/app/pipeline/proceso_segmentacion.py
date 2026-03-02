import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta
current_date = datetime.today()
from unidecode import unidecode
import streamlit as st


def cargar_y_procesar_excel(input_data):
    """
    Carga un archivo Excel, permite seleccionar hojas para concatenar,
    filtrar productos de interés y elegir una variable de análisis.
    Retorna:
        data (DataFrame): El DataFrame concatenado de las hojas seleccionadas.
        valor_ordenar (str): La variable de interés seleccionada.
        productos (list): Lista de productos seleccionados.
    """
    if input_data is not None:
        # Cargar el archivo como un objeto ExcelFile
        excel_file = pd.ExcelFile(input_data)
        lista_hojas = excel_file.sheet_names  # Lista de nombres de hojas

        st.markdown("<h4 style='text-align: center; color: #002855;'>Selecciona las hojas</h4>", unsafe_allow_html=True)

        # Crear el desplegable con selección múltiple
        hojas_seleccionadas = st.multiselect(
            label="Selecciona una o más hojas para concatenar",
            options=lista_hojas
        )

        if hojas_seleccionadas:
            # Definir las columnas que se desean leer
            columnas_seleccionadas = [
                'Codigo Asesor', 'Cedula Asesor', 'Asesor', 
                'Fecha de Venta', 'Producto', 'Monto', 
                'Modelo de Venta Final', 'Tipo de Interacción', 
                'Fecha Activación/Desembolso', 'N° Producto'
            ]

            try:
                # Leer y concatenar solo las hojas seleccionadas
                data = pd.concat(
                    [
                        pd.read_excel(
                            input_data, sheet_name=hoja, header=1, usecols=columnas_seleccionadas
                        ).assign(Hoja=hoja)  # Añadir el nombre de la hoja como una nueva columna
                        for hoja in hojas_seleccionadas  # Iterar sobre las hojas seleccionadas
                    ],
                    ignore_index=True
                )

                # Mostrar los datos en Streamlit
                st.markdown("<h4 style='text-align: center;'>Datos Cargados</h4>", unsafe_allow_html=True)
                st.write(data.head())  # Muestra las primeras filas

                # Crear un multiselect basado en los valores únicos de la columna 'Producto'
                st.markdown("<h4 style='text-align: center; color: #002855;'>Seleccione productos de interés</h4>", unsafe_allow_html=True)
                data['Producto']=data['Producto'].str.lower().apply(unidecode)
                data['Producto']=np.where(data['Producto']=='tdc','tarjeta de credito',data['Producto'])
                data['Producto']=np.where(data['Producto']=='prestamo','libre inversion',data['Producto'])
                productos = st.multiselect(
                    label="Seleccione productos de interés",
                    options=data['Producto'].str.lower().apply(unidecode).dropna().unique().tolist(),
                    default=[]  # Dejar vacío por defecto
                )

                # Crear un selectbox para la variable de interés
                st.markdown("<h4 style='text-align: center; color: #002855;'>Seleccione variable segmentar</h4>", unsafe_allow_html=True)
                valor_ordenar = st.multiselect(
                    label="Seleccione variable segmentar",
                    options=['cantidad_ventas', 'monto_total', 'ticket_promedio']
                )

                # Mostrar productos seleccionados y variable elegida
                if productos:
                    st.success(f"Productos seleccionados: {', '.join(productos)}")
                else:
                    st.warning("No seleccionaste ningún producto.")

                if valor_ordenar:  # Revisar si la lista no está vacía
                    st.success(f"Variables de interés seleccionadas: {', '.join(valor_ordenar)}")
                else:
                    st.warning("No seleccionaste ninguna variable de interés.")

                # Retornar los valores procesados
                return data, valor_ordenar, productos

            except Exception as e:
                st.error(f"Error al cargar las hojas seleccionadas: {e}")
                return None, None, None
        else:
            st.warning("Seleccione meses a analizar")
            return None, None, None
    else:
        st.info("Cargar consolidado de ventas")
        return None, None, None






def procesar_tokio_digitales(df_concatenado,valor_ordenar,productos,valor_monetario,variable_ranquear):
    if valor_monetario == 'Desembolsos':
        df_concatenado = df_concatenado[df_concatenado['Fecha Activación/Desembolso'].apply(str).str.len() > 5]
    else:
        df_concatenado = df_concatenado

    df_concatenado['Producto']=df_concatenado['Producto'].str.lower().apply(unidecode)
    df_concatenado['Monto']=df_concatenado['Monto'].astype(float)
    df_concatenado=df_concatenado[df_concatenado['Monto']!=0]
    df_concatenado['Producto']=np.where(df_concatenado['Producto']=='tdc','tarjeta de credito',df_concatenado['Producto'])
    df_concatenado['Producto']=np.where(df_concatenado['Producto']=='prestamo','libre inversion',df_concatenado['Producto'])


    def eliminar_cupos_atipicos(df_concatenado):
        """
        Elimina valores atípicos de la columna 'Monto' agrupados por la columna 'Producto'
        utilizando el método del rango intercuartílico (IQR).

        Args:
            df_concatenado (DataFrame): DataFrame de entrada con las columnas 'Producto' y 'Monto'.

        Returns:
            DataFrame: DataFrame sin valores atípicos en la columna 'Monto'.
        """
        # Crear un DataFrame vacío para almacenar los datos sin atípicos
        df_sin_atipicos = pd.DataFrame()

        # Iterar sobre las categorías únicas en la columna 'Producto'
        for producto in df_concatenado['Producto'].unique():
            # Filtrar el DataFrame por el producto actual
            df_filtrado = df_concatenado[df_concatenado['Producto'] == producto]
            
            # Calcular Q1 y Q3
            Q1 = df_filtrado['Monto'].quantile(0.25)
            Q3 = df_filtrado['Monto'].quantile(0.75)
            IQR = Q3 - Q1
            
            # Calcular límites inferior y superior
            limite_inferior = Q1 - 1.5 * IQR
            limite_superior = Q3 + 1.5 * IQR
            
            # Filtrar los datos sin atípicos
            df_filtrado_sin_atipicos = df_filtrado[
                (df_filtrado['Monto'] >= limite_inferior) & (df_filtrado['Monto'] <= limite_superior)
            ]
            
            # Agregar los datos filtrados al DataFrame final
            df_sin_atipicos = pd.concat([df_sin_atipicos, df_filtrado_sin_atipicos], ignore_index=True)

        return df_sin_atipicos
    
    df_sin_atipicos=eliminar_cupos_atipicos(df_concatenado)


    ventas_por_asesor = df_sin_atipicos.groupby(['Codigo Asesor','Producto']).agg(
        cantidad_ventas=('Codigo Asesor', 'count'),
        monto_total=('Monto', 'sum'),
        ticket_promedio=('Monto','mean')

    ).reset_index()






    ventas_por_asesor['ticket_promedio']=round(ventas_por_asesor['ticket_promedio'],0)

    ventas_por_asesor=ventas_por_asesor[ventas_por_asesor['Producto'].isin(productos)]

    def categorizar_asesor_por_producto(df, columnas_numericas):
        """
        Categoriza a los asesores basándose en una o varias columnas numéricas,
        iterando sobre las categorías en la columna 'Producto'.

        Args:
            df (DataFrame): DataFrame que contiene los datos.
            columnas_numericas (list): Lista de nombres de las columnas numéricas para calcular los límites.

        Returns:
            DataFrame: DataFrame con nuevas columnas '<columna>_clasificacion_asesor' para cada columna numérica.
        """
        # Crear una copia del DataFrame para no modificar el original
        df = df.copy()

        # Iterar por cada columna numérica proporcionada
        for columna_numerica in columnas_numericas:
            # Inicializar una nueva columna para clasificaciones
            columna_clasificacion = f"clasificacion_{columna_numerica}_por_asesor"
            df[columna_clasificacion] = np.nan

            # Iterar por cada valor único en la columna 'Producto'
            for producto in df['Producto'].unique():
                # Filtrar por la categoría actual (Producto)
                mask = df['Producto'] == producto
                df_categoria = df[mask]

                # Calcular los límites para esta categoría
                limite_central = df_categoria[columna_numerica].mean()
                des_est = df_categoria[columna_numerica].std()
                limite_superior = limite_central + 3 * des_est
                limite_inferior = limite_central - 3 * des_est

                # Calcular categorías solo para las filas de este Producto
                categorias = np.where(
                    df_categoria[columna_numerica] < limite_inferior, "Insuficiente",
                    np.where(
                        df_categoria[columna_numerica] < limite_central, "Aceptable",
                        np.where(
                            df_categoria[columna_numerica] < limite_superior, "Sobresaliente", "Excelente"
                        )
                    )
                )

                # Asignar las categorías al DataFrame original
                df.loc[mask, columna_clasificacion] = categorias

        return df


    # Mostrar el resultado
    


    
    
    resultado_final=categorizar_asesor_por_producto(ventas_por_asesor,valor_ordenar)
    resultado_final=resultado_final.sort_values(by=variable_ranquear,ascending=False)

    return resultado_final

def efectividad_por_asesor(base):
    # Agrupar por UsuarioSIP y calcular suma de Ventas y Gestión con nombres personalizados
    df_concatenado=base.copy()
    proporcion_usuarios = df_concatenado.groupby('Codigo').agg(
        Ventas_Totales=('Ventas por cédula', 'sum'),
        Gestiones_Totales=('Gestión', 'sum'),
        RPC=('RPC','sum')
    ).reset_index()
    proporcion_usuarios.head()
    proporcion_usuarios=proporcion_usuarios[proporcion_usuarios['Codigo'].apply(str).str.len()>4]
    proporcion_usuarios['Codigo']=proporcion_usuarios['Codigo'].apply('int64')
    proporcion_usuarios['Codigo']=proporcion_usuarios['Codigo'].apply(str)
    def reemplazar_atipicos_iqr(df, columna):
        """
        Reemplaza valores atípicos en una columna usando el método IQR (1.5) 
        y los sustituye con la mediana de la columna.

        Parámetros:
        - df: DataFrame de Pandas.
        - columna: Nombre de la columna donde buscar valores atípicos.

        Retorna:
        - DataFrame con los valores atípicos reemplazados por la mediana.
        """

        # Copiar DataFrame para no modificar el original
        df = df.copy()

        # Obtener valores de la columna
        datos = df[columna]

        # Calcular IQR
        Q1 = np.percentile(datos, 25)
        Q3 = np.percentile(datos, 75)
        IQR = Q3 - Q1

        # Definir límites de valores atípicos
        lim_inf = Q1 - 1.5 * IQR
        lim_sup = Q3 + 1.5 * IQR

        # Calcular la mediana
        mediana = np.median(datos)

        # Reemplazar valores atípicos por la mediana
        df[columna] = np.where((datos < lim_inf) | (datos > lim_sup), mediana, datos)

        return df
    # proporcion_usuarios=reemplazar_atipicos_iqr(proporcion_usuarios,'RPC')
    # proporcion_usuarios=reemplazar_atipicos_iqr(proporcion_usuarios,'Ventas_Totales')
    # proporcion_usuarios=reemplazar_atipicos_iqr(proporcion_usuarios,'Gestiones_Totales')

    proporcion_usuarios['Efectividad']=np.where(proporcion_usuarios['Gestiones_Totales']==0,0,
                                                proporcion_usuarios['Ventas_Totales']/proporcion_usuarios['Gestiones_Totales'])
    proporcion_usuarios['Conversión']=np.where(proporcion_usuarios['Gestiones_Totales']==0,0,
                                               proporcion_usuarios['RPC']/proporcion_usuarios['Gestiones_Totales'])

    proporcion_usuarios=reemplazar_atipicos_iqr(proporcion_usuarios,'Efectividad')
    proporcion_usuarios=reemplazar_atipicos_iqr(proporcion_usuarios,'Conversión')

    def clasificar_metrica(df,columna):
        n_muestras=df.shape[0]
        limite_central=df[columna].mean()
        ls = limite_central + 3 * np.sqrt((limite_central * (1 - limite_central)) / n_muestras)
        li = limite_central - 3 * np.sqrt((limite_central * (1 - limite_central)) / n_muestras)

        df['categoria_'+columna]=np.where(df[columna]==0,'No se encontraron valores',
                                        np.where(df[columna]<li,'Insuficiente',
                                                    np.where(df[columna]<limite_central,'Aceptable',
                                                            np.where(df[columna]<ls, 'Sobresaliente','Excelente'))))
        
        return df
    
    proporcion_usuarios=clasificar_metrica(proporcion_usuarios,'Efectividad')
    proporcion_usuarios=clasificar_metrica(proporcion_usuarios,'Conversión')

    proporcion_usuarios=proporcion_usuarios[['Codigo','categoria_Efectividad','categoria_Conversión']]
                                            
    return proporcion_usuarios

def antiguedad_colaborador(data):
    data=data[['Cedula Asesor','Codigo Asesor']]
    data.columns=['Cedula Asesor','Codigo']
    data=data.drop_duplicates(subset=['Cedula Asesor'])

    distribucion=pd.read_excel('Data/Distri.xlsx')
    distribucion['idp_ceco']=distribucion['idp_ceco'].apply(str)
    agentes_ventas_digitales =distribucion[distribucion['idp_ceco']=='122623']
    agentes_ventas_digitales=agentes_ventas_digitales.drop_duplicates(subset='nif')
    agentes_ventas_digitales['fecha_alta'] = pd.to_datetime(agentes_ventas_digitales['fecha_alta'], format='%d-%b-%Y')
    agentes_ventas_digitales=agentes_ventas_digitales[['nif','fecha_alta']]
    agentes_ventas_digitales.columns=['Cedula Asesor','fecha_alta']

    agentes_ventas_digitales["Antiguedad"] = (pd.to_datetime("today") - agentes_ventas_digitales["fecha_alta"]).dt.days // 30
    
    base_antiguedad=pd.merge(agentes_ventas_digitales,data,how='left',on='Cedula Asesor')
    # base_antiguedad['Antiguedad']=base_antiguedad['Antiguedad'].fillna(0)

    # niveles_antiguedad = [
    #     niveles_antiguedad['Antiguedad'] <= 3,
    #     (niveles_antiguedad['Antiguedad'] > 3) & (niveles_antiguedad['Antiguedad'] <= 6),
    #     (niveles_antiguedad['Antiguedad'] > 6) & (niveles_antiguedad['Antiguedad'] <= 9)
    # ]

    # valores_antiguedad = ['Nuevo', 'Junior', 'Senior']

    # # Eliminar espacio extra en el nombre de la columna
    # base_antiguedad['categoria_antiguedad'] = np.select(niveles_antiguedad, valores_antiguedad, default="Experto")
    base_antiguedad['Codigo']= base_antiguedad['Codigo'].fillna(0)
    base_antiguedad['Codigo']= base_antiguedad['Codigo'].apply('int64')
    base_antiguedad['Codigo']= base_antiguedad['Codigo'].apply(str)

    return base_antiguedad

def  concatenar_resultados(efectividad_asesoresase_tokio,efectividad_asesores,antiguedad):
    
    efectividad_asesoresase_tokio=efectividad_asesoresase_tokio.copy()
    efectividad_asesores=efectividad_asesores.copy()
    efectividad_asesoresase_tokio.rename(columns={'Codigo Asesor': 'Codigo'}, inplace=True)
    efectividad_asesores['Codigo']=efectividad_asesores['Codigo'].apply(str)
    efectividad_asesoresase_tokio['Codigo']=efectividad_asesoresase_tokio['Codigo'].apply(str)
    base_final=pd.merge(efectividad_asesoresase_tokio,efectividad_asesores,how='inner',on='Codigo')

    
    #antiguedad=pd.read_csv('Data/base_distribucion.csv',sep=";")
    #antiguedad['Codigo']=antiguedad['Codigo'].apply(str)
    
    base_final=pd.merge(base_final,antiguedad,how='left',on='Codigo')

    base_final['Antiguedad']=base_final['Antiguedad'].fillna(0)

    niveles_antiguedad = [
        base_final['Antiguedad'] <= 3,
        (base_final['Antiguedad'] > 3) & (base_final['Antiguedad'] <= 6),
        (base_final['Antiguedad'] > 6) & (base_final['Antiguedad'] <= 9)
    ]

    valores_antiguedad = ['Nuevo', 'Junior', 'Senior']

    # Eliminar espacio extra en el nombre de la columna
    base_final['categoria_antiguedad'] = np.select(niveles_antiguedad, valores_antiguedad, default="Experto")
    base_final=base_final.drop(columns=['Cedula Asesor','fecha_alta','Antiguedad'])
    return base_final


