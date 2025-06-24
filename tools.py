import json
from typing import List, Dict, Any, Optional
import os
from supabase import create_client, Client
from openai import OpenAI

def get_current_time():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %H:%M:%S")

def init_supabase_client() -> Client:
    """Initialize Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
    
    return create_client(supabase_url, supabase_key)

def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using OpenAI"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def store_document(content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Store a document with its embedding in Supabase"""
    try:
        supabase = init_supabase_client()
        
        # Generate embedding
        embedding = get_embedding(content)
        
        # Prepare document data
        doc_data = {
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {}
        }
        
        # Insert into Supabase
        result = supabase.table("documents").insert(doc_data).execute()
        
        return f"Document stored successfully with ID: {result.data[0]['id']}"
    
    except Exception as e:
        return f"Error storing document: {str(e)}"

def rag_query(query: str, limit: int = 5) -> str:
    """Perform RAG query: retrieve relevant documents and generate response"""
    try:
        supabase = init_supabase_client()
        
        # Generate embedding for the query
        query_embedding = get_embedding(query)
        
        # Perform similarity search using Supabase's vector search
        # Note: This requires pgvector extension and proper RPC function in Supabase
        result = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.7,
                "match_count": limit
            }
        ).execute()
        
        if not result.data:
            return "No relevant documents found for your query."
        
        # Extract content from retrieved documents
        contexts = []
        for doc in result.data:
            contexts.append(f"Document {doc['id']}: {doc['content']}")
        
        # Combine contexts
        combined_context = "\n\n".join(contexts)
        
        # Generate response using OpenAI with retrieved context
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""Based on the following context, please answer the question: {query}

Context:
{combined_context}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, please indicate that."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content or "No response generated"
    
    except Exception as e:
        return f"Error performing RAG query: {str(e)}"

tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current time in the US Central timezone",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "store_document",
            "description": "Store a document with embeddings in the Supabase vector database for later retrieval",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text content of the document to store"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata to associate with the document (e.g., title, source, tags)"
                    }
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rag_query",
            "description": "Perform a Retrieval Augmented Generation query to find relevant documents and generate an informed response",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or query to search for in the document database"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of documents to retrieve (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"],
            },
        },
    }
]

tool_functions = {
    "get_current_time": get_current_time,
    "store_document": lambda content, metadata=None: store_document(content, metadata),
    "rag_query": lambda query, limit=5: rag_query(query, limit)
}
