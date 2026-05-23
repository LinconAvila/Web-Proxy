import json
import os

def load_configs() -> tuple[list, dict]:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    blocked_path = os.path.join(base_dir, 'config', 'blocked.json')
    words_path = os.path.join(base_dir, 'config', 'words.json')

    lista_bloqueados = []
    dicionario_palavroes = {}

    try:
        with open(blocked_path, 'r', encoding='utf-8') as f:
            dados_bloqueados = json.load(f)
            lista_bloqueados = dados_bloqueados.get('bloqueados', [])
    except FileNotFoundError:
        print(f"Arquivo {blocked_path} não encontrado.")
        
    try:
        with open(words_path, 'r', encoding='utf-8') as f:
            dicionario_palavroes = json.load(f)
    except FileNotFoundError:
        print(f"Arquivo {words_path} não encontrado.")


    return lista_bloqueados, dicionario_palavroes


if __name__ == "__main__":
    bloqueados, palavroes = load_configs()
    print("Lista de bloqueados:", bloqueados)
    print("Dicionário de palavrões:", palavroes)