# utils.py
import sqlite3
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db_ids_from_json():
    """从 NL2SQL-Bugs.json 中提取所有 db_id"""
    with open("data/NL2SQL-Bugs.json", "r") as f:
        data = json.load(f)

    # 提取所有出现过的 db_id
    db_ids = sorted(set(example["db_id"] for example in data))

    print(f"共需要 {len(db_ids)} 个数据库：")
    for db in db_ids:
        print(db)


def extract_schema_from_sqlite(sqlite_path: str) -> str:
    """Extract table and column info from .sqlite database"""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
    schema_parts = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info('{table}');")
        cols = [col[1] for col in cursor.fetchall()]
        schema_parts.append(f"{table}({', '.join(cols)})")
    conn.close()
    return " | ".join(schema_parts)

def build_prompt(question: str, schema: str, sql: str) -> str:
    """Fill in the prompt template"""
    return f"""You are a database expert.

Given the following natural language question, SQL query, and database schema, please determine whether the SQL is semantically correct with respect to the question.

Answer with "Yes" or "No" only.

Question: {question}

Schema: {schema}

SQL: {sql}

Is the SQL semantically correct?"""

def query_gpt(prompt: str, model="gpt-4o") -> str:
    """Call OpenAI GPT-4 using modern SDK"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip().lower()

def parse_answer(text: str) -> bool:
    """Parse model's Yes/No answer to boolean"""
    if "yes" in text:
        return True
    elif "no" in text:
        return False
    else:
        return None



if __name__ == "__main__":
    prompt = "You are a helpful assistant. Respond 'yes' or 'no'. Is the sky blue?"
    result = query_gpt(prompt)
    print("[GPT Response]:", result)



