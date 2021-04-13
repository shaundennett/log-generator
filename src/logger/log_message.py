import hashlib
import datetime


class LogMessage():
    """LogMessage is a class that encapsulates the attributes and output
       behaviour for a specific log message

       Attributes
       ----------
       message_type : String
           The log message type:
           0 = Connection log message
           1 = Unknown log message
       frequency : int
           The frequency in seconds for each log entry
       message_text : String
           The log Message text
       shared : String
           Indicates whether the unique sequence should be repeated
           on another running instance in the current day
       max_count : int
           Maximum times this log message is to be generated
       unique : String
          Indicates whether each log record should be unique within the same
           run, generates a random MD5 hash to create uniqueness

       Methods
       -------
       validate(p_message_type: str, p_unique: str, p_shared: str,
                 p_message_text: str, p_frequency: int, p_max_count: int):
            Applied validation rules

        parse_unique_string(val: str)
            extract Unique and Seed from the supplied value

        output_string():
            return an ouput message based on the supplied attributes
    """

    def __init__(self, p_message_type: str, p_unique: str, p_shared: str,
                 p_message_text: str, p_frequency: int, p_max_count: int):
        """initialise the log attributes
        and calls the necessary validation functions

        Parameters
        ----------
            message_type : String
        frequency : int
            The frequency in seconds for each log entry
        message_text : String
            The log Message text
        shared : String
            Indicates whether the unique sequence should be repeated
            on another running instance in the current day
        max_count : int
            Maximum times this log message is to be generated
        unique : String
            Indicates whether each log record should be unique within the same
            run, generates a random MD5 hash to create uniqueness

        """

        self.validate(p_message_type, p_unique, p_shared,
                      p_message_text, p_frequency, p_max_count)
        self.message_type = int(p_message_type)
        self.frequency = int(p_frequency)
        self.message_text = p_message_text
        self.shared = p_shared.upper()
        self.counter = 0
        self.max_count = int(p_max_count)
        self.unique, self.seed = self.parse_unique_string(p_unique.upper())

    def validate(self, p_message_type: str, p_unique: str, p_shared: str,
                 p_message_text: str, p_frequency: int, p_max_count: int):
        """validates the log parameters
        Creates a list of validation exceptions
        Raises an exception to stop the process

        Parameters
        ----------
        message_type : String
            indicates whether it is a Connection or Unknown message
        frequency : int
            Expected to be a positive integer
        message_text : String
            Expected not to be empty
        shared : String
            Expected values Y|N though not case sensitive
        max_count : int
            Expected to be a positive integer
        unique : String
            Expected values N|Y|Y:value though not case sensitive

        Raises
        ------
            Exception:
                invalid parameters used to create log entry:
                    frequency and max_count must be positive integers
                    shared must be Y or N
                    message_type must be 0 or 1
                    message_type must have a value
        """

        issues = []
        if len(p_message_text) == 0:
            issues.append('message_type must have a value')
        if (not p_frequency.isdecimal() or int(p_frequency) < 1):
            issues.append(
                ' frequency must be a positive integer')
        # may change this to allow -1 for unlimited MAX408701
        if (not p_max_count.isdecimal() or int(p_max_count) < 0):
            issues.append(
                ' max_count must be a positive integer')
        if p_shared.upper() != 'Y' and p_shared.upper() != 'N':
            issues.append('shared must be Y or N')
        if p_message_type != '0' and p_message_type != '1':
            issues.append('message_type must be 0 or 1')

        if len(issues) > 0:
            text = text = '\n'.join(map(str, issues))
            raise Exception(
                "invalid parameters used to create log entry:" + text)

    def parse_unique_string(self, val: str) -> str:
        """parses the unique flag value wich can be :
            N
            Y
            Y:seedValue
        Raises an exception to stop the process

        Parameters
        ----------
        val : String
            The unique flag value
        Return
        ------
            Str,Str
                Unique, Seed value

        Raises
        ------
            Exception:
                Invalid value for UNIQUE flag
                 Supplied value is <val>
                 Expected Y|N with optional :seed for Y
        """

        if val == 'N':
            return 'N', ''
        elif val.startswith('Y'):
            if val.find(':') == 1:
                return 'Y', val[2:]
            else:
                return 'Y', ''
        else:
            raise Exception("Invalid value for UNIQUE flag, " +
                            "Supplied value is : " + val +
                            " Expected Y|N with optional :seed for Y")

    def output_string(self) -> str:
        """
        Outputs a formatted log messages depending on
           a combination of the following flags:
            unique
                N - all messages are the same everywhere
                Y - all messages are unique
            shared
                N - messages are unique fall all instances
                Y  -messages are sequentially predictable
                    based on the message_text across instances
                Y:seed - messages are sequentially predictable
                based on the seed across instances

        Randomness is created by generating a MD5 hash from a combination of:
            The message text
            A seed value (instead of the message text)
            The current time (down to milliseconds)
            The current year and day of the year
            An integer counter (increased every time the message is generated)

        """

        output_string = ""
        if self.unique == 'N':
            output_string = self.message_text
        elif self.unique == 'Y':
            if self.shared == 'N':
                # generate a new unique message every time
                uniqueness = str(datetime.datetime.now())
                full_string = self.message_text + " " + uniqueness
                result = hashlib.md5(full_string.encode())
                output_string = self.message_text + " " + result.hexdigest()

            elif self.shared == 'Y':
                # generate a message that is unique across multiple instances

                # if using the seed then just use that not the message text
                # allows different messages to have the same randomness
                # this gives the ability to link similar  but not identical
                # messages
                if self.seed == "":
                    uniqueness = datetime.datetime.now().strftime("%j")
                else:
                    uniqueness = self.seed
                uniqueness = uniqueness + str(self.counter)

                result = hashlib.md5(uniqueness.encode())
                output_string = self.message_text + " " + result.hexdigest()

        self.counter = self.counter + 1
        return output_string
