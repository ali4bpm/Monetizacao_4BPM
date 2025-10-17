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
# Novo caminho para o arquivo CSV que contém os dados da aba 'Base_Monetização'
CSV_DATA_PATH = "Tabela_Monetizacao_4 BPM_PM_RN.xlsx - Base_Monetização.csv"
BRASAO_PATH = "brasao.jpg"  # imagem enviada por você

# Monetization mapping (usado para cálculo de valor)
# Este dicionário MONET_MAP simula a leitura da aba 'Critérios' do seu Excel.
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
# Cria um mapa de categorias que contêm "Armas" para mapear os nomes no seu dataframe de dados
# (ex: 'Revólver' no DF é mapeado para 'Armas - Revólver' no MONET_MAP)
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
    # Outras categorias mantêm o nome
    k.split("Armas - ")[-1]: k for k in MONET_MAP.keys() if k.startswith("Armas - ")
}
CATEGORY_MAPPING.update({k:k for k in MONET_MAP.keys() if not k.startswith("Armas - ") and k != "Munições"})

# ---------------------------
# Helpers
# ---------------------------

def find_column(df, candidates):
    cols = df.columns
    for c in candidates:
        for col in cols:
            # Match exato ou match parcial case-insensitive após limpeza de espaço
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
    # Tenta um mapeamento direto ou mapeamento com 'Armas'
    return CATEGORY_MAPPING.get(cat_str, cat_str)


def compute_monetized(df, cat_col, qty_col):
    # Aplica a normalização da categoria ANTES do cálculo
    df['__CATEGORIA_NORMALIZADA'] = df[cat_col].apply(normalize_category)
    
    # Create monet_value column
    def monet_value(row):
        cat = row.get('__CATEGORIA_NORMALIZADA')
        qty = row.get(qty_col)
        
        # O nome da coluna no seu CSV é 'Custo Total (R$)', que é o valor final.
        # Se você quiser usar a fórmula Qtde * Custo Unitário, use a lógica abaixo.
        # Seu CSV já tem a coluna 'Custo Total (R$)', mas vou seguir a lógica de cálculo.
        
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
            # Fallback para categorias não mapeadas (deve ser 0.0)
            unit_cost = 0.0
            
        return qty_num * unit_cost
        
    df["_VALOR_MONETIZADO"] = df.apply(monet_value, axis=1)
    return df.drop(columns=['__CATEGORIA_NORMALIZADA']) # Remove a coluna auxiliar

# ---------------------------
# Load data (MODIFICADO PARA CSV)
# ---------------------------

try:
    # Lendo o arquivo CSV que representa a aba 'Base_Monetização'
    df_raw = pd.read_csv(CSV_DATA_PATH)
except Exception as e:
    st.sidebar.error(f"Arquivo de dados CSV '{CSV_DATA_PATH}' não encontrado ou erro na leitura: {e}")
    st.stop()

# normalizar colunas
col_map = {c: c.strip() for c in df_raw.columns}
df_raw.rename(columns=col_map, inplace=True)


# detect important columns
# Note que os nomes das colunas no seu CSV são: 'Data', 'Categoria', 'Qtde', 'Custo Unitário (R$)', 'Custo Total (R$)'
col_date = find_column(df_raw, ["Data"]) # Deve encontrar 'Data'
col_cat  = find_column(df_raw, ["Categoria"]) # Deve encontrar 'Categoria'
col_qty  = find_column(df_raw, ["Qtde"]) # Deve encontrar 'Qtde'

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
# Usamos col_cat e col_qty, mas a coluna 'Categoria' será normalizada internamente para o cálculo
df = compute_monetized(df, col_cat, col_qty)

# ---------------------------
# Sidebar (image + filters)
# ---------------------------
# ... o restante do código da sidebar permanece o mesmo
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
        # Se o brasão não for encontrado, usa uma imagem placeholder
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
    # O group by usa o 'col_cat' original, mas o cálculo de VALOR_MONETIZADO usou a categoria normalizada.
    # Se quiser agrupar pela categoria normalizada, substitua col_cat por '__CATEGORIA_NORMALIZADA' no group_by,
    # mas como a lógica de monetização já está na função compute_monetized,
    # manterei o agrupamento pelo nome original para visualização na tabela de dados.
    # Para o cálculo de valor correto, a lógica de compute_monetized é a que importa.
    
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
        # A linha de delta que você usou no código original é: st.metric("Total Monetizado (R$)", f"R$ {total_valor:,.2f}", delta=delta_label, delta_color="normal")
        # Essa linha só mostra a diferença (R$). Não precisa do delta_pct aqui.

    # Dashboard KPIs coloridos
    c1, c2, c3, c4 = st.columns([1.5,1.5,1,1])
    with c1:
        st.metric("Total Monetizado (R$)", f"R$ {total_valor:,.2f}", delta=delta_label, delta_color="normal")
    with c2:
        # Se total_qtd não for um inteiro grande, melhor formatar com separador de milhar e casas decimais se necessário
        st.metric("Total Quantidade", f"{total_qtd:,.3f}") 
    with c3:
        st.metric("Registros", f"{len(df_filt)}")
    with c4:
        st.metric("Categorias", f"{group.shape[0]}")

    st.markdown("<hr style='margin:0.5em 0;'>", unsafe_allow_html=True)


    # Tabela dinâmica interativa (AgGrid) - oculta colunas REGISTROS, % do Valor e % da Quantidade
    st.subheader("Tabela Monetização por Categoria")
    group_display = group.drop(columns=["REGISTROS", "% do Valor", "% da Quantidade"], errors="ignore")
    # Configurações de formatação para R$ e Qtde
    
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
                             hoverinfo="label+percent+value",
                             # Usando o nome da categoria normalizada para hovertext, caso haja diferença
                             hovertemplate="%{label}<br>Valor: R$ %{value:,.2f}<br>Participação: %{percent}<extra></extra>"))
    pie.update_layout(height=450, margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(pie, use_container_width=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown("<div style='text-align:center;font-size:1.1em;color:#002060;font-weight:bold;'>© 2025 4º Batalhão de Polícia Militar — 4º BPM PMRN.<br>Todos os direitos reservados.<br>Dados de monetização: 4º BPM PMRN</div>", unsafe_allow_html=True)
