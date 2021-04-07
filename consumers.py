from abc import abstractmethod, ABC

exports = ['SingleCore', 'MultiCore']

# base class for processors
class BaseProcessor(ABC):
	def __init__(self, args, scheduler):
		self._scheduler = scheduler

	@abstractmethod
	def tick(self, delta):
		pass

# simulates a single core processor that can only work on one job at a time
class SingleCore(BaseProcessor):
	def tick(self, delta):
		while delta > 0:
			# fetch job
			job = self._scheduler.getNextJob()
			#bail if no job. IE Producer is running slow and scheduler ran out of work
			if job == None:
				return

			# only process as much time as is needed for this job
			time = min(delta, job.timeLeft)
			job.runFor(delta)
			# deduct this time from delta, and allow it to carry over to next job
			delta -= time

# simulates a multi core processor that can work on as many jobs simultaneously as it has cores
class MultiCore(BaseProcessor):
	def __init__(self, args, scheduler):
		super().__init__(args, scheduler)
		# create a list of SingleCore processors
		self._singleCoreProcessors = [SingleCore(args, scheduler) for _ in range(args.cores)]

	def tick(self, delta):
		# allow each SingleCore to pick their jobs and execute
		for processor in self._singleCoreProcessors:
			processor.tick(delta)
