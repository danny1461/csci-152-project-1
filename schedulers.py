from abc import abstractmethod, ABC
from job import JobStatus
from events import classEvents
from functools import cmp_to_key

exports = ['FCFS', 'RoundRobin', 'SJN', 'FCFS_SJN_Hybrid']

# Base class for schedulers
@classEvents(['eventJobArrived', 'eventJobFinished'])
class BaseScheduler(ABC):
	def __init__(self, args):
		self._queue = []
		self._processedJobs = []
		self._nextJobIndex = 0

	# add job to the pool
	def schedule(self, job):
		job.markArrivalTime()
		self._queue.append(job)
		self.eventJobArrived.fire(job, scheduler=self)

	def jobCount(self):
		return len(self._queue)

	# clean up jobs that were completed in the last cycle
	def tick(self, delta):
		while len(self._processedJobs) > 0:
			job = self._processedJobs.pop()

			if job.status == JobStatus.FINISHED:
				self._queue.remove(job)
				self.eventJobFinished.fire(job, scheduler=self)

	# fetch the job instance that processors should be working on
	@abstractmethod
	def getNextJob(self):
		pass

# First Come First Served
class FCFS(BaseScheduler):
	# reset job pointer to beginning
	def tick(self, delta):
		super().tick(delta)
		self._nextJobIndex = 0

	def getNextJob(self):
		if self._nextJobIndex >= self.jobCount():
			return None

		index = self._nextJobIndex
		# increment job pointer
		# this is used to allow MultiCore processor to fetch multiple jobs in the order we wish
		self._nextJobIndex += 1
		self._processedJobs.append(self._queue[index])
		return self._queue[index]

class RoundRobin(BaseScheduler):
	quantumLength = 3

	def __init__(self, args):
		super().__init__(args)
		self._time = 0
		self._jobOffset = 0

	def tick(self, delta):
		self._jobOffset = 0
		self._time += delta
		if self._time >= RoundRobin.quantumLength and self.jobCount() > 0:
			self._time = 0
			self._nextJobIndex = (self._nextJobIndex + len(self._processedJobs)) % self.jobCount()

		while len(self._processedJobs) > 0:
			job = self._processedJobs.pop()

			if job.status == JobStatus.FINISHED:
				index = self._queue.index(job)
				if index > self._nextJobIndex:
					self._nextJobIndex -= 1
				self._queue.pop(index)
				self.eventJobFinished.fire(job, scheduler=self)

	def getNextJob(self):
		if self.jobCount() == 0:
			return None
		index = (self._nextJobIndex + self._jobOffset) % self.jobCount()

		# if this job was already given away, then we have looped and all possible jobs are busy
		if self._queue[index] in self._processedJobs:
			return None

		self._jobOffset += 1
		self._processedJobs.append(self._queue[index])
		return self._queue[index]

class SJN(FCFS):
	def schedule(self, job):
		super().schedule(job)
		self._queue.sort(key=lambda j: j.timeLeft)

class FCFS_SJN_Hybrid(FCFS):
	# 10 seconds of long process yielding
	threshold = 10

	def schedule(self, job):
		super().schedule(job)
		self._queue = sorted(self._queue, key=cmp_to_key(FCFS_SJN_Hybrid.comparator))

	def tick(self, delta):
		cnt = len(self._queue)
		super().tick(delta)
		if len(self._queue) < cnt:
			self._queue = sorted(self._queue, key=cmp_to_key(FCFS_SJN_Hybrid.comparator))

	@staticmethod
	def comparator(job1, job2):
		job1Old = job1.queueTime >= FCFS_SJN_Hybrid.threshold
		job2Old = job2.queueTime >= FCFS_SJN_Hybrid.threshold

		if job1Old and job2Old:
			return job1.arrivalTime - job2.arrivalTime
		elif job1Old:
			return -1
		elif job2Old:
			return 1
		
		return job1.timeLeft - job2.timeLeft

	