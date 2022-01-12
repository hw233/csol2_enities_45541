# -*- coding: utf-8 -*-
import BigWorld
import random, time, threading, weakref
import SkillTargetObjImpl, csdefine

from task.taskapps import apps
from task.utils import Function, Weaker


class BotManager():

	BOT_CHAT = 0x01					# ���쿪��
	BOT_FIGHT = 0x02				# ս������
	BOT_BUFF = 0x04					# BUFF����
	BOT_HSZ = 0x08					# ������
	BOT_FLY_TO_YEWAI = 0x10					# ���͵�Ұ��һ�����λ�ý��д��

	MSG_LIST = ["��Һð��� ���ǻ����ˣ�ʱ�䣺%d   ��� %d",
				"���������Ͻ��ؼ����·�����ʱ�䣺%d   ��� %d",
				"����3�����ˣ������Ͻ���һ�㣬ʱ�䣺%d   ��� %d",
				"�����ػ𣡣���ʱ�䣺%d   ��� %d",
				"�������ɴ��� ���ܴ�ҿ�һ����ʱ�䣺%d   ��� %d",
				"Just do it��ʱ�䣺%d   ��� %d",
				"��ʲô��������ʱ�䣺%d   ��� %d",
				"�����һ���������ʱ�䣺%d   ��� %d",
				"��ɽ�˺��������氡������ʱ�䣺%d   ��� %d",
				]

	_INSTANCE = None

	@staticmethod
	def instance():
		if BotManager._INSTANCE is None:
			BotManager._INSTANCE = BotManager()
		return BotManager._INSTANCE

	def __init__(self):
		self.state = 0						# ������ѭ��״̬
		self.timerID = 0					# timerID
		self.times = -1						# ѭ������
		self.lstClient = []					# �ͻ����б�
		self.lstRoleList = []				# ����б�

	def setState(self, state):
		"""
		�趨ѭ��״̬
		"""
		self.state = state

	def getState(self, state):
		"""
		���ѭ��״̬
		"""
		return self.state

	def getRoleList(self):
		"""
		��ȡ�����б�
		"""
		self.lstClient = [id for id in BigWorld.bots.keys()]
		self.lstRoleList = [BigWorld.bots[id].entities[id] for id in self.lstClient if BigWorld.bots[id].entities[id].__class__.__name__ == 'Role']

	def getRoleCount(self):
		"""
		��û���������
		"""
		self.getRoleList()
		return len(self.lstClient), len(self.lstRoleList)

	def moveTo(self, x, y, z, p):
		"""
		�������ƶ�
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.moveTo(x, y, z, p)

	def autoMove(self, nTime=1):
		"""
		�Ƴ�Buff
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.autoMove(False)
		def m():
			for role in self.lstRoleList:role.autoMove(True)
		BigWorld.bots.values()[0].addTimer(nTime, m, False)


	def goFengMing(self):
		"""
		�ƶ�������
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.goFengMing()

	def goFengMingCheng(self):
		"""
		�ƶ���������
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.goFengMingCheng()

	def gmCmd(self, strCmd):
		"""
		����GMָ��
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.wizCommand(strCmd)

	def beginBotLoop(self, state):
		"""
		�򿪻�����ѭ��
		"""
		self.setState(state)
		self.getRoleList()

		if self.times != -1:return
		self.times = 0

#		for role in self.lstRoleList:
#			BigWorld.bots[role.id].speed = 6


		self.timerID = BigWorld.bots.values()[0].addTimer(0.1, self.botLoop, True)

	def endBotLoop(self):
		"""
		�ر�ѭ��
		"""
		BigWorld.bots.values()[0].delTimer(self.timerID)
		self.timerID = 0
		self.times = -1

	def botLoop(self):
		"""
		������Loop
		"""
		self.times += 1
		self.getRoleList()
		if self.state & BotManager.BOT_CHAT:
			nSize = len(self.lstRoleList)
			nIndex = random.randint(0, len(BotManager.MSG_LIST) - 1)
			strMsg = BotManager.MSG_LIST[nIndex] % (self.times, nSize)
			for role in self.lstRoleList:
				if role.id % 100 == self.times % 100:
					role.sendMessage(csdefine.CHAT_CHANNEL_NEAR, strMsg)

		if self.state & BotManager.BOT_BUFF:
			for role in self.lstRoleList:
				if role.id % 100 == self.times % 100:
					role.useDefaultBuff()

		if self.state & BotManager.BOT_FIGHT:
			for role in self.lstRoleList:
				if role.id % 10 == self.times % 10:
					role.autoFightLoop()

		if self.state & BotManager.BOT_HSZ:
			for role in self.lstRoleList:
				if role.id % 50 == self.times % 50:
					role.autoUseSkill()

		if self.state & BotManager.BOT_FLY_TO_YEWAI:
			for role in self.lstRoleList:
				if role.id % 3000 == self.times % 3000:
					r = random.random()
					if r > 0.9:
						role.flyToFengmingOutSide()
					elif r > 0.8:
						role.flyToFeilaishi()
					elif r > 0.7:
						role.flyToBanquanxiang()
					elif r > 0.6:
						role.flyToBishijian()
					elif r > 0.5:
						role.flyToYinkecun()
					elif r > 0.4:
						role.flyToYunMengze02()
					elif r > 0.3:
						role.flyToYunMengze01()
					elif r > 0.2:
						role.flyToPengLai()
					elif r > 0.1:
						role.flyToBeiMing()
					elif r > 0.0:
						role.flyToKunlun()

	def fightTo(self, nID):
		"""
		�����ض���ID
		"""
		self.getRoleList()
		monster = BigWorld.bots.values()[0].entities[nID]
		target = SkillTargetObjImpl.createTargetObjEntity(monster)
		for role in self.lstRoleList:role.fightTo(monster, target, 1)

	def setPKMode(self, pkMode):
		"""
		��PK����
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.cell.setPkMode(pkMode)

	def cloneReviveItem(self):
		"""
		��������ҩƷ
		"""
		self.gmCmd("/add_item 110103001 20")

	def useItemRevive(self):
		"""
		ʹ�ø���ҩƷ
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.useItemRevive()

	def revive(self):
		"""
		����
		"""
		self.cloneReviveItem()
		def m():
			self.useItemRevive()
			self.autoMove()
		BigWorld.bots.values()[0].addTimer(1, m, False)

	def withdrawEidolon(self):
		"""
		�ջ�С����
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.withdrawEidolon()

	def protect(self):
		"""
		ս������
		"""
		self.gmCmd("/set_level 110")
		self.gmCmd("/set_attr HP_Max 1000000")
		self.gmCmd("/set_attr HP 1000000")

	def setUseSkillID( self, id ):
		"""
		���û�����ʹ�õļ���ID
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.useSkillID = id

	def autoChangeEquip( self, inf = 0  ):
		"""
		infǿ���ȼ�
		"""
		self.getRoleList()
		for role in self.lstRoleList:
			role.ChangeEquip( inf )

	def setNormalAttr( self ):
		"""
		�������еĻ����˵����Ե�һ��������
		"""
		self.getRoleList()
		for role in self.lstRoleList:
			role.setNormalAttr()

	def setFullAttr( self )	:
		"""
		�������еĻ�����������
		"""
		self.getRoleList()
		for role in self.lstRoleList:
			role.setFullAttr()

	def addSkillForTestParticle( self ):
		"""
		Ϊ�������ӷּ������������Ӽ���
		"""
		self.getRoleList()
		for role in self.lstRoleList:
			role.addSkillForTestParticle()


bots = BotManager.instance()


class TaskManager:
	"""TaskManager to handle task excuting."""

	_INSTANCE = None

	def __init__(self):
		assert self._INSTANCE is None
		self.task_to_bot = weakref.WeakValueDictionary()
		self.task_to_callback = {}
		self.tasks = {}

	@classmethod
	def instance(SELF):
		if SELF._INSTANCE is None:
			SELF._INSTANCE = TaskManager()
		return SELF._INSTANCE

	def do_task(self, key, count = 10):
		"""��ָ�������Ļ�����ִ��ĳ������"""
		if apps.create_taskapp(key) is None:
			print "No task of %s" % key
			return

		if key not in self.tasks:
			self.tasks[key] = Weaker.WeakList()

		bots = self.find_free_bots(count)

		for bot in bots:
			task = apps.create_taskapp(key)
			self.task_to_bot[task] = bot

			callback = Function.Functor(self._on_task_done, task)
			task.doneEvent().bind(callback)

			# ����callback����ΪdoneEvent���õ���������
			# �������ǿ���ã�������������callback�ͻᱻ
			# �ͷţ��޷��õ��ص�
			self.task_to_callback[task] = callback

			try:
				self.tasks[key].append(task)
				task.do(bot)
			except Exception:
				del self.task_to_bot[task]
				del self.task_to_callback[task]

	def _on_task_done(self, task):
		"""����������ͷŻ����ˣ��û����˿�������������"""
		del self.task_to_bot[task]
		del self.task_to_callback[task]

	def find_free_bots(self, count):
		"""�ҵ�ָ�������Ŀ��л�����"""
		result = []
		busy_bots = self.task_to_bot.values()

		# ��ˢ�»������б�
		bots.getRoleList()

		for bot in bots.lstRoleList:
			if count == 0:
				break
			elif bot not in busy_bots:
				result.append(bot)
				count -= 1

		return result

	def release_bot(self, bot):
		"""�ͷŻ�����"""
		task = None
		for t, b in self.task_to_bot.iteritems():
			if b is bot: task = t; break

		if task is None: return

		try:
			task.interrupt()
		except Exception, err:
			pass

		print "bot has been released."

	def release_task(self, key, count = 0):
		"""��ָֹ����������"""
		tasks = self.tasks.get(key)
		if tasks is None: return

		if count <= 0:
			count = len(tasks)

		for task in tasks[:count]:
			try:
				task.interrupt()
			except Exception:
				pass

	def release_all_tasks(self):
		"""�ͷ����л�����"""
		for task in self.task_to_bot.keys():
			try:
				task.interrupt()
			except Exception:
				pass

	def ls_task(self, key = None):
		"""��ʾ�������"""
		desc = []

		if key is not None:
			tasks = self.tasks.get(key)
			if tasks is None:
				desc.append("No task of %s" % key)
			else:
				desc.append("excuting tasks:")
				desc.append("-" * 20)
				desc.append("%-40s: %i" % (key, len(tasks)))
		else:
			for key, tasks in self.tasks.iteritems():
				desc.append("%-40s: %i" % (key, len(tasks)))

			if len(desc) > 0:
				desc.sort()
				desc.insert(0, "-" * 20)
				desc.insert(0, "excuting tasks:")
			else:
				desc.append("No excuting tasks.")

		# ����ͳ�ƿ��л����ˣ���ˢ�»������б�
		bots.getRoleList()

		desc.append("-" * 20)
		desc.append("free bots count: %i" %
			len(self.find_free_bots(len(bots.lstRoleList))))

		desc.insert(0, "=" * 50)
		desc.append("=" * 50)

		print "\n".join(desc)



task_mgr = TaskManager.instance()


# ----------------------------------------------------------
# ������������Խӿ�
# ----------------------------------------------------------
def test_task(key, count = 10):
	"""��ָ�������Ļ�����ִ��ĳ����"""
	task_mgr.do_task(key, count)

def release_task(key, count = 0):
	"""��ָֹ������������count��0��ʾ��ֹ
	����ָ��������"""
	task_mgr.release_task(key, count)

def release_all_tasks():
	"""��ֹ��������"""
	task_mgr.release_all_tasks()

def ls_task(key = None):
	"""��ʾ�������"""
	task_mgr.ls_task(key)



#############################################
#BigWorld.globalData["AntiRobotVerify_rate"] = value
