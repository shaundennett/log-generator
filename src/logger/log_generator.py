import logging
import time
import sched
import threading
import sys
import traceback
import os

from logger.graceful_killer import GracefulKiller
from logger.log_message import LogMessage


class LogDriver(threading.Thread):

    """Log driver automatically creates log messages to systout at offset
    time intervals

    Attributes
    ----------
    threading : Thread
        thread reference

    Methods
    -------
    print_error_unknown(self)
        outputs an UNKNOWN message to the log
    print_log_message(self, type)
        from the LogMessage instances passed in it determines what
        log message to generate and determines whether a subsequent
        event it to be raised based on the number of previous
        messages created
    schedule_next_event(self, type)
        Creates a new timer event from the suplied LogMessage instance
    checkDepth(self):
        Checks the Timer event queue to make sure
        it does not have too many events active
    setup_log_messages(self):
        using the file name supplied in the MESSAGE_DEFINITIONS
        environment variable.  It reads in the appropriate message definition
        file and creates a List of LogMessage objects
    run(self):
        Calls the setup_log_messages function to craete the LogMessage
            instances.
        Sets up the necessary events for each LogMessage
    level1(self):
        Entry stack trace method
    level2(self):
        the next level of stack trace
    level3(self):
        generates an exception to craete a stacktrace for the logs

    """

    def __init__(self, thread_id, name):
        """initialise the runtime variables

        Parameters
        ----------
        thread_id : str
            unique thread id
        name : str
            the thread name
        """

        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

        self.stop = False
        self.killer = GracefulKiller()
        self.FORMAT_STRING =\
            '%(asctime)s.%(msecs)03d %(levelname)s %(message)s'
        self.FORMAT_DATE = '%Y-%m-%d %H:%M:%S'
        self.CONNECTION_DELAY = 5
        self.UNKNOWN_DELAY = 30

        self.CONNECTION = 0
        self.UNKNOWN = 1

        self.max_queue_depth = 0
        self.logger = logging.getLogger('main application')
        self.logger.setLevel(logging.DEBUG)
        self.fh = logging.StreamHandler()
        self.formatter =\
            logging.Formatter(fmt=self.FORMAT_STRING, datefmt=self.FORMAT_DATE)
        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)
        self.s = sched.scheduler(time.time, time.sleep)
        self.log_messages = []
        self.file = self.get_config_file_name()

    def print_log_message(self, type: LogMessage):
        """formats an error unknown message.
        This function uses the flags defined in the logMessage instance "type"
        to generate the correct log message:
            CONNECT - generates a message
            UNKNOWN - generates a message and stack trace
        also checks the event queue depth to ensure events are managed

        All messages written to sysout

        Parameters
        ----------
        type: LogMessage
            Represents a log message instance

        Raises
        -------
            Exception
                this Exception is raised when the current timer queue
                depth against a Max Queue Depth.
                This ensures that the thread creation does not run out
                of control
            Exception is propagated
        """

        if not self.killer.kill_now:

            if type.message_type == self.UNKNOWN:
                try:
                    self.level1()
                except Exception:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    self.logger.error(type.output_string() + " " +
                                      repr(traceback.format_tb(exc_traceback)))
            elif type.message_type == self.CONNECTION:
                self.logger.error(type.output_string())
            else:
                raise Exception("Invalid message type " +
                                str(type.message_type))
            if type.counter < type.max_count or type.max_count == 0:
                self.schedule_next_event(type)
        else:
            sys.exit(99)

    def schedule_next_event(self, type: LogMessage):
        """Creates a new timer event.
        This function given a specific LogMessage (type), will generate
        the approprate timer function to re-write a log message after an
        approriate period of time

        Parameters
        ----------
        type: int
            the message type being scheduled can be one of
                self.UNKNOWN
                self.CONNECTION
        Raises
        -------
            Exception
                Exception is raised when the current timer queue
                depth against a Max Queue Depth.
            Exception is propagated
        """

        self.s.enter(type.frequency, 1, self.print_log_message, (type,))
        self.checkDepth()

    def checkDepth(self):
        """failsafe method for timer events.
        this function checks the current timer queue depth against a Max Queue
        Depth and terminates the main thread if it is too high
        This ensures that the timer queue does not fill up
        Raises
        -------
            Exception
                Exception is raised when the current timer queue
                depth against a Max Queue Depth.
            Exception is logged, the thread is killed and it is then propagated
        """
        if len(self.s.queue) > self.max_queue_depth:
            self.s.cancel
            error_message = "The number of active timer events :" +\
                            str(len(self.s.queue)) +\
                            " is greater that the expected " +\
                            "maximum number of events :" +\
                            str(self.max_queue_depth) +\
                            " this means that the timer events may not be" +\
                            " being generated in a controlled way"

            self.logger.error(error_message)
            self.killer.kill_now = True
            raise Exception(error_message)

    def run(self):
        """Executes the main thread after loading in the
        message definitions
        Test overrides are in place
        """
        self.log_messages = self.setup_log_messages()
        for current_message in self.log_messages:
            self.schedule_next_event(current_message)
        self.s.run()

    def get_max_queue_depth(self, list_of_configurations: []):
        """
            parameters
            ----------
                list_of_configurations : List
                    A list containing the message types to be created
                    for this run
            return
            ------
                int
                    The length of the list
        """
        return len(list_of_configurations)

    def get_config_file_name(self):
        """
            get the location of the message definitions based
            on the MESSAGE_DEFINITIONS environment variable
        returns
        -------
            String
                The relative file name for the message definition file
        """
        try:
            os.environ["MESSAGE_DEFINITIONS"]
        except KeyError:
            os.environ["MESSAGE_DEFINITIONS"] = "default"
        return 'logger/message_definitions/' +\
            os.environ['MESSAGE_DEFINITIONS']

    def level1(self):
        """level1 - calls level2 to generate a stack trace
        """
        self.level2()

    def level2(self):
        """level2 - calls level3 to generate a stack trace
        """
        self.level3()

    def level3(self):
        """
        Raise a stack trace.
        This function generates a stack trace to be written to sysout

        Raises
        -------
            Exception - This has triggered an exception stack trace
        """
        raise Exception(
            "This has triggered an exception stack trace : queue depth  (" +
            str(len(self.s.queue)) + ")")

    def setup_log_messages(self) -> list:
        """
        Using the environment variable MESSAGE_DEFINITIONS, or "default"
        if it is not supplied.
        The function reads and creates the individual LogMessage objects
        and stores them in a list object.
        The message definition file contains comma separated items in the
        following order:
            message_type
            unique
            shared
            message_text
            frequency
            max_count

        Return
        -------
            List
                List of LogMessage instances
        """

        iv_messages = []
        with open(self.file) as file_results:
            expected_vals = file_results.read().splitlines()

        for line in expected_vals:
            split = line.split(',')
            iv_messages.append(LogMessage(
                split[0], split[1], split[2], split[3], split[4], split[5]))
        self.max_queue_depth = self.get_max_queue_depth(expected_vals)
        return iv_messages
