import argparse
from os import path
from sys import argv, exit
import faketime

import schedulers
import producers
import consumers
import displays

# If not command line args are passed, force the help page
commandLineArgs = argv[1:]
if len(commandLineArgs) == 0:
	commandLineArgs.append('-h')

# Gets a pretty list of members of a module
def _getModuleExports(mod):
	return '[' + ', '.join(mod.exports) + ']'

# Validates user input and transforms it
def _moduleExportChecker(mod):
	def checker(value):
		if value not in mod.exports:
			raise argparse.ArgumentTypeError('%s is not a valid')
		return getattr(mod, value)
	return checker

# Gather arguments
parser = argparse.ArgumentParser(
		description='Simulate an operating system scheduler and job process environment')

parser.add_argument(
		'scheduler',
		type=_moduleExportChecker(schedulers),
		help='The class name for the scheduler: ' + _getModuleExports(schedulers))
parser.add_argument(
		'producer',
		type=_moduleExportChecker(producers),
		help='The class name for the producer: ' + _getModuleExports(producers))
parser.add_argument(
		'consumer',
		type=_moduleExportChecker(consumers),
		help='The class name for the consumer: ' + _getModuleExports(consumers))
parser.add_argument(
		'display',
		type=_moduleExportChecker(displays),
		default='console',
		help='The class name for the display system: ' + _getModuleExports(displays))
parser.add_argument(
		'--jobsFile',
		nargs='?',
		type=str,
		default='',
		help='Required if using the File Producer')
parser.add_argument(
		'--jobCount',
		nargs='?',
		type=int,
		default=50,
		help='Number of jobs to generate for the Random Producer')
parser.add_argument(
		'--jobMinTime',
		nargs='?',
		type=int,
		default=0.1,
		help='Min execution time for jobs generated by the Random Producer')
parser.add_argument(
		'--jobMaxTime',
		nargs='?',
		type=int,
		default=10,
		help='Max execution time for jobs generated by the Random Producer')
parser.add_argument(
		'--cores',
		nargs='?',
		type=int,
		default=4,
		help='How many cores the MultiCore process has')
parser.add_argument(
		'--quantumLength',
		nargs='?',
		type=int,
		default=3,
		help='How many seconds the RoundRobin algorithm devotes to a job')
parser.add_argument(
		'--time',
		nargs='?',
		type=int,
		default=60,
		help='How long to run the simulation for in seconds')
parser.add_argument(
		'--speed',
		nargs='?',
		type=float,
		default=1,
		help='How quickly to pass time by: 1 is realtime, 2 is twice as fast, etc')
parser.add_argument(
		'--logFile',
		nargs='?',
		type=str,
		default='project1-{}-output.txt'.format(int(faketime.time())),
		help='Required if using the Manual Producer')

args = parser.parse_args(commandLineArgs)

# Couple conditional requirements
if (args.speed <= 0):
	exit('Speed should be greater than 0')
if (args.producer == producers.File and not path.exists(args.jobsFile)):
	exit('Jobs file cannot be found')

# Put together chosen classes and bootstrap
faketime.setTimeDialation(args.speed)
scheduler = args.scheduler(args)
producer = args.producer(args, scheduler)
consumer = args.consumer(args, scheduler)
display = args.display(args, producer)

lastTime = faketime.time()
firstTime = faketime.time()
producer.produceJobs()

while scheduler.jobCount() > 0 or producer.count() > 0:
	delta = faketime.time() - lastTime
	lastTime = faketime.time()
	
	# Allow each module to experience the passage of time
	producer.tick(delta)
	scheduler.tick(delta)
	consumer.tick(delta)
	display.tick(delta)

display.showStats()

"""
	How does your source code address the maintenance (e.g., changing existing
	code, extending new features) requests from your manager?
		All code has been broken up into modules. Each module is dedicated to a singular
		task: scheduling, producing, consuming, displaying. Each class is implemented with
		polymorphism to help share as much common functionality as possible. New features can
		be added easily, either by working in specific classes, or adding new classes to the
		modules. If the `exports` key is updated as well, those new classes will be
		automatically incorporated.

	Describe the pros and cons:
		Pros:
			Cut down on excessive ownership or access of object instances
			Temporal cohesion avoided through the use of event handlers

		Cons:
			Lots of similarity in all the modules, like them all containing a `tick` method
			Display classes are too basic

	Please explain how you may improve from cons:
		I did at many times wish for interfaces due to the similarity of many modules in the
		initial design, but Python does not support them. It does have multi-inheritance but
		I did not pursue it.

		I really don't like this main file. It does so many unavoidable things, which always
		feels like it has extremely low cohesion and I'm alawys interested in ways to improve
		this. 
"""