import streamlit as st
import pandas as pd
from preprocessing.scripts.graphModel import create_graph_app
from preprocessing.scripts.database_ingestion import (
    ingest_database, 
    get_user_id_from_db_url,
    check_user_data_exists,
    get_user_directories
)

st.set_page_config(layout="wide")
st.title("SQL Chatbot UI")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "db_url" not in st.session_state:
    st.session_state.db_url = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "app" not in st.session_state:
    st.session_state.app = None
if "ingestion_status" not in st.session_state:
    st.session_state.ingestion_status = None

with st.sidebar:
    st.header("Database Configuration")
    
    db_url_input = st.text_input(
        "Database URL",
        value=st.session_state.db_url or "",
        placeholder="postgresql://user:password@host:port/database"
    )
    
    if st.button("Connect & Process Database", type="primary"):
        if db_url_input:
            st.session_state.db_url = db_url_input
            user_id = get_user_id_from_db_url(db_url_input)
            st.session_state.user_id = user_id
            
            if check_user_data_exists(user_id):
                st.success(f"✅ Using existing data for this database!")
                st.session_state.ingestion_status = "exists"
            else:
                st.info("🔄 Processing database. This may take a few minutes...")
                
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                def progress_callback(status, message):
                    status_placeholder.info(f"**{status.upper()}**: {message}")
                
                result = ingest_database(db_url_input, progress_callback=progress_callback)
                
                if result["status"] == "success":
                    st.success(f"✅ Successfully processed {result['table_count']} tables!")
                    st.session_state.ingestion_status = "complete"
                    progress_placeholder.empty()
                    status_placeholder.empty()
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                    st.session_state.ingestion_status = "error"
                    progress_placeholder.empty()
                    status_placeholder.empty()
                    st.stop()
        else:
            st.warning("Please enter a database URL")
    
    if st.session_state.db_url:
        st.divider()
        st.subheader("Current Database")
        st.text(st.session_state.db_url[:50] + "..." if len(st.session_state.db_url) > 50 else st.session_state.db_url)
        if st.session_state.user_id:
            st.caption(f"User ID: {st.session_state.user_id}")

if st.session_state.db_url and st.session_state.ingestion_status in ["complete", "exists"]:
    if st.session_state.app is None:
        dirs = get_user_directories(st.session_state.user_id)
        st.session_state.app = create_graph_app(
            st.session_state.db_url,
            str(dirs["chroma_db"])
        )
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["type"] == "text":
                st.markdown(message["content"])
            elif message["type"] == "dataframe":
                st.dataframe(message["content"])

    if prompt := st.chat_input("Ask a question about the database..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.app.invoke({
                        "question": prompt, 
                        "retrieved_documents": [], 
                        "sql_answer": ""
                    })
                    sql_query = response.get("sql_answer", "No SQL query generated.")
                    ai_answer_raw = response.get("ai_answer", "No answer from SQL execution.")

                    st.markdown(f"**Generated SQL Query:**")
                    st.code(sql_query, language="sql")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "type": "text", 
                        "content": f"**Generated SQL Query:**\n```sql\n{sql_query}\n```"
                    })

                    if ai_answer_raw and isinstance(ai_answer_raw, list) and len(ai_answer_raw) > 0:
                        df = pd.DataFrame(ai_answer_raw)
                        st.markdown("**SQL Query Result:**")
                        st.dataframe(df)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "type": "dataframe", 
                            "content": df
                        })
                    else:
                        st.markdown("**SQL Query Result:** No data returned.")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "type": "text", 
                            "content": "**SQL Query Result:** No data returned."
                        })

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "type": "text", 
                        "content": f"An error occurred: {e}"
                    })
else:
    st.info("👋 Welcome! Please enter your database URL in the sidebar to get started.")
    st.markdown("""
    ### How to use:
    1. Enter your PostgreSQL database connection URL in the sidebar
    2. Click "Connect & Process Database"
    3. Wait for the database to be processed (first time only)
    4. Start asking questions about your database!
    
    **Note:** Each database gets its own isolated ChromaDB to prevent data mixing.
    """)
