import numpy as np

def preco_unidade(custo_unidade, custo_salarios, prod_por_dia):
    """
    Calculate the unit cost of production
    
    Args:
        custo_unidade (float): Cost of ingredients per unit
        custo_salarios (float): Monthly salary costs
        prod_por_dia (float): Daily production of snacks
    
    Returns:
        float: Total unit cost
    """
    # Calculate monthly production (assuming 30 days per month)
    prod_mensal = prod_por_dia * 30
    
    # Calculate operational cost per unit
    custo_operacional = custo_salarios / prod_mensal
    
    # Total cost per unit
    custo_total = custo_operacional + custo_unidade
    
    return custo_total

def preco_final(custo_total, margem_lucro):
    """
    Calculate the final price with profit margin
    
    Args:
        custo_total (float): Total cost per unit
        margem_lucro (float): Desired profit margin (%)
    
    Returns:
        float: Final selling price
    """
    percentual = margem_lucro / 100
    preco_final = custo_total + (custo_total * percentual)
    return preco_final

def elasticidade(q_inicio, q_final, p_inicio, p_final):
    """
    Calculate price elasticity of demand
    
    Elasticity measures the responsiveness of quantity demanded to changes in price.
    
    Args:
        q_inicio (float): Initial quantity before price change
        q_final (float): Final quantity after price change
        p_inicio (float): Initial price before change
        p_final (float): Final price after change
    
    Returns:
        float: Price elasticity value
    """
    # Avoid division by zero
    if q_inicio == 0 or p_inicio == 0 or p_inicio == p_final:
        return None
    
    # Use midpoint formula for elasticity calculation
    # This method produces more consistent results than the simple percentage change
    q_avg = (q_inicio + q_final) / 2
    p_avg = (p_inicio + p_final) / 2
    
    delta_q = q_final - q_inicio
    delta_p = p_final - p_inicio
    
    # Calculate elasticity using the arc elasticity formula
    epd = (delta_q / q_avg) / (delta_p / p_avg)
    
    return epd

def interpret_elasticity(epd):
    """
    Interpret elasticity value and provide business insights
    
    Args:
        epd (float): Elasticity value
        
    Returns:
        tuple: (status, message) where status is one of "warning", "info", "success"
    """
    if epd is None:
        return "info", "Não foi possível calcular a elasticidade com os dados fornecidos."
    
    if epd < -1:
        return "warning", "⚠️ Atenção! Seus clientes estão muito sensíveis ao preço. Um aumento pode reduzir significativamente as vendas. Considere manter os preços atuais ou fazer ajustes menores."
    elif abs(epd - (-1)) < 0.1:  # Approximately -1
        return "info", "📊 As vendas respondem proporcionalmente às mudanças de preço. Qualquer alteração deve ser bem planejada."
    elif -1 < epd < 0:
        return "success", "✅ Boa notícia! Seus clientes são fiéis aos salgados. Você tem flexibilidade para ajustar os preços mantendo as vendas estáveis."
    elif abs(epd) < 0.1:  # Approximately 0
        return "info", "🎯 Seus salgados têm demanda garantida! Os clientes compram independentemente do preço. Possível ajustar preços com segurança."
    elif epd > 0:
        return "success", "🌟 Interessante! Seus salgados são vistos como produto premium. Os clientes associam maior preço com maior qualidade."
    else:
        return "info", "Resultado inconclusivo. Considere coletar mais dados."

def calcular_lucro_projetado(custo_unidade, preco_venda, quantidade_vendida):
    """
    Calculate projected profit
    
    Args:
        custo_unidade (float): Cost per unit
        preco_venda (float): Selling price
        quantidade_vendida (float): Number of units sold
        
    Returns:
        float: Projected profit
    """
    lucro_unitario = preco_venda - custo_unidade
    lucro_total = lucro_unitario * quantidade_vendida
    return lucro_total