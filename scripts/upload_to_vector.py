"""So according to the dartrics research paper it is mentioned to embedd the table as a multiple parts of the table to get the best info 
about the things in the table like

# --- 1. Full Documentation View ---
    # The "Kitchen Sink": Good for general, broad queries.

# --- 2. Dependency & Relationship View ---
    # Focus: How tables link (Foreign Keys). Good for "Join" questions.
    # e.g. "How do I link albums to artists?"

# --- 3. Table Metadata View ---
    # Focus: Technical specs. Good for "What columns exist?" questions.


# --- 4. Connected Tables View ---
    # Focus: Direct associations. Good for identifying neighbors.

# --- 5. Entity Relationship View (Concepts) ---
    # Focus: High-level concepts. Good for non-technical questions.
    # e.g. "Find songs by this singer" (matches "Artist" entity)


❌ Too many redundant vectors

❌ Embedding conflicts

❌ Multi-hop confusion

❌ Retrieval noise

❌ Hallucinations in SQL

BUT IT FEELS BLOATED AND UNNECESSARY SO I MADE MY OWN :)



"""

from langchain_core.documents import Document


def generate_embeddings(table_json):
    """using 5 embedding technique from the research paper"""

    table_name=table_json['name']
    

    parent_id=f"table_{table_name}"

    docs=[]

    content=f"TABLE:{table_name}. SUMMARY: {table_json['summary']}. PURPOSE: {table_json['purpose']}. DEPENDENCIES: {table_json['dependencies_thoughts']}"

    ## 1st type of embedding Full Documentation View
    docs.append(
        Document(
            page_content=content,
            metadata={"parent_id":parent_id,"type":"full_docs"}
        )
    )

    ## 2nd type of embeddings Dependency & Relationship View
    docs.append(
        Document(
            page_content=f"DEPENDENCIES FOR {table_name}: {table_json['dependencies_thoughts']}. KEYS: {', '.join(table_json['keys'])}",
            metadata={"parent_id": parent_id, "type": "dependencies"}
    ))

    ## 3rd type of embeddings Table Metadata View
    col_list = ", ".join([f"{c['column']} ({c.get('type', 'N/A')})" for c in table_json['columns']])
    docs.append(
        Document(
            page_content=f"METADATA {table_name}: COLUMNS: {col_list}",
            metadata={"parent_id": parent_id, "type": "metadata"}
    ))

    ## 4th type of embeddings Connected Tables View
    docs.append(
        Document(
            page_content=f"CONNECTIONS {table_name}: CONNECTED TO {', '.join(table_json['connected_tables'])}",
            metadata={"parent_id": parent_id, "type": "connections"}
    ))

    ## 5th type of embeddings Entity Relationship View (Concepts)
    docs.append(
        Document(
            page_content=f"CONCEPTS {table_name}: ENTITIES: {', '.join(table_json['strong_entities'])}",
            metadata={"parent_id": parent_id, "type": "entities"}
    ))

    return docs



