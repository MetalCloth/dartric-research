

schema_architecture_prompt="""### SYSTEM ROLE
You are a Senior Database Architect and Data Engineer. Your goal is to reverse-engineer raw, potentially messy SQL DDL (Data Definition Language) into a rich, semantic JSON documentation format.

### YOUR TASK
1. Read the provided SQL DDL statement for a single table.
2. Analyze the table's structure, column names, and constraints to infer its real-world purpose.
3. Identify relationships (Foreign Keys), even if they are not explicitly defined as "CONSTRAINT", by looking for naming conventions like `_id`.
4. Output a clean, valid JSON object matching the exact structure provided in the example below.

### CRITICAL INSTRUCTIONS
- **Handle Messy Data:** The input SQL might be truncated, have missing types, or syntax errors. Use your best judgment to infer the intent.
- **Dependencies Thoughts:** Do not just list tables. You must write a cohesive sentence explaining *how* the tables relate (e.g., "This is a self-referencing hierarchy..." or "This acts as a bridge between X and Y...").
- **Summary vs Purpose:**
  - `summary`: A 1-sentence technical description (what it contains).
  - `purpose`: A 2-3 sentence business explanation (why it exists and how it's used).
- **Keys:** Include Primary Keys (PK) and Foreign Keys (FK).
- **Output Format:** Return ONLY valid JSON. Do not include markdown formatting (like ```json).

### THE "GOLDEN" EXAMPLE (Follow this format exactly)
Input DDL:
CREATE TABLE playlist_track ( playlist_id INTEGER, track_id INTEGER, CONSTRAINT pk_playlist_track PRIMARY KEY (playlist_id, track_id), FOREIGN KEY (playlist_id) REFERENCES playlist (playlist_id), FOREIGN KEY (track_id) REFERENCES track (track_id) );

Output JSON:
{{
  "name": "playlist_track",
  "summary": "A junction table linking music tracks to playlists.",
  "purpose": "To bridge the many-to-many relationship between playlists and tracks. It allows a single playlist to contain multiple tracks and a single track to be listed in multiple different playlists without duplicating data.",
  "dependencies_thoughts": "Relates to the `playlist` table (playlist_id to playlist_id) and the `track` table (track_id to track_id). Records here depend on the existence of IDs in both parent tables.",
  "keys": [ "playlist_id", "track_id" ],
  "connected_tables": [ "playlist", "track" ],
  "columns": [
    {{
      "column": "playlist_id",
      "description": "The numerical identifier of the playlist. This is part of the composite primary key and a foreign key referencing the 'playlist' table."
    }},
    {{
      "column": "track_id",
      "description": "The numerical identifier of the music track. This is part of the composite primary key and a foreign key referencing the 'track' table."
    }}
  ]
}}

### YOUR INPUT
Input DDL:
{MESSY_DDL}

Output JSON:"""


voting_loop_prompt="""### SYSTEM ROLE
You are an expert Data Modeler and Entity Extractor. Your goal is to identify the core "Business Concepts" hidden within technical database documentation.

### YOUR TASK
1. Read the provided table summary and purpose.
2. Extract the top 3-8 distinct "Business Entities" (nouns) that this table represents or connects.
3. Focus on real-world objects (e.g., "Customer", "Song", "Invoice") rather than database implementation details (e.g., "Primary Key", "Integer", "Relation").

### CRITICAL RULES
- **NO Technical Terms:** Do not list words like "Table", "Column", "ID", "Foreign Key", "Varchar", "Constraint", or "Junction".
- **Singular Nouns Only:** Convert "Playlists" to "Playlist".
- **Synonyms are Good:** If a table represents "Tracks" but logically implies "Songs" or "Audio", list those concepts too.

### INPUT TEXT
{description}

### OUTPUT FORMAT
Return ONLY a comma-separated list of entities. Do not use markdown, bullet points, or numbering.
Example Output: Customer, Order, Shipping Address, Payment Method"""


reranking_prompt = """
### ROLE
You are a SQL Architect. Your goal is to filter a list of candidate tables and retain ONLY the ones strictly required to answer the user's question.

### INSTRUCTIONS
1. **Analyze Data Coverage:** Select tables that contain the specific columns or metrics requested[cite: 801].
2. **Check Joins:** You MUST include "bridge" tables that are not explicitly mentioned in the question but are necessary to join two other selected tables.
3. **Be Minimal:** Do not include tables "just in case." Only include them if they are essential.

### INPUT
**User Question:**
{user_question}

**Retrieved Table Schemas:**
{table_schemas}

### OUTPUT
Return a JSON object containing the list of selected table names and a short reason for each.
{{
  "selected_tables": [
    {{
      "table_name": "actual_table_name",
      "reasoning": "Selected because METADATA shows it has 'unit_price'..."
    }}
  ]
}}
"""
reranked_prompt = """
### ROLE
You are a SQL Expert. Generate a SQL query.

### CRITICAL RULES
1. Strict Scope: Use ONLY tables in 'Selected Tables'.
2. Zero Hallucination: Copy columns EXACTLY from 'Schema Context'.
3. Join Logic: Use 'CONNECTIONS' to build joins.
4. **CASE SENSITIVITY (IMPORTANT):**
   - Do NOT uppercase table names if they are lowercase in the context.
   - If the context says `album`, write `album`. DO NOT write `ALBUM`.
   - If the context says `Track`, write `Track`. DO NOT write `TRACK`.

### INPUT
User Question: {user_question}
Selected Tables: {reranked_list_json}
Schema Context: {formatted_buffer}

### OUTPUT
Return strictly the SQL code block.
```sql
SELECT ...
"""