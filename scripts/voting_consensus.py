import json
import re
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
# from sqlalchemy import create_engine,text
# from sqlalchemy.schema import CreateTable
from sqlalchemy import MetaData
import dotenv
from prompts import voting_loop_prompt
from dotenv import load_dotenv

load_dotenv()

os.environ['GOOGLE_API_KEY']=os.getenv('GOOGLE_API_KEY')

"""using table name table summary and table columns

example
description = f"{data['summary']} {data['dependencies_thoughts']}"

prompt_input = 
Table: {data['name']}
Columns: {columns}
Description: {description}
"""


model=ChatGoogleGenerativeAI(model='gemini-2.5-flash')

voting_loop_prompt=ChatPromptTemplate.from_template(voting_loop_prompt)

chain=voting_loop_prompt | model


raw_drafts=r"C:\Users\rawat\dartrix\Dartrix\preprocessing\raw_drafts"

dirs=os.listdir(raw_drafts)


## will make 3 llm guess this shit and most occurent word will be strong entitiy and least would be least entity would do this later on 
for i in dirs:
    file_path=os.path.join(raw_drafts,i)

    data=""

    with open(file_path,"r") as file:
        data=json.load(file)

    col_names = [c['column'] for c in data['columns']]
    columns_str = ", ".join(col_names)

    description_str = f"{data.get('summary', '')} {data.get('dependencies_thoughts', '')}"

    final_input = f"""
        Table: {data['name']}
        Columns: {columns_str}
        Context: {description_str}
        """
    
    answer=chain.invoke({'description':final_input})

    print(answer.content)

    print("-"*50)
    
    ## i also gotta merge the 2 existig raw_drafts.json and this answer.content

    raw_entities = answer.content.strip()

    clean_text = raw_entities.replace("\n", "").replace(".", "")

    entity_list = [e.strip() for e in clean_text.split(",") if e.strip()]

    data['strong_entities'] = entity_list

    with open(file_path,"w") as file:
        json.dump(data,file,indent=2)


    print("done for the fucking {i}.json")






        