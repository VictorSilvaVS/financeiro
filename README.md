# 🚀 Financeiro - Secure Vault

Um sistema de gestão financeira pessoal de **alta segurança** e **extrema personalização**, projetado para quem busca controle total sobre seu dinheiro com privacidade absoluta.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Security](https://img.shields.io/badge/security-Argon2id%20%2B%20AES--128-red)
![Frontend](https://img.shields.io/badge/frontend-Vanilla%20JS%20%2B%20CSS-green)
![Backend](https://img.shields.io/badge/backend-FastAPI%20%2B%20SQLite-lightgrey)

---

## 🔐 Segurança Nível "Vault" (Absurdo)

Este sistema foi construído sob o princípio de **Defesa em Profundidade**. Diferente de apps comuns, aqui seus dados não estão apenas salvos; eles estão fortificados.

-   **Hashing de Senha Argon2id**: Vencedor do Password Hashing Competition, resistente a ataques de GPU e Side-channel.
-   **Criptografia de Dados em Repouso (AES-128 GCM)**: Campos sensíveis (descrições, valores, nomes de caixinhas e configurações) são encriptados usando Fernet antes de tocarem o banco de dados.
-   **Chave de Mestra Independente**: Uma `vault.key` é gerada fisicamente no servidor. Sem ela, o banco de dados é um amontoado de bytes inúteis.
-   **Autenticação JWT**: Sessões seguras e stateless.
-   **Rate Limiting**: Proteção contra ataques de força bruta integrada (SlowAPI).

## ✨ Funcionalidades Principais

-   **Dashboard Dinâmico**: Visualização de saldo, ganhos e despesas em tempo real.
-   **Personalização UI/UX Total**:
    *   **Temas**: Escolha sua cor de destaque (Primary Color).
    *   **Tipografia**: Seleção entre 4 estilos de fonte (Outfit, Roboto, Montserrat, Playfair).
    *   **Layout Flexível (LDR/RDL)**: Mude a barra lateral de lado com um clique.
-   **Globalização (i18n)**:
    *   **Multi-idioma**: Português, Inglês e Espanhol (incluindo dicas e citações).
    *   **Multi-moeda**: Suporte a Real (BRL), Dólar (USD), Euro (EUR), Libra (GBP) e Iene (JPY).
    *   **Formatação Cultural**: Formatos de milhar e decimal ajustados automaticamente por moeda (Ex: `,` vs `.` conforme o país).
-   **Sistema de Caixinhas**: Crie metas de reserva com barra de progresso e investimentos diretos.
-   **Configurações em Nuvem**: Suas preferências estéticas são salvas criptografadas no servidor.

## 🛠️ Stack Tecnológica

### Backend
-   **FastAPI**: Framework de alta performance.
-   **SQLAlchemy**: ORM para gestão de dados.
-   **Cryptography (Fernet)**: Para encriptação simétrica.
-   **Argon2-cffi**: Para hashing seguro.
-   **SlowAPI**: Para proteção de endpoints.

### Frontend
-   **Vanilla JS**: Lógica limpa e rápida sem frameworks pesados.
-   **Vanilla CSS**: Design moderno com Glassmorphism e animações 60fps.
-   **Google Fonts**: Tipografia premium integrada.
-   **Font Awesome**: Iconografia profissional.

---

## ⚙️ Instalação e Configuração

### 1. Pré-requisitos
-   Python 3.8+
-   Pip (gestor de pacotes)

### 2. Configuração do Ambiente
Crie um arquivo `.env` na raiz do projeto conforme o modelo abaixo:

```env
SECRET_KEY=sua_chave_secreta_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./secure_vault.db
VAULT_KEY_PATH=vault.key
STATIC_DIR=static
TEMPLATES_DIR=templates
HOST=0.0.0.0
PORT=8000
```

### 3. Rodar o Sistema
Na primeira execução, o sistema gerará a `vault.key` e o banco de dados automaticamente.

```bash
python main.py
```

### 4. Backup (Importante!)
**Mantenha seu arquivo `vault.key` seguro.** Se você perdê-lo, não será possível descriptografar os dados do banco de dados, mesmo tendo a senha do usuário.

---

## 📄 Licença
Este projeto é de uso público e focado em segurança máxima. 

**Financeiro- Controle absoluto, segurança absurda.**
