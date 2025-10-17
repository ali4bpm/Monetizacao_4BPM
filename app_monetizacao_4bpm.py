


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
from st_aggrid import AgGrid, GridOptionsBuilder
from PIL import Image
import base64

st.set_page_config(
    page_title="MONETIZAÇÃO BATALHÃO POTENGI - 4º BPM PMRN", page_icon="brasao.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Config / assets
# ---------------------------
EXCEL_POSSIBLE_PATHS = [
    "Tabela_Monetizacao_4 BPM_PM_RN.xlsx"
]
BRASAO_PATH = "brasao.jpg"  # imagem enviada por você

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

# ---------------------------
# Helpers
# ---------------------------

def try_load_excel(EXCEL_POSSIBLE_PATHS):
   caminho_arquivo='Tabela_Monetizacao_4_BPM_PM_RN.xlsx'
   df = pd.read_excel(caminho_arquivo, sheet_name=None)
        return df

def detect_sheet_and_columns(sheets_dict):
    # Prefer sheet named like 'Base_Monetização' (se existir) ou primeira
    preferred_names = ["Base_Monetização", "Base_Monetizacao", "Base_Monetização ", "Base_Monetização1", "Base_Monetização (1)"]
    sheet_name = None
    for n in sheets_dict.keys():
        if any(pref.lower() in n.lower() for pref in preferred_names):
            sheet_name = n
            break
    if sheet_name is None:
        # fallback to first sheet
        sheet_name = list(sheets_dict.keys())[0]
    df = sheets_dict[sheet_name].copy()
    # normalize columns
    col_map = {c: c.strip() for c in df.columns}
    df.rename(columns=col_map, inplace=True)
    return sheet_name, df

def find_column(df, candidates):
    cols = df.columns
    for c in candidates:
        for col in cols:
            if c.lower() == col.lower() or c.lower() in col.lower():
                return col
    return None

def ensure_datetime(df, col):
    df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def compute_monetized(df, cat_col, qty_col):
    # Create monet_value column
    def monet_value(row):
        cat = row.get(cat_col)
        qty = row.get(qty_col)
        if pd.isna(qty) or qty == "":
            return 0.0
        try:
            qty_num = float(qty)
        except:
            return 0.0
        # get unit cost
        if cat in MONET_MAP:
            unit_cost = MONET_MAP[cat][1]
        else:
            # fallback: if category contains known key
            matched = None
            for k in MONET_MAP.keys():
                if isinstance(cat, str) and k.lower() in cat.lower():
                    matched = k
                    break
            unit_cost = MONET_MAP[matched][1] if matched else 0.0
        return qty_num * unit_cost
    df["_VALOR_MONETIZADO"] = df.apply(monet_value, axis=1)
    return df

# ---------------------------
# Load data
# ---------------------------
path_used, sheets = try_load_excel(EXCEL_POSSIBLE_PATHS)
if sheets is None:
    st.sidebar.error("Arquivo Excel não encontrado automaticamente. Coloque o arquivo .xlsx na mesma pasta do app ou atualize o caminho em EXCEL_POSSIBLE_PATHS no código.")
    st.stop()

sheet_name, df_raw = detect_sheet_and_columns(sheets)

# detect important columns
col_date = find_column(df_raw, ["DATA", "Data", "data"])
col_cat  = find_column(df_raw, ["Categoria", "categoria", "CATEGORIA", "Tipo", "produto"])
col_qty  = find_column(df_raw, ["Quantidade", "quantidade", "Qtd", "QTD", "Valor", "peso", "PESO", "Quantidade_apreendida", "QTD_APREENDIDA"])

if col_date is None:
    st.error("Não foi possível localizar a coluna de data na planilha. Certifique-se de ter uma coluna com datas (ex: 'DATA' ou 'Data').")
    st.stop()
if col_cat is None:
    st.error("Não foi possível localizar a coluna de categoria (ex: 'Categoria').")
    st.stop()
if col_qty is None:
    # se não achar quantidade, assumimos 1 por registro
    df_raw["__QUANTIDADE_ASSUMIDA"] = 1
    col_qty = "__QUANTIDADE_ASSUMIDA"

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
    st.image(BRASAO_PATH, use_container_width=True)
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
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

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
**Objetivo do aplicativo:**  
Aplicativo para análise e monetização das apreensões registradas na Base_Monetização. Permite filtrar por data e categoria, gerar tabela dinâmica com valores monetizados, visualizar participação percentual e comparar com período anterior.

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
    # group by category
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
        delta_pct = None
    else:
        delta_val = total_valor - prev_total_valor
        if prev_total_valor == 0:
            pct_change = np.nan
        else:
            pct_change = (delta_val / prev_total_valor) * 100
        delta_label = f"R$ {delta_val:,.2f}"
        delta_pct = f"{pct_change:.2f}%" if not np.isnan(pct_change) else "N/A"

    # Dashboard KPIs coloridos
    c1, c2, c3, c4 = st.columns([1.5,1.5,1,1])
    with c1:
        st.metric("Total Monetizado (R$)", f"R$ {total_valor:,.2f}", delta=delta_label, delta_color="normal")
    with c2:
        st.metric("Total Quantidade", f"{int(total_qtd):,}")
    with c3:
        st.metric("Registros", f"{len(df_filt)}")
    with c4:
        st.metric("Categorias", f"{group.shape[0]}")

    st.markdown("<hr style='margin:0.5em 0;'>", unsafe_allow_html=True)


    # Tabela dinâmica interativa (AgGrid) - oculta colunas REGISTROS, % do Valor e % da Quantidade
    st.subheader("Tabela Monetização por Categoria")
    group_display = group.drop(columns=["REGISTROS", "% do Valor", "% da Quantidade"], errors="ignore")
    gb = GridOptionsBuilder.from_dataframe(group_display.reset_index(drop=True))
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(editable=False, groupable=True, filter=True, resizable=True, sortable=True)
    gb.configure_side_bar()
    gb.configure_selection('single')
    gridOptions = gb.build()
    AgGrid(group_display.reset_index(drop=True), gridOptions=gridOptions, height=420, theme='alpine', fit_columns_on_grid_load=True)

    

    # ---------------------------
    # Indicator: compare total_valor vs previous period
    prev_total_valor = df_prev["_VALOR_MONETIZADO"].sum() if not df_prev.empty else 0.0
    if prev_total_valor == 0 and total_valor == 0:
        delta_label = "Sem dados"
        delta_pct = None
    else:
        delta_val = total_valor - prev_total_valor
        if prev_total_valor == 0:
            pct_change = np.nan
        else:
            pct_change = (delta_val / prev_total_valor) * 100
        delta_label = f"R$ {delta_val:,.2f}"
        delta_pct = f"{pct_change:.2f}%" if not np.isnan(pct_change) else "N/A"

    # ---------------------------
    # 3D Chart (Plotly)
    # ---------------------------
    st.subheader("Visualização 3D — Valor monetizado por categoria")

    # for plotly 3D we create x (index), y (zeros), z (values) and draw as 3D bars via scatter with lines
    x = group[col_cat].astype(str)
    z = group["VALOR_MONETIZADO"].values
    perc = group["% do Valor"].values
    y = np.zeros(len(x))

    # Create 3D bar-like using markers with vertical lines to 'simulate' bars.
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
                          hoverinfo="label+percent+value"))
    pie.update_layout(height=450, margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(pie, use_container_width=True)

# ---------------------------
# Footer
# ---------------------------
df = compute_monetized(df, col_cat, col_qty)
st.markdown("---")
df_filt = df.loc[mask].copy()
df_prev = df.loc[mask_prev].copy()
st.markdown("---")
st.markdown("<div style='text-align:center;font-size:1.1em;color:#002060;font-weight:bold;'>© 2025 4º Batalhão de Polícia Militar — 4º BPM PMRN.<br>Todos os direitos reservados.<br>Dados de monetização: 4º BPM PMRN</div>", unsafe_allow_html=True)
