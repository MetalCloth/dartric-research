"""
Reads DB schema, writes to Folder 1
"""


import json
import re
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine,text
from sqlalchemy.schema import CreateTable
from sqlalchemy import MetaData
import dotenv
from prompts import schema_architecture_prompt
from dotenv import load_dotenv

load_dotenv()

os.environ['GOOGLE_API_KEY']=os.getenv('GOOGLE_API_KEY')


model=ChatGoogleGenerativeAI(model='gemini-2.5-flash')
engine = create_engine("postgresql+psycopg2://postgres:19283746@localhost:5432/chinook")

schema_architecture_prompt=ChatPromptTemplate.from_template(schema_architecture_prompt)

chain= schema_architecture_prompt | model  

output_folder=r"C:\Users\rawat\dartrix\Dartrix\preprocessing\raw_drafts"


metadata = MetaData()
metadata.reflect(bind=engine)


## does one at a time but i will make it 10 at a time
for table in metadata.sorted_tables:
    print(f"Processing table: {table.name}...")
    
    content = CreateTable(table).compile(engine)
    
    answer = chain.invoke({'MESSY_DDL': content})
    raw_text = answer.content

    clean_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        if not clean_text:
            raise ValueError("AI returned empty string")

        json_data = json.loads(clean_text)

        if "name" not in json_data:
            json_data["name"] = table.name

        file_path = os.path.join(output_folder, f"{table.name}.json")
        with open(file_path, "w") as f:
            json.dump(json_data, f, indent=2)
            
        print(f"Saved: {table.name}.json")

    except json.JSONDecodeError as e:
        print(f"JSON ERROR on {table.name}: {e}")
        print(f"   Raw Content was: {raw_text[:200]}") 
    except Exception as e:
        print(f"GENERIC ERROR on {table.name}: {e}")

    print("-" * 50)