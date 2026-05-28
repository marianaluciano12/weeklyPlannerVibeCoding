# 🍎 Guia de Configuração Mac

## Passos de Configuração

### Passo 1: Instalar o Homebrew

O Homebrew é o gestor de pacotes do Mac — permite instalar ferramentas de desenvolvimento com um único comando.

Abre o Terminal e executa:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

✅ **Verificar a instalação**

```bash
brew --version
```

---

### Passo 2: Instalar o VSCode

```bash
brew install --cask visual-studio-code
```

Depois de instalar, abre o VSCode. Em seguida, abre a Paleta de Comandos com `Cmd+Shift+P`, escreve `shell command` e seleciona **"Install 'code' command in PATH"**.

✅ **Verificar a instalação**

```bash
code --version
```

💡 **Extensões recomendadas:** Python (Microsoft), GitLens, Pylance. Clica no ícone de extensões na barra lateral (`Cmd+Shift+X`) e pesquisa pelo nome.

---

### Passo 3: Instalar o Python

```bash
brew install python
```

✅ **Verificar a instalação**

```bash
python3 --version
```

Resultado esperado: `Python 3.13.x`

📦 **Verificar o pip**

```bash
pip3 --version
```

---

### Passo 4: Instalar o Git

```bash
brew install git
```

✅ **Verificar a instalação**

```bash
git --version
```

Deves ver algo como: `git version 2.45.0`

⚙️ **Configurar o Git (obrigatório)**

Antes de usares o Git pela primeira vez, identifica-te. Usa o teu nome real e o email com que criaste a conta no GitHub:

```bash
git config --global user.name "O Teu Nome"
git config --global user.email "o.teu@email.com"
```

Para verificar a configuração:

```bash
git config --list
```

💡 Esta configuração só é feita uma vez — o Git vai guardá-la e usá-la automaticamente em todos os teus projetos.

---

### Passo 5: Clonar o Repositório

Com as ferramentas instaladas, já podes clonar o repositório boilerplate.

Cria uma pasta onde vais guardar os teus projetos:

```bash
mkdir -p ~/Documents/github
cd ~/Documents/github
```

Clona o repositório — substitui o URL pelo link fornecido na aula:

```bash
git clone [URL do repositório aqui]
```

Abre a pasta no VSCode:

```bash
cd nome-do-projeto
code .
```

---

### Passo 6: Criar e Ativar o Ambiente Virtual

> Criar o ambiente virtual

```bash
python3 -m venv .venv
```

> Ativar o ambiente (sempre que não vires `(.venv)` no terminal)

```bash
source .venv/bin/activate
```

> Atualizar o pip

```bash
python -m pip install --upgrade pip
```

**Erros como "developer tools not found":**

```bash
xcode-select --install
```

---

## Instalar Pacotes

> Instalar bibliotecas (executa isto sempre que adicionares novos pacotes)

```bash
pip install -r requirements.txt
```

> Ou instalar apenas um específico

```bash
pip install <nome_do_pacote>
```

---

## Resolução de Problemas

**❓ "python" não é reconhecido como comando**

Usa `python3` em vez de `python` no macOS.

**❓ VSCode não abre ficheiros .py com o Python correto**

Clica no nome do interpretador no canto inferior direito do VSCode.  
Seleciona o Python da pasta `.venv`.  
Se não aparecer: `Cmd+Shift+P` → `Python: Select Interpreter` → escolhe a opção com `.venv`.

**❓ Erro de permissões (Permission denied)**

Se vires `Permission denied`, o problema é que o script não tem permissão de execução:

```bash
chmod +x nome-do-ficheiro.sh
```

**❓ Homebrew não instala**

Certifica-te que tens as Xcode Command Line Tools instaladas — o Homebrew precisa delas:

```bash
xcode-select --install
```

Depois tenta instalar o Homebrew novamente. Consulta [https://brew.sh](https://brew.sh) para instruções atualizadas.

**❓ Ainda tens problemas?**

Não te preocupes — pede ajuda ao teu instrutor ou abre uma questão no canal de suporte da turma.
