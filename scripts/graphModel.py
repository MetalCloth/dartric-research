from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langgraph.graph import START, END, StateGraph
from ..prompts import reranking_prompt, reranked_prompt
from langchain_core.documents import Document
from sqlalchemy import create_engine, text
from typing import TypedDict, Optional, List

load_dotenv()

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

embedding_model = GoogleGenerativeAIEmbeddings(model='gemini-embedding-001')
model = ChatGoogleGenerativeAI(model='gemini-2.5-flash')


def clean_sql(text):
    cleaned = text.replace("```sql", "").replace("```", "").strip()
    return cleaned


class AgentState(TypedDict):
    question: str
    retrieved_documents: List[Document]
    wastage: Optional[str]
    reranked_docs: Optional[str]
    ai_answer: Optional[str]
    sql_answer: str


def create_graph_app(db_url: str, chroma_db_path: str):
    engine = create_engine(db_url)
    vectordb = Chroma(
        embedding_function=embedding_model,
        persist_directory=chroma_db_path
    )
    
    def call_retriever(state: AgentState):
        print("CALLING RETRIEVER \n")
        question = state['question']
        retrieved_info = vectordb.similarity_search_with_score(question, k=7)
        state['retrieved_documents'] = retrieved_info
        return state

    def format_docs(state: AgentState):
        print("FORMATTING DOC \n")
        retrieved_docs = state['retrieved_documents']
        buffer = {}

        for docs, score in retrieved_docs:
            table_id = docs.metadata['parent_id']
            table_content = docs.page_content

            if table_id not in buffer:
                buffer[table_id] = []

            buffer[table_id].append(table_content)
        
        context_string = ""
        for table_id, content in buffer.items():
            clean_name = table_id.replace('table_', '')
            context_string += f"--- TABLE: {clean_name} ---\n"
            context_string += "\n".join(content)
            context_string += "\n\n"

        state['wastage'] = context_string
        return state

    def reranking_retrieval(state: AgentState):
        print("RERANKING RETRIEVER \n")
        prompt = ChatPromptTemplate.from_template(reranking_prompt)
        chain = prompt | model
        reranked_docs = chain.invoke({
            'user_question': state['question'],
            'table_schemas': state['wastage']
        })
        state['reranked_docs'] = reranked_docs.content
        return state
    
    def agent_calling(state: AgentState):
        print("CALLING AGENT \n")
        prompt = ChatPromptTemplate.from_template(reranked_prompt)
        chain = prompt | model
        sql_response = chain.invoke({
            'user_question': state['question'],
            'reranked_list_json': state['reranked_docs'],
            'formatted_buffer': state['wastage']
        })
        state['sql_answer'] = sql_response.content
        return state
    
    def returning_sql(state: AgentState):
        print("INVOKING SQL")
        cleaned_sql = clean_sql(state['sql_answer'])

        with engine.connect() as conn:
            result = conn.execute(text(cleaned_sql))
            column_names = result.keys()
            rows = result.fetchall()
            ai_answer = [dict(zip(column_names, row)) for row in rows]
            print(f"Fetched {len(ai_answer)} rows")

        state['ai_answer'] = ai_answer
        return state
    
    graph = StateGraph(AgentState)

    graph.add_node('invoke_retrieval', call_retriever)
    graph.add_node('format_docs', format_docs)
    graph.add_node('rerank_docs', reranking_retrieval)
    graph.add_node('invoke_agent', agent_calling)
    graph.add_node('returning_sql', returning_sql)

    graph.add_edge(START, 'invoke_retrieval')
    graph.add_edge('invoke_retrieval', 'format_docs')
    graph.add_edge('format_docs', 'rerank_docs')
    graph.add_edge('rerank_docs', 'invoke_agent')
    graph.add_edge('invoke_agent', 'returning_sql')
    graph.add_edge('returning_sql', END)

    return graph.compile()


DEFAULT_DB_URL = "postgresql://postgres.ywftdjkjdchwmnmytrjj:shivanshkimkc@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
DEFAULT_CHROMA_PATH = r'C:\Users\rawat\dartrix\Dartrix\preprocessing\scripts\brain_db'

app = create_graph_app(DEFAULT_DB_URL, DEFAULT_CHROMA_PATH)

if __name__ == '__main__':
    question = input("Enter your question")
    response = app.invoke({'question': question, 'retrieved_documents': [], 'sql_answer': ''})
    print(response['sql_answer'])
    print(response['ai_answer'])
