# Used to spoof time in the app
# Allows for time dilation to have time pass faster

from time import time as realtime

_time = None
_lastTime = None
_dialation = 1

def setTimeDialation(dialation=1):
	global _dialation
	_dialation = dialation

# main export
def time():
	global _time, _lastTime
	if (_time == None):
		_time = realtime()
	_lastTime = realtime()
	return _time + (_lastTime - _time) * _dialation