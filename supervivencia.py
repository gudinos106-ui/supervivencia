import sqlite3
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import base64
from fpdf import FPDF 
import urllib.parse

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Seguridad Alimentaria", layout="wide")

# --- 2. BASE DE DATOS Y FUNCIONES ---
def conectar_db():
    conn = sqlite3.connect('despensa_familiar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS INVENTARIO
                 (PRODUCTO TEXT, CANTIDAD REAL, FECHA_VENCIMIENTO TEXT, FECHA_REGISTRO TEXT)''')
    conn.commit()
    return conn

def generar_pdf_con_alertas(df):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(200, 0, 0) 
    pdf.cell(0, 10, text="LISTA DE COMPRAS (ALERTAS CRITICAS)", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(0, 0, 0)
    
    comprar = df[df['ESTADO'].str.contains("🔴|🟡")]
    if not comprar.empty:
        for index, row in comprar.iterrows():
            pdf.cell(0, 10, text=f"- {row['PRODUCTO']}: {row['ESTADO']}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 10, text="No hay compras urgentes pendientes.", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, text="DETALLE COMPLETO DE INVENTARIO", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(50, 10, "PRODUCTO", border=1)
    # CAMBIO CRÍTICO AQUÍ: Usamos 'TOTAL EN BODEGA' en lugar de 'CANTIDAD'
    pdf.cell(40, 10, "CANTIDAD", border=1)
    pdf.cell(50, 10, "ESTADO", border=1, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", size=10)
    for index, row in df.iterrows():
        pdf.cell(50, 10, str(row['PRODUCTO']), border=1)
        pdf.cell(40, 10, str(row['TOTAL EN BODEGA']), border=1)
        estado_texto = row['ESTADO'].replace("🔴 ","").replace("🟡 ","").replace("🟢 ","")
        pdf.cell(50, 10, estado_texto, border=1, new_x="LMARGIN", new_y="NEXT")
        
    return bytes(pdf.output())

# --- 3. DISEÑO Y CSS MEJORADO ---
def apply_ultra_styles(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
            bg_style = f"""
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-attachment: fixed;
                background-size: cover;
            }}
            """
    except:
        bg_style = ".stApp { background-color: #f4f7f6; }"

    st.markdown(f"""
        <style>
        {bg_style}
    
        /* ESTO CREA LA CAPA TRANSPARENTOSA DETRÁS DE LAS LETRAS */
        .block-container {{
          background-color: rgba(255, 255, 255, 0.70) !important; /* El 0.85 es la transparencia */
          padding: 50px !important;
          border-radius: 30px !important; /* Bordes redondeados para que se vea moderno */
          box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important; /* Una sombra externa para dar profundidad */
          margin-top: 30px !important;
        }}

        /* Reforzamos el color de la letra para que sea bien negro sobre el fondo claro */
        html, body, [class*="st-"], .stMarkdown p, label {{
            font-size: 30px !important;
            color: #000000 !important;
        }}
    
        /* Ajuste para que los títulos resalten sobre la transparencia */
        h1, h3 {{
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 10px;
        padding: 10px;
         }}
         
        /* FUERZA BRUTA PARA TEXTO GENERAL */
        html, body, [class*="st-"], .stMarkdown p, label {{
            font-size: 30px !important;
            line-height: 1.8 !important;
        }}

        /* ETIQUETAS DE FORMULARIO (MÁS GRANDES AÚN) */
        .stWidgetLabel p {{
            font-size: 28px !important;
            font-weight: bold !important;
            color: #000000 !important;
        }}

        /* PESTAÑAS (TABS) */
        button[data-baseweb="tab"] p {{
            font-size: 28px !important;
            font-weight: 800 !important;
        }}
        
         /* MÉTRICAS (Los números grandes de "46 días") */
         [data-testid="stMetricValue"] {{
             font-size: 100px !important;
             font-weight: 900 !important;
             color: #1f77b4 !important;    /* Un azul fuerte para que resalte */
             line-height: 2 !important;
         }}
         
        /* BOTONES */
        .stButton button p {{
            font-size: 23px !important;
            font-weight: bold !important;
        }}

        /* TABLAS */
        .stTable td, .stTable th {{
            font-size: 24px !important;
        }}
        
        /* TÍTULOS */
        h1 {{ font-size: 60px !important; }}
        h3 {{ font-size: 40px !important; color: #1f77b4 !important; }}

        /* --- NUEVOS AJUSTES PARA COMPACTAR LA TABLA --- */
        
        /* 1. Reduce el espacio vertical entre las filas de la tabla */
        [data-testid="stHorizontalBlock"] {{
            gap: 0rem !important;
            margin-bottom: -10px !important; /* Esto quita el ancho excesivo de arriba */
        }}

        /* 2. Hace que los textos de la tabla sean más compactos */
        .stMarkdown p {{
            font-size: 26px !important; /* Ajustamos un poco el tamaño letras para que no estire la celda */
            line-height: 1.2 !important; /* Reduce el espacio entre líneas de texto */
        }}

        /* 3. Ajuste específico para que el buscador no sea tan gigante */
        .stTextInput input {{
            font-size: 30px !important;
            padding: 15px !important;
        }}

        /* 4. Reduce el espacio del encabezado de la tabla */
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 15px !important;
            margin-bottom: 10px !important;
        }}
        
        </style>
        """, unsafe_allow_html=True)

# --- 4. DATOS MAESTROS (CORREGIDOS CON UNIDADES) ---
# Asegúrate de que est_maestro tenga este formato de 3 datos:
est_maestro = {
    # --- ENLATADOS ---
    "Atún": [1, "und", "Enlatados"],
    "Sardinas": [1, "und", "Enlatados"],
    "Maíz Dulce": [1, "und", "Enlatados"],
    "Garganzos": [1, "und", "Enlatados"],
    "Vegetales Mixto": [1, "und", "Enlatados"],
    "Champiñones": [1, "und", "Enlatados"],
    "Frutas en almibar": [1, "und", "Enlatados"],
    "Frijoles Molidos": [1, "und", "Enlatados"],
    
    # --- VERDURAS/FRUTAS (FRESCOS) ---
    "Papa": [100, "g", "Verduras (Frescos)"],
    "Cebolla": [50, "g", "Verduras (Frescos)"],
    "Tomate": [50, "g", "Verduras (Frescos)"],
    "Zanahoria": [100, "g", "Verduras (Frescos)"],
    "Bananos": [50, "g", "Frutas (Frescos)"],
    "Piña": [100, "g", "Frutas (Frescos)"],
    "Manzana": [90, "g", "Frutas (Frescos)"],
    "Papaya": [100, "g", "Frutas (Frescos)"],
    "Melón": [100, "g", "Frutas (Frescos)"],
    "Remolacha": [80, "g", "Verduras (Frescos)"],
    "Yuca": [150, "g", "Verduras (Frescos)"],
    "Tiquisque": [120, "g", "Verduras (Frescos)"],
    "Pepino": [80, "g", "Verduras (Frescos)"],
    "Aguacate": [80, "g", "Verduras (Frescos)"],
    "Plátanos": [150, "g", "Verduras (Frescos)"],

    
    # --- ALIMENTOS SECOS ---
    "Arroz": [75, "g", "Alimentos Secos"],
    "Frijoles Negros": [60, "g", "Alimentos Secos"],
    "Pasta": [80, "g", "Alimentos Secos"],
    "Harina de Maiz": [80, "g", "Alimentos Secos"],
    "Harina de Trigo": [80, "g", "Alimentos Secos"],
    "Avena": [40, "g", "Alimentos Secos"],
    "Cereales": [30, "g", "Alimentos Secos"],
    "Azúcar": [30, "g", "Alimentos Secos"],
    "Sal": [5, "g", "Alimentos Secos"],
    "Lentejas": [60, "g", "Alimentos Secos"],
    "Garganzos": [60, "g", "Alimentos Secos"],
    "Leche en Polvo": [30, "g", "Alimentos Secos"],
    "Café": [10, "g", "Alimentos Secos"],
    
    # --- LIQUIDOS/GRASAS ---
    "Agua": [2000, "ml", "Liquidos"],
    "Aceite Vegetal": [15, "ml", "Aceites/Grasas"],
    "Aceite de Coco": [15, "ml", "Aceites/Grasas"],
    "Aceite de Oliva": [15, "ml", "Aceites/Grasas"],
    "Mantequilla": [15, "g", "Aceites/Grasas"],

    # --- PROTEÍNAS / FRESCOS ---
    "Huevos": [2, "und", "Proteinas"],
    "Pollo": [80, "g", "Proteinas"],
    "Pescado": [80, "g", "Proteinas"],
    "Carne Res": [80, "g", "Proteinas"],
    "Carne de cerdo": [80, "g", "Proteinas"],
    "Embutidos": [20, "g", "Proteinas"],
    "Queso": [20, "g", "Proteinas"],
    "Leche Larga Vida": [100, "ml", "Proteinas"],
    
    # --- CONDIMENTOS Y SALSAS ---
    "Salsa de Tomate": [15, "g", "Salsas"],
    "Mostaza": [10, "g", "Salsas"],
    "Salsa Barbacoa": [10, "g", "Salsas"],
    "Mayonesa": [15, "g", "Salsas"],

    # --- MASCOTAS (Prioridad Familiar) ---
    "Alimento Perro": [150, "g", "Mascotas"],
    "Alimento Gato": [50, "g", "Mascotas"],
    "Premios/Treats": [10, "g", "Mascotas"],
    "Arena Sanitaria": [500, "g", "Mascotas"],

    # --- HIGIENE PERSONAL ---
    "Jabón de Baño": [0.1, "und", "Higiene"],
    "Papel Higiénico": [0.5, "und", "Higiene"],
    "Crema Dental": [0.05, "und", "Higiene"],
    "Cepillo dental": [0.1, "und", "Higiene"],
    "Jabon de mano": [0.1, "und", "Higiene"],
    "Shampoo": [0.3, "und", "Higiene"],
    "Crema de peinar": [0.02, "und", "Higiene"],
    "Toallas sanitarias": [0.03, "und", "Higiene"],
    "Desodorante": [0.03, "und", "Higiene"],
    "Toallas Húmedas": [0.03, "und", "Higiene"],
    "Shampoo": [0.02, "und", "Higiene"],
    
     
    # --- PRODUCTO DE LIMPIEZA ---
    "CLORO": [0.5, "ml", "Limpieza"],
    "Desifectante": [0.1, "ml", "Limpieza"],
    "Jabon en Polvo": [300, "g", "Limpieza"],
    "Lavatrastos": [0.03, "und", "Limpieza"],
}

apply_ultra_styles("edited-image.png")

st.markdown('<h1>🛡 Control Alimentaria</h1>', unsafe_allow_html=True)
# En lugar de st.markdown("### 📋 Tablero de Control Maestro") usa:
st.markdown('<div class="section-header"><h3>📋 Calculadora de Alimentos</h3></div>', unsafe_allow_html=True)

tab_calculadora, tab_emergencia, tab_comunidad = st.tabs([
    "🏠 MI DESPENSA",  
    "🚨 KIT DE EMERGENCIA",
    "🤝 COMUNIDAD"
])
    #tabla de calculadora
with tab_calculadora:
    st.markdown('<h3>📊 Gestión de Inventario</h3>', unsafe_allow_html=True)
    
    modo_critico = st.toggle("🆘 ACTIVAR RACIONAMIENTO CRÍTICO", help="Reduce el consumo al 50% para emergencias")
    
    with st.container():
        col1, col2 = st.columns(2)
        # --- AQUÍ ESTABA EL ERROR DE ESPACIOS, YA CORREGIDO ---
        with col1:
            personas = st.number_input("Cuantas personas hay en tu familia", min_value=1, value=4, key="inv_pers")
            # Debajo de 'personas = st.number_input(...)'
            tiene_mascotas = st.checkbox("🐾 ¿Tienes mascotas en casa?")

            if tiene_mascotas:
               n_mascotas = st.number_input("¿Cuántas mascotas tienes?", min_value=1, value=1, key="inv_masc")
            else:
                n_mascotas = 0
            # --- LISTA ACTUALIZADA DE CATEGORÍAS (Día 6) ---
            categorias = [
                "Enlatados", 
                "Alimentos Secos", 
                "Verduras (Frescos)", 
                "Frutas (Frescos)", 
                "Liquidos", 
                "Aceites/Grasas", 
                "Proteinas", 
                "Salsas", 
                "Mascotas", 
                "Higiene", 
                "Limpieza",  
                "OTRO (Personalizado)"
            ]

            # El menú desplegable ahora mostrará todas las opciones nuevas
            cat_elegida = st.selectbox("📂 1. Elige Categoría", categorias)            # 2. Filtrado de productos

            if cat_elegida == "OTRO (Personalizado)":
                producto_lista = ["OTRO (Personalizado)"]
            else:
                producto_lista = sorted([p for p, v in est_maestro.items() if (len(v) > 2 and v[2] == cat_elegida)])
            
            seleccion = st.selectbox(f"🔍 2. Busca en {cat_elegida}", producto_lista, key="inv_prod")
            
            if seleccion == "OTRO (Personalizado)":
                producto = st.text_input("¿Qué vas a guardar?", key="prod_manual").strip()
                medida_pro = st.selectbox("Unidad de medida", ["Kilos", "Gramos", "Litros", "Mililitros", "Unidades"], key="uni_manual_pro")
                dosis_manual = st.number_input(f"Consumo diario por persona ({medida_pro})", value=0.100, format="%.3f")
                
                if "Kilos" in medida_pro or "Gramos" in medida_pro:
                    u_interna = "g"; val_d = dosis_manual * 1000 if "Kilos" in medida_pro else dosis_manual
                elif "Litros" in medida_pro or "Mililitros" in medida_pro:
                    u_interna = "ml"; val_d = dosis_manual * 1000 if "Litros" in medida_pro else dosis_manual
                else:
                    u_interna = "und"; val_d = dosis_manual
                datos = [val_d, u_interna]
            else:
                producto = seleccion
                datos = est_maestro.get(producto, [50, "g", "Otros"])
            
            fecha_compra = st.date_input("Fecha de registro", datetime.now(), key="inv_fcompra")

        with col2:
            # 1. Definimos la unidad (esto lo dejamos igual)
            unidad_base = datos[1]
            if cat_elegida == "OTRO (Personalizado)":
                etiqueta_bodega = medida_pro
            else:
                etiqueta_bodega = "Kilos" if unidad_base == "g" else "Litros" if unidad_base == "ml" else "Unidades"

            # --- 💡 LA CALCULADORA ---
            with st.expander("🔢 CALCULAR POR PAQUETES"):
                st.write(f"Si compraste varias bolsas de {etiqueta_bodega}:")
                c_calc1, c_calc2 = st.columns(2)
                n_bolsas = c_calc1.number_input("¿Cuántas bolsas?", min_value=1, value=1, key="calc_bolsas")
                peso_bolsa = c_calc2.number_input(f"Peso de cada una", min_value=0.01, value=1.80, format="%.2f", key="calc_peso")
                
                resultado_bolsas = round(n_bolsas * peso_bolsa, 2)
                st.info(f"Total a ingresar: {resultado_bolsas} {etiqueta_bodega}")

                # 2. El cuadro de cantidad ahora usa el resultado de la calculadora como 'value'
                cantidad_total = st.number_input(
                f"¿Cantidad total en {etiqueta_bodega}?", 
                min_value=0.01, 
                value=float(resultado_bolsas), # <-- ¡Aquí está la magia de la conexión!
                format="%.2f", 
                key=f"inv_cant_{producto.replace(' ', '_')}"
            )

            # 3. El resto sigue igual
            # --- MEJORA DE CONSUMO (Idea de tu hija) ---
            cantidad_total = st.number_input(f"¿Cantidad total en {etiqueta_bodega}?", min_value=0.01, value=1.0, format="%.2f", key="inv_cant")
            fecha_vence = st.date_input("Fecha de Vencimiento", datetime.now() + timedelta(days=365), key="inv_fvence")
            frecuencia_diaria = st.slider("¿Cuantas veces al dia lo comen?", 1, 3, 1, key="inv_frec")
            dias_semana = st.slider("¿Cuántos días por semana?", 1, 7, 7, key="inv_dias_sem")
            
    # --- 🛠️ CORRECCIÓN DE LÓGICA (Día 6 - Versión Final) ---
    dosis_base = datos[0]
    unidad_base = datos[1]
    factor_crisis = 0.5 if modo_critico else 1.0
    # para sacar el promedio diario real.
    f_ajustada = (frecuencia_diaria * dias_semana) / 7

    if unidad_base == "g": 
        consumo_familiar = (personas * (dosis_base / 1000) * f_ajustada) * factor_crisis
        display_unidad = "Kg"
    elif unidad_base == "ml": 
        consumo_familiar = (personas * (dosis_base / 1000) * f_ajustada) * factor_crisis
        display_unidad = "Litros"
    else: 
        consumo_familiar = (personas * dosis_base * f_ajustada) * factor_crisis
        display_unidad = "Unidades"

    # 2. Cálculo de días totales
    d_paz = int(cantidad_total / (consumo_familiar if consumo_familiar > 0 else 0.001))
    
    # 3. TRADUCCIÓN A MESES (Para que la jefa esté feliz)
    m_reserva = d_paz // 30
    d_restantes = d_paz % 30
    
    if m_reserva > 0:
        tiempo_final = f"{m_reserva} meses y {d_restantes} días"
    else:
        tiempo_final = f"{d_paz} días"

    # --- 📊 MOSTRAR RESULTADOS (UNA SOLA VEZ) ---
    st.markdown("---")
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.metric("TIEMPO DE DURACION:", tiempo_final)
        
    with res_col2:
        st.metric("CONSUMO DIARIO FAMILIAR:", f"{round(consumo_familiar, 2)} {display_unidad}")

    if st.button("📥 GUARDAR EN MI INVENTARIO"):
        conn = conectar_db()
        c = conn.cursor()
        c.execute("INSERT INTO INVENTARIO VALUES (?, ?, ?, ?)", 
                  (producto.upper(), cantidad_total, fecha_vence.strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        st.success("¡Registro guardado!")

    # --- SECCIÓN DEL BUSCADOR (Para impacientes 🚀) ---
    st.markdown("---")
    st.markdown('<h3 style="text-align: center; color: white;"> REGISTRO DE INVENTARIO</h3>', unsafe_allow_html=True)

    # 1. Traemos los datos de la DB
    conn = conectar_db()
    query = """
        SELECT PRODUCTO, SUM(CANTIDAD) as TOTAL_CANTIDAD, 
               MIN(FECHA_VENCIMIENTO) as FECHA_VENCIMIENTO
        FROM INVENTARIO
        GROUP BY PRODUCTO
    """
    df_db = pd.read_sql_query(query, conn)
    conn.close()
    
    # 2. Buscador Único (Compacto a la izquierda)
    col_bus1, col_bus2 = st.columns([1, 2])
    with col_bus1:
        busqueda = st.text_input("🔍 Buscador...", placeholder="Buscar...", key="buscador_final_pro").strip().lower()

    # 3. Filtrado lógico
    if not df_db.empty:
        if busqueda:
            df_mostrar = df_db[df_db['PRODUCTO'].str.lower().str.contains(busqueda)]
        else:
            df_mostrar = df_db

     # 3. ENCABEZADOS: Van FUERA del else para que se vean siempre
        st.markdown("---")
        pesos_tabla = [1, 0.8, 1, 1, 1, 0.4]

        h1, h2, h3, h4, h5, h6 = st.columns(pesos_tabla)
        h1.write("**PRODUCTO**")
        h2.write("**BODEGA**")
        h3.write("**VENCE EL**")
        h4.write("**SE AGOTA**")
        h5.write("**ESTADO**")
        h6.write("**BORRAR**")
        st.markdown("---")

        # --- 5. EL BUCLE DE LA TABLA ---
        for index, row in df_mostrar.iterrows():
            # IMPORTANTE: Usamos los mismos pesos que los encabezados para que todo alinee
            c1, c2, c3, c4, c5, c6 = st.columns(pesos_tabla) 

            p_nombre = str(row['PRODUCTO']).strip().title()
            
         # 1. Buscamos en el maestro con respaldo de seguridad
            datos_m = est_maestro.get(p_nombre, [50, "g", "Otros"])
            dosis = datos_m[0]
            uni_tipo = datos_m[1]
            u_txt = "Kg" if uni_tipo == "g" else "lt" if uni_tipo == "ml" else "Und"
            
            # 2. Identificamos la cantidad (usando el total sumado)
            cant_final = row['TOTAL_CANTIDAD'] if 'TOTAL_CANTIDAD' in row else row.get('CANTIDAD', 0)
            
            # 3. Variables de cálculo
            p_fami = personas if 'personas' in locals() else 4
            f_diaria = frecuencia if 'frecuencia' in locals() else 1
            f_crisis = 0.5 if ('modo_critico' in locals() and modo_critico) else 1.0
            
            cons_dia = p_fami * (dosis/1000 if uni_tipo in ["g","ml"] else dosis) * f_diaria * f_crisis
            
            # 4. Cálculo de días
            dias_paz = int(cant_final / (cons_dia if cons_dia > 0 else 0.001))
            fecha_fin = (datetime.now() + timedelta(days=dias_paz)).strftime('%d/%m/%Y')
            
            # 5. Dibujo de datos
            c1.write(f"**{p_nombre}**")
            c2.write(f"{cant_final} {u_txt}")
            
            # 1. Recuperamos la fecha de vencimiento guardada (o 'N/A' si no hay)
            f_vence_str = row.get('FECHA_VENCIMIENTO', row.get('fecha_vencimiento', 'N/A'))
            # 2. Mostramos los datos en las columnas correspondientes
            c3.write(f"📅 {f_vence_str}")  # Fecha del empaque

            # 3. Lógica inteligente para la fecha de agotamiento
            if f_vence_str != 'N/A':
                try:
                    # Convertimos textos a fechas para comparar
                    dt_vence = datetime.strptime(f_vence_str, '%Y-%m-%d')
                    dt_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
                    # Si se acaba después de vencerse, ponemos un aviso
                    if dt_fin > dt_vence:
                       c4.write(f"⚠️ {dt_fin.strftime('%d/%m/%Y')}") 
                    else:
                        c4.write(f"⏳ {dt_fin.strftime('%d/%m/%Y')}")
                except:
                    c4.write(f"⏳ {fecha_fin}")
            else:
                c4.write(f"⏳ {fecha_fin}")
            
            # --- CÁLCULO DE TIEMPO CLARO (Idea de tu hija) ---
            meses_paz = dias_paz // 30
            dias_restantes = dias_paz % 30
            
            if meses_paz > 0:
                tiempo_formateado = f"{meses_paz}m y {dias_restantes}d"
            else:
                tiempo_formateado = f"{dias_paz}d"

            # Semáforo actualizado
            emoji = "🟢" if dias_paz > 15 else "🟡" if dias_paz > 7 else "🔴"
            c5.write(f"{emoji} {tiempo_formateado}")
            
            # 6. Botón borrar (Borra por nombre para mantener la suma correcta)
            if c6.button("🗑️", key=f"btn_del_{index}_{p_nombre}"):
                conn = conectar_db()
                c = conn.cursor()
                c.execute("DELETE FROM INVENTARIO WHERE PRODUCTO = ?", (row['PRODUCTO'],))
                conn.commit()
                conn.close()
                st.rerun()               

    # 1. MOVER ESTA FUNCIÓN ARRIBA (Antes del botón del PDF)
def calcular_tiempo_texto(row):
    try:
        p_nom = str(row.get('PRODUCTO', '')).strip().title()
        datos_prod = est_maestro.get(p_nom, [50, "g", "Otros"])
        dosis, uni = datos_prod[0], datos_prod[1]
        
        # Valores por defecto si no existen
        p_f = personas if 'personas' in locals() else 4
        
        cant_actual = row.get('TOTAL_CANTIDAD', 0)
        cons_dia = p_f * (dosis/1000 if uni in ["g","ml"] else dosis)
        dias_paz = int(cant_actual / (cons_dia if cons_dia > 0 else 0.001))
        
        meses = dias_paz // 30
        dias_rest = dias_paz % 30
        return f"{meses}m, {dias_rest}d" if meses > 0 else f"{dias_paz}d"
    except:
        return "Pendiente"

# -# --- BOTÓN DE PDF SIN ERRORES DE ENCODE ---
if st.button("📄 GENERAR PDF DE DESPENSA"):
    if not df_db.empty:
        try:
            from fpdf.enums import XPos, YPos
            
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font("Helvetica", 'B', 16)
            pdf.cell(0, 10, "INVENTARIO DE SUPERVIVENCIA", 0, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(10)
            
            # Encabezados
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(60, 10, "PRODUCTO", 1)
            pdf.cell(40, 10, "CANTIDAD", 1)
            pdf.cell(45, 10, "VENCIMIENTO", 1)
            pdf.cell(45, 10, "ESTADO", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.set_font("Helvetica", size=10)
            
            # Datos
            for _, fila in df_db.iterrows():
                nombre = str(fila.get('PRODUCTO', 'Item'))
                stock = str(fila.get('TOTAL_CANTIDAD', '0'))
                vence = str(fila.get('FECHA_VENCIMIENTO', 'N/A'))
                est_txt = "RELLENAR" if float(stock) < 5 else "OK"
                
                pdf.cell(60, 8, nombre[:25], 1)
                pdf.cell(40, 8, stock, 1)
                pdf.cell(45, 8, vence, 1)
                pdf.cell(45, 8, est_txt, 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # LA CLAVE: pdf.output() ya devuelve los bytes listos en fpdf2
            pdf_raw = pdf.output()

            # 2. CONVERSIÓN CRÍTICA: Pasamos de bytearray a bytes
            pdf_bytes = bytes(pdf_raw)
            
            st.download_button(
                label="📲 DESCARGAR PDF AHORA",
                data=pdf_bytes,
                file_name="inventario_despensa.pdf",
                mime="application/pdf",
                key="btn_descarga_final_perfecta"
            )
            st.success("¡Listo! El PDF se ha generado correctamente.")
            
        except Exception as e:
            st.error(f"Error técnico: {e}")

   # --- BLOQUE WHATSAPP CORREGIDO ---
if not df_db.empty:
    import urllib.parse
    
    # 1. Tu número con código de país (Ej: 506 para Costa Rica) SIN espacios ni guiones
    numero_tel = "506XXXXXXXX" # <-- Pon tu número real aquí
    
    # 2. Preparamos la lista de productos
    items = df_db['PRODUCTO'].tolist()
    lista_texto = "\n".join([f"• {i}" for i in items])
    
    # 3. El mensaje que quieres enviar
    mensaje_final = f"🚨 *REPORTE DE SUMINISTROS*\n\nInventario actual:\n{lista_texto}"
    
    # 4. LA CLAVE: Codificar el texto para que WhatsApp lo entienda
    mensaje_codificado = urllib.parse.quote(mensaje_final)
    
    # 5. La URL oficial de WhatsApp
    url_wa = f"https://api.whatsapp.com/send?phone={numero_tel}&text={mensaje_codificado}"
    
    # 6. Dibujamos el botón verde
    st.markdown(f"""
        <a href="{url_wa}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #25D366; color: white; padding: 15px; 
                 text-align: center; border-radius: 10px; font-weight: bold; font-size: 18px;">
                📲 Enviar Inventario a WhatsApp
            </div>
        </a>
    """, unsafe_allow_html=True)    

with tab_emergencia:
    st.markdown("### 🚨 Kit de Supervivencia Dinámico (Familiar y Mascotas) 🐾")
    
    # 1. Selector de Tiempo y Personas
    col_config1, col_config2 = st.columns(2)
    with col_config1:
        opcion_tiempo = st.selectbox(
            "¿Para cuánto tiempo quieres prepararte?",
            ["72 Horas", "1 Mes", "3 Meses", "6 Meses", "1 Año"]
        )
        # Convertimos la opción a días para la matemática
        dias_map = {"72 Horas": 3, "1 Mes": 30, "3 Meses": 90, "6 Meses": 180, "1 Año": 365}
        dias_objetivo = dias_map[opcion_tiempo]
        
    with col_config2:
        num_personas = st.number_input("Personas en el hogar:", min_value=1, value=4)

    # 2. Diccionarios con cantidades base (lo que consume 1 persona en 1 día)
    # Formato: "Objeto": [Cantidad_diaria_por_persona, "Unidad"]
    dict_med = {
        "Guantes de látex": [2, "pares"],
        "Alcohol en gel (ml)": [15, "ml"],
        "Analgésicos/Ibuprofeno": [2, "pastillas"],
        "Gasas estériles": [0.5, "unidades"],
        "Alcohol 70° (500ml)": [0.033, "botellas"],
        "Agua oxigenada (500ml)": [0.033, "botellas"],
        "Suero Oral": [0.066, "sobres"],
        "Vendas y gasas esteriles": [0.33, "unidades"],
        "Curitas/Banditas": [0.33, "unidades"],      # ~10 al mes
        "Repelente": [0.016, "frascos"],           # 0.5 frascos al mes
        "Bloqueador Solar": [0.006, "frascos"],     # 0.2 frascos al mes
        "Yodo/Povidona": [0.003, "frascos"],        # Dura mucho tiempo
        "Analgésicos/Ibuprofeno": [0.2, "pastillas"],
        "Mascarillas": [0.5, "unidades"],
        "Termómetro": [0.1, "unidades"],
        "Antidiarreicos": [2, "pastillas"],
        "Medicación personal": [1, "pastillas"],
        "Tijeras y pinzas": [0.1, "unidades"],
    }
    
    dict_mochila = {
        "Agua (Litros)": [2, "litros"],
        "Barras de cereal": [2, "unidades"],
        "Papel Higiénico": [0.2, "rollos"],
        "Pilas/Baterías": [0.13, "unidades"],       # ~4 al mes
        "Fósforos/Cajitas": [0.066, "cajitas"],      # 2 al mes
        "Cloro (Litros)": [0.016, "litros"],         # 0.5 litros al mes
        "Velas y encendedor": [0.1, "unidades"],
        "Navaja multiusos": [0.1, "unidades"],
        "Manta térmica": [0.1, "unidades"],
        "Pito/Silbato": [0.1, "unidades"],
        "Linterna y pilas": [0.1, "unidades"],
        "Baterías cargadas": [0.1, "unidades"],
        "Impermeable": [0.1, "unidades"],
        "Cuerda": [0.1, "unidades"],
        "Cinta Adhesiva": [0.1, "unidades"],
    }
    
    dict_mascotas = {
        "Agua Mascota (ml)": [500, "ml"],
        "Bolsas desechos": [3, "unidades"],
        "Comida Mascota (g)": [300, "gramos"],
        "Arena para Gato (5kg)": [0.033, "sacos"],   # 1 saco al mes
        "Desparasitante": [0.011, "pastillas"],     # 1 cada 3 meses
        "Shampoo Mascota": [0.003, "botellas"],      # 0.1 al mes
        "Bolsas Desechos": [3, "unidades"],
        "Medicinas de la mascota": [3, "unidades"],
    }

    # 3. Interfaz de Columnas
    col_e1, col_e2, col_e3 = st.columns(3)
    faltantes = []

    def mostrar_seccion(titulo, diccionario, columna, prefijo):
        with columna:
            st.subheader(titulo)
            for item, valores in diccionario.items():
                # MATEMÁTICA: Cantidad * Personas * Días
                total_necesario = round(valores[0] * num_personas * dias_objetivo, 1)
                # Redondeo hacia arriba para unidades enteras (ej: rollos de papel)
                if valores[1] in ["unidades", "rollos", "latas", "pares"]:
                    total_necesario = int(total_necesario) + (1 if total_necesario % 1 > 0 else 0)
                
                texto_item = f"{item}: {total_necesario} {valores[1]}"
                
                if st.checkbox(texto_item, key=f"{prefijo}_{item}_{opcion_tiempo}"):
                    pass
                else:
                    faltantes.append(f"{titulo}: {texto_item}")

    mostrar_seccion("💊 Botiquín", dict_med, col_e1, "med")
    mostrar_seccion("🎒 Suministros", dict_mochila, col_e2, "moch")
    mostrar_seccion("🐾 Mascotas", dict_mascotas, col_e3, "pet")

    # 4. Barra de Progreso
    total_items = len(dict_med) + len(dict_mochila) + len(dict_mascotas)
    marcados_count = total_items - len(faltantes)
    progreso = marcados_count / total_items
    st.progress(progreso)
    st.write(f"Nivel de preparación para {opcion_tiempo}: {int(progreso*100)}%")

    # 5. Botón de PDF (Ya viene con las cantidades calculadas)
    if st.button("🚨 GENERAR LISTA DE COMPRAS"):
        if not faltantes:
            st.success("¡Estás listo para sobrevivir un año! Pura Vida. 🇨🇷")
        else:
            # Aquí iría tu código de FPDF usando la lista 'faltantes'
            st.info(f"Generando lista para {len(faltantes)} artículos pendientes...")
            # (El código del PDF se mantiene igual, solo que ahora 'faltantes' ya trae los números calculados)

#tabla de comunidad        
with tab_comunidad:
    st.markdown("### 🤝 Muro de Intercambio Vecinal")
    st.write("¡Pura Vida! Si te sobra algo o necesitas algo, publícalo aquí para que tus vecinos lo vean.")

    # --- FORMULARIO PARA PUBLICAR ---
    with st.expander("📝 Publicar un anuncio (Trueque)"):
        with st.form("nuevo_post"):
            nombre = st.text_input("Tu nombre/apodo")
            mensaje = st.text_area("¿Qué ofreces o qué buscas? (Ej: Doña Anabel: Tengo harina por vencer, ¿quién cambia?)")
            boton_publicar = st.form_submit_button("Publicar en el muro")
            
            if boton_publicar and nombre and mensaje:
                conn = conectar_db()
                c = conn.cursor()
                c.execute("INSERT INTO MURO VALUES (?, ?, ?)", 
                          (nombre, mensaje, datetime.now().strftime('%d/%m/%Y %H:%M')))
                conn.commit()
                conn.close()
                st.success("¡Tu mensaje ha sido publicado!")
                st.rerun() # Refresca para ver el mensaje nuevo

    st.markdown("---")
    st.markdown("#### 💬 Publicaciones Recientes")

    # --- LECTURA DEL MURO (Asegúrate de que esté así) ---
    conn = conectar_db()
    # MUY IMPORTANTE: Debes escribir 'rowid,' antes del asterisco '*'
    query = "SELECT rowid, * FROM MURO ORDER BY rowid DESC LIMIT 10"
    df_muro = pd.read_sql_query(query, conn)
    conn.close()

    if not df_muro.empty:
        for index, row in df_muro.iterrows():
            # Mantenemos tu diseño de burbuja elegante
            m_id = row['rowid']
            st.markdown(f"""
                <div style="background-color: rgba(255, 255, 255, 0.5); 
                            padding: 20px; 
                            border-radius: 15px; 
                            border-left: 8px solid #1f77b4; 
                            margin-bottom: 5px;
                            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                    <small style="color: #555;">{row['FECHA']}</small><br>
                    <strong style="font-size: 24px; color: #1f77b4;">👤 {row['AUTOR']} dice:</strong><br>
                    <p style="font-size: 22px; margin-top: 10px;">{row['MENSAJE']}</p>
                </div>
            """, unsafe_allow_html=True)

            # --- BOTONES DE GESTIÓN (Editar y Eliminar) ---
            # Usamos el rowid que viene de tu SELECT *
            m_id = row['rowid'] 
            
            c_ed1, c_ed2, c_spacer = st.columns([1, 1, 4])
            
            # 1. BOTÓN ELIMINAR
            if c_ed1.button("🗑️ Quitar", key=f"del_{m_id}"):
                conn = conectar_db()
                c = conn.cursor()
                c.execute("DELETE FROM MURO WHERE rowid = ?", (m_id,))
                conn.commit()
                conn.close()
                st.rerun()

            # 2. BOTÓN EDITAR (Lógica simple)
            if c_ed2.button("✏️ Editar", key=f"edit_{m_id}"):
                st.session_state[f"editando_{m_id}"] = True

            # Si el usuario le dio a editar, mostramos el campo para corregir
            if st.session_state.get(f"editando_{m_id}", False):
                nuevo_texto = st.text_area("Corrige tu mensaje:", value=row['MENSAJE'], key=f"txt_{m_id}")
                if st.button("✅ Guardar Cambios", key=f"save_{m_id}"):
                    conn = conectar_db()
                    c = conn.cursor()
                    c.execute("UPDATE MURO SET MENSAJE = ? WHERE rowid = ?", (nuevo_texto, m_id))
                    conn.commit()
                    conn.close()
                    st.session_state[f"editando_{m_id}"] = False
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True) # Espacio entre publicaciones
