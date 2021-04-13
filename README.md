# python-log generator

<h1>Log generator</h1> 

This application generates error log messages to the SYSOUT.  It will be used to simulate application activity so that the log output can be picked up and used by a downstream process.


<h2>How log-generator works</h2>

This application works by generating any number of 2 different timer events at differing intervals for a fixed number times

```<timestamp> ERROR Connection Unable to connect to server <optional unique MD5 string> ```

```<timestamp> ERROR Unknown <optional unique MD5 string> <stack trace> ```

ERROR Unknown type errors have an addiitonal stack trace and represent an error that has not been encountered previously

The number and type of messages generated is defined by a message definition file located in the /logger/message_definitions folder
The message definition file to use in any deployment is specified during deployment time as a template parameter

=======

```MESSSAGE_DEFINITION_FILENAME```

If not specified, the log-generator used a file named 'default'

The message generator file containes 1-n formatted strings in the following format:

``` 0,N,N,Some unique CONNECTION message,3,3000 ```

Each comma separated value is defined below pased on position

POS

1 - MESSAGE_TYPE (0) Connection (1) Unknown
2 - UNIQUE (Y or N or Y:seed) - indicated whether each message generated should be different from any previous message. If an optional seed is defined, the MD5 is based on that seed instead of the message text. 
3 - SHARED (Y or N) - indicates whether the sequence of unique messages should be predicable and follow a sequence when run in a different instance.  This allows "unique" messages to be generated in multiple places simulating a siumilar failure on multiple deployments
4 - MESSAGE_TEXT - The message text to be written when a message is generated, note that if the message is declared to be unique it will have an additional MD5 "random" string appended
5 - FREQUENCY (1-n) the frequency in seconds for generating each message
6 - MAX (1-n) the maximum number of message to generate before terminating the timer event for the message

A resulting message will look like:

2020-11-17 15:25:46.877 ERROR Unknown error generated f5c150afbfbcef941def203e85cf40bc ['  File "C:\\AIAS\\log-generator\\src\\logger\\log_generator.py", line 121, in print_log_message\n    self.level1()\n', '  File "C:\\AIAS\\log-generator\\src\\logger\\log_generator.py", line 228, in level1\n    self.level2()\n', '  File "C:\\AIAS\\log-generator\\src\\logger\\log_generator.py", line 233, in level2\n    self.level3()\n', '  File "C:\\AIAS\\log-generator\\src\\logger\\log_generator.py", line 244, in level3\n    raise Exception(\n']

As each timer event is called, the log text is written to SYSOUT as a formatted string, then the timer event is immediately set up again.  This causes the component to loop until the MAX is reached for thatr message type.  If run as a thread then the process can be terminated by setting the instance of "graceful_killer.py", the instance variable <b>killer.kill_now</b> to True

A safety check is employed in the the max_queue_depth variable which terminates the main loop if the timer queue has more than 2 items in it, as this would imply that the timers have not been created correctly.


```MESSSAGE_DEFINITION_FILENAME```

If not specified, the log-generator used a file named 'default'

The message generator file containes 1-n formatted strings in the following format:

``` 0,N,N,Some unique CONNECTION message,3,3000 ```

Each comma separated value is defined below passed on position

POS:
<ul>
<li>1 - MESSAGE_TYPE (0) Connection (1) Unknown</li>
<li>2 - UNIQUE (Y or N or Y:seed) - indicated whether each message generated should be different from any previous message. If an optional seed is defined, the MD5 is based on that seed instead of the message text. </li>
<li>4 - MESSAGE_TEXT - The message text to be written when a message is generated, note that if the message is declared to be unique it will have an additional MD5 "random" string appended</li>
<li>5 - FREQUENCY (1-n) the frequency in seconds for generating each message</li>
<li>6 - MAX (0-n) the maximum number of message to generate before terminating the timer event for the message, 0 indicates no max limit and will generate messages indefinitely</li>

</ul>
A resulting message will look like:

<p>2020-11-17 15:25:46.877 ERROR Unknown error generated f5c150afbfbcef941def203e85cf40bc ['  File "C:\\AIAS\\log-generator\\src\\logger\\log_generator.py", line 121, in print_log_message\n    self.level1()\n', '  File "C:\\AIAS\\log-generator\\src\\logger\\log_generator.py", line 228, in level1\n    self.level2()\n', '  File "C:\\AIAS\\log-generator\\src\\logger\\log_generator.py", line 233, in level2\n    self.level3()\n', '  File "C:\\AIAS\\log-generator\\src\\logger\\log_generator.py", line 244, in level3\n    raise Exception(\n']

As each timer event is called, the log text is written to SYSOUT as a formatted string, then the timer event is immediately set up again.  This causes the component to loop until the MAX is reached for thatr message type.  If run as a thread then the process can be terminated by setting the instance of "graceful_killer.py", the instance variable <b>killer.kill_now</b> to True

A safety check is employed in the the max_queue_depth variable which terminates the main loop if the timer queue has more than 2 items in it, as this would imply that the timers have not been created correctly.

<h2>Running log-generator on OpenShift</h2>


<h4>Deploy in OpenShift as a template</h4>
  
In OpenShift, add from a Template, and search for "log-generator"
If you do not wish to use the default values then supply values for the following parameters:
<ul>
<li>MESSSAGE_DEFINITION_FILENAME  (the name of the message_definition file to use, "default" if not found or supplied)</li>
<li>APP_NAME  (an override for the APP_NAME label)</li>
<li>CONTAINER_NAME (an override for the CONTAINER_NAME label)</li>
</ul>
<h2>Running log-generator locally</h2>
<h4>docker</h4>
To run this application, navigate to the root of the application and build the code in a docker container using the following command:

docker build -t log-generator -f Dockerfile .

once built, run the following command to start the container in detached mode:

docker run -d log-generator

take note of the container id that is output from the above command, then logs can be viewed using the following command:

docker logs <containerId>

<h4>locally</h4>
To run this application without docker, in the terminal, navigate to the src directory and run_app.sh

