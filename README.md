# Controle Financeiro Inteligente

Projeto de portfólio em Python que une desenvolvimento de sistemas e conceitos de gestão financeira/contábil.

## Funcionalidades

- Cadastro e exclusão de receitas e despesas.
- Persistência dos dados em banco SQLite local.
- Indicadores: receitas, despesas, resultado e margem do período.
- Gráfico de receitas x despesas por mês.
- Gráfico de despesas por categoria.
- Filtros por período, tipo e categoria.
- Exportação de relatórios em CSV para abrir no Excel.
- Dados fictícios para demonstração.

## Tecnologias

- Python
- Streamlit
- SQLite
- Pandas
- Plotly

## Requisitos

- Python 3.10 ou superior
- Internet na primeira instalação das bibliotecas

## Como executar no Windows

1. Baixe e extraia o ZIP.
2. Abra a pasta `controle-financeiro-inteligente`.
3. Na barra de endereço do Explorador de Arquivos, digite `cmd` e pressione Enter.
4. Crie um ambiente virtual:

   ```bat
   py -m venv .venv
   ```

5. Ative o ambiente virtual:

   ```bat
   .venv\Scripts\activate
   ```

6. Instale as dependências:

   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Inicie o sistema:

   ```bat
   streamlit run app.py
   ```

8. O navegador deverá abrir automaticamente. Se não abrir, acesse o endereço mostrado no terminal, normalmente `http://localhost:8501`.

### Se o comando `py` não funcionar

Tente usar `python` no lugar de `py`. Se nenhum funcionar, instale o Python pelo site oficial e marque a opção **Add Python to PATH** durante a instalação.

## Como testar

- Abra **Carregar exemplos** na barra lateral para inserir dados fictícios.
- Veja os indicadores e gráficos em **Visão geral**.
- Cadastre movimentações em **Lançamentos**.
- Gere e baixe o CSV em **Relatórios**.

Os dados ficam no arquivo `financeiro.db`, criado automaticamente na pasta do projeto. Não o apague se quiser manter seus lançamentos.

## Publicar no GitHub

1. Crie uma conta em https://github.com, caso ainda não tenha.
2. Crie um repositório público chamado `controle-financeiro-inteligente`.
3. Não envie o arquivo `financeiro.db` caso contenha dados pessoais ou reais. O `.gitignore` já exclui esse banco.
4. Abra o terminal na pasta do projeto e execute:

   ```bash
   git init
   git add .
   git commit -m "Projeto inicial: Controle Financeiro Inteligente"
   git branch -M main
   git remote add origin https://github.com/SEU-USUARIO/controle-financeiro-inteligente.git
   git push -u origin main
   ```

5. Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub. O Git precisa estar instalado e configurado.

## Publicar uma demonstração online (opcional)

Uma opção comum é o Streamlit Community Cloud, conectado ao repositório GitHub. Consulte https://streamlit.io/cloud e siga o fluxo de implantação indicado na plataforma. Para uma demonstração pública, use apenas dados fictícios. O armazenamento local pode não ser persistente entre reinicializações ou implantações, dependendo do ambiente.

## Ideia de evolução

- Editar lançamentos.
- Login e permissões.
- Metas orçamentárias.
- Comparativo mês a mês.
- Importação de extrato CSV.
- Testes automatizados.
- Banco de dados hospedado para implantação multiusuário.

## Aviso

Projeto educacional e gerencial. Não substitui escrituração contábil, cálculo tributário ou sistema financeiro profissional.
