# -*- coding: gb18030 -*-

import weakref
import Timer
from .Task import Task
from .utils.Function import Functor


# Task group contains a set of tasks, also it's a Task
# tasks do parallelly.
class TaskGroup(Task):

	def __init__(self):
		Task.__init__(self)
		self.tasks = []

	def __str__(self):
		total = len(self.tasks)
		maxshow = min(3, total)
		current = 0
		showstr = self.__class__.__name__ + "(%s)"
		taskstr = []

		while current < maxshow:
			if current == maxshow - 1:
				if maxshow < total:
					taskstr.append("..(%i).." % (total - maxshow))
				taskstr.append(str(self.tasks[-1]))
				break
			else:
				taskstr.append(str(self.tasks[current]))
				current += 1

		return showstr % "-".join(taskstr)

	def do(self, target):
		"""do all tasks"""
		for task in self.tasks:
			task.do(target)
		self.done()

	def addTask(self, task):
		""""""
		self.tasks.append(task)

	def removeTask(self, task):
		""""""
		try:
			self.tasks.remove(task)
		except ValueError, e:
			pass

	def removeAt(self, index):
		""""""
		try:
			self.tasks.pop(index)
		except IndexError, e:
			pass


# Serial task group drived from TaskGroup,
# tasks will be done serially
class SerialTaskGroup(TaskGroup):

	def __init__(self):
		TaskGroup.__init__(self)
		self.currentIndex = -1
		self.currentTimer = 0
		self.target = None

	def do(self, target):
		"""do the task"""
		self.target = weakref.ref(target)

		if len(self.tasks):
			self.currentIndex = -1
			self.doNext()
		else:
			self.done()

	def doNext(self):
		"""执行下一个任务"""
		try:
			nextIndex = self.currentIndex + 1
			next = self.tasks[nextIndex]
			self.currentIndex = nextIndex

			next.doneEvent().bind(self._onTaskDone)
			next.do(self.target())

		except IndexError:
			print "All tasks done on serial group"
			self.done()

		except Exception, err:
			print "Serial group done on error occurs:"
			print err
			self.done()

	def _onTaskDone(self):
		"""Current task done callback.
		Do the follow task at later tick to avoid
		stack overflow in case that too many tasks
		in the task series."""
		self.currentTimer = Timer.addTimer(0.0, 0, self.doNext)

	def interrupt(self):
		"""打断任务组执行"""
		Timer.cancelTimer(self.currentTimer)

		try:
			current = self.tasks[self.currentIndex]
			current.doneEvent().unbind(self._onTaskDone)
			current.interrupt()
		finally:
			self.done()


# ParallelTaskGroup contains a set of tasks, also it's a Task.
# Set of tasks do parallelly. This task will be done when the last
# task done.
class ParallelTaskGroup(TaskGroup):

	def __init__(self):
		TaskGroup.__init__(self)
		self.timers = []
		self.doneCounter = 0

	def do(self, target):
		self.doneCounter = len(self.tasks)

		if self.doneCounter == 0:
			self.done()
			return

		self.timers = []

		for task in self.tasks:
			task.doneEvent().bind(self._onTaskDone)
			self.timers.append(Timer.addTimer(0, 0, Functor(task.do, target)))

	def _onTaskDone(self):
		self.doneCounter -= 1

		if self.doneCounter == 0:
			print "All tasks on parallel group done."
			self.done()

	def interrupt(self):
		""""""
		for timer in self.timers:
			Timer.cancelTimer(timer)

		for task in self.tasks:
			task.doneEvent().unbind(self._onTaskDone)
			try:
				task.interrupt()
			except Exception:
				pass

		self.done()


# ParallelTaskGroup contains a set of parallelly tasks and one primary
# task, also it's a Task.This task will be done when the primary task done.
class PrimacyParallelGroup(TaskGroup):

	def __init__(self):
		TaskGroup.__init__(self)
		self.timers = []
		self.primary_task = None

	def do(self, target):
		if len(self.tasks) == 0:
			self.done()
			return

		self.timers = []
		self.primary_task.doneEvent().bind(self._on_primary_task_done)

		for task in self.tasks:
			self.timers.append(Timer.addTimer(0, 0, Functor(task.do, target)))

	def set_primary_task(self, task):
		self.primary_task = task

	def interrupt(self):
		""""""
		for timer in self.timers:
			Timer.cancelTimer(timer)

		self.primary_task.doneEvent().unbind(self._on_primary_task_done)

		for task in self.tasks:
			try:
				task.interrupt()
			except Exception:
				pass

		self.done()

	def _on_primary_task_done(self):
		print "Primacy group done on primary task done."
		self.interrupt()
