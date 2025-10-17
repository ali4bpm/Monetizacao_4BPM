import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
from st_aggrid import AgGrid, GridOptionsBuilder
from PIL import Image
import base64
import io # Importação necessária para ler o CSV como string

st.set_page_config(
    page_title="MONETIZAÇÃO BATALHÃO POTENGI - 4º BPM PMRN", page_icon="brasao.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Config / assets
# ---------------------------
# Novo caminho: Agora, esta variável contém o CONTEÚDO do CSV em formato string.
CSV_DATA_CONTENT = """Data,Categoria,Unidade de Medida,Custo Unitário (R$),Qtde,Custo Total (R$)
2025-09-01,Artesanal Curta,Unidade,500,5,2500
2025-09-03,Artesanal Curta,Unidade,500,1,500
2025-09-03,Munição,Unidade,15,3,45
2025-09-03,Maconha,Kg,2168.4,0.09,195.156
2025-09-03,Cloridrato de cocaína,Kg,180000,0.03,5400
2025-09-04,Maconha,Kg,2168.4,0.09,195.156
2025-09-04,Cloridrato de cocaína,Kg,180000,0.05,9000
2025-09-04,Motocicletas,Unidade,18889.78,1,18889.78
2025-09-07,Artesanal Curta,Unidade,500,1,500
2025-09-07,Munição,Unidade,15,17,255
2025-09-09,Revólver,Unidade,3000,1,3000
2025-09-09,Munição,Unidade,15,1,15
2025-09-10,Cloridrato de cocaína,Kg,180000,0.017,3060
2025-09-10,Crack,Kg,20000,0.02,400
2025-09-10,Revólver,Unidade,3000,1,3000
2025-09-10,Munição,Unidade,15,1,15
2025-09-12,Munição,Unidade,15,28,420
2025-09-12,Revólver,Unidade,3000,1,3000
2025-09-12,Pistola,Unidade,5000,1,5000
2025-09-12,Veículos de passeio,Unidade,55092.43,1,55092.43
2025-09-13,Maconha,Kg,2168.4,17.1,37079.640000000007
2025-09-13,Crack,Kg,20000,0.5,10000
2025-09-13,Cloridrato de cocaína,Kg,180000,0.51,91800
2025-09-14,Veículos de passeio,Unidade,55092.43,1,55092.43
2025-09-17,Cloridrato de cocaína,Kg,180000,0.015,2700
2025-09-18,Maconha,Kg,2168.4,0.034,73.725600000000014
2025-09-19,Maconha,Kg,2168.4,0.067,145.2828
2025-09-19,Crack,Kg,20000,0.007,140
2025-09-19,Cloridrato de cocaína,Kg,180000,0.031,5580
2025-09-19,Revólver,Unidade,3000,1,3000
2025-09-19,Dinheiro apreendido,R$,32.3,1,32.3
2025-09-19,Munição,Unidade,15,12,180
2025-09-22,Revólver,Unidade,3000,1,3000
2025-09-22,Munição,Unidade,15,5,75
2025-09-22,Veículos de passeio,Unidade,55092.43,1,55092.43
2025-09-23,Crack,Kg,20000,0.054,1080
2025-09-24,Cloridrato de cocaína,Kg,180000,0.004,720
2025-09-24,Revólver,Unidade,3000,2,6000
2025-09-24,Dinheiro apreendido,R$,1,40,40
2025-09-24,Munição,Unidade,15,8,120
2025-09-24,Motocicletas,Unidade,18889.78,1,18889.78
2025-09-25,Maconha,Kg,2168.4,0.157,340.4388
2025-09-25,Crack,Kg,20000,0.225,4500
2025-09-25,Cloridrato de cocaína,Kg,180000,0.03,5400
2025-09-25,Revólver,Unidade,3000,1,3000
2025-09-25,Munição,Unidade,15,6,90
2025-09-26,Dinheiro apreendido,R$,1,108.15,108.15
2025-09-26,Maconha,Kg,2168.4,0.106,229.8504
2025-09-27,Maconha,Kg,2168.4,2.036,4414.8624
2025-09-27,Crack,Kg,20000,0.042,840
2025-09-27,Cloridrato de cocaína,Kg,180000,0.006,1080
2025-09-27,Artesanal Longa,Unidade,600,1,600
2025-09-27,Munição,Unidade,15,1,15
2025-09-30,Revólver,Unidade,3000,1,3000
2025-09-30,Munição,Unidade,15,1,15
2025-09-30,Crack,Kg,20000,0.001,20
2025-10-01,Dinheiro apreendido,R$,1,76,76
2025-10-01,Motocicletas,Unidade,18889.78,1,18889.78
2025-10-01,Maconha,Kg,2168.4,0.026,56.3784
2025-10-02,Dinheiro apreendido,R$,1,85.6,85.6
2025-10-02,Maconha,Kg,2168.4,0.036,78.0624
2025-10-03,Veículos de passeio,Unidade,55092.43,1,55092.43
2025-10-03,Motocicletas,Unidade,18889.78,1,18889.78
2025-10-03,Maconha,Kg,2168.4,0.09,195.156
2025-10-04,Dinheiro apreendido,R$,1,500,500
2025-10-04,Maconha,Kg,2168.4,0.023,49.873200000000004
2025-10-04,Crack,Kg,20000,0.036,720
2025-10-04,Cloridrato de cocaína,Kg,180000,0.09,16200
2025-10-05,Dinheiro apreendido,R$,1,162,162
2025-10-05,Pistola,Unidade,5000,1,5000
2025-10-05,Munição,Unidade,15,26,390
2025-10-05,Maconha,Kg,2168.4,1.092,2367.8928
2025-10-07,Munição,Unidade,15,26,390
2025-10-07,Maconha,Kg,2168.4,0.072,156.1248
2025-10-07,Cloridrato de cocaína,Kg,180000,0.017,3060
2025-10-09,Metralhadora e Submetralhadora,Unidade,30000,1,30000
2025-10-09,Munição,Unidade,15,8,120
2025-10-09,Cloridrato de cocaína,Kg,180000,0.6,108000
2025-10-10,Dinheiro apreendido,R$,1,370,370
2025-10-10,Motocicletas,Unidade,18889.78,1,18889.78
2025-10-10,Maconha,Kg,2168.4,0.04,86.736
2025-10-10,Crack,Kg,20000,0.032,640
2025-10-10,Cloridrato de cocaína,Kg,180000,0.03,5400
2025-10-11,Dinheiro apreendido,R$,1,27,27
2025-10-11,Artesanal Curta,Unidade,500,1,500
2025-10-11,Maconha,Kg,2168.4,0.103,223.3452
2025-10-11,Crack,Kg,20000,0.001,20
2025-10-11,Cloridrato de cocaína,Kg,180000,0.02,3600
2025-10-12,Dinheiro apreendido,R$,1,50,50
2025-10-12,Artesanal Curta,Unidade,500,2,1000
2025-10-12,Munição,Unidade,15,2,30
2025-10-12,Maconha,Kg,2168.4,0.043,93.241199999999992
2025-10-12,Cloridrato de cocaína,Kg,180000,0.008,1440
2025-10-13,Maconha,Kg,2168.4,0.03,65.052
2025-10-14,Motocicletas,Unidade,18889.78,1,18889.78
2025-10-14,Maconha,Kg,2168.4,0.041,88.90440000000001
2025-10-14,Cloridrato de cocaína,Kg,180000,0.035,6300.0000000000009
2025-10-15,Dinheiro apreendido,R$,1,46,46
2025-10-15,Revólver,Unidade,3000,1,3000
2025-10-15,Munição,Unidade,15,4,60
2025-10-15,Cloridrato de cocaína,Kg,180000,0.11,19800
2025-10-16,Dinheiro apreendido,R$,1,143.75,143.75
2025-10-16,Maconha,Kg,2168.4,0.003,6.5052
2025-10-16,Crack,Kg,20000,0.002,40
2025-10-16,Cloridrato de cocaína,Kg,180000,0.003,540
"""
BRASAO_PATH = "brasao.jpg" 

# Monetization mapping (usado para cálculo de valor)
MONET_MAP = {
    "Maconha": ( "Kg", 2168.4 ),
    "Haxixe": ( "Kg", 12000.0 ),
    "Pasta base": ( "Kg", 120000.0 ),
    "Cloridrato de cocaína": ( "Kg", 180000.0 ),
    "Crack": ( "Kg", 20000.0 ),
    "Anfetaminas": ( "Unidade", 6.0 ),
    "Barbitúricos": ( "Unidade", 6.0 ),
    "LSD": ( "Ponto", 30.0 ),
    "Lança-perfume": ( "Caixa", 1250.0 ),
    "Ecstasy": ( "Unidade", 40.0 ),
    "Cigarro": ( "Pacote", 35.0 ),
    "Armas - Revólver": ( "Unidade", 3000.0 ),
    "Armas - Revólver Artesanal": ( "Unidade", 500.0 ),
    "Armas - Pistola": ( "Unidade", 5000.0 ),
    "Armas - Fuzil": ( "Unidade", 40000.0 ),
    "Armas - Metralhadora e Submetralhadora": ( "Unidade", 30000.0 ),
    "Armas - Espingarda": ( "Unidade", 5000.0 ),
    "Armas - Espingarda Artesanal": ( "Unidade", 600.0 ),
    "Armas - Carabina": ( "Unidade", 5000.0 ),
    "Munições": ( "Unidade", 15.0 ),
    "Veículos de passeio": ( "Unidade", 55092.43 ),
    "Motocicletas": ( "Unidade", 18889.78 ),
    "Veículos pesados": ( "Unidade", 120980.0 ),
    "Dinheiro apreendido": ( "R$", 1.0 ),
}

# CRIAÇÃO DO MAPA DE CATEGORIAS (Corrigido para incluir 'Artesanal Longa')
CATEGORY_MAPPING = {
    'Artesanal Curta': 'Armas - Revólver Artesanal',
    'Revólver': 'Armas - Revólver',
    'Pistola': 'Armas - Pistola',
    'Fuzil': 'Armas - Fuzil',
    'Metralhadora e Submetralhadora': 'Armas - Metralhadora e Submetralhadora',
    'Espingarda': 'Armas - Espingarda',
    'Espingarda Artesanal': 'Armas - Espingarda Artesanal',
    'Carabina': 'Armas - Carabina',
    'Munição': 'Munições', 
    'Dinheiro apreendido': 'Dinheiro apreendido',
    # NOVO: Mapeando "Artesanal Longa" para "Espingarda Artesanal"
    'Artesanal Longa': 'Armas - Espingarda Artesanal',
}

# Adiciona o mapeamento para categorias de 'Armas' usando a parte do nome após "Armas - "
armas_auto = {
    k.split("Armas - ")[-1]: k for k in MONET_MAP.keys() if k.startswith("Armas - ")
}
CATEGORY_MAPPING.update(armas_auto)

# Adiciona o mapeamento para as outras categorias que mapeiam para si mesmas
outras_auto = {
    k: k for k in MONET_MAP.keys() if not k.startswith("Armas - ") and k != "Munições"
}
CATEGORY_MAPPING.update(outras_auto)

# ---------------------------
# Helpers
# ---------------------------

def find_column(df, candidates):
    cols = df.columns
    for c in candidates:
        for col in cols:
            if c.lower() == col.strip().lower() or c.lower() in col.strip().lower():
                return col
    return None

def ensure_datetime(df, col):
    df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def normalize_category(cat):
    """Normaliza a categoria para corresponder às chaves do MONET_MAP."""
    if pd.isna(cat):
        return cat
    cat_str = str(cat).strip()
    return CATEGORY_MAPPING.get(cat_str, cat_str)


def compute_monetized(df, cat_col, qty_col):
    df['__CATEGORIA_NORMALIZADA'] = df[cat_col].apply(normalize_category)
    
    def monet_value(row):
        cat = row.get('__CATEGORIA_NORMALIZADA')
        qty = row.get(qty_col)
        
        if pd.isna(qty) or qty == "":
            return 0.0
        try:
            qty_num = float(qty)
        except:
            return 0.0
        
        if cat == 'Dinheiro apreendido':
             # Para dinheiro apreendido, a quantidade (Qtde) é o valor monetário, 
             # e o custo unitário (MONET_MAP) é 1.0, então é apenas a quantidade.
             return qty_num
        
        # get unit cost
        if cat in MONET_MAP:
            unit_cost = MONET_MAP[cat][1]
        else:
            unit_cost = 0.0
            
        return qty_num * unit_cost
        
    df["_VALOR_MONETIZADO"] = df.apply(monet_value, axis=1)
    return df.drop(columns=['__CATEGORIA_NORMALIZADA'])

# ---------------------------
# Load data (CORRIGIDO PARA LER O CONTEÚDO DA STRING)
# ---------------------------

try:
    # Lê o conteúdo da string como se fosse um arquivo
    df_raw = pd.read_csv(io.StringIO(CSV_DATA_CONTENT))
except Exception as e:
    st.sidebar.error(f"Erro na leitura dos dados internos: {e}")
    st.stop()

# normalizar colunas (remover espaços)
col_map = {c: c.strip() for c in df_raw.columns}
df_raw.rename(columns=col_map, inplace=True)


# detect important columns
col_date = find_column(df_raw, ["Data"])
col_cat  = find_column(df_raw, ["Categoria"])
col_qty  = find_column(df_raw, ["Qtde"])

if col_date is None:
    st.error("Não foi possível localizar a coluna de data (esperado: 'Data').")
    st.stop()
if col_cat is None:
    st.error("Não foi possível localizar a coluna de categoria (esperado: 'Categoria').")
    st.stop()
if col_qty is None:
    st.error("Não foi possível localizar a coluna de quantidade (esperado: 'Qtde').")
    st.stop()


# normalize date
df = df_raw.copy()
df = ensure_datetime(df, col_date)

# drop rows sem data
df = df[~df[col_date].isna()].copy()

# compute monetized
df = compute_monetized(df, col_cat, col_qty)

# ---------------------------
# Sidebar (image + filters)
# ---------------------------
with st.sidebar:
    # Tenta carregar a imagem do brasão
    try:
        Image.open(BRASAO_PATH)
        st.image(BRASAO_PATH, use_container_width=True)
    except FileNotFoundError:
        st.warning(f"Imagem de ícone '{BRASAO_PATH}' não encontrada. Substituindo por um placeholder.")
    
    st.markdown("### Filtros")
    # date range
    min_date = df[col_date].min()
    max_date = df[col_date].max()
    date_range = st.date_input(
        "Período",
        value=(min_date.date() if pd.notna(min_date) else pd.to_datetime("today").date(),
               max_date.date() if pd.notna(max_date) else pd.to_datetime("today").date())
    )
    # Garante que sempre teremos start_date e end_date como datas únicas
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
    elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date = end_date = date_range
        
    # categories
    unique_cats = sorted(df[col_cat].dropna().astype(str).unique())
    selected_cats = st.multiselect("Categorias", options=unique_cats, default=unique_cats)
    st.markdown("---")
    st.markdown("**Instruções**: selecione período e categorias. O app calculará o valor monetizado usando os critérios oficiais listados no cabeçalho.")
    st.markdown("---")


# ---------------------------
# Title + description + criteria block
# ---------------------------

# Background image styling (institucional, translúcido) e remoção de ícones fork/github/menu
def get_base64_image(img_path):
    try:
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

BRASAO_BASE64 = get_base64_image(BRASAO_PATH)
PAGE_BG = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background: linear-gradient(rgba(0,32,96,0.80), rgba(0,32,96,0.80)), url('data:image/jpg;base64,{BRASAO_BASE64}');
    background-size: 40%, cover;
    background-repeat: no-repeat;
    background-position: center center;
}}
.block-container {{
    background: rgba(255,255,255,0.90);
    border-radius: 18px;
    padding: 2rem 2rem 2rem 2rem;
}}
.stApp {{
    font-family: 'Segoe UI', Arial, sans-serif;
}}
/* Esconde ícones de fork, github e menu */
[data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
.css-1q7i1vy.e1fqkh3o3 {{ display: none !important; }}
</style>
"""
st.markdown(PAGE_BG, unsafe_allow_html=True)


# Título centralizado com brasão
st.markdown(f"""
<div style='display:flex;flex-direction:column;align-items:center;justify-content:center;margin-bottom:0.5em;'>
    <img src='data:image/jpg;base64,{BRASAO_BASE64}' width='120' style='margin-bottom:0.2em;'>
    <h1 style='color:#002060;text-align:center;font-weight:900;margin:0;'>MONETIZAÇÃO BATALHÃO POTENGI - 4º BPM PMRN</h1>
</div>
""", unsafe_allow_html=True)

# description + monetization criteria
st.markdown(
    """
**Objetivo do aplicativo:** Aplicativo para análise e monetização das apreensões registradas na Base_Monetização. Permite filtrar por data e categoria, gerar tabela dinâmica com valores monetizados, visualizar participação percentual e comparar com período anterior.

**Critérios de monetização (Categoria — Unidade — Custo Unitário R$):**
"""
)
# show criteria table
crit_df = pd.DataFrame([
    {"Categoria": k, "Unidade de Medida": MONET_MAP[k][0], "Custo Unitário (R$)": MONET_MAP[k][1]} for k in MONET_MAP
])
st.dataframe(crit_df.sort_values("Categoria").reset_index(drop=True))

st.markdown("---")

# ---------------------------
# Filtering
# ---------------------------
start_dt = pd.to_datetime(start_date)
end_dt   = pd.to_datetime(end_date) + pd.Timedelta(hours=23, minutes=59, seconds=59)

mask = (df[col_date] >= start_dt) & (df[col_date] <= end_dt) & (df[col_cat].astype(str).isin(selected_cats))
df_filt = df.loc[mask].copy()

# ------------- compute comparison period (same duration immediately before start_dt)
period_days = (end_dt - start_dt).days + 1
prev_end = start_dt - pd.Timedelta(seconds=1)
prev_start = prev_end - pd.Timedelta(days=period_days-1)
mask_prev = (df[col_date] >= prev_start) & (df[col_date] <= prev_end) & (df[col_cat].astype(str).isin(selected_cats))
df_prev = df.loc[mask_prev].copy()

# ---------------------------
# Aggregations & pivot
# ---------------------------
if df_filt.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
else:
    
    group = df_filt.groupby(col_cat).agg(
        QUANTIDADE = (col_qty, "sum"),
        VALOR_MONETIZADO = ("_VALOR_MONETIZADO", "sum"),
        REGISTROS = (col_date, "count")
    ).reset_index().sort_values("VALOR_MONETIZADO", ascending=False)

    total_valor = group["VALOR_MONETIZADO"].sum()
    total_qtd   = group["QUANTIDADE"].sum()
    # percentages
    group["% do Valor"] = (group["VALOR_MONETIZADO"] / total_valor * 100).fillna(0).round(2)
    group["% da Quantidade"] = (group["QUANTIDADE"] / total_qtd * 100).fillna(0).round(2)
    group["VALOR_MONETIZADO"] = group["VALOR_MONETIZADO"].round(2)
    group["QUANTIDADE"] = group["QUANTIDADE"].round(3)


    # Indicator: compare total_valor vs previous period
    prev_total_valor = df_prev["_VALOR_MONETIZADO"].sum() if not df_prev.empty else 0.0
    if prev_total_valor == 0 and total_valor == 0:
        delta_label = "Sem dados"
    else:
        delta_val = total_valor - prev_total_valor
        delta_label = f"R$ {delta_val:,.2f}"

    # Dashboard KPIs coloridos
    c1, c2, c3, c4 = st.columns([1.5,1.5,1,1])
    with c1:
        st.metric("Total Monetizado (R$)", f"R$ {total_valor:,.2f}", delta=delta_label, delta_color="normal")
    with c2:
        st.metric("Total Quantidade", f"{total_qtd:,.3f}") 
    with c3:
        st.metric("Registros", f"{len(df_filt)}")
    with c4:
        st.metric("Categorias", f"{group.shape[0]}")

    st.markdown("<hr style='margin:0.5em 0;'>", unsafe_allow_html=True)


    # Tabela dinâmica interativa (AgGrid) - oculta colunas REGISTROS, % do Valor e % da Quantidade
    st.subheader("Tabela Monetização por Categoria")
    group_display = group.drop(columns=["REGISTROS", "% do Valor", "% da Quantidade"], errors="ignore")
    
    gb = GridOptionsBuilder.from_dataframe(group_display.reset_index(drop=True))
    gb.configure_column("VALOR_MONETIZADO", valueFormatter='`R$ ` + value.toLocaleString("pt-BR", {minimumFractionDigits: 2, maximumFractionDigits: 2})')
    gb.configure_column("QUANTIDADE", valueFormatter='value.toLocaleString("pt-BR", {minimumFractionDigits: 3, maximumFractionDigits: 3})')
    
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(editable=False, groupable=True, filter=True, resizable=True, sortable=True)
    gb.configure_side_bar()
    gb.configure_selection('single')
    gridOptions = gb.build()
    AgGrid(group_display.reset_index(drop=True), gridOptions=gridOptions, height=420, theme='alpine', allow_unsafe_jscode=True, fit_columns_on_grid_load=True)

    
    # ---------------------------
    # 3D Chart (Plotly)
    # ---------------------------
    st.subheader("Visualização 3D — Valor monetizado por categoria")

    x = group[col_cat].astype(str)
    z = group["VALOR_MONETIZADO"].values
    perc = group["% do Valor"].values
    y = np.zeros(len(x))

    fig = go.Figure()
    for i, (xi, yi, zi, pi) in enumerate(zip(x, y, z, perc)):
        fig.add_trace(go.Scatter3d(
            x=[i, i],
            y=[0, 0],
            z=[0, zi],
            mode='lines+markers',
            marker=dict(size=6),
            line=dict(width=8),
            name=f"{xi} — R$ {zi:,.2f} ({pi:.2f}%)",
            hoverinfo='text',
            hovertext=f"{xi}<br>Valor: R$ {zi:,.2f}<br>{pi:.2f}%"
        ))
    fig.update_layout(
        scene=dict(
            xaxis=dict(tickvals=list(range(len(x))), ticktext=list(x), title="Categoria"),
            yaxis=dict(title=""),
            zaxis=dict(title="Valor (R$)")
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=600,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # Also show pie for easy percentual view
    st.subheader("Distribuição percentual (pizza)")
    pie = go.Figure(go.Pie(labels=group[col_cat].astype(str), values=group["VALOR_MONETIZADO"], hole=0.35,
                             hoverinfo="label+percent+value",
                             hovertemplate="%{label}<br>Valor: R$ %{value:,.2f}<br>Participação: %{percent}<extra></extra>"))
    pie.update_layout(height=450, margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(pie, use_container_width=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown("<div style='text-align:center;font-size:1.1em;color:#002060;font-weight:bold;'>© 2025 4º Batalhão de Polícia Militar — 4º BPM PMRN.<br>Todos os direitos reservados.<br>Dados de monetização: 4º BPM PMRN</div>", unsafe_allow_html=True)
