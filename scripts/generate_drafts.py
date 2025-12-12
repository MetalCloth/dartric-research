"""
Reads DB schema, writes to Folder 1
"""

"""ERD"""


import json
import re
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine,text
from sqlalchemy.schema import CreateTable
from sqlalchemy import MetaData,inspect
import dotenv
from prompts import schema_architecture_prompt
from dotenv import load_dotenv

load_dotenv()

os.environ['GOOGLE_API_KEY']=os.getenv('GOOGLE_API_KEY')

model=ChatGoogleGenerativeAI(model='gemini-2.5-flash')
DB_URL = "postgresql://postgres.ywftdjkjdchwmnmytrjj:shivanshkimkc@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DB_URL)

schema_architecture_prompt=ChatPromptTemplate.from_template(schema_architecture_prompt)

chain= schema_architecture_prompt | model  

output_folder=r"C:\Users\rawat\dartrix\Dartrix\preprocessing\supa_drafts"


metadata = MetaData()
metadata.reflect(bind=engine)

# ## does one at a time but i will make it 10 at a time
# for table_name in metadata.tables:
#     print(f"Processing table: {table_name}...")
    
#     # content = CreateTable(table).compile(engine)

#     if table_name in ['embeddings', 'embeddings_documents']:
#         continue

#     if table_name.startswith("pg_"):
#         continue

#     # print(content)
#     table = metadata.tables[table_name]
#     content = CreateTable(table).compile(engine)
    
#     answer = chain.invoke({'MESSY_DDL': content})
#     raw_text = answer.content

#     clean_text = re.sub(r"```json|```", "", raw_text).strip()

#     try:
#         if not clean_text:
#             raise ValueError("AI returned empty string")

#         json_data = json.loads(clean_text)

#         if "name" not in json_data:
#             json_data["name"] = table

#         # file_path = os.path.join(output_folder, f"{table.name}.json")
#         # with open(file_path, "w") as f:
#         #     json.dump(json_data, f, indent=2)

#         # print(json_data)
            
#         print(f"Saved: {table}.json")
#         break

#     except json.JSONDecodeError as e:
#         print(f"JSON ERROR on {table}: {e}")
#         print(f"   Raw Content was: {raw_text[:200]}") 
#     except Exception as e:
#         print(f"GENERIC ERROR on {table}: {e}")

#     print("-" * 50)


# # for table_name in metadata.tables:
                
# #                 # --- FILTERS ---
# #                 # Skip the AI tables (fixes NullType error)
# #                 if table_name in ['embeddings', 'embeddings_documents']:
# #                     continue
# #                 # Skip the Partition tables (noise)
# #                 # if "payment_p" in table_name:
# #                 #     continue
# #                 # Skip internal Postgres tables
# #                 if table_name.startswith("pg_"):
# #                     continue

# #                 # Generate DDL
# #                 table = metadata.tables[table_name]
# #                 ddl = CreateTable(table).compile(engine)
                
# #                 # Write to file
# #                 f.write(f"-- Table: {table_name}\n")
# #                 f.write(str(ddl).strip() + ";\n\n")
# #                 print(f"   Saved: {table_name}")



try:
    engine = create_engine(DB_URL)
    metadata = MetaData()
    

    metadata.reflect(bind=engine)
    print(f"✅ Connected! Found {len(metadata.tables)} tables.")
    f=0
    

    for table_name in metadata.tables:
        
        if table_name in ['embeddings', 'embeddings_documents']:
            continue

        if table_name.startswith("pg_"):
            continue


        table = metadata.tables[table_name]
        ddl = CreateTable(table).compile(engine)
        content=str(ddl).strip() + ";\n\n"
        print(f"-- Table: {table_name}\n")
        # print()
        answer=chain.invoke({'MESSY_DDL':content})
        raw_text=answer.content
        clean_text = re.sub(r"```json|```", "", raw_text).strip()
        json_data = json.loads(clean_text)

        file_path=os.path.join(output_folder,f"{table_name}.json")

        with open(file_path,"w") as f:
            json.dump(json_data,f,indent=2)

        print(f"   Saved: {table_name}")
        # break
        

except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Hint: If 'Name not known', change aws-0 to aws-1 in the db_host variable.")
