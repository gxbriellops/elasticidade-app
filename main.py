def qntFuncionarios():
    Soma = int(input("Somando todos os funcionários, qual o total de salarios? "))
    return Soma

def preçoUnidade(CustoUnid, CustoSala, ProdUmDia: int):
    cOperacional = CustoSala/ProdUmDia
    custoTotal = cOperacional + CustoUnid
    return custoTotal


def preçoFinal (CustoTotal: int, Lucro: float):
    porc = Lucro/100
    precoFinal = CustoTotal + (CustoTotal * porc)
    return precoFinal

def dadosDaSemana():
    """
    This function tracks the number of snacks sold on each day of the week.

    The function initializes a dictionary with each day of the week and prompts the user to input the number of snacks sold on each day. 
    The final dictionary contains the total number of snacks sold on each day.
    """
    numVendas = {"Segunda Feira": 0, "Terça Feira": 0 , "Quarta Feira": 0, "Quinta Feira": 0, "Sexta Feira": 0, "Sabado": 0, "Domingo": 0}

    totalVendasSemana = 0

    for c, dia in enumerate(numVendas):
        vendas = int(input(f"Quantas vendas foram feitas no dia [{dia}]: "))
        numVendas[dia] = vendas
        totalVendasSemana += vendas

    totalAprox = totalVendasSemana * 4.3

    return totalAprox

def elasticidade (qInicio, Qfinal, Pinicio, Pfinal):
    """
    qInicio = quantidade inicial antes de alterar o $
    Qfinal = quantidade final depois de alterar o $
    Pinicio = preço inicial antes de alterar o $
    Pfinal = preço final depois de alterar o $

    """
    deltaQ = Qfinal - qInicio
    deltaP = Pfinal - Pinicio
    if qInicio == 0 or Pinicio == 0:  # Evitar divisão por zero
        return None
    Epd = (deltaQ/qInicio) /  (deltaP/Pinicio)
    return Epd