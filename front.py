import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
import plotly.express as px

# Import improved modules
import main as m
import database as db

# Set page configuration
st.set_page_config(
    page_title="Lanchonete do Amaro - Análise de Preços",
    page_icon="🥪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
    }
    .section-header {
        font-size: 1.5rem;
        color: #34495e;
        margin-top: 1rem;
    }
    .insight-box {
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .insight-box.warning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .insight-box.success {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .insight-box.info {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
    }
    .chart-title {
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .data-source {
        font-size: 0.8rem;
        color: #6c757d;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# Create database if it doesn't exist
db.create_database()

# App title and introduction
st.markdown('<h1 class="main-header">🥪 Lanchonete do Amaro - Análise de Preços</h1>', unsafe_allow_html=True)

col_intro1, col_intro2 = st.columns([2, 1])
with col_intro1:
    st.markdown("""
    Para a Lanchonete do Amaro, entender como os clientes respondem às mudanças nos 
    preços dos salgados é essencial. Esta análise nos ajuda a encontrar o equilíbrio 
    perfeito entre preços competitivos e lucratividade, mantendo nossos clientes satisfeitos.
    """)
    
with col_intro2:
    # Display current date
    st.info(f"📅 Data da análise: {datetime.now().strftime('%d/%m/%Y')}")

st.markdown("<hr>", unsafe_allow_html=True)

# Section 1: Production Costs
st.markdown('<h2 class="section-header">📊 Custos de Produção do Salgado</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    custo_unidade = st.number_input("Custo dos ingredientes (por unidade): R$", 
                                    min_value=0.01, value=2.50, step=0.01, format="%.2f")
with col2:
    soma_salarios = st.number_input("Custos com funcionários (mensal): R$", 
                                   min_value=1.0, value=2000.0, step=100.0, format="%.2f")
with col3:
    producao_diaria = st.number_input("Produção de salgados por dia:", 
                                     min_value=1, value=100, step=10)
with col4:
    margem_lucro = st.number_input("Margem de lucro desejada (%):", 
                                  min_value=0.0, max_value=500.0, value=30.0, step=5.0, format="%.1f")

# Calculate unit price
preco_unidade = m.preco_unidade(custo_unidade, soma_salarios, producao_diaria)
preco_sugerido = m.preco_final(preco_unidade, margem_lucro)

col_result1, col_result2, col_result3 = st.columns([1, 1, 1])
with col_result1:
    st.metric("Custo por unidade", f"R$ {preco_unidade:.2f}")
with col_result2:
    st.metric("Preço sugerido", f"R$ {preco_sugerido:.2f}")
with col_result3:
    # Profit per unit
    lucro_por_unidade = preco_sugerido - preco_unidade
    st.metric("Lucro por unidade", f"R$ {lucro_por_unidade:.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# Section 2: Pricing and Sales
st.markdown('<h2 class="section-header">🏷️ Definição do Preço de Venda</h2>', unsafe_allow_html=True)

col5, col6 = st.columns(2)
with col5:
    preco_final = st.number_input("Preço de venda do salgado: R$", 
                                 min_value=0.01, value=preco_sugerido, step=0.50, format="%.2f")
    
    # Show comparison with suggested price
    if preco_final < preco_sugerido:
        st.warning(f"⚠️ Preço abaixo do sugerido (R$ {preco_sugerido:.2f})")
    elif preco_final > preco_sugerido:
        st.success(f"💰 Preço acima do sugerido (R$ {preco_sugerido:.2f})")
    else:
        st.info(f"✓ Preço igual ao sugerido")

with col6:
    vendas_por_dia = st.number_input("Quantidade média de salgados vendidos por dia:", 
                                    min_value=1, value=int(producao_diaria * 0.8), step=10)
    vendas_por_mes = vendas_por_dia * 30
    
    # Show comparison with production
    utilizacao = (vendas_por_dia / producao_diaria) * 100
    st.metric("Utilização da capacidade", f"{utilizacao:.1f}%", 
             delta=f"{vendas_por_dia - producao_diaria} unidades/dia")

# Register data button
col_btn1, col_btn2 = st.columns([1, 3])
with col_btn1:
    inserir_dados = st.button("📝 Registrar Dados", use_container_width=True)
    
    if inserir_dados:
        if preco_unidade is not None:
            # Insert data into the database
            db.insert_data(
                data_adicionada=db.get_current_date(),
                precoInicio=preco_unidade,
                precoFinal=preco_final,
                quantidadeInicio=producao_diaria,
                quantidadeFinal=vendas_por_mes,
                elasticidade=None
            )
            st.success("✅ Dados registrados com sucesso!")
        else:
            st.error("❌ Erro: Calcule o preço sugerido antes de inserir os dados.")

st.markdown("<br>", unsafe_allow_html=True)

# Section 3: Elasticity Analysis
st.markdown('<h2 class="section-header">📈 Análise de Elasticidade</h2>', unsafe_allow_html=True)

# Get latest data from the database
latest_data = db.get_latest_data()

col_analise1, col_analise2 = st.columns([1, 3])
with col_analise1:
    calcular_elasticidade = st.button("🔍 Analisar Impacto", use_container_width=True)

if calcular_elasticidade and latest_data:
    preco_inicio, preco_final, quantidade_inicio, quantidade_final, _ = latest_data
    
    # Calculate elasticity
    elasticidade_valor = m.elasticidade(quantidade_inicio, quantidade_final, preco_inicio, preco_final)
    
    # Update elasticity in the database
    if elasticidade_valor is not None:
        db.update_elasticity(elasticidade_valor)
        
        # Get interpretation
        status, mensagem = m.interpret_elasticity(elasticidade_valor)
        
        # Display elasticity value and interpretation
        st.markdown(f"<h3>Elasticidade preço-demanda: {elasticidade_valor:.2f}</h3>", unsafe_allow_html=True)
        st.markdown(f'<div class="insight-box {status}">{mensagem}</div>', unsafe_allow_html=True)
        
        # Visualize elasticity with a gauge chart
        col_gauge1, col_gauge2, col_gauge3 = st.columns([1, 3, 1])
        with col_gauge2:
            # Create a simple gauge visualization using Matplotlib
            fig, ax = plt.subplots(figsize=(10, 2))
            
            # Define gauge range and positions
            gauge_min, gauge_max = -3, 3
            gauge_range = np.linspace(gauge_min, gauge_max, 100)
            
            # Define colors for different sections
            cmap = plt.cm.RdYlGn_r
            colors = cmap(np.linspace(0, 1, len(gauge_range)))
            
            # Create the gauge
            ax.barh(y=0, width=0.6, left=gauge_range, height=0.2, color=colors)
            
            # Add labels
            ax.text(gauge_min, -0.3, "Muito Elástico", ha='center', va='center', fontsize=8)
            ax.text(0, -0.3, "Unitário", ha='center', va='center', fontsize=8)
            ax.text(gauge_max, -0.3, "Inelástico", ha='center', va='center', fontsize=8)
            
            # Set indicator position (constrained to the gauge limits)
            indicator_pos = max(min(elasticidade_valor, gauge_max), gauge_min)
            ax.plot([indicator_pos, indicator_pos], [-0.2, 0.4], 'k', linewidth=2)
            ax.text(indicator_pos, 0.6, f"{elasticidade_valor:.2f}", ha='center', va='center', fontweight='bold')
            
            # Clean up the chart
            ax.set_xlim(gauge_min * 1.1, gauge_max * 1.1)
            ax.set_ylim(-0.5, 1)
            ax.axis('off')
            
            # Display the chart
            st.pyplot(fig)
    else:
        st.error("Não foi possível calcular a elasticidade com os dados fornecidos.")
elif calcular_elasticidade:
    st.warning("Nenhum dado encontrado para calcular elasticidade. Registre os dados primeiro.")

st.markdown("<br>", unsafe_allow_html=True)

# Section 4: Business Performance
st.markdown('<h2 class="section-header">📊 Desempenho do Negócio</h2>', unsafe_allow_html=True)
st.caption("Analise as tendências por período para tomar decisões estratégicas.")

# Time period selection
opcao = st.selectbox(
    "Selecione o período de análise", 
    ("Todos os registros", "Última semana", "Últimos 15 dias", 
     "Último mês", "Últimos 2 meses", "Últimos 3 meses", "Últimos 4 meses")
)

# Map option to number of days
periodo_map = {
    "Todos os registros": None,
    "Última semana": 7,
    "Últimos 15 dias": 15,
    "Último mês": 30,
    "Últimos 2 meses": 60,
    "Últimos 3 meses": 90,
    "Últimos 4 meses": 120
}
num_dias = periodo_map[opcao]

# Get filtered data
dados_filtrados = db.get_filtered_data(num_dias)

# Check if we have data to display
if not dados_filtrados.empty:
    # Convert elasticity to numeric type (in case it was stored as string)
    dados_filtrados['elasticidade'] = pd.to_numeric(dados_filtrados['elasticidade'], errors='coerce')
    
    # Format date column for better display
    dados_filtrados['data_formatada'] = dados_filtrados['data_adicionada'].dt.strftime('%d/%m/%Y')
    
    # Ensure all numeric columns are properly formatted
    numeric_cols = ['precoInicio', 'precoFinal', 'quantidadeInicio', 'quantidadeFinal', 'elasticidade']
    for col in numeric_cols:
        dados_filtrados[col] = pd.to_numeric(dados_filtrados[col], errors='coerce')

    # Calculate profit values for charts
    dados_filtrados['lucro_unitario'] = dados_filtrados['precoFinal'] - dados_filtrados['precoInicio']
    dados_filtrados['lucro_total'] = dados_filtrados['lucro_unitario'] * dados_filtrados['quantidadeFinal']
    dados_filtrados['margem_percentual'] = (dados_filtrados['lucro_unitario'] / dados_filtrados['precoFinal']) * 100

    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Análise de Preços e Vendas", "Elasticidade e Tendências", "Projeções"])

    with tab1:
        # First row of charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown('<p class="chart-title">Evolução do Preço de Venda (R$)</p>', unsafe_allow_html=True)
            
            # Line chart for price evolution
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(dados_filtrados['data_formatada'], dados_filtrados['precoFinal'], 'o-', color='#3498db', linewidth=2)
            ax.fill_between(dados_filtrados['data_formatada'], dados_filtrados['precoFinal'], color='#3498db', alpha=0.3)
            
            # Add line for cost price for comparison
            ax.plot(dados_filtrados['data_formatada'], dados_filtrados['precoInicio'], '--', color='#e74c3c', linewidth=1.5, label='Custo')
            
            # Calculate profit margin area
            ax.fill_between(dados_filtrados['data_formatada'], 
                           dados_filtrados['precoInicio'],
                           dados_filtrados['precoFinal'], 
                           color='#2ecc71', alpha=0.2, label='Margem de Lucro')
            
            # Format the chart
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.legend()
            
            # Show the chart
            st.pyplot(fig)
            
        with col_chart2:
            st.markdown('<p class="chart-title">Quantidade Vendida vs. Produção (unidades/mês)</p>', unsafe_allow_html=True)
            
            # Create bar chart for production vs. sales
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Define bar width and positions
            bar_width = 0.35
            index = np.arange(len(dados_filtrados))

            # Create bars
            bars1 = ax.bar(
                index - bar_width / 2,
                dados_filtrados['quantidadeInicio'],
                bar_width,
                label='Produção',
                color='#3498db',
                alpha=0.7
            )

            bars2 = ax.bar(
                index + bar_width / 2,
                dados_filtrados['quantidadeFinal'],
                bar_width,
                label='Vendas',
                color='#f39c12',
                alpha=0.7
            )
            
            # Calculate utilization rate
            util_rate = dados_filtrados['quantidadeFinal'] / dados_filtrados['quantidadeInicio'] * 100
            
            # Add utilization rate as a line
            ax2 = ax.twinx()
            ax2.plot(index, util_rate, 'r-', linewidth=2, label='Taxa de Utilização (%)')
            ax2.set_ylim(0, 120)
            ax2.set_ylabel('Taxa de Utilização (%)')
            
            # Format the chart
            ax.set_xticks(index)
            ax.set_xticklabels(dados_filtrados['data_formatada'], rotation=45)
            ax.legend(loc='upper left')
            ax2.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        # Second row of charts
        col_chart3, col_chart4 = st.columns(2)
        
        with col_chart3:
            st.markdown('<p class="chart-title">Lucro Projetado por Período (R$)</p>', unsafe_allow_html=True)
            
            # Create bar chart for profit
            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.bar(dados_filtrados['data_formatada'], dados_filtrados['lucro_total'], 
                         color='#2ecc71', alpha=0.7)
            
            # Add data labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 100,
                       f'R$ {height:.0f}', ha='center', va='bottom', rotation=0)
            
            # Format chart
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3, axis='y')
            ax.set_ylabel('Lucro Total (R$)')
            
            plt.tight_layout()
            st.pyplot(fig)
            
        with col_chart4:
            st.markdown('<p class="chart-title">Comparativo de Preço e Margem (%)</p>', unsafe_allow_html=True)
            
            # Create chart
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Plot price line
            ax.plot(dados_filtrados['data_formatada'], dados_filtrados['precoFinal'], 'o-', 
                   color='#3498db', linewidth=2, label='Preço (R$)')
            
            # Create second y-axis for margin percentage
            ax2 = ax.twinx()
            ax2.plot(dados_filtrados['data_formatada'], dados_filtrados['margem_percentual'], 's-', 
                    color='#e74c3c', linewidth=2, label='Margem (%)')
            ax2.set_ylabel('Margem de Lucro (%)')
            
            # Format chart
            ax.set_ylabel('Preço de Venda (R$)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Combine legends
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            plt.tight_layout()
            st.pyplot(fig)

    with tab2:
        # First row of elasticity charts
        col_elast1, col_elast2 = st.columns(2)
        
        with col_elast1:
            st.markdown('<p class="chart-title">Tendência de Elasticidade ao Longo do Tempo</p>', unsafe_allow_html=True)
            
            # Create elasticity trend chart
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Plot elasticity line
            ax.plot(dados_filtrados['data_formatada'], dados_filtrados['elasticidade'], 'o-', 
                   color='#9b59b6', linewidth=2)
            
            # Add reference lines
            ax.axhline(y=-1, color='#95a5a6', linestyle='--', alpha=0.7, label='Elasticidade Unitária')
            ax.axhline(y=0, color='#7f8c8d', linestyle='--', alpha=0.7, label='Inelástico')
            
            # Add shaded regions for interpretation
            ax.fill_between(dados_filtrados['data_formatada'], -5, -1, color='#e74c3c', alpha=0.1, label='Muito Elástico')
            ax.fill_between(dados_filtrados['data_formatada'], -1, 0, color='#f39c12', alpha=0.1, label='Elástico')
            ax.fill_between(dados_filtrados['data_formatada'], 0, 5, color='#2ecc71', alpha=0.1, label='Inelástico/Premium')
            
            # Format chart
            ax.set_ylim(-3, 3)
            ax.set_ylabel('Elasticidade')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.legend(loc='lower right')
            
            plt.tight_layout()
            st.pyplot(fig)
            
        with col_elast2:
            st.markdown('<p class="chart-title">Distribuição da Elasticidade</p>', unsafe_allow_html=True)
            
            # Create histogram of elasticity values
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Filter out nan values
            elasticity_values = dados_filtrados['elasticidade'].dropna()
            
            if not elasticity_values.empty:
                # Create histogram
                bins = np.linspace(-3, 3, 15)  # Create 15 bins between -3 and 3
                n, bins, patches = ax.hist(elasticity_values, bins=bins, 
                                         color='#9b59b6', alpha=0.7, edgecolor='black')
                
                # Color bins based on elasticity interpretation
                bin_centers = 0.5 * (bins[:-1] + bins[1:])
                for i, patch in enumerate(patches):
                    if bin_centers[i] < -1:
                        patch.set_facecolor('#e74c3c')  # Red for highly elastic
                    elif -1 <= bin_centers[i] < 0:
                        patch.set_facecolor('#f39c12')  # Orange for elastic
                    else:
                        patch.set_facecolor('#2ecc71')  # Green for inelastic/premium
                
                # Add vertical lines for reference
                ax.axvline(x=-1, color='black', linestyle='--', alpha=0.7)
                ax.axvline(x=0, color='black', linestyle='--', alpha=0.7)
                
                # Add text annotations
                ax.text(-2, ax.get_ylim()[1]*0.9, "Muito Elástico", ha='center', fontsize=9)
                ax.text(-0.5, ax.get_ylim()[1]*0.9, "Elástico", ha='center', fontsize=9)
                ax.text(1.5, ax.get_ylim()[1]*0.9, "Inelástico/Premium", ha='center', fontsize=9)
                
                # Format chart
                ax.set_xlabel('Elasticidade')
                ax.set_ylabel('Frequência')
                ax.set_xlim(-3, 3)
                plt.grid(True, alpha=0.3, axis='y')
            else:
                ax.text(0.5, 0.5, "Dados insuficientes para gerar histograma", 
                       ha='center', va='center', transform=ax.transAxes)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        # Second row of elasticity charts
        col_elast3, col_elast4 = st.columns(2)
        
        with col_elast3:
            st.markdown('<p class="chart-title">Relação entre Preço e Elasticidade</p>', unsafe_allow_html=True)
            
            # Create scatter plot of price vs elasticity
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Filter out nan values
            valid_data = dados_filtrados.dropna(subset=['elasticidade'])
            
            if not valid_data.empty:
                # Create scatter plot
                scatter = ax.scatter(valid_data['precoFinal'], valid_data['elasticidade'], 
                                   s=80, c=valid_data['elasticidade'], cmap='RdYlGn_r', 
                                   alpha=0.7, edgecolor='black')
                
                # Add reference lines
                ax.axhline(y=-1, color='gray', linestyle='--', alpha=0.7)
                ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
                
                # Format chart
                ax.set_xlabel('Preço (R$)')
                ax.set_ylabel('Elasticidade')
                ax.set_ylim(-3, 3)
                plt.grid(True, alpha=0.3)
                
                # Add colorbar
                cbar = plt.colorbar(scatter, ax=ax)
                cbar.set_label('Elasticidade')
            else:
                ax.text(0.5, 0.5, "Dados insuficientes para gerar gráfico", 
                       ha='center', va='center', transform=ax.transAxes)
            
            plt.tight_layout()
            st.pyplot(fig)
            
        with col_elast4:
            st.markdown('<p class="chart-title">Elasticidade vs Quantidade Vendida</p>', unsafe_allow_html=True)
            
            # Create scatter plot of sales quantity vs elasticity
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Filter out nan values
            valid_data = dados_filtrados.dropna(subset=['elasticidade'])
            
            if not valid_data.empty:
                # Create scatter plot
                scatter = ax.scatter(valid_data['quantidadeFinal'], valid_data['elasticidade'], 
                                   s=80, c=valid_data['elasticidade'], cmap='RdYlGn_r', 
                                   alpha=0.7, edgecolor='black')
                
                # Add reference lines
                ax.axhline(y=-1, color='gray', linestyle='--', alpha=0.7)
                ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
                
                # Format chart
                ax.set_xlabel('Quantidade Vendida (unidades/mês)')
                ax.set_ylabel('Elasticidade')
                ax.set_ylim(-3, 3)
                plt.grid(True, alpha=0.3)
                
                # Add colorbar
                cbar = plt.colorbar(scatter, ax=ax)
                cbar.set_label('Elasticidade')
                
                # Try to fit a linear regression line
                if len(valid_data) >= 2:
                    try:
                        from scipy import stats
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            valid_data['quantidadeFinal'], valid_data['elasticidade'])
                        
                        # Plot regression line
                        x_line = np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 100)
                        y_line = slope * x_line + intercept
                        ax.plot(x_line, y_line, 'r--', alpha=0.7)
                        
                        # Add correlation coefficient
                        ax.text(0.05, 0.95, f'Correlação: {r_value:.2f}', transform=ax.transAxes, 
                               fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
                    except:
                        pass  # Skip regression if it fails
            else:
                ax.text(0.5, 0.5, "Dados insuficientes para gerar gráfico", 
                       ha='center', va='center', transform=ax.transAxes)
            
            plt.tight_layout()
            st.pyplot(fig)

    with tab3:
        # Predictions and projections tab
        st.markdown('<p class="chart-title">Projeções de Vendas com Base na Elasticidade</p>', unsafe_allow_html=True)
        
        # Create input fields for simulation
        col_sim1, col_sim2, col_sim3 = st.columns(3)
        
        with col_sim1:
            # Get current price from latest data if available
            current_price = preco_final
            if latest_data:
                _, current_price, _, current_quantity, _ = latest_data
                current_quantity = current_quantity / 30  # Convert monthly to daily
            else:
                current_quantity = vendas_por_dia
            
            # Input for new price
            novo_preco = st.number_input("Simular novo preço: R$", 
                                        min_value=0.01, value=float(current_price), step=0.50, format="%.2f")
            st.caption(f"Preço atual: R$ {current_price:.2f}")
            
        with col_sim2:
            # Get latest elasticity
            elasticidade_atual = None
            if latest_data and latest_data[4] is not None:
                elasticidade_atual = latest_data[4]
            
            # Input for elasticity override
            usar_elasticidade = st.number_input("Elasticidade para simulação:", 
                                              min_value=-5.0, max_value=5.0, 
                                              value=float(elasticidade_atual if elasticidade_atual is not None else -0.8), 
                                              step=0.1, format="%.2f")
            
            st.caption("Use a elasticidade calculada ou ajuste manualmente")
            
        with col_sim3:
            # Button to run simulation
            st.write("")  # Spacer
            st.write("")  # Spacer
            simular = st.button("🧮 Simular Cenário", use_container_width=True)
            
        # Run projection if button is clicked
        if simular:
            # Calculate projected sales
            variacao_preco = (novo_preco - current_price) / current_price
            variacao_quantidade = variacao_preco * usar_elasticidade
            nova_quantidade = current_quantity * (1 + variacao_quantidade)
            
            # Display projection results
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                # Create comparison chart
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Set bar positions
                bar_width = 0.35
                index = np.arange(2)
                
                # Calculate revenue
                receita_atual = current_price * current_quantity * 30  # Monthly revenue
                receita_nova = novo_preco * nova_quantidade * 30  # Monthly revenue
                
                # Create bars for quantity
                bars1 = ax.bar(index - bar_width/2, [current_quantity, nova_quantidade], 
                              bar_width, label='Vendas diárias', color='#3498db')
                
                # Create second y-axis for revenue
                ax2 = ax.twinx()
                bars2 = ax2.bar(index + bar_width/2, [receita_atual, receita_nova], 
                               bar_width, label='Receita mensal', color='#e74c3c')
                
                # Add data labels
                for bar in bars1:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                           f'{height:.0f}', ha='center', va='bottom')
                
                for bar in bars2:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 100,
                            f'R$ {height:.0f}', ha='center', va='bottom')
                
                # Format chart
                ax.set_xticks(index)
                ax.set_xticklabels(['Cenário Atual', 'Cenário Projetado'])
                ax.set_ylabel('Vendas (unidades/dia)')
                ax2.set_ylabel('Receita (R$/mês)')
                
                # Combine legends
                lines1, labels1 = ax.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
                
                plt.tight_layout()
                st.pyplot(fig)
                
            with col_res2:
                # Display impact metrics
                variacao_percentual_vendas = variacao_quantidade * 100
                variacao_percentual_receita = ((receita_nova - receita_atual) / receita_atual) * 100
                
                st.markdown("### Impacto Projetado")
                
                # Create metrics cards
                if variacao_percentual_vendas >= 0:
                    st.success(f"📈 Vendas: +{variacao_percentual_vendas:.1f}% ({nova_quantidade:.0f} unidades/dia)")
                else:
                    st.warning(f"📉 Vendas: {variacao_percentual_vendas:.1f}% ({nova_quantidade:.0f} unidades/dia)")
                    
                if variacao_percentual_receita >= 0:
                    st.success(f"💰 Receita: +{variacao_percentual_receita:.1f}% (R$ {receita_nova:.2f}/mês)")
                else:
                    st.warning(f"💰 Receita: {variacao_percentual_receita:.1f}% (R$ {receita_nova:.2f}/mês)")
                
                # Calculate profit metrics
                custo_unitario = preco_unidade
                lucro_atual = (current_price - custo_unitario) * current_quantity * 30
                lucro_novo = (novo_preco - custo_unitario) * nova_quantidade * 30
                variacao_percentual_lucro = ((lucro_novo - lucro_atual) / lucro_atual) * 100
                
                if variacao_percentual_lucro >= 0:
                    st.success(f"✅ Lucro: +{variacao_percentual_lucro:.1f}% (R$ {lucro_novo:.2f}/mês)")
                else:
                    st.warning(f"⚠️ Lucro: {variacao_percentual_lucro:.1f}% (R$ {lucro_novo:.2f}/mês)")
                
                # Provide recommendation
                st.markdown("### Recomendação")
                if variacao_percentual_lucro > 5:
                    st.markdown(f'<div class="insight-box success">✅ <b>Recomendado:</b> A alteração para R$ {novo_preco:.2f} deve gerar um aumento significativo no lucro. Considere implementar esta mudança.</div>', unsafe_allow_html=True)
                elif variacao_percentual_lucro > 0:
                    st.markdown(f'<div class="insight-box info">ℹ️ <b>Considere testar:</b> A alteração para R$ {novo_preco:.2f} deve gerar um pequeno aumento no lucro. Recomenda-se testar em parte do negócio primeiro.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="insight-box warning">⚠️ <b>Não recomendado:</b> A alteração para R$ {novo_preco:.2f} deve reduzir o lucro total. Mantenha o preço atual ou considere outras opções.</div>', unsafe_allow_html=True)
        else:
            st.info("Clique em 'Simular Cenário' para ver a projeção de impacto da alteração de preço.")
else:
    # If no data available, display a message
    st.warning("Nenhum dado disponível para análise. Registre os dados primeiro.")
    
    # Display sample charts with dummy data
    st.markdown("### Visualização com dados de exemplo")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=10, freq='W')
    sample_data = pd.DataFrame({
        'data_formatada': dates.strftime('%d/%m/%Y'),
        'precoInicio': np.linspace(2.5, 3.0, 10),
        'precoFinal': np.linspace(5.0, 6.5, 10),
        'quantidadeInicio': np.ones(10) * 100,
        'quantidadeFinal': np.linspace(90, 110, 10),
        'elasticidade': np.linspace(-1.5, -0.5, 10)
    })
    
    # Display sample chart
    fig = px.line(
        sample_data,
        x='data_formatada',
        y='elasticidade',
        markers=True,
        title='Exemplo: Tendência de Elasticidade',
        labels={'data_formatada': 'Data', 'elasticidade': 'Elasticidade'},
        template='plotly_white'
    )

    # Ajustar layout do gráfico
    fig.update_layout(  
        title={'x': 0.5},  # Centralizar o título
        xaxis=dict(tickangle=45),  # Rotacionar os rótulos do eixo X
        yaxis=dict(title='Elasticidade'),
        margin=dict(l=20, r=20, t=40, b=20)  # Ajustar margens
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)  
    
    st.info("Os gráficos acima são apenas exemplos. Registre dados reais para obter análises personalizadas.")

# Add footer with information
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>Lanchonete do Amaro - Sistema de Análise de Preços © 2025</small><br>
    <small>Desenvolvido com ❤️ usando Streamlit e Pandas</small>
</div>
""", unsafe_allow_html=True)