import unittest
import time
import os
from testfixtures import LogCapture
from logger.log_generator import LogDriver
import logger.log_message as log_message
import collections
from unittest import mock


class LoggerTest(unittest.TestCase):
    """test suite for log-generator.py"""

    def test_logger_simple_connection(self):
        """
            GIVEN I specify 5 CONNECTION messages
            WHEN I start the logging thread and check after 10 seconds
            THEN I will have generated 5 identical messages
            AND and the logger will terminate
        """
        self.maxDiff
        os.environ["MESSAGE_DEFINITIONS"] = "test_logger_simple_connection"

        expected_vals = []
        with open('./test/test-log-generator/' +
                  'test_logger_simple_connection.txt') \
                as file_results:
            expected_vals = file_results.read().splitlines()

            with LogCapture() as log:
                thread1 = LogDriver(1, "Thread-1")
                thread1.file = \
                    'test/message_definitions/test_logger_simple_connection'
                thread1.start()
                time.sleep(10)
            thread1 = None

            self.assertEqual(expected_vals[0],
                             log.records[0].getMessage())
            self.assertEqual(expected_vals[4],
                             log.records[4].getMessage())

            self.assertEqual(5, len(log.records),
                             "Incorrect number of messages written")

    def test_logger_random_unknown_connection(self):
        """
            GIVEN I specify 2 UNKNOWN messages, each unique
            WHEN I run  the logger 2 times
            THEN I will have generated at 4 completely unique messages
        """
        testname = "test_logger_random_unknown_connection"

        self.maxDiff = None
        os.environ["MESSAGE_DEFINITIONS"] = testname

        expected_vals = []
        with open('./test/test-log-generator/' +
                  testname + ".txt") \
                as file_results:
            expected_vals = file_results.read().splitlines()

        with LogCapture() as log:
            thread1 = LogDriver(1, "Thread-1")
            thread1.file = \
                'test/message_definitions/' + testname
            thread1.start()
            time.sleep(5)
        thread1 = None
        firstrun = []
        for logitem in log.records:
            firstrun.append(logitem.getMessage())

        self.assertIsNot(log.records[0].
                         getMessage().
                         find(expected_vals[0]), -1)

        self.assertIsNot(log.records[0].
                         getMessage().
                         find(expected_vals[1]), -1)

        self.assertIsNot(log.records[0].
                         getMessage().
                         find(expected_vals[2]), -1)

        self.assertEqual(2, len(log.records),
                         "Incorrect number of messages written")

        with LogCapture() as log:
            thread2 = LogDriver(1, "Thread-1")
            thread2.file = \
                'test/message_definitions/' + testname
            thread2.start()
            time.sleep(5)
        thread2 = None
        secondrun = []
        for logitem in log.records:
            secondrun.append(logitem.getMessage())

        self.assertFalse(collections.Counter(firstrun)
                         == collections.Counter(secondrun))

    def test_logger_random_unknown_shared(self):
        """
            GIVEN I specify 2 UNKNOWN messages,unique, but repeatable
            WHEN I run the logger 2 times
            THEN I will have generated at 2 unique messages each run
            and these are repeatable in the second run
        """

        testname = "test_logger_random_unknown_shared"

        self.maxDiff = None
        os.environ["MESSAGE_DEFINITIONS"] = testname

        expected_vals = []
        with open('./test/test-log-generator/' +
                  testname + ".txt") \
                as file_results:
            expected_vals = file_results.read().splitlines()

        with LogCapture() as log:
            thread1 = LogDriver(1, "Thread-1")
            thread1.file = \
                'test/message_definitions/' + testname
            thread1.start()
            time.sleep(5)
        thread1 = None
        firstrun = []
        for logitem in log.records:
            firstrun.append(logitem.getMessage())

        self.assertIsNot(log.records[0].
                         getMessage().
                         find(expected_vals[0]), -1)

        self.assertIsNot(log.records[0].
                         getMessage().
                         find(expected_vals[1]), -1)

        self.assertIsNot(log.records[0].
                         getMessage().
                         find(expected_vals[2]), -1)

        self.assertEqual(2, len(log.records),
                         "Incorrect number of messages written")

        with LogCapture() as log:
            thread2 = LogDriver(1, "Thread-1")
            thread2.file = \
                'test/message_definitions/' + testname
            thread2.start()
            time.sleep(5)
        thread2 = None
        secondrun = []
        for logitem in log.records:
            secondrun.append(logitem.getMessage())

        self.assertTrue(collections.Counter(firstrun)
                        == collections.Counter(secondrun))

    def xtest_logger_queue_depth(self):
        """
            GIVEN I have run the logger and I have set
                the max queue depth to 0
            WHEN I trigger triggered 2 messages
            THEN The logger should terminate with a message indicating that
            the queue depth is exceeded
        """
        self.maxDiff = None
        expected_vals = []
        os.environ["MESSAGE_DEFINITIONS"] = "default"
        with open('./test/test-log-generator/' +
                  'test_logger_queue_depth.txt') \
                as file_results:
            expected_vals = file_results.read().splitlines()

        with LogCapture() as log:

            with mock.patch('logger.log_generator.LogDriver') as mock_class:
                mock_class.return_value.get_config_file_name.return_value =\
                     'test/message_definitions/test_logger_queue_depth'
                mock_class.return_value.get_max_queue_depth.return_value = 0

                thread1 = LogDriver(1, "Thread-1")
                thread1.file = \
                    'test/message_definitions/test_logger_queue_depth'
                thread1.max_queue_depth = 0
                thread1.start()
                time.sleep(3)

            self.assertEqual(expected_vals[0],
                             log.records[0].getMessage())

    def test_logMessage_validation_ok(self):
        """
            GIVEN I supply valid values for all message parameters
            WHEN I supply all valid values
            THEN no validation errors will be picked up
        """
        try:
            result = log_message.LogMessage("0", "Y:seed1", "Y",
                                            "Error Message", "10", "5")
            self.assertEqual(0, result.message_type)
            self.assertEqual('Y', result.unique)
            self.assertEqual('SEED1', result.seed)
            self.assertEqual('Error Message', result.message_text)
            self.assertEqual(10, result.frequency)
            self.assertEqual(5, result.max_count)
            self.assertEqual(0, result.counter)
        except Exception:
            self.assertTrue("Raised an exception and it should not have")

    def test_logMessage_validation_fail_message_type(self):
        """
            GIVEN I instantiate an instance of LogMessage
            WHEN I supply an invalid message_type value of 2
            THEN validation will fail and state that:
            "log entry:message_type must be 0 or 1"
        """
        result = None
        with self.assertRaises(Exception) as context:
            result = log_message.LogMessage("2", "Y:seed1", "Y",
                                            "Error Message", "10", "5")
        self.assertIsNone(result)
        self.assertEqual("invalid parameters used to create" +
                         " log entry:message_type must be 0 or 1",
                         str(context.exception))

    def test_logMessage_validation_fail_unique(self):
        """
            GIVEN I instantiate an instance of LogMessage
            WHEN I supply an invalid value for the "unique" flag
            N:seed1
            THEN validation will fail and state that:
            "Supplied value is : N:SEED1 Expected Y|N
            with optional :seed for Y"
        """
        result = None
        with self.assertRaises(Exception) as context:
            result = log_message.LogMessage("0", "N:seed1", "Y",
                                            "Error Message", "10", "5")
        self.assertIsNone(result)
        self.assertEqual("Invalid value for UNIQUE flag," +
                         " Supplied value is : N:SEED1 Expected Y|N" +
                         " with optional :seed for Y",
                         str(context.exception))

    def test_logMessage_validation_fail_frequency(self):
        """
            GIVEN I instantiate an instance of LogMessage
            WHEN I supply an invalid value for the "frequency" flag
            value = "X"
            THEN validation will fail and state that:
            "frequency and max_count must be positive integers"
        """
        result = None
        with self.assertRaises(Exception) as context:
            result = log_message.LogMessage("0", "Y", "Y",
                                            "Error Message", "X", "5")
        self.assertIsNone(result)
        self.assertEqual("invalid parameters used to create log entry:" +
                         " frequency must be a positive integer",
                         str(context.exception))

    def test_logMessage_validation_fail_max_count(self):
        """
            GIVEN I instantiate an instance of LogMessage
            WHEN I supply an invalid value for the "max count" flag
            value = "N"
            THEN validation will fail and state that:
            "frequency and max_count must be positive integers"
        """
        result = None
        with self.assertRaises(Exception) as context:
            result = log_message.LogMessage("0", "Y:seed1", "Y",
                                            "Error Message", "10", "N")
        self.assertIsNone(result)
        self.assertEqual("invalid parameters used to create log entry:" +
                         " max_count must be a positive integer",
                         str(context.exception))

    def test_logMessage_validation_fail_multiple(self):
        """
            GIVEN I instantiate an instance of LogMessage
            WHEN I supply multiple invalid values
            message_type = "n"
            max_count = 'N"
            THEN validation will fail and state multiple issues:
            "frequency and max_count must be positive integers"
            ""message_type must be 0 or 1"

        """
        result = None
        with self.assertRaises(Exception) as context:
            result = log_message.LogMessage("n", "Y:seed1", "Y",
                                            "Error Message", "10", "N")
        self.assertIsNone(result)
        self.assertEqual(
            "invalid parameters used to create log entry:" +
            " max_count must be a positive integer\n" +
            "message_type must be 0 or 1",
            str(context.exception))

    def test_logMessage_output_predict_single(self):
        """
            GIVEN I instantiate an instance of LogMessage
            WHEN rquest a predictable non-unique log message
            Unique = "N"
            Shared = 'N"
            THEN each message from the output_string function
            should be predictable and not contain a random string
        """
        result = log_message.LogMessage("0", "N", "N",
                                        "Error Message", "10", "5")
        self.assertEqual(
            "Error Message", result.output_string())

    def test_logMessage_output_unpredictable_single(self):
        """
            GIVEN I instantiate an instance of LogMessage
            WHEN rquest a predictable unique log message
            Unique = "Y"
            Shared = 'N"
            THEN each message from the output_string function
            should be unique and contain a random string
        """
        logger1 = log_message.LogMessage("1", "Y", "N",
                                         "Random1 Message", "10", "5")
        logger2 = log_message.LogMessage("1", "Y", "N",
                                         "Random1 Message", "10", "5")
        result1 = logger1.output_string()
        time.sleep(1)
        result2 = logger2.output_string()

        self.assertNotEqual(
            result1, result2)

    def test_logMessage_output_unpredictable_shared(self):
        """
            GIVEN I instantiate an instance of LogMessage
            WHEN I request a predictable unique log message to be shared
                Unique = "Y"
                 Shared = 'Y"
            THEN each message from the output_string function
            should be unique and contain a random string
            It should also be the same for subsequent runs
        """
        logger1 = log_message.LogMessage("1", "Y", "Y",
                                         "Random2 Message", "10", "5")
        logger2 = log_message.LogMessage("1", "Y", "Y",
                                         "Random2 Message", "10", "5")
        self.assertEqual(
            logger1.output_string(), logger2.output_string())
        self.assertEqual(
            logger1.output_string(), logger2.output_string())


if __name__ == "__main__":
    unittest.main()
