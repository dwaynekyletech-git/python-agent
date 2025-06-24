# Python Agent with RAG

A Python-based AI agent with OpenAI integration and Retrieval Augmented Generation (RAG) capabilities using Supabase.

## Features

- **AI Chat Agent**: Interactive chat with GPT-4
- **Tool System**: Extensible tool framework
- **RAG Integration**: Store and retrieve documents with semantic search
- **Vector Database**: Supabase with pgvector for embeddings

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Supabase Database Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Go to the SQL Editor in your Supabase dashboard
3. Run the SQL commands from `supabase_setup.sql` to create the necessary tables and functions
4. Make sure the pgvector extension is enabled

### 4. Run the Agent

```bash
python main.py
```

## Available Tools

- **get_current_time**: Returns current time in US Central timezone
- **store_document**: Store documents with embeddings for RAG
- **rag_query**: Query the document database with semantic search

## Usage Examples

### Storing Documents
```
You: Store this document: "Python is a high-level programming language known for its simplicity and readability."
```

### RAG Queries
```
You: What do you know about Python programming?
```

The agent will automatically use the RAG system to find relevant documents and provide informed responses.

## RAG System Details

The RAG system uses:
- **OpenAI text-embedding-3-small** for generating embeddings
- **Supabase + pgvector** for vector storage and similarity search
- **Cosine similarity** for finding relevant documents
- **GPT-4** for generating responses based on retrieved context

## Database Schema

The `documents` table stores:
- `id`: Primary key
- `content`: Document text content
- `embedding`: Vector embedding (1536 dimensions)
- `metadata`: Optional JSON metadata
- `created_at`: Timestamp

## Customization

You can extend the system by:
- Adding new tools in `tools.py`
- Modifying the RAG parameters (similarity threshold, result count)
- Adding document preprocessing or chunking
- Implementing different embedding models