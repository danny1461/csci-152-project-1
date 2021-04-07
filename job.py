from enum import Enum
from events import classEvents
from faketime import time

class JobStatus(Enum):
	RUNNING = 1
	FINISHED = 2

@classEvents(['eventArrived', 'eventStarted', 'eventFinished'])
class Job:
	# static int to auto assign an id to jobs
	_nextId = 0

	# fetches the next id
	@staticmethod
	def getNextJobId():
		id = Job._nextId
		# increments the static variable for next time
		Job._nextId += 1
		return id

	def __init__(self, executeTime, delay = 0):
		self._id = Job.getNextJobId()
		self._delay = delay
		self._creationTime = time()
		self._arrivalTime = None
		self._executeTime = executeTime
		self._timeLeft = executeTime
		self._serviceTime = None
		self._finishTime = None

	def __str__(self):
		return 'Job #{}'.format(self.id)

	# getters
	@property
	def id(self):
		return self._id

	@property
	def arrivalTime(self):
		return self._arrivalTime

	@property
	def executeTime(self):
		return self._executeTime
	
	@property
	def serviceTime(self):
		if self._serviceTime == None:
			return -1
		return self._serviceTime - self._creationTime

	@property
	def status(self):
		return JobStatus.RUNNING if self._finishTime == None else JobStatus.FINISHED

	@property
	def timeLeft(self):
		return self._timeLeft

	@property
	def waitTime(self):
		if self._serviceTime == None:
			return -1
		return self._serviceTime - self._arrivalTime

	@property
	def processTime(self):
		if self._finishTime == None:
			return -1
		return self._finishTime - self._serviceTime

	@property
	def totalTime(self):
		if self._finishTime == None or self._arrivalTime == None:
			return -1
		return self._finishTime - self._arrivalTime

	@property
	def delay(self):
		return self._delay

	@property
	def queueTime(self):
		if self._arrivalTime == None:
			return -1

		if self._finishTime != None:
			return self._finishTime - self._arrivalTime

		return time() - self._arrivalTime

	def markServiceTime(self):
		if self._serviceTime == None:
			self._serviceTime = time()
			self.eventStarted.fire(job=self)
	
	def markArrivalTime(self):
		if self._arrivalTime == None:
			self._arrivalTime = time()
			self.eventArrived.fire(job=self)

	def markFinishTime(self):
		if self._finishTime == None:
			self._finishTime = time()
			self.eventFinished.fire(job=self)

	# simulates running this task for delta time
	def runFor(self, delta):
		self.markServiceTime()

		self._timeLeft -= delta
		if (self._timeLeft <= 0):
			self.markFinishTime()