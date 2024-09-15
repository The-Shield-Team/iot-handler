import unittest
from unittest.mock import Mock, patch
from device_manager import DeviceManager

class TestDeviceManager(unittest.TestCase):

    def setUp(self):
        self.mock_supabase_client = Mock()
        self.device_manager = DeviceManager(self.mock_supabase_client)

    def test_get_device_status_success(self):
        mock_data = [{"in_or_out": "in", "room_id": "room1"}]
        self.mock_supabase_client.table().select().eq().limit().execute.return_value.data = mock_data

        result = self.device_manager.get_device_status("device1")

        self.assertEqual(result, {"device_id": "device1", "in_or_out": "in", "room_id": "room1"})

    def test_get_device_status_not_found(self):
        self.mock_supabase_client.table().select().eq().limit().execute.return_value.data = []

        result = self.device_manager.get_device_status("device1")

        self.assertIsNone(result)

    def test_update_device_data_success(self):
        self.mock_supabase_client.table().update().eq().execute.return_value.data = [{"id": "device1"}]

        result = self.device_manager.update_device_data("device1", "room1", "in")

        self.assertTrue(result)

    def test_update_device_data_not_found(self):
        self.mock_supabase_client.table().update().eq().execute.return_value.data = []

        result = self.device_manager.update_device_data("device1", "room1", "in")

        self.assertFalse(result)

    def test_determine_new_status_out_to_in(self):
        current_status = {"in_or_out": "out", "room_id": None}
        new_room = "room1"

        result = self.device_manager.determine_new_status(current_status, new_room)

        self.assertEqual(result, {"in_or_out": "in", "room_id": "room1"})

    def test_determine_new_status_in_to_out(self):
        current_status = {"in_or_out": "in", "room_id": "room1"}
        new_room = "room1"

        result = self.device_manager.determine_new_status(current_status, new_room)

        self.assertEqual(result, {"in_or_out": "out", "room_id": None})

    def test_determine_new_status_room_change(self):
        current_status = {"in_or_out": "in", "room_id": "room1"}
        new_room = "room2"

        result = self.device_manager.determine_new_status(current_status, new_room)

        self.assertEqual(result, {"in_or_out": "in", "room_id": "room2"})

    @patch('device_manager.logger')
    def test_process_device_update_success(self, mock_logger):
        self.device_manager.get_device_status = Mock(return_value={"in_or_out": "out", "room_id": None})
        self.device_manager.update_device_data = Mock(return_value=True)

        result = self.device_manager.process_device_update("device1", "room1")

        self.assertEqual(result, {"statusCode": 200, "body": "Data updated successfully"})
        mock_logger.info.assert_called_with("Determined new status: {'in_or_out': 'in', 'room_id': 'room1'}")

    @patch('device_manager.logger')
    def test_process_device_update_not_found(self, mock_logger):
        self.device_manager.get_device_status = Mock(return_value=None)

        result = self.device_manager.process_device_update("device1", "room1")

        self.assertEqual(result, {"statusCode": 404, "body": "Device not found"})
        mock_logger.warning.assert_called_with("No data found for device_id: device1")

if __name__ == '__main__':
    unittest.main()