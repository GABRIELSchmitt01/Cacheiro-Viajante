"""
Algoritmo Genético para o Problema do Caixeiro Viajante (TSPLIB EUC_2D).
Uso: python algoritmo_genetico.py berlin52.tsp
Instalação: Python 3.10+ (não requer bibliotecas externas).
"""
import math
import random
import sys

SEMENTE = 42
TAMANHO_POPULACAO = 150
GERACOES = 500
TAXA_MUTACAO = 0.15
ELITISMO = 2

def ler_tsplib(caminho):
    """Lê coordenadas de instâncias TSPLIB no formato NODE_COORD_SECTION/EUC_2D."""
    cidades = {}
    lendo_coordenadas = False
    tipo_distancia = "EUC_2D"
    with open(caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha:
                continue
            if linha.startswith("EDGE_WEIGHT_TYPE"):
                tipo_distancia = linha.split(":")[-1].strip()
            if linha == "NODE_COORD_SECTION":
                lendo_coordenadas = True
                continue
            if linha == "EOF":
                break
            if lendo_coordenadas:
                partes = linha.split()
                if len(partes) >= 3:
                    cidade = int(partes[0])
                    cidades[cidade] = (float(partes[1]), float(partes[2]))
    if not cidades:
        raise ValueError("Não encontrei NODE_COORD_SECTION no arquivo.")
    if tipo_distancia != "EUC_2D":
        raise ValueError(f"Este código aceita EUC_2D; encontrado: {tipo_distancia}")
    return cidades

def distancia(a, b, cidades):
    x1, y1 = cidades[a]
    x2, y2 = cidades[b]
    # TSPLIB EUC_2D usa arredondamento para o inteiro mais próximo.
    return int(math.sqrt((x1-x2)**2 + (y1-y2)**2) + 0.5)

def custo_rota(rota, cidades):
    total = 0
    for i in range(len(rota)):
        total += distancia(rota[i], rota[(i+1) % len(rota)], cidades)
    return total

def torneio(populacao, cidades, k=4):
    candidatos = random.sample(populacao, k)
    return min(candidatos, key=lambda rota: custo_rota(rota, cidades))

def cruzamento_ordem(pai1, pai2):
    """Order Crossover (OX): preserva a ordem relativa e não repete cidades."""
    n = len(pai1)
    inicio, fim = sorted(random.sample(range(n), 2))
    filho = [None] * n
    filho[inicio:fim] = pai1[inicio:fim]
    genes_restantes = [gene for gene in pai2 if gene not in filho]
    posicoes = list(range(fim, n)) + list(range(0, inicio))
    for pos, gene in zip(posicoes, genes_restantes):
        filho[pos] = gene
    return filho

def mutacao(rota):
    """Inverte um trecho da rota, mantendo cada cidade exatamente uma vez."""
    if random.random() < TAXA_MUTACAO:
        i, j = sorted(random.sample(range(len(rota)), 2))
        rota[i:j+1] = reversed(rota[i:j+1])
    return rota

def algoritmo_genetico(cidades):
    random.seed(SEMENTE)
    genes = list(cidades.keys())
    populacao = []
    for _ in range(TAMANHO_POPULACAO):
        rota = genes[:]
        random.shuffle(rota)
        populacao.append(rota)

    melhor = min(populacao, key=lambda rota: custo_rota(rota, cidades))[:]
    melhor_custo = custo_rota(melhor, cidades)

    for geracao in range(GERACOES):
        populacao.sort(key=lambda rota: custo_rota(rota, cidades))
        nova_populacao = [rota[:] for rota in populacao[:ELITISMO]]
        while len(nova_populacao) < TAMANHO_POPULACAO:
            pai1 = torneio(populacao, cidades)
            pai2 = torneio(populacao, cidades)
            filho = cruzamento_ordem(pai1, pai2)
            filho = mutacao(filho)
            nova_populacao.append(filho)
        populacao = nova_populacao
        candidato = min(populacao, key=lambda rota: custo_rota(rota, cidades))
        custo = custo_rota(candidato, cidades)
        if custo < melhor_custo:
            melhor, melhor_custo = candidato[:], custo

    return melhor, melhor_custo

def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "berlin52.tsp"
    cidades = ler_tsplib(caminho)
    melhor_rota, melhor_custo = algoritmo_genetico(cidades)
    rota_fechada = melhor_rota + [melhor_rota[0]]
    print(f"Instância: {caminho}")
    print(f"Número de cidades: {len(cidades)}")
    print(f"Custo total do melhor ciclo encontrado: {melhor_custo}")
    print("Ordem das cidades (inclui retorno à origem):")
    print(" -> ".join(map(str, rota_fechada)))

if __name__ == "__main__":
    main()
