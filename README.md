# 🚀 Financeiro - Secure Vault

Um sistema de gestão financeira pessoal de **alta segurança** e **extrema personalização**, projetado para quem busca controle total sobre seu dinheiro com privacidade absoluta.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Security](https://img.shields.io/badge/security-Argon2id%20%2B%20AES--256--GCM%20%2B%20Integrity-red)
![Frontend](https://img.shields.io/badge/frontend-Vanilla%20JS%20%2B%20CSS-green)
![Backend](https://img.shields.io/badge/backend-FastAPI%20%2B%20SQLite-lightgrey)

---

## 🔐 Segurança Nível "Absolute Zero" (Fortaleza de Infraestrutura)

Este sistema foi refatorado para eliminar falhas lógicas e gargalos de performance, atingindo um padrão de arquitetura de segurança de elite:

-   **Argon2id (ASIC-Resistant)**: Configurado com `time_cost=4`, `memory_cost=100MB` e `parallelism=8`. Parâmetros que superam os padrões da OWASP para máxima resistência contra ataques de dicionário e hardware especializado.
-   **Integridade via Tag GCM (Galois/Counter Mode)**: Abandonamos o hash de arquivo externo (que causava gargalos de I/O) em favor da verificação em tempo real via hardware. Cada campo criptografado possui sua própria tag de autenticação AES-256. Se **um único bit** for alterado no banco de dados, a CPU detecta instantaneamente e bloqueia a leitura.
-   **Master Secret Híbrido (RAM & Disk)**: O sistema utiliza o segredo mestre para derivar as chaves de encriptação. Você pode configurar via variável de ambiente `VAULT_MASTER_SECRET` no seu arquivo `.env` ou utilizar o arquivo físico `vault.key`. O sistema prioriza o ambiente, mas garante a existência do arquivo para facilitar backups físicos.
-   **Derivação de Chave via HKDF v3**: Utilizamos o padrão HKDF (HMAC-based Key Derivation) para expandir o segredo mestre em uma chave de criptografia de 256 bits robusta.
-   **Middleware de Proteção de Camada 7**:
    *   **Content-Security-Policy (CSP)**: Bloqueia injeções de scripts externos maliciosos.
    *   **X-Frame-Options (DENY)**: Previne ataques de Clickjacking.
    *   **X-Content-Type-Options (nosniff)**: Impede que o navegador tente "adivinhar" tipos de arquivos, mitigando ataques de Sniffing.
-   **Autenticação JWT & Rate Limiting**: Sessões efêmeras e proteção contra brute-force integrada.
-   **Autenticação JWT**: Sessões seguras e stateless.
-   **Rate Limiting**: Proteção contra ataques de força bruta integrada (SlowAPI).

## Funcionalidades Principais

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

## Stack Tecnológica

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

## Instalação e Configuração

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

## Licença
Este projeto é de uso público e focado em segurança máxima. 

**Financeiro- Controle absoluto, segurança absurda.**
