import Simulador
from yaml_loader import carrega_modelo

# C = servidores, MU = taxa por servidor (clientes/hora = 60 / tempo médio em min)
PARAMS_INICIAL = {
    1: {"nome": "Caixa",        "C": 2, "MU": 60 / 5},
    2: {"nome": "Gerente",      "C": 2, "MU": 60 / 10},
    3: {"nome": "Documentação", "C": 1, "MU": 60 / 7},
}

# Melhorado: Caixa passa para 3 servidores
PARAMS_MELHORADO = {
    1: {"nome": "Caixa",        "C": 3, "MU": 60 / 5},
    2: {"nome": "Gerente",      "C": 2, "MU": 60 / 10},
    3: {"nome": "Documentação", "C": 1, "MU": 60 / 7},
}


def roda(arquivo, params, titulo):
    filas, gerador, fila_inicial, tempo_inicial = carrega_modelo(arquivo)
    sim = Simulador.Simulador(filas, gerador, fila_id_primeira_chegada=fila_inicial, primeira_chegada=tempo_inicial)
    resultado = sim.simula()

    print("=" * 60)
    print(f"{titulo}  ({arquivo})")
    print("=" * 60)
    print(f"Tempo global da simulação: {resultado['tempo_global']:.4f}")
    print(f"Aleatórios usados: {resultado['aleatorios_usados']}")
    print()

    indices = {}
    for fila_id in sorted(resultado["filas"]):
        r = resultado["filas"][fila_id]
        p = params[fila_id]
        C, MU = p["C"], p["MU"]
        probs = r["probabilidades"]

        N = sum(pi * i for i, pi in enumerate(probs))
        D = sum(pi * min(i, C) * MU for i, pi in enumerate(probs))
        U = sum(pi * min(i, C) / C for i, pi in enumerate(probs))
        W = N / D if D > 0 else 0
        indices[fila_id] = {"N": N, "D": D, "U": U * 100, "W": W * 60, "perdas": r["perdas"]}

        print(f"--- FILA {fila_id} ({p['nome']}) ---")
        print(f"Perdas: {r['perdas']}")
        print("Estado | Tempo acumulado | Probabilidade")
        for estado, (t, pi) in enumerate(zip(r["tempo_acumulado_por_estado"], probs)):
            print(f"{estado:6d} | {t:15.4f} | {pi:.6f}")
        print(f"N (população):      {N:.4f} clientes")
        print(f"D (vazão):          {D:.4f} clientes/h")
        print(f"U (utilização):     {U * 100:.2f}%")
        print(f"W (tempo resposta): {W:.4f} h = {W * 60:.2f} min")
        print()

    return indices


ini = roda("modelo.yml", PARAMS_INICIAL, "MODELO INICIAL")
mel = roda("modelo_melhorado.yml", PARAMS_MELHORADO, "MODELO MELHORADO")

# Resumo comparativo
print("=" * 60)
print("COMPARAÇÃO (inicial -> melhorado)")
print("=" * 60)
for fila_id in sorted(ini):
    nome = PARAMS_INICIAL[fila_id]["nome"]
    print(f"--- FILA {fila_id} ({nome}) ---")
    for chave, rotulo in [("N", "N (clientes)"), ("D", "D (clientes/h)"), ("U", "U (%)"),
                          ("W", "W (min)"), ("perdas", "Perdas")]:
        a, b = ini[fila_id][chave], mel[fila_id][chave]
        var = f"{(b - a) / a * 100:+.1f}%" if a != 0 else "n/a"
        print(f"{rotulo:15s} {a:10.4f} -> {b:10.4f}   variação: {var}")
    print()