from supabase import Client
from typing import Dict, Any, Optional
from logger_config import logger


class DeviceManager:
    def __init__(self, supabase_client: Client):
        self.supabase_client = supabase_client

    def process_device_update(self, device_id: str, room: str) -> Dict[str, Any]:
        current_status = self.get_device_status(device_id)
        new_status = self.determine_new_status(current_status, room)

        if new_status is None:
            logger.warning(f"No data found for device_id: {device_id}")
            return {"statusCode": 404, "body": "Device not found"}

        logger.info(f"Determined new status: {new_status}")

        update_success = self.update_device_data(
            device_id, new_status["room_id"], new_status["in_or_out"]
        )

        if update_success:
            return {"statusCode": 200, "body": "Data updated successfully"}
        else:
            return {"statusCode": 404, "body": "Device not found or update failed"}

    def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        try:
            data = (
                self.supabase_client.table("devices")
                .select("in_or_out", "room_id")
                .eq("id", device_id)
                .limit(1)
                .execute()
            )

            if not data.data:
                logger.warning(f"No data found for device_id: {device_id}")
                return None

            device_data = data.data[0]
            return {
                "device_id": device_id,
                "in_or_out": device_data["in_or_out"],
                "room_id": device_data["room_id"],
            }
        except Exception as e:
            logger.error(f"Error fetching device status: {str(e)}")
            raise

    def update_device_data(
        self, device_id: str, room: Optional[str], status: str
    ) -> bool:
        try:
            update_result = (
                self.supabase_client.table("devices")
                .update({"room_id": room, "in_or_out": status})
                .eq("id", device_id)
                .execute()
            )
            if update_result.data:
                logger.info(f"Device {device_id} updated successfully in Supabase")
                return True
            else:
                logger.warning(f"No device found with id {device_id} to update")
                return False
        except Exception as e:
            logger.error(f"Error updating device data: {str(e)}")
            raise

    @staticmethod
    def determine_new_status(
        current_status: Optional[Dict[str, Any]], new_room: str
    ) -> Optional[Dict[str, Any]]:
        if current_status is None:
            return None

        if current_status["in_or_out"] == "out":
            return {"in_or_out": "in", "room_id": new_room}

        if current_status["room_id"] == new_room:
            return {"in_or_out": "out", "room_id": None}

        return {"in_or_out": "in", "room_id": new_room}
