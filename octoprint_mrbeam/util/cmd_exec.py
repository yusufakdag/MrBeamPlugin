
import logging
import subprocess
from octoprint_mrbeam.mrb_logger import mrb_logger


_logger = mrb_logger("octoprint.plugins.mrbeam.cmd_exec")


TIMEOUT_CMD_TEMPLATE = "timeout {timeout:.2f} {cmd}"
TIMEOUT_EXIT_CODE = 124

def exec_cmd(cmd, timeout=0.0):
	'''
	Executes a system command
	:param cmd:
	:return: True if system returncode was 0,
			 False if the command returned with an error,
			 None if there was an exception.
	'''
	code = None
	cmd = TIMEOUT_CMD_TEMPLATE.format(timeout=timeout, cmd=cmd)

	_logger.debug("_execute_command() command: '%s'", cmd)
	try:
		code = subprocess.call(cmd, shell=True)
	except Exception as e:
		#  not sure if we will ever have a valid value for code here...?
		if code == TIMEOUT_EXIT_CODE:
			_logger.debug("Command timed out: '%s', return code: %s, Exception: %s", cmd, code, e)
		else:
			_logger.debug("Failed to execute command '%s', return code: %s, Exception: %s", cmd, code, e)
		return None

	_logger.debug("_execute_command() command return code: '%s'", code)
	return code == 0


def exec_cmd_output(cmd, timeout=10.0, log_cmd=True):
	'''
	Executes a system command and returns its output.
	:param cmd:
	:return: Tuple(String:output , int return_code)
			If system returncode was not 0 (zero), output will be None
	'''

	output = None
	code = 0

	cmd = TIMEOUT_CMD_TEMPLATE.format(timeout=timeout, cmd=cmd)

	if log_cmd:
		_logger.debug("_execute_command() command: '%s'", cmd)
	else:
		_logger.debug("_execute_command() command (log_cmd=False)")
	try:
		output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		code = e.returncode

		if log_cmd == False and cmd is not None:
			cmd = cmd[:50]+'...' if len(cmd)>30 else cmd

		output = e.output
		# if log_cmd == False and e.output is not None:
		# 	output = e.output[:30]+'...' if len(e.output)>30 else e.output
		if code == TIMEOUT_EXIT_CODE:
			_logger.debug("Command timed out: '%s', return code: %s, output: '%s'", cmd, e.returncode, output)
		else:
			_logger.debug("Fail to execute command '%s', return code: %s, output: '%s'", cmd, e.returncode, output)

	return output, code
