import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional

load_dotenv(".env")

class SupabaseClientSingleton:
    _instance: Optional[Client] = None

    @classmethod
    def get_instance(cls) -> Client:
        if cls._instance is None:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError("Supabase URL or key is missing")

            cls._instance = create_client(supabase_url, supabase_key)
        return cls._instance