# Web Proxy com Controle de Conteúdo
### Sistemas para Internet 2 — FURG — 2026/1
**Autores:** Lucas Derick Silva Pereira e Lincon Avila de Souza  
**Professor:** Prof. Dr. André Prisco Vargas

---

## Por que escolhemos Flask?

Usamos **Python 3** com **Flask** e a biblioteca **requests**.

A alternativa seria trabalhar diretamente com sockets TCP, o que daria mais controle sobre o fluxo de bytes — mas exigiria escrever do zero o parsing de cabeçalhos HTTP, gestão de buffers e controle de conexões concorrentes. O Flask resolve tudo isso e nos deixou focar no que importava: as regras do proxy em si.

**O que funcionou bem:**
- Código legível e rápido de escrever
- Integração natural com Jinja2 para a página de bloqueio
- A biblioteca `requests` tornou o repasse das chamadas simples e confiável

**O que foi difícil:**
- Flask não foi feito para proxy: o método `CONNECT` do HTTPS precisou de tratamento manual fora do fluxo normal, via `proxy/tunnel.py`
- O cabeçalho `Accept-Encoding: gzip` causou um bug silencioso — o servidor respondia com HTML compactado e o filtro tentava aplicar regex em bytes comprimidos. A solução foi remover esse cabeçalho da requisição enviada ao servidor de origem, forçando resposta em texto puro

---

## Pré-requisitos

- Python 3.x instalado no sistema

---

## Instalação e Execução

**1. Criar e ativar o ambiente virtual:**

No Windows PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

No Linux/WSL:
```bash
python3 -m venv venv
source venv/bin/activate
```

**2. Instalar as dependências:**
```bash
pip install -r requirements.txt
```

**3. Iniciar o servidor:**
Se você estiver na pasta do repositório pai, entre primeiro em `Web-Proxy`:

```powershell
cd Web-Proxy
```

No Windows PowerShell:
```powershell
python app.py
```

No Linux/WSL:
```bash
python3 app.py
```

O servidor ficará ativo em `http://localhost:5000`

---

## Como usar

Basta passar a URL completa depois do endereço do proxy:

```
# Acesso normal
http://localhost:5000/http://www.pudim.com.br

# Domínio bloqueado
http://localhost:5000/http://www.instagram.com
```

---

## Sobre o HTTPS

O filtro de palavras funciona **apenas em tráfego HTTP**. Sites HTTPS cifram o conteúdo com TLS/SSL — o proxy enxerga só bytes cifrados e não consegue aplicar nenhuma substituição. Para mais detalhes, ver a seção 2.3 do relatório técnico.

---

## Estrutura do Projeto

```
proxy/
  config.py     # carrega os JSONs de configuração
  blocker.py    # verifica se o domínio está bloqueado
  filter.py     # aplica substituições no HTML
  logger.py     # registra acessos em logs/log.json
  tunnel.py     # trata conexões HTTPS (método CONNECT)
config/
  blocked.json  # lista de domínios bloqueados
  words.json    # dicionário de substituições
templates/
  blocked.html  # página exibida ao bloquear um domínio
logs/
  log.json      # histórico de acessos (gerado automaticamente)
app.py          # ponto de entrada do servidor
```

---

## Uso de IA

Usamos o Gemini como apoio em partes específicas: organização do `words.json`, ponto de partida para a expressão regular do filtro e estrutura inicial do CSS da página de bloqueio. A lógica de integração entre os módulos, os ajustes de caminho do `config.py` e o tratamento do `CONNECT` no `tunnel.py` foram escritos e depurados por nós.