from abc import abstractmethod, ABC
from events import classEvents
from random import uniform
from job import Job
from csv import reader

exports = ['Random', 'CSVFile']

# base class for producers
@classEvents(['eventNewJob'])
class BaseProducer(ABC):
	def __init__(self, args, scheduler):
		self._args = args
		self._scheduler = scheduler
		self._time = 0
		self._queue = []

	# determine if it's time to release a job to the scheduler
	def tick(self, delta):
		if len(self._queue) == 0:
			return

		self._time += delta
		while len(self._queue) > 0:
			(delay, job) = self._queue[0]

			if delay > self._time:
				break

			self._queue.pop(0)
			self._scheduler.schedule(job)

	def count(self):
		return len(self._queue)

	@abstractmethod
	def produceJobs(self):
		pass

class Random(BaseProducer):
	def produceJobs(self):
		delay = 0
		for i in range(self._args.jobCount):
			executeTime = uniform(self._args.jobMinTime, self._args.jobMaxTime)
			delay += 1
			job = Job(executeTime, delay)
			self.eventNewJob.fire(job)
			self._queue.append((delay, job))

class CSVFile(BaseProducer):
	def produceJobs(self):
		with open(self._args.jobsFile, 'r') as handle:
			# parse the file as CSV
			csvReader = reader(handle, delimiter=',')
			for row in csvReader:
				# cast each column value to float
				row = list(map(lambda s: float(s.strip()), row))
				job = Job(row[1], row[0])
				self.eventNewJob.fire(job)
				self._queue.append((row[0], job))
			self._queue.sort(key=lambda x: x[0])