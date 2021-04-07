from weakref import ref

# EventHandler by Daniel Flynn @2021
# Came about from a desire to have a weak reference powered auto unsubscription system

# Class decorator that accepts a list of events to add to the class instances
def classEvents(events):
	def eventDecorator(cls):
		oldInit = None
		if hasattr(cls, '__init__'):
			oldInit = cls.__init__

		def newInit(self, *args, **kwargs):
			# invoke original __init__, passing along any arguments
			if oldInit != None:
				oldInit(self, *args, **kwargs)

			# construct event handlers
			for name in events:
				setattr(self, name, EventHandler())

		# override class's __init__ method
		cls.__init__ = newInit

		return cls
	return eventDecorator

# Event handler system
class EventHandler:
	def __init__(self):
		self._handlers = []

	# subscribes to the event
	def on(self, callback):
		# detect if given callback is a bound method
		if hasattr(callback, '__self__'):
			# bound function, add a weakref to the bound instance and store the underlying function
			val = (callback.__func__, ref(callback.__self__))
			self._handlers.append(val)
		else:
			# store basic callback. IE lambda, global function
			self._handlers.append(callback)

	# unsubscribes to the event
	def off(self, callback):
		# detect if given callback is a bound method
		if hasattr(callback, '__self__'):
			val = (callback.__func__, ref(callback.__self__))
			self._handlers.remove(val)
		else:
			# basic callback
			self._handlers.remove(callback)

	# detects any weakrefs that have lost their binding and removes those subscriptions
	def _flush(self):
		# Used to avoid mutating _handlers while iterating over it
		toRemove = []
		for val in self._handlers:
			if type(val) == tuple and val[1]() == None:
				toRemove.append(val)
		for val in toRemove:
			self._handlers.remove(val)

	# triggers the event passing along any parameters to each callback
	def fire(self, *args, **kwargs):
		self._flush()

		for val in self._handlers:
			if type(val) == tuple:
				val[0](val[1](), *args, **kwargs)
			else:
				print(val)
				val(*args, **kwargs)

	# counts the event listeners
	def count(self):
		self._flush()

		return len(self._handlers)