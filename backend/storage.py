import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional
from supabase import create_client, Client

# Connects to your Database
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db():
    if not supabase: 
        raise Exception("No Supabase Connection Found")
    return supabase

async def list_conversations() -> List[Dict]:
    try:
        res = get_db().table("conversations").select("id, title, created_at, messages").order("created_at", desc=True).execute()
        return [
            {
                "id": r["id"], 
                "title": r.get("title", "New"), 
                "created_at": r["created_at"], 
                "message_count": len(r.get("messages", []))
            } 
            for r in res.data
        ]
    except Exception:
        return []

async def get_conversation(cid: str) -> Optional[Dict]:
    try:
        res = get_db().table("conversations").select("*").eq("id", cid).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None

async def create_conversation(cid: str = None) -> Dict:
    cid = cid or str(uuid.uuid4())
    new_convo = {
        "id": cid, 
        "title": "New Conversation", 
        "created_at": datetime.now(timezone.utc).isoformat(), 
        "messages": []
    }
    try: 
        get_db().table("conversations").insert(new_convo).execute()
    except Exception:
        pass
    return new_convo

async def save_conversation(cid: str, data: Dict):
    try: 
        get_db().table("conversations").upsert(data).execute()
    except Exception:
        pass

async def update_conversation_title(cid: str, title: str):
    try: 
        get_db().table("conversations").update({"title": title}).eq("id", cid).execute()
    except Exception:
        pass

async def add_user_message(cid: str, content: str):
    convo = await get_conversation(cid)
    if convo:
        convo["messages"].append({"role": "user", "content": content})
        await save_conversation(cid, convo)

async def add_assistant_message(cid: str, s1: Dict, s2: Dict, s3: str):
    convo = await get_conversation(cid)
    if convo:
        convo["messages"].append({
            "role": "assistant", 
            "content": s3, 
            "meta": {
                "stage1": s1, 
                "stage2": s2, 
                "stage3": s3
            }
        })
        await save_conversation(cid, convo)
