# PetPlus Petshop - Sistema de Gestão

## Visão Geral do Projeto
PetPlus é um sistema web para gestão de petshop desenvolvido em Flask. Ele permite o gerenciamento completo de clientes, pets, produtos, funcionários e vendas, com funcionalidades CRUD integradas ao banco de dados MySQL.

## Funcionalidades
- Cadastro, edição e exclusão de clientes
- Cadastro, edição e exclusão de pets (vinculados a clientes)
- Cadastro, edição e exclusão de produtos (com categorias)
- Cadastro, edição e exclusão de funcionários
- Cadastro, edição e exclusão de vendas (vinculando clientes e funcionários)
- Visualização de listas e detalhes de cada entidade
- Autenticação de usuários (login e logout)
- Interface responsiva com Bootstrap

## Tecnologias Utilizadas
- **Flask**: Framework web em Python
- **MySQL**: Banco de dados relacional
- **HTML/CSS**: Estrutura e estilo das páginas
- **Bootstrap**: Design responsivo e componentes visuais

## Instruções de Instalação

### Pré-requisitos
- Python 3.x
- MySQL Server
- MySQL Connector para Python (`mysql-connector-python`)

### Instalação
1. Clone o repositório:
   ```
   git clone <repository-url>
   cd Petshop
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```
   python -m venv venv
   venv\Scripts\activate  # No Windows
   # ou
   source venv/bin/activate  # No Linux/Mac
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure o banco de dados MySQL:
   - Certifique-se de que o MySQL está rodando.
   - Execute o script `MySQL.sql` para criar as tabelas:
     ```
     mysql -u root -p < MySQL.sql
     ```
   - Ajuste as configurações de conexão no início do arquivo `app.py` conforme seu usuário e senha do MySQL.

### Executando a Aplicação
1. Inicie o servidor Flask:
   ```
   python app.py
   ```

2. Acesse no navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Uso
- Faça login ou registre-se.
- Utilize o menu para acessar clientes, pets, produtos, funcionários e vendas.
- Realize operações de cadastro, edição e exclusão conforme necessário.

## Observações
- O banco de dados deve estar criado e acessível antes de rodar a aplicação.
- O arquivo `requirements.txt` deve conter `flask`, `flask-session`, `mysql-connector-python` e outras dependências necessárias.
- As tabelas do banco de dados estão descritas no arquivo `MySQL.sql`.

## Licença
Não há informações sobre a licença deste projeto. Certifique-se de verificar as permissões de uso e distribuição.