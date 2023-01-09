import concurrent
from enum import Enum
from threading import Event, Thread

from .robot import Robot
from .singleton import Singleton
from . import EVA_IP_ADDRESS, EVA_TOKEN
from queue import Queue
import logging
import uuid


class RobotManagerException(Exception):
    pass


class RobotManager(Singleton):
    def __init__(self, logger=logging.getLogger(__name__)):
        self._robot = Robot(eva_ip_address=EVA_IP_ADDRESS, token=EVA_TOKEN)
        self._logger = logger
        self._logger.info("RobotManager initilized)")
        self._actions = []
        self._current_plate = None
        self._actions_queue = Queue()
        self._kill_event = Event()
        self._threads = []
        self.start_threads()

    def start_threads(self):
        for f in [self.action_processor_thread, self.killer_thread]:
            th = Thread(target=f, name=f.__name__)
            self._threads.append(th)
            self._logger.info("Starting thread {}".format(th.name))
            th.start()



    def action_request(self, action, machine, slot, plate_name, options=None):
        position = "{}-{}".format(machine, slot)
        self._logger.info("Requested action {} for {} plate {}".format(action, position, plate_name))
        action_id = str(uuid.uuid4())
        action_element = {
            'action': action,
            'position': position,
            'plate_name': plate_name,
            'id': action_id,
        }
        self._actions_queue.put(action_element)
        return action_id

    def shutdown(self):
        self._logger.info("Shutdown command received")
        self._kill_event.set()

    def action_scheduler(self):
        done_actions = []
        self._logger.info("Scheduler: actions are {}".format(self._actions))
        for i, a in enumerate(self._actions):
            print("\nevaluating {}".format(a))
            print("current_plate: {}".format(self._current_plate))

            if a["action"] == "pick" and self._current_plate is None:
                print("action is pick")
                self._current_plate = a["plate_name"]
                try:
                    self._robot.pick_up_plate(a["position"], a["plate_name"])
                except RobotManagerException as e:
                    self._logger.info("Received exception during transfer: {}".format(e))
                done_actions.append(a)

            if a["action"] == "drop" \
                    and a["plate_name"] == self._current_plate:
                print("Drop plate!")
                self._robot.drop_plate(a["position"], a["plate_name"])
                self._current_plate = None
                done_actions.append(a)
            print("Ended cycle {}; actions: {}".format(i, self._actions))

        for da in done_actions:
            self._actions.remove(da)

    def action_processor_thread(self):
        self._logger.info("Entered action processor thread")
        while not self._kill_event.isSet():
            self._logger.info("action processor thread waiting for element")
            new_action = self._actions_queue.get()
            if new_action['action'] == "pick":
                self._logger.info("Adding action in the beginning: {}".format(new_action))
                self._actions.insert(0, new_action)
            else:
                self._actions.append(new_action)
            self._logger.info("action processor thread elaborating element")
            self.action_scheduler()
        self._logger.info("action processor thread exiting")

    def killer_thread(self):
        self._logger.info("kill thread waiting for event")
        self._kill_event.wait()
        self._logger.info("kill thread event detected")
        self._actions_queue.join()
        self._logger.info("kill thread exiting")


