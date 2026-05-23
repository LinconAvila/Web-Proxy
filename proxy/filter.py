import re
from proxy.config import load_configs

def filter_content(html:str) -> tuple[str, bool]:
    _, palavroes = load_configs()
    html_modificado = html
    foi_filtrado = False

    for palavrao, substituto in palavroes.items():
        padrao = re.compile(re.escape(palavrao), re.IGNORECASE)

        if padrao.search(html_modificado):
            html_modificado = padrao.sub(substituto, html_modificado)
            foi_filtrado = True
    
    return html_modificado, foi_filtrado