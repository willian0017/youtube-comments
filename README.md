# YouTube Comments Extractor

Aplicação web para buscar, filtrar, selecionar e exportar comentários de vídeos do YouTube.

---

## 🚀 Funcionalidades

- 🔍 **Busca por URL**: Extração de comentários fornecendo diretamente o link do vídeo do YouTube.
- 🔢 **Limite Configurável**: Definição da quantidade máxima de comentários a serem recuperados.
- 🔀 **Ordenação**:
  - Mais relevantes (`relevance`)
  - Mais recentes (`time`)
- 👍 **Métricas**: Exibição da contagem de curtidas de cada comentário.
- ☑️ **Seleção de Comentários**:
  - Seleção individual
  - Seleção ou desmarcação em massa (*Select/Deselect All*)
- 🧹 **Filtros Avançados (Opcionais)**:
  - Remover comentários compostos apenas por emojis
  - Remover comentários vazios
  - Remover comentários contendo links/URLs
  - Remover comentários duplicados
- 📊 **Exportação para Excel**:
  - Exportação dos comentários selecionados para formato `.xlsx`
  - Links diretos para cada comentário inclusos na planilha
- 📱 **Interface Responsiva**: Design adaptado para telas mobile e desktop.
- 🐳 **Pronto para Docker**: Configuração simplificada via Docker Compose.

---

## 🛠️ Tecnologias

### Frontend
- **Next.js** (React)
- **TypeScript**
- **Tailwind CSS**

### Backend
- **Python 3.13+**
- **FastAPI**
- **Google YouTube Data API v3**
- **OpenPyXL**

### Infraestrutura
- **Docker** & **Docker Compose**

---

## 📁 Estrutura do Projeto

```text
youtube-comments/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   └── services/
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── types/
│   ├── .env.example
│   ├── Dockerfile
│   └── .dockerignore
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 📋 Requisitos Prévios

Antes de começar, certifique-se de ter instalado em sua máquina:
- **Node.js**: v22+
- **Python**: v3.13+
- **Docker Desktop** (opcional, para execução via containers)
- Uma chave válida da **YouTube Data API v3** ([Google Cloud Console](https://console.cloud.google.com/))

---

## ⚙️ Configuração de Ambiente

### 1. Backend

Crie um arquivo `.env` na pasta `backend/`:

```env
YOUTUBE_API_KEY=sua_api_key_aqui
```

### 2. Frontend

Crie um arquivo `.env.local` na pasta `frontend/`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> ⚠️ **Atenção:** Os arquivos `.env` e `.env.local` contêm dados sensíveis e **não** devem ser commitados no Git. Use apenas os arquivos `.env.example` como referência.

---

## 🐳 Executando com Docker (Recomendado)

Na raiz do projeto, execute:

```bash
docker compose up --build
```

Acesse os serviços nos seguintes endereços:
- 💻 **Frontend**: http://localhost:3000
- ⚙️ **Backend**: http://localhost:8000
- 📖 **Documentação Interativa (Swagger)**: http://localhost:8000/docs

Para parar e remover os containers:

```bash
docker compose down
```

---

## 💻 Executando sem Docker

### Backend

1. Navegue até o diretório do backend:
   ```bash
   cd backend
   ```

2. Crie e ative um ambiente virtual:
   - **Windows:**
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicie o servidor FastAPI:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

### Frontend

1. Em outro terminal, navegue até a pasta do frontend:
   ```bash
   cd frontend
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

4. Acesse a aplicação em: http://localhost:3000

---

## 🔌 Endpoints da API

### 1. Buscar Comentários
`POST /youtube/comments`

**Exemplo de Payload:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "max_comments": 100,
  "remove_emoji_only": true,
  "remove_empty": true,
  "remove_links": false,
  "remove_duplicates": false,
  "order": "relevance"
}
```

---

### 2. Exportar para Excel
`POST /export/excel`

Gera um arquivo `.xlsx` contendo as seguintes colunas:
- **Autor**
- **Comentário**
- **Curtidas**
- **Data**
- **Link do comentário**

---

## 🛡️ Segurança

- Nunca publique ou comite chaves de API para repositórios públicos (GitHub/GitLab).
- Certifique-se de que os seguintes arquivos estejam listados no seu `.gitignore`:
  - `.env`
  - `.env.local`
  - `.env.production`

---

## ⚠️ Limitações

- A aplicação está sujeita às cotas e limites impostos pela **YouTube Data API v3**.
- Vídeos com comentários desativados, privados ou indisponíveis não retornarão dados.
- O volume total de comentários depende da quantidade retornada diretamente pela API do YouTube.

---

## 📄 Licença

Este projeto é de uso pessoal e educacional.
