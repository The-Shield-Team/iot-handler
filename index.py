import os
from supabase import create_client
from dotenv import load_dotenv
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(".env")


def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL or key is missing")

    return create_client(supabase_url, supabase_key)


def get_device_status(supabase_client, device_id: str, room: str) -> str:
    data = (
        supabase_client.table("IotTests")
        .select("in_or_out, created_at")
        .eq("device_id", device_id)
        .eq("room", room)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    logger.info(f"Retrieved data from Supabase: {data}")

    if not data.data:
        logger.warning("No existing data found for the device and room")
        return "in"  # Default to "in" if no previous data

    return "in" if data.data[0]["in_or_out"] == "out" else "out"


def insert_device_data(supabase_client, device_id: str, room: str, status: str):
    insert_result = (
        supabase_client.table("IotTests")
        .insert(
            {
                "device_id": device_id,
                "room": room,
                "in_or_out": status,
            }
        )
        .execute()
    )
    logger.info("Data inserted successfully into Supabase")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info(f"Received event: {event}")

    try:
        supabase_client = get_supabase_client()

        device_id = event.get("device_id")
        room = event.get("room")

        if not device_id or not room:
            logger.error("Missing device_id or room in the event")
            return {"statusCode": 400, "body": "Missing required parameters"}

        logger.info(f"Processing data for device_id: {device_id}, room: {room}")

        status = get_device_status(supabase_client, device_id, room)
        logger.info(f"Determined new status: {status}")

        insert_device_data(supabase_client, device_id, room, status)

        return {"statusCode": 200, "body": "Data inserted successfully"}

    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        return {"statusCode": 500, "body": "Server configuration error"}
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return {"statusCode": 500, "body": "Error processing data"}
