# Sistema de Cantina FuraFila

Sistema web moderno para gerenciamento de cantina com interface intuitiva e funcionalidades completas.

## Funcionalidades

### Para Clientes
- Visualização do cardápio em tempo real
- Fazer pedidos online
- Acompanhar status dos pedidos
- Sistema de carrinho de compras

### Para Estudantes
- Todas as funcionalidades de cliente
- **10% de desconto automático** em todos os pedidos
- Cadastro com matrícula

### Para Funcionários
- Aprovar/negar pedidos
- Gerenciar estoque dos itens
- Abrir/fechar cantina
- Visualizar pedidos pendentes

### Para Gerentes
- Todas as funcionalidades de funcionário
- Gerenciar usuários do sistema
- Adicionar/remover itens do cardápio
- Editar pedidos antes da aprovação
- Controle administrativo completo

## Tecnologias Utilizadas

- **Backend**: Python + Flask
- **Banco de Dados**: SQLite com WAL mode
- **Frontend**: HTML5 + TailwindCSS + Alpine.js
- **Arquitetura**: MVC com padrão DAO

## Instalação e Execução

1. **Clone o projeto**
   ```
   git clone https://github.com/YanAdriel01/cantina-furafila
   ```

2. **Instale as dependências**
   ```
   pip install flask
   ```

3. **Execute o sistema**
   ```
   python app.py
   ```

4. **Acesse no navegador**
   - URL: `http://localhost:5000`
   - O banco de dados será criado automaticamente na primeira execução

## Credenciais de Teste

- **👨‍💼 Gerente**: admin@admin.com / admin123
- **👷 Funcionário**: funcionario@funcionario.com / funcionario123
- **👤 Cliente**: cliente@cliente.com / cliente123
- **🎓 Estudante**: estudante@estudante.com / estudante123

## Estrutura do Projeto

```
cantina-furafila/
├── app.py                 # Aplicação principal
├── config/               # Configurações
├── database/            # Gerenciamento de dados
│   ├── dao/            # Data Access Objects
│   └── database_manager.py
├── models/             # Modelos de negócio
├── routes/             # Rotas da aplicação
├── templates/          # Templates HTML
├── utils/              # Utilitários
└── README.md
```
