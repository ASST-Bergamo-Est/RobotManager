import logging
import unittest

import pytest

from ..robot_manager.movement import MovementException
from ..robot_manager.robot import Movement
from ..robot_manager.robot import Robot, RobotException
from ..robot_manager.EvaHelper import EvaHelper
from mock import patch, Mock

FAKE_IP_ADDRESS = "fakeipaddress"
FAKE_TOKEN = "faketoken"
fake_logger = logging.getLogger()

PICK_POS1 = "OT1-SLOT1"
PICK_POS2 = "OT1-SLOT2"
DROP_POS1 = "OT2-SLOT5"
DROP_POS2 = "OT2-SLOT6"
PLATE_NAME1 = "REAGENT"
PLATE_NAME2 = "WASH"


# class FakeEvaHelper:
#     def __init__(self):
#         pass
#
#     def connect(self, *args, **kwargs):
#         pass
#
#
# class FakeMovement:
#     transfer_calls = 0
#
#     def __init__(self):
#         self.__class__.transfer_calls = 0
#
#     @classmethod
#     def transfer_plate(cls, *args, **kwargs):
#         cls.transfer_calls += 1
#
#     @classmethod
#     def reset_calls(cls):
#         cls.transfer_calls = 0
#
#     @classmethod
#     def check_calls(cls, calls):
#         if cls.transfer_calls != calls:
#             raise Exception("Calls expected {} got {}".format(calls, cls.transfer_calls))


# @pytest.fixture
# @patch.object(Movement, "__init__", FakeMovement.__init__)
# @patch.object(EvaHelper, "connect")
# def robot(mock_connect):
#     _robot = Robot(eva_ip_address=FAKE_IP_ADDRESS, token=FAKE_TOKEN, logger=fake_logger)
#     return _robot


class ManagerPlateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._eva_helper_patcher = patch("RobotManager.robot_manager.robot.EvaHelper")
        self._movement_patcher = patch("RobotManager.robot_manager.robot.Movement")
        self._mock_eh = self._eva_helper_patcher.start()
        self._mock_movement = self._movement_patcher.start()
        self._r = Robot(FAKE_IP_ADDRESS, FAKE_TOKEN)

    def tearDown(self) -> None:
        self._mock_eh.stop()
        self._mock_movement.stop()

    def test_instance_creation(self):
        assert self._r

    def test_pickup_is_executed(self):
        self._r.pick_up_plate(PICK_POS1)
        self._mock_movement().pick_plate.assert_called()

    def test_drop_is_executed(self):
        self._r.drop_plate(DROP_POS1)
        self._mock_movement().drop_plate.assert_called()

    def test_pick_plate_not_grabbed_exception_is_caught(self):
        self._mock_movement().pick_plate.side_effect = MovementException("Test")
        with self.assertRaises(RobotException):
            self._r.pick_up_plate(PICK_POS1)

    def test_movement_exception_is_caught_drop(self):
        self._mock_movement().drop_plate.side_effect = MovementException("Test")
        with self.assertRaises(RobotException):
            self._r.drop_plate(DROP_POS1)
