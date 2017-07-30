# python-subprocess2

Extensions on the python subprocess module. Importing subprocess2 will extend the global "subprocess" module (only additions, no modifications, so it's safe). 


PyDoc Reference
---------------

The full PyDoc reference for extended subprocess modules can be found at: http://pythonhosted.org/python-subprocess2/


Popen
=====

Additions to Popen class:


**waitUpTo**


This method adds the ability to specify a timeout when waiting for a subprocess to complete.


	Popen.waitUpTo (timeoutSeconds, pollInterval)

	Wait up to a certain number of seconds for the process to end.


**waitOrTerminate**

This method allows specifying a timeout, like waitUpTo, but will also handle terminating or killing the application if it exceeds the timeout (see full documentation for details and parameters)


	def waitOrTerminate(self, timeoutSeconds, pollInterval=DEFAULT_POLL_INTERVAL, terminateToKillSeconds=SUBPROCESS2_DEFAULT_TERMINATE_TO_KILL_SECONDS):


Background Task Management
==========================

One of the benefits to modern computing is the ability to multitask. Your application may want to start several sub processes at once, and have them all collecting output simultaneously. The standard python "subprocess" module does not provide a simple approach through it's API to do this.

subprocess2 extends the Popen module by adding the notion of a "Background Task." When you call "runInBackground" on a pipe object, it will create and start a thread to automatically handle that process. 

Calling "runInBackground" on a pipe returns a "BackgroundTaskInfo" option, which is dynamically updated as the status the subprocess progresses. 

If you have open streams (stdout, stderr), they will automatically be read in non-blocking fashion into "stdoutData" and "stderrData" respectively on that object. 

When the subprocess terminates, the "returnCode" field will be set, and "isFinished" will be marked True.


You can use this to farm out 10 processes quickly, collect all their data, and wait for them to complete. Other uses may be long-running associated proccesses, such as several searches collecting data, all being used to update a display.


By default, data will be stored as bytes. To decode with a specific encoding (e.x. utf-8), pass the codec name as the "encoding" argument.


**BackgroundTask PyDoc Reference:**

http://pythonhosted.org/python-subprocess2/subprocess2.BackgroundTask.html


**runInBackground:**

	def runInBackground(self, pollInterval=.1, encoding=False):
		'''
			runInBackground - Create a background thread which will manage this process, automatically read from streams, and perform any cleanups

			The object returned is a "BackgroundTaskInfo" object, and represents the state of the process. It is updated automatically as the program runs,
			and if stdout or stderr are streams, they are automatically read from and populated into this object.

			@see BackgroundTaskInfo for more info or http://pythonhosted.org/python-subprocess2/subprocess2.BackgroundTask.html

			@param pollInterval - Amount of idle time between polling
			@param encoding - Default False. If provided, data will be decoded using the value of this field as the codec name (e.x. "utf-8"). Otherwise, data will be stored as bytes.
		'''

Object returned is of type BackgroundTaskInfo ( http://pythonhosted.org/python-subprocess2/subprocess2.BackgroundTask.html#BackgroundTaskInfo ):

**BackgroundTaskInfo**


		'''
			BackgroundTaskInfo - Represents a task that was sent to run in the background. Will be updated as the status of that process changes.

				Can be used like an object or a dictionary.

			This object populates its data automatically as the program runs in the background, managed by a thread.

			FIELDS:

				stdoutData - Bytes read automatically from stdout, if stdout was a pipe, or from stderr if stderr was set to subprocess.STDOUT
				stderrData - Bytes read automatically from stderr, if different pipe than stdout.
				isFinished - False while the background application is running, True when it completes.
				returnCode - None if the program has not completed, otherwise the numeric return code.
				timeElapsed - Float of how many seconds have elapsed since the last update (updates happen very close to the "pollInterval" provided when calling runInBackground)

		'''


*Example:*

	import subprocess2 as subprocess


	pipe1 = subprocess.Popen(......, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	pipe2 = subprocess.Popen(......, stdout=subprocess.PIPE)

	pipe1Info = pipe1.runInBackground()
	pipe2Info = pipe2.runInBackground()


will have two processes running in the background, collecting their output automatically, and cleaning up automatically.

If you decide later you wait to block the current context until one of those pipes complete, you can pull it back into foreground (while maintaining the automatic population of streams/values) by calling "waitToFinish" on the BackgroundTaskInfo.


	def waitToFinish(self, timeout=None, pollInterval=.1):

			Wait (Block current thread), optionally with a timeout, until background task completes.


*Example (continued):*

	pipe1Info = pipe1.runInBackground()

	# ....do some hard work here...
	sys.stdout.write('Current output: ' + pipe1Info.stdoutData.decode('utf-8'))
	# .... more hard work...

	returnCode = pipe1Info.waitToFinish()

Simple
======

subprocess2 provides a "Simple" class, which provides simple, direct, and intuitive static methods for running subprocesses and gathering output.


*Example*

Get list of all executable files in current directory (and subdirs) as an array:

	import subprocess2

	executableFiles = subprocess2.Simple.runGetOutput('find . -type f -executable').split('\n')[:-1] # All but last entry because of final newline in output


Functions include:

**runGetOutput**

Simpliest method -- pass a command, get output on return.

	runGetOutput(cmd, raiseOnFailure=False, encoding=sys.getdefaultencoding())

		runGetOutput - Simply runs a command and returns the output as a string. Use #runGetResults if you need something more complex.


*Example:*

	import subprocess2

	try:
		executableFiles = subprocess2.Simple.runGetOutput('find . -type f -executable', raiseOnFailure=True).split('\n')[:-1]
	except subprocess2.Simple.SimpleCommandFailure as e:
		sys.stderr.write('Command failed [return=%d]: stderr = %s\n' %(e.returnCode, e.stderr) )


**runGetResults**

More complicated, returns results in a dict. See docstring for all options.

	runGetResults(cmd, stdout=True, stderr=True, encoding=sys.getdefaultencoding())

		runGetResults - Simple method to run a command and return the results of the execution as a dict.


*Example:*

	import subprocess2

	results = subprocess2.Simple.runGetResults('find . -type f -executable')

	if results['returnCode'] != 0:
		sys.stderr.write('Command failed [return=%d]: stderr = %s\n' %(results['returnCode'], results['stderr']))
	else:
		executableFiles = results['stdout'].split('\n')[:-1]


**"Simple" PyDoc**

See: http://pythonhosted.org/python-subprocess2/subprocess2.simple.html for the pydoc of the "Simple" helper


Constants
---------

DEFAULT\_POLL\_INTERVAL = .05 *Number of seconds as default for polling interval*

SUBPROCESS2\_DEFAULT\_TERMINATE\_TO\_KILL\_SECONDS = 1.5 *Default number of seconds between SIGTERM and SIGKILL for Popen.waitOrTerminate method*


SUBPROCESS2\_PROCESS\_COMPLETED  = 0 *Mask value for noting that process completed by itself*
SUBPROCESS2\_PROCESS\_TERMINATED = 1 *Mask value for noting that process was sent SIGTERM*
SUBPROCESS2\_PROCESS\_KILLED     = 2 *Mask value for noting that process was sent SIGKILL*


Compatability
-------------

Officially supported python versions are 2.7, 3.4, 3.5, and 3.6.


Tests / Examples
----------------

Tests are written using the GoodTests ( <https://github.com/kata198/GoodTests> ) framework.

The tests can be found in the "tests" directory of the project root.

Use runTests.py in that directory to download GoodTests (if not already available/installed) and run the test suite against the local instance of subprocess2.
