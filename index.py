from device_manager import DeviceManager
from supabase_client import SupabaseClientSingleton
from logger_config import logger
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info(f"Received event: {event}")

    try:
        supabase_client = SupabaseClientSingleton.get_instance()
        device_manager = DeviceManager(supabase_client)

        device_id = event.get("device_id")
        room = event.get("room")

        if not device_id or not room:
            logger.error("Missing device_id or room in the event")
            return {"statusCode": 400, "body": "Missing required parameters"}

        logger.info(f"Processing data for device_id: {device_id}, room: {room}")

        result = device_manager.process_device_update(device_id, room)
        return result

    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        return {"statusCode": 500, "body": "Server configuration error"}
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return {"statusCode": 500, "body": "Error processing data"}


if __name__ == "__main__":
    lambda_handler({"device_id": "1", "room": "1"}, None)
