# -*- coding: gb18030 -*-

import time
import weakref
import random
import math

import Timer
from .utils import Function
from .utils.Event import Event


# ------------------------------------------------
# base classes of task
# ------------------------------------------------
class Task:

	def __init__(self):
		self._done_event = None

	def __str__(self):
		return self.__class__.__name__

	def __repr__(self):
		return self.__str__()

	def do(self, target):
		pass

	def done(self):
		"""Done doesn't indicate any state of failure or success.
		It only means the task is over. So every task should invoke
		done whenever it's end."""
		if self._done_event:
			self._done_event.trigger()

	def doneEvent(self):
		if self._done_event is None:
			self._done_event = Event("DoneEvent")
		return self._done_event


class StoppableTask(Task):

	def __init__(self):
		Task.__init__(self)

	def interrupt(self):
		pass


class LoopTask(StoppableTask):

	def __init__(self, start, interval):
		StoppableTask.__init__(self)
		self.start = start
		self.interval = interval
		self.timer_id = 0
		self.target = None

	def do(self, target):
		self.target = weakref.ref(target, self._onTargetMiss)
		if self.timer_id:
			Timer.cancelTimer(self.timer_id)
		self.timer_id = Timer.addTimer(self.start, self.interval, self._onLoop)

	def interrupt(self):
		StoppableTask.interrupt(self)
		Timer.cancelTimer(self.timer_id)

	def _onLoop(self):
		pass

	def _onTargetMiss(self, ref_obj):
		self.interrupt()


# ------------------------------------------------
# application classes of task
# ------------------------------------------------
class Wait(StoppableTask):

	def __init__(self, t):
		StoppableTask.__init__(self)
		self.wait_time = t
		self.timer_id = 0

	def do(self, target):
		self.timer_id = Timer.addTimer(self.wait_time, 0, self._timeout)

	def _timeout(self):
		self.done()

	def interrupt(self):
		Timer.cancelTimer(self.timer_id)
		self.done()


# ------------------------------------------------
# һЩ��Ҫ���г�ʱ������������ʹ��Timeout������
# ���з�װ������:
# task = Timeout(PositionDetect(pos), 10)
# task.do(target)
# ���ǣ�task��ʼִ�к󣬻����λ�ü�⣬ͬʱ�趨10
# �볬ʱ��������10��λ�ü�⻹û��������λ�ü����
# ��ᱻ��ֹ��
# ------------------------------------------------
class Timeout(Wait):

	def __init__(self, task, timeout):
		Wait.__init__(self, timeout)

		assert isinstance(task, StoppableTask)
		self.task = task

	def do(self, target):
		Wait.do(self, target)
		self.task.doneEvent().bind(self._on_task_done)
		self.task.do(target)

	def interrupt(self):
		self._interrupt_task()
		Wait.interrupt(self)

	def _timeout(self):
		self._interrupt_task()
		Wait._timeout(self)

	def _on_task_done(self):
		Timer.cancelTimer(self.timer_id)
		self.done()

	def _interrupt_task(self):
		self.task.doneEvent().unbind(self._on_task_done)
		self.task.interrupt()


# ------------------------------------------------
# һЩ��Ҫ����ѭ��������������ʹ��Loop������
# ���з�װ������:
# task = Loop(Talk(1, "I am a bot!"), 0, 3)
# task.do(target)
# ���ǣ�task��ʼִ�к�����Ŀ���ÿ��3��˵һ�䡰
# I am a bot��������ѭ����
# ------------------------------------------------
class Loop(LoopTask):

	def __init__(self, task, start, interval):
		LoopTask.__init__(self, start, interval)
		self.task = task

	def interrupt(self):
		LoopTask.interrupt(self)
		self.done()

	def _onLoop(self):
		self.task.do(self.target())


# ------------------------------------------------
# һЩ��Ҫ�ظ�ִ�е��������ʹ��Repeat������
# ���з�װ������:
# task = Repeat(Talk(1, "I am a bot!"))
# task.do(target)
# ���ǣ�task��ʼִ�к�target�᲻��˵��
# I am a bot����ֱ������ϻ��ߵ���ָ��������
# ------------------------------------------------
class Repeat(StoppableTask):

	def __init__(self, task, count = -1):
		StoppableTask.__init__(self)
		self.task = task
		self.count = count
		self.counter = 0
		self.target = None
		self.timer_id = 0

	def do(self, target):
		self.target = weakref.ref(target)
		self.task.doneEvent().bind(self._on_task_done)
		self.counter = max(0, self.count)
		self._do_task()

	def interrupt(self):
		StoppableTask.interrupt(self)
		Timer.cancelTimer(self.timer_id)

		try:
			self.task.doneEvent().unbind(self._on_task_done)
			self.task.interrupt()
		except Exception:
			pass

		self.done()

	def _do_task(self):
		self.task.do(self.target())

	def _on_task_done(self):
		self.counter -= 1

		if self.count > 0 and self.counter == 0:
			self.done()
		else:
			self.timer_id = Timer.addTimer(0, 0, self._do_task)


class EchoTime(Task):

	def do(self, target):
		print "Now time is", time.time()
		self.done()


class Teleport(Task):

	def __init__(self, spaceLabel=None, position=None):
		Task.__init__(self)
		self.spaceLabel = spaceLabel
		self.position = position

	def do(self, target):
		""""""
		target.flySpace(self.spaceLabel, self.position)
		self.done()


class Move(Task):

	def __init__(self, position=None):
		Task.__init__(self)
		self.position = position

	def do(self, target):
		""""""
		target.moveToPos(self.position)
		self.done()


class Talk(Task):

	def __init__(self, channel=None, content=None, target=""):
		Task.__init__(self)
		self.channel = channel
		self.content = content
		self.target = target

	def do(self, target):
		""""""
		target.sendMessage(self.channel, self.content, self.target)
		self.done()


class PositionDetect(LoopTask):

	def __init__(self, position, range = 0.5, interval = 0.5):
		LoopTask.__init__(self, interval, interval)
		self.destination = position
		self.range = range
		self._failure_event = None

	def interrupt(self):
		LoopTask.interrupt(self)
		self.done()

	def fail(self):
		if self._failure_event:
			self._failure_event.trigger()
		self.done()

	def failureEvent(self):
		if self._failure_event is None:
			self._failure_event = Event("FailureEvent")
		return self._failure_event

	def _onLoop(self):
		if self.target().position.distTo(self.destination) < self.range:
			Timer.cancelTimer(self.timer_id)
			self.done()

	def _onTargetMiss(self, ref_obj):
		LoopTask._onTargetMiss(self, ref_obj)
		self.fail()


class RandomMove(Task):

	def __init__(self, center, range):
		Task.__init__(self)
		self.center = center
		self.range = range

	def do(self, target):
		position = Function.random_position(self.center, self.range)
		target.moveToPos(position)
		self.done()


class WizCommand(Task):

	def __init__(self, cmd):
		Task.__init__(self)
		self.command = cmd

	def do(self, target):
		target.wizCommand(self.command)
		self.done()


# ------------------------------------------------
# ������ս���������
# ------------------------------------------------
class FocusTarget(LoopTask):
	"""��һ��ָ��NPC���͵�entity��ΪĿ�꣬
	ͨ��ѭ����⣬ֱ���ҵ�ָ��entityΪֹ��"""

	def __init__(self, class_names):
		LoopTask.__init__(self, 0.5, 0.5)
		# class_name�б����Ԫ��
		self.class_names = class_names

	def _onLoop(self):
		target = self.target()
		entity = target.entities_nearest_by_class_names(self.class_names)

		if entity:
			target.bind_target(entity)
			self.interrupt()

	def interrupt(self):
		LoopTask.interrupt(self)
		self.done()


class FocusSelf(Task):
	"""���Լ�����ΪĿ��"""

	def do(self, target):
		target.bind_target(target)
		self.done()


class FocusEnemy(LoopTask):
	"""��һ���ɹ���NPC���͵�entity��ΪĿ�꣬
	ͨ��ѭ����⣬ֱ���ҵ�ָ��entityΪֹ��"""

	def __init__(self, class_names = ()):
		LoopTask.__init__(self, 0.5, 0.5)
		self.class_names = class_names

	def _onLoop(self):
		target = self.target()

		if self.class_names:
			enemy = target.enemy_nearest_by_class_names(self.class_names)
		else:
			# �����ָ��class_names����ô�����ȡ�����һ���ɹ���Ŀ��
			enemy = target.enemy_nearest()

		if enemy:
			target.bind_target(enemy)
			self.interrupt()

	def interrupt(self):
		LoopTask.interrupt(self)
		self.done()


class TestTarget(Task):
	"""���Ի����˵�Ŀ���Ƿ���Ч"""

	def do(self, target):
		assert target.get_target()


class TargetInvalid(LoopTask):
	"""�����⵽Ŀ����Ч�ͽ���"""

	def __init__(self):
		LoopTask.__init__(self, 0.0, 0.5)

	def _onLoop(self):
		target = self.target()
		if target.get_target() is None:
			self.interrupt()

	def interrupt(self):
		LoopTask.interrupt(self)
		self.done()


class TargetCanNotFight(LoopTask):
	"""�����⵽Ŀ�겻��ս���ͽ���"""

	def __init__(self):
		LoopTask.__init__(self, 0.0, 0.5)

	def _onLoop(self):
		target = self.target()
		target_target = target.get_target()
		if target_target is None or not target.can_fight_to(target_target):
			self.interrupt()

	def interrupt(self):
		LoopTask.interrupt(self)
		self.done()


class TargetDead(LoopTask):
	"""�����⵽Ŀ�������ͽ���"""

	def __init__(self):
		LoopTask.__init__(self, 0.0, 0.5)

	def _onLoop(self):
		target = self.target()
		target_target = target.get_target()
		if target_target is None or target.entity_dead(target_target):
			self.interrupt()

	def interrupt(self):
		LoopTask.interrupt(self)
		self.done()


class FollowTarget(LoopTask):
	"""����Ŀ�ֱ꣬�����ⲿ��ϻ���Ŀ����ʧ"""

	def __init__(self, range = 3.0):
		LoopTask.__init__(self, 1.0, 1.0)
		self.range = range

	def _onLoop(self):
		target = self.target()
		target_target = target.get_target()

		if target_target is None:
			self.interrupt()
		elif target.position.distTo(target_target.position) > self.range:
			target.moveToPos(target_target.position)

	def interrupt(self):
		LoopTask.interrupt(self)
		self.done()


class SeekTarget(LoopTask):
	"""׷��Ŀ�꣬�������ָ�������ھ�ֹͣ"""

	def __init__(self, range = 2.5):
		LoopTask.__init__(self, 0.5, 0.5)
		self.range = range

	def _onLoop(self):
		target = self.target()
		target_target = target.get_target()

		if target_target is None or\
			target.position.distTo(target_target.position) < self.range:
			self.interrupt()
		else:
			target.moveToPos(target_target.position)

	def interrupt(self):
		LoopTask.interrupt(self)
		self.done()


class SpellTarget(Task):
	"""�Ե�ǰĿ��ʹ��ָ������"""

	def __init__(self, skill_id):
		Task.__init__(self)
		self.skill_id = skill_id

	def do(self, target):
		target.spell_target(target.targetID, self.skill_id)
		self.done()


class ProfessionSpell(Task):
	"""ָ��ְҵʩ��ָ������"""

	def __init__(self, skill_id, profession):
		Task.__init__(self)
		self.skill_id = skill_id
		self.profession = profession

	def do(self, target):
		if target.getClass() == self.profession:
			target.spell_target(target.targetID, self.skill_id)
		self.done()


class AddSkills(Task):
	"""��ָ��ְҵ�Ļ�������Ӽ���"""

	def __init__(self, skills, profession):
		Task.__init__(self)
		self.skills = skills
		self.profession = profession

	def do(self, target):
		if target.getClass() == self.profession:
			for skill_id in self.skills:
				target.wizCommand("/add_skill %d" % skill_id)
		self.done()


class InvokeMethod(Task):
	"""����ָ���ķ��������ڵ���"""

	def __init__(self, method, *args, **kwargs):
		Task.__init__(self)
		self.method = script
		self.args = args
		self.kwargs = kwargs

	def do(self, target):
		getattr(target, self.method)(*self.args, **self.kwargs)
		self.done()
