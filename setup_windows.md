# 🪟 Guia de Configuração Windows

## Passos de Configuração

### Passo 1: Instalar o VSCode

O VSCode (Visual Studio Code) é o editor de código que vamos usar. É gratuito, leve e tem IA integrada.

1. Abre o browser e vai a [https://code.visualstudio.com](https://code.visualstudio.com)
2. Clica em "Download for Windows" — o botão azul grande.
3. Abre o ficheiro `VSCodeSetup-x64-x.x.x.exe` que foi descarregado.
4. No instalador, aceita o contrato e deixa todas as opções por defeito. Certifica-te que assinala: **Add to PATH**
5. Clica em "Install" e depois "Finish".

✅ **Verificar a instalação**

```powershell
code --version
```

Deves ver um número de versão, por exemplo: `1.90.0`

💡 **Extensões recomendadas:** Python (Microsoft), GitLens, Pylance. Clica no ícone de extensões na barra lateral (`Ctrl+Shift+X`) e pesquisa pelo nome.

---

### Passo 2: Instalar o Python

> Verificar se o Python já está instalado:

```powershell
python --version
```

**Erros como "Python is not recognized":**

> **Método 1:** Instalar o Python usando o PowerShell

```powershell
winget install Python.Python.3.13
```

> **Método 2:** Download manual

1. Vai a [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Clica no botão amarelo "Download Python 3.x.x".
3. Abre o instalador. **MUITO IMPORTANTE:** na primeira janela, assinala a caixa **Add Python to PATH** em baixo antes de clicar em Install.

⚠️ Se não assinalares "Add Python to PATH", o Python não vai funcionar no terminal. Se te esqueceres, desinstala e volta a instalar.

4. Clica em "Install Now" e aguarda.
5. No fim, clica em "Disable path length limit" se aparecer essa opção — é recomendado.
6. Clica em "Close".

✅ **Verificar a instalação**

```powershell
python --version
```

Resultado esperado: `Python 3.13.x`

📦 **Verificar o pip**

```powershell
pip --version
```

---

### Passo 3: Instalar o Git

> **Método 1:** Instalar usando o PowerShell

```powershell
winget install Git.Git
```

> **Método 2:** Download manual

1. Vai a [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. O download começa automaticamente. Abre o instalador.
3. Deixa todas as opções por defeito exceto uma: em **"Choosing the default editor used by Git"**, seleciona **"Use Visual Studio Code as Git's default editor"**.
4. Em **"Adjusting your PATH environment"**, mantém **"Git from the command line and also from 3rd-party software"**.
5. Continua a clicar "Next" até ao fim e clica "Install".

✅ **Verificar a instalação**

Fecha e volta a abrir o Terminal/PowerShell após a instalação, depois executa:

```powershell
git --version
```

Deves ver algo como: `git version 2.45.0`

⚙️ **Configurar o Git (obrigatório)**

Antes de usares o Git pela primeira vez, identifica-te. Usa o teu nome real e o email com que criaste a conta no GitHub:

```powershell
git config --global user.name "O Teu Nome"
git config --global user.email "o.teu@email.com"
```

Para verificar a configuração:

```powershell
git config --list
```

💡 Esta configuração só é feita uma vez — o Git vai guardá-la e usá-la automaticamente em todos os teus projetos.

---

### Passo 4: Clonar o Repositório

Com as ferramentas instaladas, já podes clonar o repositório boilerplate.

Cria uma pasta onde vais guardar os teus projetos. Abre o PowerShell e executa:

```powershell
mkdir "$HOME\Documents\github"
cd "$HOME\Documents\github"
```

Clona o repositório — substitui o URL pelo link fornecido na aula:

```powershell
git clone [URL do repositório aqui]
```

Abre a pasta no VSCode:

```powershell
cd nome-do-projeto
code .
```

---

### Passo 5: Criar e Ativar o Ambiente Virtual

> Criar o ambiente virtual

```powershell
python -m venv .venv
```

> Ativar o ambiente (sempre que não vires `(.venv)` no terminal)

```powershell
.venv\Scripts\activate
```

> Atualizar o pip

```powershell
python -m pip install --upgrade pip
```

**Erros como "running scripts is disabled on this system":**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Erros como "developer tools not found":**

```powershell
pip install --upgrade pip setuptools wheel
```

---

## Instalar Pacotes

> Instalar bibliotecas (executa isto sempre que adicionares novos pacotes)

```powershell
pip install -r requirements.txt
```

> Ou instalar apenas um específico

```powershell
pip install <nome_do_pacote>
```

---

## Resolução de Problemas

**❓ "python" não é reconhecido como comando**

Isto significa que o Python não está no PATH. Resolve assim:

1. Desinstala o Python (Definições → Aplicações → Python → Desinstalar)
2. Volta a instalar e não te esqueças de assinalar **"Add Python to PATH"**

**❓ "git" não é reconhecido como comando**

Fecha e volta a abrir o Terminal/PowerShell após a instalação do Git.  
Se persistir: Painel de Controlo → Sistema → Variáveis de Ambiente → PATH → verifica se o caminho do Git está lá (normalmente `C:\Program Files\Git\cmd`)

**❓ VSCode não abre ficheiros .py com o Python correto**

Clica no nome do interpretador no canto inferior direito do VSCode.  
Seleciona o Python da pasta `.venv`.  
Se não aparecer: `Ctrl+Shift+P` → `Python: Select Interpreter` → escolhe a opção com `.venv`.

**❓ Erro "running scripts is disabled on this system"**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**❓ Ainda tens problemas?**

Não te preocupes — pede ajuda ao teu instrutor ou abre uma questão no canal de suporte da turma.
