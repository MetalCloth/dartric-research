"""I will make a connection between Retrieval and the LLM TO GENERATE SQL QUERY THE LAST STEP FOR THIS DEMO DARTRIX"""
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
import os
from langchain_core.prompts import ChatPromptTemplate
# from ai_core.prompts import conditional_prompt,summarizing_prompt,chat_prompt,fucking_summarizer
from dotenv import load_dotenv
from langchain import tools
from langchain_chroma import Chroma
from langgraph.graph import START,END,StateGraph
from prompts import reranking_prompt,reranked_prompt
from langchain_core.documents import Document
# from database.vectorstore import Retriever,Store
# from ai_core.utils import PreProcessing
from sqlalchemy import create_engine,text
from typing import TypedDict,Optional,List,Dict,Any

from pydantic import BaseModel
load_dotenv()

# engine = create_engine("postgresql+psycopg2://postgres:19283746@localhost:5432/chinook")
DB_URL = "postgresql://postgres.ywftdjkjdchwmnmytrjj:shivanshkimkc@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DB_URL)


def clean_sql(text):
    """Removes markdown formatting like ```sql and ```"""
    cleaned = text.replace("```sql", "").replace("```", "").strip()
    return cleaned

os.environ['GOOGLE_API_KEY']=os.getenv('GOOGLE_API_KEY')


embedding_model=GoogleGenerativeAIEmbeddings(model='gemini-embedding-001')

model=ChatGoogleGenerativeAI(model='gemini-2.5-flash')

vectordb=Chroma(embedding_function=embedding_model,persist_directory=r'C:\Users\rawat\dartrix\Dartrix\preprocessing\scripts\brain_db')


class AgentState(TypedDict):
    question:str
    retrieved_documents:List[Document]
    wastage:Optional[str]
    reranked_docs:Optional[str]
    ai_answer:Optional[str]
    sql_answer:str


def call_retriever(state:AgentState):
    print("CALLING RETRIEVER \n")
    question=state['question']

    retrieved_info=vectordb.similarity_search_with_score(question,k=7)

    state['retrieved_documents']=retrieved_info

    # print(retrieved_info)

    return state


def format_docs(state:AgentState):

    """According to the paper it is said to merge the retrieval shits on basis of table name"""
    print("FORMATTING DOC \n")
    retrieved_docs=state['retrieved_documents']

    buffer={}

    for docs,score in retrieved_docs:
        table_id=docs.metadata['parent_id']

        table_content=docs.page_content

        if table_id not in buffer:
            buffer[table_id]=[]

        buffer[table_id].append(table_content)
    
    context_string=""

    for table_id,content in buffer.items():
        clean_name = table_id.replace('table_', '')
        context_string += f"--- TABLE: {clean_name} ---\n"
        context_string += "\n".join(content)
        context_string += "\n\n"

    state['wastage']=context_string

    return state


def reranking_retrieval(state:AgentState):
    """According to the paper it is said to merge the retrieval shits on basis of table name"""
    print("RERANKING RETRIEVER \n")

    prompt=ChatPromptTemplate.from_template(reranking_prompt)

    chain=prompt | model

    reranked_docs=chain.invoke({'user_question':state['question'],'table_schemas':state['wastage']})

    state['reranked_docs']=reranked_docs.content

    return state

def agent_calling(state:AgentState):
    """Converts llm call to SQL"""

    print("CALLING AGENT \n")


    prompt=ChatPromptTemplate.from_template(reranked_prompt)

    chain= prompt | model

    sql_respone=chain.invoke({'user_question':state['question'],'reranked_list_json':state['reranked_docs'],'formatted_buffer':state['wastage']})

    state['sql_answer']=sql_respone.content

    return state

def returning_sql(state:AgentState):
    """Invoking the SQL"""

    print("INVOKING SQL")

    cleaned_sql=clean_sql(state['sql_answer'])

    ai_answer=[]


    with engine.connect() as conn:
        # 'text()' is required by SQLAlchemy for raw strings
        result = conn.execute(text(cleaned_sql))

        for r in result:
            print(r)
        
        # Print results
        ai_answer=result

    
    state['ai_answer']=ai_answer
    return state




graph=StateGraph(AgentState)

graph.add_node('invoke_retrieval',call_retriever)

graph.add_node('format_docs',format_docs)

graph.add_node('rerank_docs',reranking_retrieval)

graph.add_node('invoke_agent',agent_calling)

graph.add_node('returning_sql',returning_sql)

graph.add_edge(START,'invoke_retrieval')

graph.add_edge('invoke_retrieval','format_docs')

graph.add_edge('format_docs','rerank_docs')

graph.add_edge('rerank_docs','invoke_agent')

graph.add_edge('invoke_agent','returning_sql')

graph.add_edge('returning_sql',END)

app=graph.compile()

if __name__=='__main__':
    question=input("ENter your question")

    response=app.invoke({'question':question,'retrieved_documents':[],'sql_answer':''})

    print(response['sql_answer'])
    print(response['ai_answer'])