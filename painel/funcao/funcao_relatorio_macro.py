import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import re
from wordcloud import WordCloud, STOPWORDS
import json
import unicodedata
from html import escape



# --- helpers ---
def _nonempty_any(v):
    """True se v (string/list) tiver algo não vazio."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return False
    if isinstance(v, list):
        return any(str(x).strip() for x in v if x is not None)
    s = str(v).strip()
    return s not in ("", "none", "null")

def _col_bool(df, col):
    """Série booleana True se a coluna existir e tiver conteúdo não vazio (str/list)."""
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    return df[col].apply(_nonempty_any)

def _pick_first_col(df, candidates):
    """Retorna o primeiro nome de coluna existente; senão None."""
    return next((c for c in candidates if c in df.columns), None)

def _has_ref_legenda_produtos(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return False
    if isinstance(val, str):
        s = val.strip()
        if s == "" or s.lower() in ("none", "null"):
            return False
        try:
            val = json.loads(s)
        except Exception:
            return False
    if isinstance(val, dict):
        val = [val]
    if not isinstance(val, list):
        return False
    for item in val:
        if isinstance(item, dict):
            ref = item.get("ref") or item.get("codigo") or item.get("code") or item.get("sku")
            if ref is not None and str(ref).strip() != "":
                return True
    return False

# --- parte 1 ---
def app_funcao_conceito_basico_parte01(base_filtrada):
    df = base_filtrada.copy()

    with st.container():
        c1, c2, c3, c4 = st.columns(4)

        total_posts = len(df)

        # rosto
        col_face = _pick_first_col(df, ["imagem_face_presente"])
        pct_faces = (pd.to_numeric(df[col_face], errors="coerce").fillna(0).astype(int).mean()*100) if col_face else 0

        # texto na imagem: tenta várias formas
        pct_prod = 0
        if "imagem_texto_presente" in df.columns:
            pct_prod = (pd.to_numeric(df["imagem_texto_presente"], errors="coerce").fillna(0).astype(int).mean()*100)
        elif "imagem_texto_detectado" in df.columns:
            pct_prod = (pd.to_numeric(df["imagem_texto_detectado"], errors="coerce").fillna(0).astype(int).mean()*100)
        elif "imagem_num_blocos_texto" in df.columns:
            pct_prod = ((pd.to_numeric(df["imagem_num_blocos_texto"], errors="coerce").fillna(0) > 0).mean()*100)
        elif "imagem_texto_proporcao" in df.columns:
            pct_prod = ((pd.to_numeric(df["imagem_texto_proporcao"], errors="coerce").fillna(0) > 0).mean()*100)

        # média de caracteres
        avg_chars = df["caption"].astype(str).str.len().mean() if "caption" in df.columns else 0

        # métricas (sem **; use o CSS para negrito)
        c1.metric("Qtd. de Publicações", total_posts)
        c2.metric("% de Publicações com Rosto", f"{pct_faces:.1f}%")
        c3.metric("% de Publicações com Texto na Imagem", f"{pct_prod:.1f}%")
        c4.metric("Média de Caracteres por Legenda", f"{avg_chars:.0f}")

# --- parte 2 ---
def app_funcao_conceito_basico_parte02(base_filtrada):
    df = base_filtrada.copy()

    with st.container():
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

        # menções (@)
        menc_img = _col_bool(df, "imagem_mencoes_ocr")
        menc_leg = _col_bool(df, "legenda_mencoes")
        pct_mentions = ((menc_img | menc_leg).mean()*100)

        # hashtags
        hash_img = _col_bool(df, "imagem_hashtags_ocr")
        hash_leg = _col_bool(df, "legenda_hashtags")
        pct_hashtags = ((hash_img | hash_leg).mean()*100)

        # URLs
        url_img = _col_bool(df, "imagem_url_detectada")
        url_leg = _col_bool(df, "legenda_urls")
        pct_urls = ((url_img | url_leg).mean()*100)

        # cupons (imagem + legenda em variantes)
        cup_leg_col = _pick_first_col(df, ["legenda_codigos_cupons", "legenda_codigos.cupons"])
        cup_leg = _col_bool(df, cup_leg_col) if cup_leg_col else pd.Series(False, index=df.index)
        cup_img = _col_bool(df, "imagem_codigo_cupom")
        pct_cupons = ((cup_img | cup_leg).mean()*100)

        # cód. vendedora (variantes)
        vend_leg_col = _pick_first_col(df, ["legenda_codigos_codigos_vendedora", "legenda_codigos.codigos_vendedora"])
        vend_leg = _col_bool(df, vend_leg_col) if vend_leg_col else pd.Series(False, index=df.index)
        pct_cod_vendedor = (vend_leg.mean()*100)

        # 'ref' em legenda_produtos
        if "legenda_produtos" in df.columns:
            tem_ref = df["legenda_produtos"].apply(_has_ref_legenda_produtos)
            pct_ref_legenda = tem_ref.mean() * 100
        else:
            pct_ref_legenda = 0.0

        # emoticoins
        emo_img = _col_bool(df, "imagem_emoticoins")
        emo_leg = _col_bool(df, "legenda_emoticoins")
        pct_emoticoins = ((emo_img | emo_leg).mean()*100)

        # multi-marca (binária 0/1)
        if "legenda_multi_marca" in df.columns:
            s = pd.to_numeric(df["legenda_multi_marca"], errors="coerce").fillna(0).clip(0,1)
            pct_multi_marca = s.mean() * 100
        else:
            pct_multi_marca = 0.0

        # métricas
        c1.metric("% Publi. com Menções (@)", f"{pct_mentions:.1f}%")
        c2.metric("% Publi. com Hashtags", f"{pct_hashtags:.1f}%")
        c3.metric("% Publi. com Url", f"{pct_urls:.1f}%")
        c4.metric("% Publi. com Cupons", f"{pct_cupons:.1f}%")
        c5.metric("% Publi. com Cód. de Vendedor", f"{pct_cod_vendedor:.1f}%")
        c6.metric("% Publi. com Código 'ref' na Legenda", f"{pct_ref_legenda:.1f}%")
        c7.metric("% Publi. com Emoticoins", f"{pct_emoticoins:.1f}%")
        c8.metric("% Publi. com +1 Marca", f"{pct_multi_marca:.1f}%")



# Gráfico de barras para tipos de post
def app_funcao_tipo_post(base_filtrada):

    # distribuição por post_type -> % do total
    counts = (base_filtrada["post_type"]
              .value_counts(dropna=False)
              .rename_axis("post_type")
              .reset_index(name="count"))
    counts["percent"] = counts["count"] / counts["count"].sum() * 100

    # ordenar por percentual (desc)
    counts = counts.sort_values("percent", ascending=False).reset_index(drop=True)

    fig = px.bar(
        counts,
        x="post_type",
        y="percent",
        text=counts["percent"].map(lambda v: f"{v:.2f}%"),
        labels={"post_type": "Tipo de Publi.", "percent": "% de publicações"},
        title="% de publicações pelo tipo de publicação",
        color_discrete_sequence=["#213ac7"],
    )

    # fundo transparente + sem grade
    fig.update_layout(
        yaxis_tickformat=".2f",            # casa decimal alinhada ao texto
        yaxis_title="% de publicações",
        xaxis_title="Tipo de Publicação",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,                  # só 1 série
        margin=dict(l=10, r=10, t=50, b=10),
    )

    # manter ordem custom; rótulos fora e sem corte
    fig.update_xaxes(
        showgrid=False, zeroline=False,
        categoryorder="array", categoryarray=counts["post_type"],
    )
    fig.update_yaxes(showgrid=False, zeroline=False)
    fig.update_traces(textposition="outside", cliponaxis=False)

    st.plotly_chart(fig, use_container_width=True)



# ------------------------------------------
# Funções auxiliares
# ------------------------------------------
def _prepare_datetime(df: pd.DataFrame, tz: str = "America/Sao_Paulo") -> pd.DataFrame:
    out = df.copy()
    # Garante datetime tz-aware a partir de strings ISO (com Z)
    out["post_date"] = pd.to_datetime(out["post_date"], errors="coerce", utc=True)
    out = out.dropna(subset=["post_date", "post_type"])
    # Converte para o fuso desejado
    out["post_date_local"] = out["post_date"].dt.tz_convert(tz)
    return out

def _style_plot(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Tipo de post",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

# ------------------------------------------
# Visualizações
# ------------------------------------------
def chart_por_hora(df_local: pd.DataFrame):
    df_local["hora"] = df_local["post_date_local"].dt.floor("H")
    g = (df_local.groupby(["hora", "post_type"])
                .size()
                .reset_index(name="count")
                .sort_values("hora"))

    fig = px.line(
        g,
        x="hora",
        y="count",
        color="post_type",
        markers=True,
        labels={"hora": "Data e hora", "count": "Qtd. publicações", "post_type": "Tipo de post"},
        title="Publicações por tipo — agreg. por hora",
    )
    _style_plot(fig)
    return fig

def chart_por_dia(df_local: pd.DataFrame, barmode: str = "group"):
    df_local["dia"] = df_local["post_date_local"].dt.floor("D")
    g = (df_local.groupby(["dia", "post_type"])
                .size()
                .reset_index(name="count")
                .sort_values("dia"))

    fig = px.bar(
        g,
        x="dia",
        y="count",
        color="post_type",
        barmode=barmode,  # "group" ou "stack"
        text=g["count"].map(lambda v: f"{v}"),
        labels={"dia": "Dia", "count": "Qtd. publicações", "post_type": "Tipo de post"},
        title="Publicações por tipo — agreg. por dia",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    _style_plot(fig)
    return fig

# ------------------------------------------
# App principal
# ------------------------------------------
def app_funcao_temporal(base_filtrada: pd.DataFrame):
    viz = st.radio(
        "Escolha a visualização:",
        options=("Data e hora (por hora)", "Por dia"),
        index=0,
        horizontal=True,
    )

    df_local = _prepare_datetime(base_filtrada)

    if viz == "Data e hora (por hora)":
        fig = chart_por_hora(df_local)
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Se preferir empilhado, troque para "stack"
        barmode = "group"
        fig = chart_por_dia(df_local, barmode=barmode)
        st.plotly_chart(fig, use_container_width=True)


def app_funcao_objetos(base_filtrada):
    if "imagem_objetos" not in base_filtrada.columns:
        st.warning("Coluna 'imagem_objetos' não encontrada no DataFrame.")
        return

    # 1) Normalização e split por "/"
    objetos_series = (
        base_filtrada["imagem_objetos"]
        .fillna("")
        .astype(str)
        .apply(lambda s: [
            t.strip().lower()
            for t in s.split("/")
            if t and t.strip().lower() not in ("", "none", "null")
        ])
    )

    # 2) Explode e contagem
    objetos_explodido = objetos_series.explode().dropna()
    if objetos_explodido.empty:
        st.info("Sem objetos para exibir.")
        return

    contagem = objetos_explodido.value_counts().reset_index()
    contagem.columns = ["objeto", "count"]

    # 3) Top 10 (+ % opcional)
    top10 = contagem.head(10).copy()
    total_ocorrencias = int(objetos_explodido.shape[0])
    top10["percent"] = (top10["count"] / total_ocorrencias) * 100

    # Inicial maiúscula (apenas display). Use .str.title() se quiser cada palavra capitalizada.
    top10["objeto_fmt"] = top10["objeto"].astype(str).str.strip().str.capitalize()

    # 4) Gráfico (sem watermark)
    top10 = top10.sort_values("count", ascending=True)
    fig = px.bar(
        top10,
        x="count",
        y="objeto_fmt",
        orientation="h",
        text=top10.apply(lambda r: f"{r['count']} ({r['percent']:.1f}%)", axis=1),
        labels={"count": "Quantidade", "objeto_fmt": "Objeto"},
        title="Top 10 objetos detectados na imagem",
        color_discrete_sequence=["#213ac7"],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=top10["objeto_fmt"])

    # estilo limpo (fundo transparente e sem grade)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title="Quantidade")
    fig.update_yaxes(showgrid=False, zeroline=False, title="Objeto")

    st.plotly_chart(fig, use_container_width=True)

def app_funcao_hashtags(base_filtrada):

    if "legenda_hashtags" not in base_filtrada.columns:
        st.warning("Coluna 'legenda_hashtags' não encontrada no DataFrame.")
        return

    def _split_hashtags(val):
        # None / NaN
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return []

        # Se for lista, normaliza item a item
        if isinstance(val, list):
            items = val
        else:
            # Trata como string; separa por espaços, vírgulas, ponto-e-vírgula, '/', '|' e quebras de linha
            s = str(val).strip()
            if s == "" or s.lower() in ("none", "null"):
                return []
            items = re.split(r"[,\s;/|]+", s)

        # Normaliza: remove '#' duplicado, espaços, caixa-baixa
        norm = []
        for it in items:
            tag = str(it).strip()
            if not tag:
                continue
            tag = tag.lstrip("#").strip()   # remove '#' à esquerda
            if not tag:
                continue
            tag = tag.lower()
            norm.append(tag)
        return norm

    # Série de listas → explode
    series = base_filtrada["legenda_hashtags"].apply(_split_hashtags)
    exploded = series.explode().dropna()

    if exploded.empty:
        st.info("Sem hashtags para exibir.")
        return

    # Contagem e Top 20
    contagem = exploded.value_counts().reset_index()
    contagem.columns = ["hashtag", "count"]

    top20 = contagem.head(20).copy()
    total = int(exploded.shape[0])
    top20["percent"] = (top20["count"] / max(total, 1)) * 100

    # Rótulo exibido com '#'
    top20["hashtag_fmt"] = "#" + top20["hashtag"].astype(str)

    # Gráfico: barras horizontais, azul, sem fundo/grade
    top20 = top20.sort_values("count", ascending=True)
    fig = px.bar(
        top20,
        x="count",
        y="hashtag_fmt",
        orientation="h",
        text=top20.apply(lambda r: f"{r['count']} ({r['percent']:.1f}%)", axis=1),
        labels={"count": "Quantidade", "hashtag_fmt": "Hashtag"},
        title="Top 20 hashtags (hashtags na legenda)",
        color_discrete_sequence=["#213ac7"],
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=top20["hashtag_fmt"])

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title="Quantidade")
    fig.update_yaxes(showgrid=False, zeroline=False, title="Hashtag")

    st.plotly_chart(fig, use_container_width=True)



def app_funcao_cor_predominantes_dia(base_filtrada: pd.DataFrame, tz: str = "America/Sao_Paulo"):
    """
    Cores dominantes por dia (composição %), ordenadas do maior para o menor.
    - Consolida categorias e sinônimos/variações:
      azul, multicolored, verde, amarelo, bege, branco, preto, unknown, rosa,
      vermelho, marrom, laranja, cinza, floral, multicolor, colorido, multi,
      multicolorido, roxo, pink, multi_colorido...
    - 'não identificado' aparece com hatch (textura) no gráfico.
    Requer colunas: 'post_date' (UTC/ISO) e 'imagem_cor_dominante'.
    """

    req = {"post_date", "imagem_cor_dominante"}
    if not req.issubset(base_filtrada.columns):
        st.warning(f"Faltam colunas: {sorted(req - set(base_filtrada.columns))}")
        return

    # ---------- helpers ----------
    FINAL_CLASSES = {
        "amarelo","azul","verde","vermelho","rosa","roxo",
        "laranja","marrom","cinza","branco","bege","multicolorida"
    }

    # mapa de sinônimos/variações -> classe final
    NORMALIZA = {
        # multicoloridos e variações
        "multicolored": "multicolorida",
        "multicolor": "multicolorida",
        "multicolorido": "multicolorida",
        "multi": "multicolorida",
        "multi colorido": "multicolorida",
        "multi_colorido": "multicolorida",
        "colorido": "multicolorida",

        # inglês -> pt
        "blue": "azul", "yellow": "amarelo", "black": "preto", "white": "branco",
        "green": "verde", "red": "vermelho", "pink": "rosa", "purple": "roxo",
        "orange": "laranja", "brown": "marrom", "gray": "cinza", "grey": "cinza",

        # outros rótulos frequentes
        "unknown": "não identificado",
        "floral": "multicolorida",   # padrão/estampa → trata como multicolorida
    }

    COLOR_MAP = {
        "amarelo"      : "#FFD23F",
        "azul"         : "#1f77b4",
        "verde"        : "#2ca02c",
        "vermelho"     : "#d62728",
        "rosa"         : "#e377c2",
        "roxo"         : "#9467bd",
        "laranja"      : "#ff7f0e",
        "marrom"       : "#8c564b",
        "cinza"        : "#7f7f7f",
        "branco"       : "#e5e5e5",
        "bege"         : "#D2B48C",
        "multicolorida": "#17becf",
        "não identificado": "#000000",
    }

    def _norm_text(s: str) -> str:
        s = (s or "").lower().replace("_", " ").strip()
        s = "".join(ch for ch in unicodedata.normalize("NFD", s) if not unicodedata.combining(ch))
        return s

    def _consolida_cor(raw: str) -> str:
        x = _norm_text(raw)
        if x in ("", "none", "null"):
            return "não identificado"
        if x in NORMALIZA:
            return NORMALIZA[x]
        if x in FINAL_CLASSES:
            return x
        if x.startswith("multi"):
            return "multicolorida"
        return "não identificado"

    # ---------- preparar dados ----------
    df = base_filtrada.copy()
    df["post_date"] = pd.to_datetime(df["post_date"], errors="coerce", utc=True)
    df = df.dropna(subset=["post_date"])
    df["post_date_local"] = df["post_date"].dt.tz_convert(tz)
    df["dia"] = df["post_date_local"].dt.floor("D")

    df["cor_cat"] = df["imagem_cor_dominante"].astype(str).apply(_consolida_cor)

    if df["cor_cat"].eq("não identificado").all():
        st.info("Todas as cores foram classificadas como 'não identificado'. Verifique os rótulos de origem.")
        return

    # ---------- agregação e % por dia ----------
    g = df.groupby(["dia", "cor_cat"]).size().reset_index(name="count")
    g["percent"] = g["count"] / g.groupby("dia")["count"].transform("sum") * 100
    g["padrao"] = g["cor_cat"].map(lambda c: "desconhecida" if c == "não identificado" else "normal")

    # ---------- ORDENAR DO MAIOR PARA O MENOR ----------
    # calculamos o percentual médio global por cor para definir a ordem
    ordem_global = (
        g.groupby("cor_cat")["percent"]
         .mean()
         .sort_values(ascending=False)
         .index.tolist()
    )

    # Garantir que todas as cores do COLOR_MAP apareçam no final se inexistentes
    for cor in COLOR_MAP.keys():
        if cor not in ordem_global:
            ordem_global.append(cor)

    # Reordena o DataFrame por dia e percent (desc) só para consistência visual interna
    g = g.sort_values(["dia", "percent"], ascending=[True, False])

    # ---------- gráfico ----------
    fig = px.bar(
        g,
        x="dia",
        y="percent",
        color="cor_cat",
        barmode="stack",
        labels={"dia": "Dia", "percent": "% do dia", "cor_cat": "Cor"},
        title="Cores predominantes por dia (composição %)",
        color_discrete_map=COLOR_MAP,
        category_orders={"cor_cat": ordem_global},  # <- ordena do maior para menor
        pattern_shape="padrao",
        pattern_shape_map={"normal": "", "desconhecida": "x"},
    )

    # estilo
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        legend_title_text=None,
        showlegend=True,
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False, tickformat=".0f", range=[0, 100])

    st.plotly_chart(fig, use_container_width=True)






def _norm_txt(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower()
    # remove acentos
    s = "".join(ch for ch in unicodedata.normalize("NFD", s) if not unicodedata.combining(ch))
    return s

def _parse_emocoes(val):
    """Aceita None, lista, ou string estilo '[alegria, urgencia]' e retorna lista normalizada."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return []

    # já é lista?
    if isinstance(val, list):
        items = val
    else:
        s = str(val).strip()
        if s in ("", "none", "null"):
            return []
        # tenta JSON
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                items = parsed
            elif isinstance(parsed, str):
                items = [parsed]
            else:
                # cai no split manual
                items = re.split(r"[,\;/|]+", s.strip("[]"))
        except Exception:
            # split manual
            items = re.split(r"[,\;/|]+", s.strip("[]"))

    # normalização + mapa de equivalências (ex.: 'urgencia' -> 'urgência')
    MAP = {
        "urgencia": "urgência",
        "exclusividade": "exclusividade",
        "entusiasmo": "entusiasmo",
        "alegria": "alegria",
        "ansiedade": "ansiedade",
        "medo": "medo",
        "tristeza": "tristeza",
        "raiva": "raiva",
        "surpresa": "surpresa",
        # adicione outros se aparecerem
    }

    out = []
    for it in items:
        t = _norm_txt(it)
        if not t:
            continue
        # remove aspas remanescentes
        t = t.strip("'\" ")
        # aplica mapa (com acento “bonitinho” quando conhecido)
        out.append(MAP.get(t, t))
    return out

def app_funcao_emocoes_legenda(base_filtrada: pd.DataFrame, top_n: int = 10):
    """
    Gera um Top N de emoções (contagem e % ao lado), a partir de df['legenda_sentimento_emocoes'].
    """
    col = "legenda_sentimento_emocoes"
    if col not in base_filtrada.columns:
        st.warning(f"Coluna '{col}' não encontrada.")
        return

    # Série de listas
    series = base_filtrada[col].apply(_parse_emocoes)
    exploded = series.explode().dropna()

    if exploded.empty:
        st.info("Sem emoções para exibir.")
        return

    # contagem e % sobre o total de ocorrências (cada emoção em cada post conta 1)
    contagem = exploded.value_counts().reset_index()
    contagem.columns = ["emocao", "count"]
    total_ocorr = int(exploded.shape[0])
    contagem["percent"] = contagem["count"] / max(1, total_ocorr) * 100

    top = contagem.head(top_n).copy()
    # rótulo bonito (primeira letra maiúscula) — apenas display
    top["emocao_fmt"] = top["emocao"].astype(str).str.strip().str.capitalize()

    # barras horizontais (amarelo → azul)
    top = top.sort_values("count", ascending=True)
    fig = px.bar(
        top,
        x="count",
        y="emocao_fmt",
        orientation="h",
        text=top.apply(lambda r: f"{r['count']} ({r['percent']:.1f}%)", axis=1),
        labels={"count": "Quantidade", "emocao_fmt": "Emoção"},
        title=f"Top emoções na legenda",
        color_discrete_sequence=["#213ac7"]
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=top["emocao_fmt"])

    # estilo limpo
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title="Quantidade")
    fig.update_yaxes(showgrid=False, zeroline=False, title="Emoção")

    st.plotly_chart(fig, use_container_width=True)




def app_funcao_nuvem_palavras(
    base_filtrada: pd.DataFrame,
    min_publicacoes_default: int = 3,
    stopwords_extra: set[str] | None = None,
):
    """
    Nuvem de palavras do caption com:
      - limpeza (URLs, #/@, emojis, pontuação)
      - stopwords PT + extras
      - filtro: mínimo de publicações (DF)
      - filtro manual: palavras para remover
      - colormap YlGnBu (amarelo→azul) e fundo transparente
    """
    if "caption" not in base_filtrada.columns:
        st.warning("Coluna 'caption' não encontrada.")
        return

    # ============================
    # Filtros lado a lado (UI)
    # ============================
    col1, col2 = st.columns(2)
    with col1:
        min_posts = st.slider(
            "**Mínimo de publicações por palavra**",
            min_value=1, max_value=50, value=min_publicacoes_default, step=1
        )
    with col2:
        manual_raw = st.text_input(
            "**Remover palavras manualmente (sep.: farmrio, roupa, ; ou |)**",
            value=""
        )

    # ============================
    # Limpeza e tokenização
    # ============================
    URL_RE   = re.compile(r"https?://\S+|www\.\S+", re.I)
    EMOJI_RE = re.compile(r"[\U00010000-\U0010FFFF]", flags=re.UNICODE)
    # mantém letras acentuadas e dígitos; remove o resto
    PUNCT_RE = re.compile(r"[^\w\sáàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ]", re.UNICODE)
    TOK_RE   = re.compile(r"\b[\wáàâãéèêíïóôõöúçñ]{2,}\b", re.UNICODE)

    def clean_text(t: str) -> str:
        t = str(t or "")
        t = URL_RE.sub(" ", t)
        t = re.sub(r"[#@]", " ", t)
        t = EMOJI_RE.sub(" ", t)
        t = PUNCT_RE.sub(" ", t)
        t = re.sub(r"\s+", " ", t).strip().lower()
        return t

    PT_STOP = {
        "a","o","as","os","um","uma","uns","umas","de","da","do","das","dos",
        "e","é","em","no","na","nos","nas","para","pra","pro","por","com","sem",
        "que","se","são","ser","foi","era","sua","seu","suas","seus","meu","minha",
        "meus","minhas","teu","tua","teus","tuas","nosso","nossa","nossos","nossas",
        "isso","isto","aquele","aquela","aquilo","esse","essa","estes","estas",
        "já","hoje","amanhã","ontem","mais","menos","muito","muita","muitos","muitas",
        "pouco","pouca","poucos","poucas","quando","onde","como","também","tbm",
        "q","d","la","lá","aí","ai","porque","porquê","ne","num","tá","to","tô",
        "tem","têm","ter","cada","entre","sobre","até","ou","seja"
    }
    if stopwords_extra:
        PT_STOP |= {str(x).lower() for x in stopwords_extra}

    # Stopwords manuais digitadas (mesma limpeza/tokenização para casar com os tokens)
    manual_tokens = set(TOK_RE.findall(clean_text(manual_raw)))
    PT_STOP |= manual_tokens

    def tokens_from_caption(t: str) -> list[str]:
        t = clean_text(t)
        return [tok for tok in TOK_RE.findall(t) if tok not in PT_STOP]

    captions = base_filtrada["caption"].astype(str).fillna("")
    docs_tokens = captions.map(tokens_from_caption)

    # ============================
    # DF (nº de publicações) e TF
    # ============================
    doc_freq = Counter()
    term_freq = Counter()
    for toks in docs_tokens:
        doc_freq.update(set(toks))  # aparece em quantos posts
        term_freq.update(toks)      # total de ocorrências

    kept = {w for w, c in doc_freq.items() if c >= min_posts}
    freqs = {w: term_freq[w] for w in kept}

    st.caption(f"{len(kept)} termos após filtros • stopwords manuais: {', '.join(sorted(manual_tokens)) or '—'}")

    if not freqs:
        st.info("Nenhuma palavra passou o filtro. Ajuste o mínimo ou as remoções manuais.")
        return

    
    wc = WordCloud(
        width=1200, height=450,
        background_color=None, mode="RGBA",     # fundo transparente
        colormap="YlGnBu",                      # amarelo → azul
        prefer_horizontal=0.9,
        min_font_size=10,
        max_words=400
    ).generate_from_frequencies(freqs)

    fig, ax = plt.subplots(figsize=(12, 4), dpi=120)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig, clear_figure=True)


AZUL = "#213ac7"

# ----------------- helpers -----------------
def _split_por_barra(val):
    """Divide por '/', trata None/NaN/'none'/'null' como ['Desconhecido'].
       Aceita também lista (cada item pode conter '/')."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ["Desconhecido"]
    if isinstance(val, list):
        tokens = []
        for v in val:
            if v is None: 
                continue
            for t in str(v).split("/"):
                t = t.strip()
                if t:
                    tokens.append(t)
        return tokens if tokens else ["Desconhecido"]
    s = str(val).strip()
    if s == "" or s.lower() in {"none", "null", "[]"}:
        return ["Desconhecido"]
    parts = [t.strip() for t in s.split("/") if t.strip() != ""]
    return parts if parts else ["Desconhecido"]

def _contagem_categorias(df: pd.DataFrame, col: str, dedup_por_post: bool = True) -> pd.DataFrame:
    """Retorna DataFrame com ['categoria','count'] ordenado desc."""
    if col not in df.columns:
        return pd.DataFrame(columns=["categoria", "count"])
    # lista de listas
    serie = df[col].apply(_split_por_barra)
    if dedup_por_post:
        serie = serie.apply(lambda lst: sorted(set(lst)))
    expl = serie.explode().dropna()
    if expl.empty:
        return pd.DataFrame(columns=["categoria", "count"])
    cont = expl.value_counts().reset_index()
    cont.columns = ["categoria", "count"]
    return cont

def _plot_barh_counts(cont: pd.DataFrame, titulo: str, ylab: str):
    """Barras horizontais, azul sólido, rótulo fora, fundo transparente."""
    if cont.empty:
        st.info(f"Sem dados para **{titulo}**.")
        return
    # display: capitaliza e troca '_' por espaço; mantém "Desconhecido"
    cont = cont.copy()
    cont["categoria_fmt"] = cont["categoria"].astype(str).apply(
        lambda x: "Desconhecido" if x.strip().lower()=="desconhecido"
        else x.replace("_"," ").strip().capitalize()
    )
    # ordena para barras horizontais
    cont = cont.sort_values("count", ascending=True)
    fig = px.bar(
        cont, x="count", y="categoria_fmt", orientation="h",
        text=cont["count"].map(str),
        labels={"count":"Quantidade", "categoria_fmt": ylab},
        title=titulo,
        color_discrete_sequence=[AZUL],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=cont["categoria_fmt"])
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title="Quantidade")
    fig.update_yaxes(showgrid=False, zeroline=False, title=ylab)
    st.plotly_chart(fig, use_container_width=True)

# ----------------- 6 visualizações -----------------
def grafico_topicos_imagem(df: pd.DataFrame, top_n: int | None = None):
    cont = _contagem_categorias(df, "imagem_topicos")
    if top_n: cont = cont.head(top_n)
    _plot_barh_counts(cont, "Tópicos associados à Imagem", "Tópico (imagem)")

def grafico_gatilhos_imagem(df: pd.DataFrame, top_n: int | None = None):
    cont = _contagem_categorias(df, "imagem_gatilhos")
    if top_n: cont = cont.head(top_n)
    _plot_barh_counts(cont, "Gatilhos utilizados na Imagem", "Gatilho (imagem)")

def grafico_ctas_imagem(df: pd.DataFrame, top_n: int | None = None):
    cont = _contagem_categorias(df, "imagem_cta_tipo")
    if top_n: cont = cont.head(top_n)
    _plot_barh_counts(cont, "CTAs utilizados na Imagem", "CTA (imagem)")

def grafico_topicos_legenda(df: pd.DataFrame, top_n: int | None = None):
    cont = _contagem_categorias(df, "legenda_topicos")
    if top_n: cont = cont.head(top_n)
    _plot_barh_counts(cont, "Tópicos associados à Legenda", "Tópico (legenda)")

def grafico_gatilhos_legenda(df: pd.DataFrame, top_n: int | None = None):
    cont = _contagem_categorias(df, "legenda_gatilhos")
    if top_n: cont = cont.head(top_n)
    _plot_barh_counts(cont, "Gatilhos utilizados na Legenda", "Gatilho (legenda)")

def grafico_ctas_legenda(df: pd.DataFrame, top_n: int | None = None):
    cont = _contagem_categorias(df, "legenda_cta")
    if top_n: cont = cont.head(top_n)
    _plot_barh_counts(cont, "CTAs utilizados na Legenda", "CTA (legenda)")






# lista oficial de colunas (booleanas/0-1/strings "true"/"1")
CONTEXT_FARM_COLS = [
    "imagem_contexto_farm_cabide_visivel",
    "imagem_contexto_farm_arara_visivel",
    "imagem_contexto_farm_steamer_visivel",
    "imagem_contexto_farm_modo_retrato",
    "imagem_contexto_farm_provador_lotado",
    "imagem_contexto_farm_reflexo_espelho",
    "imagem_contexto_farm_interior_loja",
    "imagem_contexto_farm_foco_look",
    "imagem_contexto_farm_foco_acessorio",
    "imagem_contexto_farm_foco_textura",
    "imagem_contexto_farm_roupas_dobradas",
    "imagem_contexto_farm_cortina_visivel",
    "imagem_contexto_farm_manequim_visivel",
    "imagem_contexto_farm_etiqueta_preco_visivel",
    "imagem_contexto_farm_sacola_visivel",
    "imagem_contexto_farm_selfie_no_espelho",
    "imagem_contexto_farm_logo_marca_visivel",
]

def _series_to_bool(s: pd.Series) -> pd.Series:
    """Converte uma série (bool, numérica, string) para booleano.
    True se valor booleano True, numérico > 0, ou string em {'true','1','sim','yes','y','verdadeiro'}.
    NaN/None/vazio viram False.
    """
    if s.dtype == bool:
        return s.fillna(False)

    # tenta numérico (>0)
    s_str = s.astype(str).str.strip().str.lower()
    num = pd.to_numeric(s_str, errors="coerce")
    mask_num = num.fillna(0) > 0

    # strings verdadeiras
    truthy = {"true", "1", "sim", "yes", "y", "verdadeiro"}
    mask_str = s_str.isin(truthy)

    return (mask_num | mask_str).fillna(False)

def _fmt_label(col: str) -> str:
    """Torna o rótulo legível."""
    base = col.replace("imagem_contexto_farm_", "").replace("_", " ").strip()
    return base.capitalize()

def etapa_filtro_contexto_farm(base_filtrada: pd.DataFrame):
    st.subheader("🎛️ Filtro por Contexto FARM")

    # apenas colunas disponíveis no DF
    available = [c for c in CONTEXT_FARM_COLS if c in base_filtrada.columns]
    if not available:
        st.warning("Nenhuma coluna de contexto FARM encontrada no DataFrame.")
        return base_filtrada

    # multiselect com labels amigáveis
    label_map = {c: _fmt_label(c) for c in available}
    inv_label_map = {v: k for k, v in label_map.items()}

    selected_labels = st.multiselect(
        "Selecione os sinais (o post deve conter **todos**):",
        options=[label_map[c] for c in available],
        default=[],
    )
    selected_cols = [inv_label_map[lbl] for lbl in selected_labels]

    # aplica filtro (AND entre as colunas selecionadas)
    if selected_cols:
        mask_all = pd.Series(True, index=base_filtrada.index)
        for col in selected_cols:
            mask_all &= _series_to_bool(base_filtrada[col])
        df_filtrado = base_filtrada.loc[mask_all].copy()
    else:
        df_filtrado = base_filtrada.copy()

    # resultado (por enquanto: apenas quantidade)
    st.metric("Quantidade de publicações (filtradas)", len(df_filtrado))

    return df_filtrado



import pandas as pd
import streamlit as st
from html import escape

def _is_http_url(x: str) -> bool:
    try:
        return isinstance(x, str) and x.startswith(("http://", "https://"))
    except Exception:
        return False

def mosaico_imagens(
    df: pd.DataFrame,
    thumb_col: str = "thumbnail",
    tz: str = "America/Sao_Paulo",
    key: str = "mosaico_main",
    ordenar: str = "Mais recentes",      # "Mais recentes" | "Mais antigos" | "Sem ordenação"
    mostrar_legenda: bool = True,         # usa a coluna 'caption'
    abrir_nova_aba: bool = True,
    colunas: int = 5,                     # nº de colunas no mosaico
    por_pagina: int = 40,                 # nº máx de imagens por página
    proporcao: str = "1 / 1",             # aspect-ratio opcional apenas p/ placeholder
):
    st.subheader("🧩 Mosaico de Imagens")

    if thumb_col not in df.columns:
        st.warning(f"Coluna '{thumb_col}' não encontrada.")
        return

    data = df.copy()

    # Datas (mantidas caso queira ordenar por data)
    if "post_date" in data.columns:
        data["post_date"] = pd.to_datetime(data["post_date"], errors="coerce", utc=True)
        try:
            data["post_date_local"] = data["post_date"].dt.tz_convert(tz)
        except Exception:
            data["post_date_local"] = data["post_date"]
    # Apenas URLs válidas e únicas
    data = (
        data[data[thumb_col].apply(_is_http_url)]
        .drop_duplicates(subset=[thumb_col])
        .reset_index(drop=True)
    )
    if data.empty:
        st.info("Nenhuma imagem válida para exibir.")
        return

    # Ordenação
    if ordenar != "Sem ordenação" and "post_date" in data.columns:
        data = data.sort_values("post_date", ascending=(ordenar == "Mais antigos"))

    # Controles
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.0, 1.0])
    with c1:
        ord_sel = st.selectbox(
            "Ordenar por",
            ["Mais recentes", "Mais antigos", "Sem ordenação"],
            index=["Mais recentes","Mais antigos","Sem ordenação"].index(ordenar),
            key=f"{key}_order",
        )
    with c2:
        mostrar_legenda = st.checkbox("Mostrar legendas (caption)", value=mostrar_legenda, key=f"{key}_legend")
    with c3:
        colunas = st.number_input("Colunas", 2, 10, value=colunas, step=1, key=f"{key}_cols")
    with c4:
        por_pagina = st.number_input("Por página", 10, 200, value=por_pagina, step=10, key=f"{key}_pp")

    if ord_sel != ordenar:
        st.session_state.pop(f"{key}_page", None)
        st.rerun()

    total = len(data)
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
    page = st.session_state.get(f"{key}_page", 1)
    page = st.number_input("Página", 1, total_paginas, value=page, step=1, key=f"{key}_page")

    ini = (page - 1) * por_pagina
    fim = min(ini + por_pagina, total)
    page_df = data.iloc[ini:fim].reset_index(drop=True)

    # CSS mínimo para garantir legenda alinhada à esquerda e espaçamento
    st.markdown(
        f"""
        <style>
        .mosaic-caption-left-{key} {{
            text-align: left;
            margin-top: 6px;
            font-size: 0.92rem;
            line-height: 1.3rem;
        }}
        .mosaic-tile-{key} {{
            width: 100%;
        }}
        .mosaic-tile-{key} .placeholder {{
            aspect-ratio: {proporcao};
            width: 100%;
            background: #f2f2f2;
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Render do mosaico
    rows = (len(page_df) + colunas - 1) // colunas
    for r in range(rows):
        cols = st.columns(colunas)
        for c in range(colunas):
            i = r * colunas + c
            if i >= len(page_df):
                break
            row = page_df.iloc[i]
            url = str(row[thumb_col])
            cap = (row.get("caption") or "").strip() if mostrar_legenda else ""

            with cols[c]:
                # Imagem
                if abrir_nova_aba:
                    # link clicável que abre em nova aba
                    st.markdown(
                        f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">',
                        unsafe_allow_html=True,
                    )
                    st.image(url, use_container_width=True)
                    st.markdown("</a>", unsafe_allow_html=True)
                else:
                    st.image(url, use_container_width=True)

                # Legenda embaixo, alinhada à esquerda
                if cap:
                    st.markdown(f'<div class="mosaic-caption-left-{key}">{escape(cap)}</div>', unsafe_allow_html=True)

    st.caption(f"Mostrando {ini+1}–{fim} de {total} imagens • Página {page}/{total_paginas}")