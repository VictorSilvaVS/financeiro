# 🚀 Financeiro - Secure Vault

Um sistema de gestão financeira pessoal de **alta segurança** e **extrema personalização**, projetado para quem busca controle total sobre seu dinheiro com privacidade absoluta.

![Version](https://img.shields.io/badge/version-4.0.0-blue)
![Security](https://img.shields.io/badge/security-Atomic%20Cryptography%20%2B%20AES--256--GCM%20%2B%20HMAC-red)
![Frontend](https://img.shields.io/badge/frontend-Vanilla%20JS%20%2B%20CSS-green)
![Backend](https://img.shields.io/badge/backend-FastAPI%20%2B%20SQLite-lightgrey)

---

## 🔐 Segurança Nível "Atomic Fortress" (Arquitetura Inviolável)

Este sistema foi refatorado para o padrão de segurança atômica, onde cada registro é uma unidade independente e verificável:

-   **Criptografia Atômica (HMAC-SHA256)**: Cada transação e caixinha possui um token de integridade único. Se **um único bit** for alterado manualmente no banco de dados, o Vault detecta a violação e tranca o acesso instantaneamente.
-   **Vínculo Físico de Estado (AAD)**: Utilizamos *Additional Authenticated Data* para prender a criptografia aos metadados do usuário (username e hash de senha). Isso significa que os dados não podem ser movidos para outro usuário ou descriptografados se a senha for alterada externamente no DB.
-   **Argon2id (ASIC-Resistant)**: Hashing de senha com proteção contra hardware especializado (GPUs/ASICs).
-   **Master Secret Híbrido (RAM & Disk)**: O sistema utiliza um segredo mestre derivado para gerar chaves de 256 bits. Pode ser injetado via `VAULT_MASTER_SECRET` (RAM) ou lido do arquivo `vault.key`.
-   **Zero-Knowledge & HKDF v3**: O servidor nunca conhece sua chave de cifragem final; ela é derivada em tempo real usando HKDF (HMAC-based Key Derivation).
-   **Proteção de Camada 7 (Hardened Headers)**:
    *   **CSP (Content-Security-Policy)**: Bloqueia XSS.
    *   **X-Frame-Options**: Impede Clickjacking.
    *   **HSTS**: Força comunicações seguras.

## Funcionalidades Principais

-   **Dashboard Dinâmico**: Visualização de saldo, ganhos e despesas em tempo real.
-   **Personalização UI/UX Total**:
    *   **Temas**: Escolha sua cor de destaque (Primary Color).
    *   **Tipografia**: Seleção entre fontes premium (Outfit, Roboto, Montserrat, Playfair).
    *   **Layout Adaptativo**: Barra lateral alternável (Esquerda/Direita).
-   **Globalização (i18n)**:
    *   **Multi-idioma**: Português, Inglês e Espanhol.
    *   **Multi-moeda**: BRL, USD, EUR, GBP, JPY com formatação cultural automática.
-   **Sistema de Caixinhas**: Gestão de metas com barras de progresso e depósitos atômicos.
-   **Configurações em Nuvem**: Suas preferências visuais são salvas de forma criptografada.

## Stack Tecnológica

### Backend
-   **FastAPI**: Performance extrema e tipagem robusta.
-   **SQLAlchemy**: Gestão de dados via ORM.
-   **Cryptography (AES-GCM)**: Padrão ouro de encriptação autenticada.
-   **SlowAPI**: Proteção contra força bruta (Rate Limiting).

### Frontend
-   **Vanilla JS & CSS**: Performance de 60fps sem dependências pesadas.
-   **Glassmorphism Design**: Interface moderna e premium.

---

## Instalação e Configuração

### 1. Configuração do Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua_chave_jwt_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./secure_vault.db
VAULT_MASTER_SECRET=seu_segredo_mestre_hex_64_chars
STATIC_DIR=static
TEMPLATES_DIR=templates
HOST=0.0.0.0
PORT=8000
```

### 2. Rodar o Sistema
```bash
# Sincroniza o banco de dados com a nova segurança atômica
python migrate.py

# Inicia o Vault
python main.py
```

### 3. Backup (Crítico!)
**Guarde seu `vault.key`.** Sem ele ou o segredo no `.env`, seus dados tornam-se lixo digital indecifrável.

---

## Licença
Este sistema é focado em privacidade absoluta e controle total do usuário.

**Financeiro - Segurança Atômica, Privacidade Absoluta.**
