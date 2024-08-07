from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional, Annotated, Tuple, Any
from enum import Enum
from random_op import rand
import sqlite3

app = FastAPI()

class Side(str, Enum):
    attacker = "attacker"
    defender = "defender"

class Operator(BaseModel):
    name: str
    side: Side
    banned: Optional[bool] = False

operators = []

@app.get("/roulette")
async def get_rand_operators(side: str, n: int = 1, 
                             attackerbans: Optional[Annotated[List[str] | None, Query()]] = None, 
                             defenderbans: Optional[Annotated[List[str] | None, Query()]] = None):
    
    if side not in ['a', 'd']:
        return {"error": "Invalid side"}
    
    results = execute_db_command("SELECT name, icon FROM operators WHERE side = ?", (side))
    names = [r[0] for r in results]
    
    try:
        if side == 'd':
            result = rand([('attackerbans', attackerbans), ('defenderbans', defenderbans), ('defenders', n), ('attackers', None)], defenders=names)
        elif side == 'a':
            result = rand([('attackerbans', attackerbans), ('defenderbans', defenderbans), ('defenders', None), ('attackers', n)], attackers=names)
        
        icons = get_rand_ops_icons(result)
        
        return {
            "operator_names": result,
            "operator_icons": icons
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/operators")
async def get_operators(side: str):
    results = execute_db_command(f"SELECT name, icon FROM operators WHERE side=? ORDER BY id ASC", (side,))
    names = [r[0] for r in results]
    icons = [r[1] for r in results]
    
    return {
        "operator_names": names,
        "operator_icons": icons
    }
    

def get_rand_ops_icons(operators):
    placeholders = ','.join('?' for _ in operators)
    
    case_statement = ' '.join(f"WHEN ? THEN {i}" for i in range(len(operators)))
    
    query = f"""
    SELECT icon 
    FROM operators 
    WHERE name IN ({placeholders}) 
    ORDER BY CASE name {case_statement} END
    """
    
    results = execute_db_command(query, tuple(operators) + tuple(operators))
    return [r[0] for r in results]
    

def execute_db_command(command: str, params: Optional[Tuple[Any, ...]] = ()) -> List[Tuple[Any, ...]]:
    # Example usage
    # results = execute_db_command("SELECT * FROM operators WHERE side = ?", ('a',))
    # print(results)
    try:
        conn = sqlite3.connect('operators.db')
        cursor = conn.cursor()
        cursor.execute(command, params)
        
        if command.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            conn.commit()
        
        if command.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            return results
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)