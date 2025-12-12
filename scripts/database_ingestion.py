"""
Automated Database Ingestion Pipeline
Takes a database URL, processes it, and creates user-specific embeddings
"""
import json
import re
import os
import hashlib
import uuid
from pathlib import Path
from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import CreateTable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
import time

from .upload_to_vector import generate_embeddings
from ..prompts import schema_architecture_prompt

load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

# Base directories for user data
BASE_DIR = Path(__file__).parent.parent.parent
USER_DATA_DIR = BASE_DIR / "user_data"


def get_user_id_from_db_url(db_url: str) -> str:
    """Generate a unique user ID from database URL"""
    # Create a hash of the DB URL to get a consistent user ID
    hash_obj = hashlib.md5(db_url.encode())
    return hash_obj.hexdigest()[:16]


def get_user_directories(user_id: str) -> dict:
    """Get all directory paths for a specific user"""
    user_dir = USER_DATA_DIR / user_id
    return {
        "base": user_dir,
        "drafts": user_dir / "drafts",
        "chroma_db": user_dir / "chroma_db"
    }


def ensure_user_directories(user_id: str) -> dict:
    """Create user directories if they don't exist"""
    dirs = get_user_directories(user_id)
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    return dirs


def ingest_database(db_url: str, progress_callback=None) -> dict:
    """
    Main ingestion function that processes a database and creates embeddings
    
    Args:
        db_url: Database connection URL
        progress_callback: Optional callback function(status, message) for progress updates
    
    Returns:
        dict with user_id, status, and paths
    """
    try:
        # Generate user ID from DB URL
        user_id = get_user_id_from_db_url(db_url)
        dirs = ensure_user_directories(user_id)
        
        if progress_callback:
            progress_callback("connecting", f"Connecting to database...")
        
        # Step 1: Connect to database and extract schema
        engine = create_engine(db_url)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        table_count = len([t for t in metadata.tables 
                          if t not in ['embeddings', 'embeddings_documents'] 
                          and not t.startswith('pg_')])
        
        if progress_callback:
            progress_callback("extracting", f"Found {table_count} tables. Extracting schema...")
        
        # Step 2: Generate JSON drafts for each table
        model = ChatGoogleGenerativeAI(model='gemini-2.5-flash')
        schema_prompt = ChatPromptTemplate.from_template(schema_architecture_prompt)
        chain = schema_prompt | model
        
        processed_tables = 0
        for table_name in metadata.tables:
            # Skip system tables
            if table_name in ['embeddings', 'embeddings_documents']:
                continue
            if table_name.startswith("pg_"):
                continue
            
            try:
                table = metadata.tables[table_name]
                ddl = CreateTable(table).compile(engine)
                content = str(ddl).strip() + ";\n\n"
                
                if progress_callback:
                    progress_callback("processing", f"Processing table: {table_name} ({processed_tables + 1}/{table_count})")
                
                # Generate JSON documentation
                answer = chain.invoke({'MESSY_DDL': content})
                raw_text = answer.content
                clean_text = re.sub(r"```json|```", "", raw_text).strip()
                json_data = json.loads(clean_text)
                
                # Save to user-specific drafts folder
                file_path = dirs["drafts"] / f"{table_name}.json"
                with open(file_path, "w") as f:
                    json.dump(json_data, f, indent=2)
                
                processed_tables += 1
                time.sleep(0.5)  # Rate limiting
                
            except json.JSONDecodeError as e:
                if progress_callback:
                    progress_callback("warning", f"JSON error on {table_name}: {str(e)[:100]}")
                continue
            except Exception as e:
                if progress_callback:
                    progress_callback("warning", f"Error processing {table_name}: {str(e)[:100]}")
                continue
        
        if progress_callback:
            progress_callback("embedding", f"Creating embeddings for {processed_tables} tables...")
        
        # Step 3: Create embeddings and store in ChromaDB
        embedding_model = GoogleGenerativeAIEmbeddings(model='gemini-embedding-001')
        vectordb = Chroma(
            embedding_function=embedding_model,
            persist_directory=str(dirs["chroma_db"])
        )
        
        # Process all JSON files and create embeddings
        json_files = list(dirs["drafts"].glob("*.json"))
        total_files = len(json_files)
        
        for idx, json_file in enumerate(json_files):
            try:
                if progress_callback:
                    progress_callback("embedding", f"Embedding {json_file.stem} ({idx + 1}/{total_files})")
                
                with open(json_file, 'r') as f:
                    content = json.load(f)
                
                docs = generate_embeddings(content)
                
                for doc in docs:
                    vectordb.add_documents([doc])
                
                time.sleep(1)  # Rate limiting for API
                
            except Exception as e:
                if progress_callback:
                    progress_callback("warning", f"Error embedding {json_file.stem}: {str(e)[:100]}")
                continue
        
        if progress_callback:
            progress_callback("complete", f"Successfully processed {processed_tables} tables!")
        
        return {
            "user_id": user_id,
            "status": "success",
            "table_count": processed_tables,
            "chroma_db_path": str(dirs["chroma_db"]),
            "drafts_path": str(dirs["drafts"]),
            "db_url": db_url
        }
        
    except Exception as e:
        error_msg = str(e)
        if progress_callback:
            progress_callback("error", f"Ingestion failed: {error_msg}")
        return {
            "user_id": user_id if 'user_id' in locals() else None,
            "status": "error",
            "error": error_msg
        }


def check_user_data_exists(user_id: str) -> bool:
    """Check if user data already exists (ingestion already done)"""
    dirs = get_user_directories(user_id)
    chroma_db_path = dirs["chroma_db"]
    # Check if ChromaDB exists and has data
    return chroma_db_path.exists() and (chroma_db_path / "chroma.sqlite3").exists()

