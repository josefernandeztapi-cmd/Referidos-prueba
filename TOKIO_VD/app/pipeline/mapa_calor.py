import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd



def resumen_grafico(df):
    # Seleccionar productos disponibles mediante un multiselect
    all_products = sorted(df['Producto'].unique())
    selected_products = st.multiselect("Selecciona productos:", options=all_products, default=all_products)

    # Seleccionar categorías de antigüedad disponibles
    all_categories = sorted(df['categoria_antiguedad'].dropna().unique())
    selected_categories = st.multiselect("Selecciona categoría de antigüedad:", options=all_categories, default=all_categories)

    # Filtrar el DataFrame según los productos y categoría de antigüedad seleccionados
    df_filtered = df[df['Producto'].isin(selected_products) & df['categoria_antiguedad'].isin(selected_categories)]

    # Pivot: filas = Codigo, columnas = Producto, valores = cantidad_ventas
    df_pivot = df_filtered.pivot(index='Codigo', columns='Producto', values='cantidad_ventas')

    if df_pivot.empty:
        st.write("No se encontraron datos para los filtros seleccionados.")
        return None

    # Lista de opciones para la cantidad de registros a mostrar
    opciones = [10, 20, 30, 40, 50, 60]
    num_total_registros = df_pivot.shape[0]
    opciones_filtradas = [op for op in opciones if op <= num_total_registros]
    if not opciones_filtradas:
        opciones_filtradas = [num_total_registros]

    num_rows = st.selectbox("Número de registros a mostrar verticalmente:", options=opciones_filtradas, index=0)
    df_pivot = df_pivot.iloc[:num_rows, :]

    # Número de columnas (productos) en el pivot
    num_cols = df_pivot.shape[1]

    # Crear figura y ejes: un subplot por producto
    fig, axes = plt.subplots(nrows=1, ncols=num_cols, figsize=(4*num_cols, 8), sharey=True)
    if num_cols == 1:
        axes = [axes]

    # Para cada columna (producto), graficamos su heatmap con su propia escala (vmin, vmax)
    for ax, col in zip(axes, df_pivot.columns):
        data_col = df_pivot[[col]]
        # Calcular el mínimo y máximo de la columna
        vmin_col = data_col.min().min()
        vmax_col = data_col.max().max()
        # Crear anotaciones: formatear cada valor a 1 decimal
        annot = data_col.applymap(lambda x: f"{x:.1f}" if pd.notnull(x) else "")
        # Graficar el heatmap para la columna usando su propio vmin y vmax
        sns.heatmap(data_col, annot=annot, fmt="", cmap="YlGnBu", ax=ax,
                    cbar=True, vmin=vmin_col, vmax=vmax_col)
        ax.set_title(f"Producto: {col}", fontsize=12)
        ax.set_xlabel("")
        ax.set_ylabel("Código", fontsize=10)
        ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    return fig



def resaltar_totales(val):
    """Resalta en negrita las celdas de la fila y columna de totales"""
    if val.name == "Total" or val.index[-1] == "Total":
        return ['font-weight: bold'] * len(val)
    return [''] * len(val)

def graficar_clasificacion_2(df):
    # Filtrar las columnas que contienen 'clasificacion' en su nombre
    all_clasificacion = [col for col in df.columns if 'clasificacion' in col]
    
    # Selección única de la variable de clasificación
    selected_clasificacion = st.selectbox("Selecciona una clasificación:", options=all_clasificacion)

    # Selección de categorías de antigüedad
    all_categories = sorted(df['categoria_antiguedad'].dropna().unique())
    selected_categories = st.multiselect("Selecciona categoría de antigüedad:", options=all_categories, default=all_categories)

    # Aplicar filtro de categoría de antigüedad
    df_filtered = df[df['categoria_antiguedad'].isin(selected_categories)]

    # Crear la tabla de clasificación con totales
    tabla_clasificacion = pd.crosstab(df_filtered["Producto"], df_filtered[selected_clasificacion], margins=True, margins_name="Total").reset_index()

    # Aplicar formato de negrita a los totales
    tabla_clasificacion_styled = tabla_clasificacion.style.apply(resaltar_totales, axis=1).apply(resaltar_totales, axis=0)

    # Reemplazar guiones bajos por espacios y convertir a formato título
    titulo = selected_clasificacion.replace('_', ' ').title()
    st.subheader(f"{titulo}")

    # Mostrar la tabla con formato
    st.dataframe(tabla_clasificacion_styled)


