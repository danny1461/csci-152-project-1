from abc import ABC, abstractmethod
from collections import OrderedDict

exports = ['Console', 'LogFile']

class BaseDisplay:
	# def __init__(self, args, scheduler, producer):
	def __init__(self, args, producer):
		# subscribe to events
		self._latencyTotal = 0
		self._time = 0
		self._completedJobs = OrderedDict()
		self._waitingJobs = OrderedDict()
		self._jobs = OrderedDict()
		producer.eventNewJob.on(self._onNewJob)
		# scheduler.eventJobArrived.on(self._onJobArrival)
		# scheduler.eventJobFinished.on(self._onJobFinished)

	def tick(self, delta):
		self._time += delta
		if self._time > 1:
			self._time = 0
			self._printStatus()

	def _onNewJob(self, job):
		job.eventStarted.on(self._onJobStarted)
		job.eventFinished.on(self._onJobFinished)
		self._waitingJobs[job.id] = {
			'atime': job.delay,
			'etime': job.executeTime,
			'stime': job.serviceTime,
			'ptime': job.processTime
		}

	# def _onJobArrival(self, job, **kw):
	# 	self._output('Job #{} with {} execute time arrived'.format(job.id, job.executeTime))

	# def _onJobFinished(self, job, **kw):
	# 	self._output('Job #{} finished. It sat for {:.2f}s and finished after {:.2f}s'.format(job.id, job.waitTime, job.processTime))

	def _onJobStarted(self, job):
		meta = self._waitingJobs.pop(job.id)
		meta['stime'] = job.serviceTime
		self._jobs[job.id] = meta

	def _onJobFinished(self, job):
		self._latencyTotal += job.totalTime
		meta = self._jobs.pop(job.id)
		meta['ptime'] = job.processTime
		self._completedJobs[job.id] = meta
		job.eventStarted.off(self._onJobStarted)
		job.eventFinished.off(self._onJobFinished)

	def _printStatus(self):
		self._output('{} jobs waiting in queue, {} finished'.format(len(self._waitingJobs), len(self._completedJobs)))
		self._output('Job #   | Arrival Time | Execute Time | Service Time')
		for id, meta in self._jobs.items():
			self._output('Job {:<3} | {:{w}.{prec}f} | {:{w}.{prec}f} | {:{w}.{prec}f}'.format(id, meta['atime'], meta['etime'], meta['stime'], w=12, prec=2))
		self._output('\n')

	def showStats(self):
		self._output('Averaged latency: {:.2f}'.format(self._latencyTotal / len(self._completedJobs)))
		pass

	@abstractmethod
	def _output(self, msg):
		pass

# Simply outputs event messages to the console
class Console(BaseDisplay):
	def _output(self, msg):
		print(msg)

# Simply outputs event messages to a log file
class LogFile(BaseDisplay):
	def __init__(self, args, scheduler):
		super().__init__(args, scheduler)
		self._file = args.logFile

	def _output(self, msg):
		with open(self._file, 'a+') as handle:
			handle.write(msg + '\n')