"""Make an embedding for the SQL query things like to make and local embedding"""
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json
from langchain_core.documents import Document

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
load_dotenv()
from upload_to_vector import generate_embeddings


os.environ['GOOGLE_API_KEY']=os.getenv('GOOGLE_API_KEY')


model=GoogleGenerativeAIEmbeddings(model='gemini-embedding-001')
vectordb=Chroma(embedding_function=model,persist_directory='./chroma_db')
# print(model.invoke("HI I AM GAY"))



def embed_documents(file_path):
    print(file_path)
    """Embed the documents into the fuckng chromadb blud"""
    with open(file_path,'r') as file:
        content=json.load(file)

        docs=generate_embeddings(content)
    
    # print(docs[0])

    


    for i in docs:
        # Document(page_content=i
        x=Document(page_content=i.page_content,metadata=i.metadata)
        # print(i.page_content)
        # break
        vectordb.add_documents([x])

    print("DONE BLUD")


if __name__=='__main__':

    raw_draft_path=r'C:\Users\rawat\dartrix\Dartrix\preprocessing\raw_drafts'

    dirs=os.listdir(raw_draft_path)
    
    for i in dirs:
        path=os.path.join(raw_draft_path,i)
        embed_documents(path)





