import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Analizador Financiero Avanzado",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stAlert {
        border-radius: 10px;
    }
    .metric-box {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .section-title {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
    }
    .comparison-header {
        background-color: #3498db;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("📈 Analizador Financiero Comparativo")

# Sidebar para entrada de datos
with st.sidebar:
    st.header("🔍 Configuración del Análisis")
    
    # Entrada de los tickers
    ticker1 = st.text_input("Empresa principal (Ej: NVDA, AAPL):", "NVDA").upper()
    ticker2 = st.text_input("Empresa a comparar (Ej: AMD, INTC):", "").upper()
    
    # Validación de los tickers
    def validate_ticker(ticker):
        try:
            data = yf.Ticker(ticker)
            info = data.info
            return bool(info)
        except Exception:
            return False
    
    if not validate_ticker(ticker1):
        st.error(f"⚠️ Ticker {ticker1} inválido, por favor revise")
        st.stop()
    
    if ticker2 and not validate_ticker(ticker2):
        st.error(f"⚠️ Ticker {ticker2} inválido, por favor revise")
        st.stop()
    
    st.success(f"✅ Datos válidos para {ticker1}" + (f" y {ticker2}" if ticker2 else ""))
    st.markdown("---")
    
    # Selector de período
    period = st.selectbox(
        "Período histórico:",
        ["1y", "3y", "5y", "10y"],
        index=2
    )
    
    st.markdown("---")
    st.markdown("**📊 Visualización:**")
    chart_type = st.radio(
        "Tipo de gráfico:",
        ["Línea", "Velas"],
        index=0,
        horizontal=True
    )
    
    st.markdown("---")
    st.markdown("**💾 Exportar Datos**")
    if st.button("Generar Reporte PDF (Demo)"):
        st.info("Función de exportación en desarrollo")

# Función para obtener datos con caché
@st.cache_data(ttl=3600)
def get_stock_data(ticker, period):
    try:
        data = yf.download(ticker, period=f"{period}")
        return data
    except Exception as e:
        st.error(f"Error al obtener datos para {ticker}: {e}")
        return None

# Obtener datos para ambas empresas
ticker1_data = get_stock_data(ticker1, period)
ticker1_info = yf.Ticker(ticker1).info

if ticker2:
    ticker2_data = get_stock_data(ticker2, period)
    ticker2_info = yf.Ticker(ticker2).info

# Verificar columnas disponibles
def get_price_column(data):
    available_columns = data.columns.tolist()
    return 'Adj Close' if 'Adj Close' in available_columns else 'Close'

if ticker1_data is None or ticker1_data.empty:
    st.error(f"No se pudieron obtener datos para {ticker1}")
    st.stop()

price_col1 = get_price_column(ticker1_data)

if ticker2 and (ticker2_data is None or ticker2_data.empty):
    st.warning(f"No se pudieron obtener datos para {ticker2}")
    ticker2 = None  # Desactivar comparación si hay errores

# Información de las empresas
st.header("🏢 Información de las Empresas")
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"{ticker1_info.get('shortName', ticker1)}")
    st.markdown(f"**Sector:** {ticker1_info.get('sector', 'No disponible')}")
    st.markdown(f"**Industria:** {ticker1_info.get('industry', 'No disponible')}")
    st.markdown(f"**País:** {ticker1_info.get('country', 'No disponible')}")
    st.markdown("---")
    st.write(ticker1_info.get('longBusinessSummary', 'Descripción no disponible.'))

with col2:
    if ticker2:
        st.subheader(f"{ticker2_info.get('shortName', ticker2)}")
        st.markdown(f"**Sector:** {ticker2_info.get('sector', 'No disponible')}")
        st.markdown(f"**Industria:** {ticker2_info.get('industry', 'No disponible')}")
        st.markdown(f"**País:** {ticker2_info.get('country', 'No disponible')}")
        st.markdown("---")
        st.write(ticker2_info.get('longBusinessSummary', 'Descripción no disponible.'))
    else:
        st.info("Ingrese una segunda empresa para comparar")

# Datos clave comparativos
st.header("📊 Comparación de Métricas Clave")
metrics_cols = st.columns(2)

with metrics_cols[0]:
    st.markdown(f"<div class='comparison-header'>{ticker1}</div>", unsafe_allow_html=True)
    
    current_price = ticker1_info.get('currentPrice', ticker1_info.get('regularMarketPrice'))
    prev_close = ticker1_info.get('previousClose')
    if current_price and prev_close:
        change = ((current_price - prev_close) / prev_close) * 100
        st.metric("Precio Actual", 
                 f"${current_price:.2f}", 
                 f"{change:.2f}%")
    
    st.metric("Capitalización", 
             f"${ticker1_info.get('marketCap', 0)/1e9:.2f}B" if ticker1_info.get('marketCap') else "N/D")
    st.metric("P/E Ratio", 
             f"{ticker1_info.get('trailingPE', 'N/D')}")
    st.metric("Dividend Yield", 
             f"{ticker1_info.get('dividendYield', 0)*100:.2f}%" if ticker1_info.get('dividendYield') else "N/D")

with metrics_cols[1]:
    if ticker2:
        st.markdown(f"<div class='comparison-header'>{ticker2}</div>", unsafe_allow_html=True)
        
        current_price2 = ticker2_info.get('currentPrice', ticker2_info.get('regularMarketPrice'))
        prev_close2 = ticker2_info.get('previousClose')
        if current_price2 and prev_close2:
            change2 = ((current_price2 - prev_close2) / prev_close2) * 100
            st.metric("Precio Actual", 
                     f"${current_price2:.2f}", 
                     f"{change2:.2f}%")
        
        st.metric("Capitalización", 
                 f"${ticker2_info.get('marketCap', 0)/1e9:.2f}B" if ticker2_info.get('marketCap') else "N/D")
        st.metric("P/E Ratio", 
                 f"{ticker2_info.get('trailingPE', 'N/D')}")
        st.metric("Dividend Yield", 
                 f"{ticker2_info.get('dividendYield', 0)*100:.2f}%" if ticker2_info.get('dividendYield') else "N/D")
    else:
        st.info("Ingrese una segunda empresa para ver comparación")

# Gráfico comparativo de precios
st.header("📈 Comparación de Precios Históricos")

if chart_type == "Línea":
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ticker1_data.index, 
        y=ticker1_data[price_col1], 
        mode='lines',
        name=ticker1,
        line=dict(color='#3498db', width=2)
    ))
    
    if ticker2:
        price_col2 = get_price_column(ticker2_data)
        fig.add_trace(go.Scatter(
            x=ticker2_data.index, 
            y=ticker2_data[price_col2], 
            mode='lines',
            name=ticker2,
            line=dict(color='#e74c3c', width=2)
        ))
else:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=ticker1_data.index,
        open=ticker1_data['Open'],
        high=ticker1_data['High'],
        low=ticker1_data['Low'],
        close=ticker1_data['Close'],
        name=ticker1,
        increasing_line_color='#2ecc71',
        decreasing_line_color='#e74c3c'
    ))

fig.update_layout(
    title=f"Comparación de precios históricos - {ticker1}" + (f" vs {ticker2}" if ticker2 else ""),
    xaxis_title="Fecha",
    yaxis_title="Precio (USD)",
    template="plotly_white",
    hovermode="x unified",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# Cálculo de rendimientos comparativos
st.header("📊 Rendimientos Anualizados Comparativos")

def calculate_cagr(start_value, end_value, years):
    return (end_value / start_value) ** (1/years) - 1

periods = {
    "1 año": "1y",
    "3 años": "3y",
    "5 años": "5y"
}

returns_data = {}
for period_name, period_code in periods.items():
    period_data1 = yf.download(ticker1, period=period_code)
    if not period_data1.empty:
        price_col = get_price_column(period_data1)
        start_price1 = period_data1[price_col].iloc[0]
        end_price1 = period_data1[price_col].iloc[-1]
        years = len(period_data1) / 252
        returns_data[f"{ticker1} {period_name}"] = calculate_cagr(start_price1, end_price1, years) * 100
    
    if ticker2:
        period_data2 = yf.download(ticker2, period=period_code)
        if not period_data2.empty:
            price_col = get_price_column(period_data2)
            start_price2 = period_data2[price_col].iloc[0]
            end_price2 = period_data2[price_col].iloc[-1]
            years = len(period_data2) / 252
            returns_data[f"{ticker2} {period_name}"] = calculate_cagr(start_price2, end_price2, years) * 100

if returns_data:
    returns_df = pd.DataFrame.from_dict(returns_data, orient='index', columns=['Rendimiento'])
    st.table(returns_df.style.format("{:.2f}%"))
    
    st.markdown("""
    <div class="metric-box">
        <h4 class="section-title">📝 Explicación del cálculo</h4>
        <p>El rendimiento anualizado (CAGR) se calcula usando la fórmula:</p>
        <p><code>CAGR = (Valor Final / Valor Inicial)^(1/Número de Años) - 1</code></p>
        <p>Este cálculo considera el precio al inicio y al final del período para determinar 
        el rendimiento compuesto anualizado, que es la mejor medida para comparar inversiones 
        en diferentes períodos de tiempo.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No se pudieron calcular los rendimientos.")

# Cálculo de riesgo comparativo
st.header("⚠️ Comparación de Riesgo")

if not ticker1_data.empty:
    ticker1_data['Daily Return'] = ticker1_data[price_col1].pct_change()
    daily_vol1 = ticker1_data['Daily Return'].std()
    annual_vol1 = daily_vol1 * np.sqrt(252)
    
    risk_cols = st.columns(2)
    
    with risk_cols[0]:
        st.markdown(f"<div class='comparison-header'>{ticker1}</div>", unsafe_allow_html=True)
        st.metric("Volatilidad Diaria", f"{daily_vol1*100:.2f}%")
        st.metric("Volatilidad Anualizada", f"{annual_vol1*100:.2f}%")
    
    if ticker2:
        price_col2 = get_price_column(ticker2_data)
        ticker2_data['Daily Return'] = ticker2_data[price_col2].pct_change()
        daily_vol2 = ticker2_data['Daily Return'].std()
        annual_vol2 = daily_vol2 * np.sqrt(252)
        
        with risk_cols[1]:
            st.markdown(f"<div class='comparison-header'>{ticker2}</div>", unsafe_allow_html=True)
            st.metric("Volatilidad Diaria", f"{daily_vol2*100:.2f}%")
            st.metric("Volatilidad Anualizada", f"{annual_vol2*100:.2f}%")
    
    st.markdown("""
    <div class="metric-box">
        <h4 class="section-title">📝 Explicación del riesgo</h4>
        <p>La volatilidad anualizada representa la desviación estándar de los rendimientos diarios del activo, 
        multiplicada por la raíz cuadrada de 252 (días bursátiles en un año).</p>
        <p>Este valor indica qué tan variable ha sido el precio de la acción históricamente. 
        Valores más altos indican mayor riesgo.</p>
        <p><strong>Interpretación:</strong></p>
        <ul>
            <li>Menos del 15%: Baja volatilidad</li>
            <li>15%-30%: Volatilidad moderada</li>
            <li>Más del 30%: Alta volatilidad</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Gráfico de distribución de rendimientos comparativo
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(
        x=ticker1_data['Daily Return'].dropna(),
        nbinsx=50,
        marker_color='#3498db',
        opacity=0.7,
        name=ticker1
    ))
    
    if ticker2:
        fig_dist.add_trace(go.Histogram(
            x=ticker2_data['Daily Return'].dropna(),
            nbinsx=50,
            marker_color='#e74c3c',
            opacity=0.7,
            name=ticker2
        ))
    
    fig_dist.update_layout(
        title="Distribución Comparativa de Rendimientos Diarios",
        xaxis_title="Rendimiento Diario",
        yaxis_title="Frecuencia",
        template="plotly_white",
        barmode='overlay'
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)
else:
    st.warning("No hay datos suficientes para calcular la volatilidad.")

# Sección de noticias
st.header("📰 Últimas Noticias")

try:
    news = yf.Ticker(ticker1).news
    if news:
        for item in news[:3]:
            with st.expander(f"{item['title']} - {item['publisher']}"):
                st.write(item.get('summary', 'No hay resumen disponible.'))
                st.markdown(f"[Leer más]({item['link']})")
    else:
        st.info("No hay noticias recientes disponibles.")
except Exception:
    st.warning("No se pudieron cargar las noticias.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9em;">
    <p>Analizador Financiero - Datos proporcionados por Yahoo Finance</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)