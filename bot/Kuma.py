# -*- coding: utf-8 -*-
import BigWorld
import random, time, threading, weakref
import SkillTargetObjImpl, csdefine

from task.taskapps import apps
from task.utils import Function, Weaker


class BotManager():

	BOT_CHAT = 0x01					# 聊天开关
	BOT_FIGHT = 0x02				# 战斗开关
	BOT_BUFF = 0x04					# BUFF开关
	BOT_HSZ = 0x08					# 火蛇阵
	BOT_FLY_TO_YEWAI = 0x10					# 传送到野外一个随机位置进行打怪

	MSG_LIST = ["大家好啊， 我是机器人，时间：%d   人物： %d",
				"下雨啦，赶紧回家收衣服啦，时间：%d   人物： %d",
				"暗黑3出来了，还不赶紧搞一搞，时间：%d   人物： %d",
				"创世必火！！，时间：%d   人物： %d",
				"凡人修仙传， 介绍大家看一看，时间：%d   人物： %d",
				"Just do it！时间：%d   人物： %d",
				"看什么看，滚！时间：%d   人物： %d",
				"看，灰机！！！，时间：%d   人物： %d",
				"人山人海啊，好玩啊！！，时间：%d   人物： %d",
				]

	_INSTANCE = None

	@staticmethod
	def instance():
		if BotManager._INSTANCE is None:
			BotManager._INSTANCE = BotManager()
		return BotManager._INSTANCE

	def __init__(self):
		self.state = 0						# 机器人循环状态
		self.timerID = 0					# timerID
		self.times = -1						# 循环次数
		self.lstClient = []					# 客户端列表
		self.lstRoleList = []				# 玩家列表

	def setState(self, state):
		"""
		设定循环状态
		"""
		self.state = state

	def getState(self, state):
		"""
		获得循环状态
		"""
		return self.state

	def getRoleList(self):
		"""
		获取人物列表
		"""
		self.lstClient = [id for id in BigWorld.bots.keys()]
		self.lstRoleList = [BigWorld.bots[id].entities[id] for id in self.lstClient if BigWorld.bots[id].entities[id].__class__.__name__ == 'Role']

	def getRoleCount(self):
		"""
		获得机器人数量
		"""
		self.getRoleList()
		return len(self.lstClient), len(self.lstRoleList)

	def moveTo(self, x, y, z, p):
		"""
		机器人移动
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.moveTo(x, y, z, p)

	def autoMove(self, nTime=1):
		"""
		移除Buff
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.autoMove(False)
		def m():
			for role in self.lstRoleList:role.autoMove(True)
		BigWorld.bots.values()[0].addTimer(nTime, m, False)


	def goFengMing(self):
		"""
		移动到凤鸣
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.goFengMing()

	def goFengMingCheng(self):
		"""
		移动到凤鸣城
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.goFengMingCheng()

	def gmCmd(self, strCmd):
		"""
		输入GM指令
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.wizCommand(strCmd)

	def beginBotLoop(self, state):
		"""
		打开机器人循环
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
		关闭循环
		"""
		BigWorld.bots.values()[0].delTimer(self.timerID)
		self.timerID = 0
		self.times = -1

	def botLoop(self):
		"""
		机器人Loop
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
		攻击特定的ID
		"""
		self.getRoleList()
		monster = BigWorld.bots.values()[0].entities[nID]
		target = SkillTargetObjImpl.createTargetObjEntity(monster)
		for role in self.lstRoleList:role.fightTo(monster, target, 1)

	def setPKMode(self, pkMode):
		"""
		打开PK开关
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.cell.setPkMode(pkMode)

	def cloneReviveItem(self):
		"""
		制作复活药品
		"""
		self.gmCmd("/add_item 110103001 20")

	def useItemRevive(self):
		"""
		使用复活药品
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.useItemRevive()

	def revive(self):
		"""
		复活
		"""
		self.cloneReviveItem()
		def m():
			self.useItemRevive()
			self.autoMove()
		BigWorld.bots.values()[0].addTimer(1, m, False)

	def withdrawEidolon(self):
		"""
		收回小精灵
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.withdrawEidolon()

	def protect(self):
		"""
		战斗保护
		"""
		self.gmCmd("/set_level 110")
		self.gmCmd("/set_attr HP_Max 1000000")
		self.gmCmd("/set_attr HP 1000000")

	def setUseSkillID( self, id ):
		"""
		设置机器人使用的技能ID
		"""
		self.getRoleList()
		for role in self.lstRoleList:role.useSkillID = id

	def autoChangeEquip( self, inf = 0  ):
		"""
		inf强化等级
		"""
		self.getRoleList()
		for role in self.lstRoleList:
			role.ChangeEquip( inf )

	def setNormalAttr( self ):
		"""
		设置所有的机器人得属性到一个基本量
		"""
		self.getRoleList()
		for role in self.lstRoleList:
			role.setNormalAttr()

	def setFullAttr( self )	:
		"""
		设置所有的机器人满属性
		"""
		self.getRoleList()
		for role in self.lstRoleList:
			role.setFullAttr()

	def addSkillForTestParticle( self ):
		"""
		为测试粒子分级给机器人增加技能
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
		"""让指定数量的机器人执行某件任务"""
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

			# 保存callback，因为doneEvent中用的是弱引用
			# 如果不作强引用，则出了这个函数callback就会被
			# 释放，无法得到回调
			self.task_to_callback[task] = callback

			try:
				self.tasks[key].append(task)
				task.do(bot)
			except Exception:
				del self.task_to_bot[task]
				del self.task_to_callback[task]

	def _on_task_done(self, task):
		"""任务结束后，释放机器人，让机器人可以做其他任务"""
		del self.task_to_bot[task]
		del self.task_to_callback[task]

	def find_free_bots(self, count):
		"""找到指定数量的空闲机器人"""
		result = []
		busy_bots = self.task_to_bot.values()

		# 先刷新机器人列表
		bots.getRoleList()

		for bot in bots.lstRoleList:
			if count == 0:
				break
			elif bot not in busy_bots:
				result.append(bot)
				count -= 1

		return result

	def release_bot(self, bot):
		"""释放机器人"""
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
		"""终止指定类型任务"""
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
		"""释放所有机器人"""
		for task in self.task_to_bot.keys():
			try:
				task.interrupt()
			except Exception:
				pass

	def ls_task(self, key = None):
		"""显示任务情况"""
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

		# 下面统计空闲机器人，先刷新机器人列表
		bots.getRoleList()

		desc.append("-" * 20)
		desc.append("free bots count: %i" %
			len(self.find_free_bots(len(bots.lstRoleList))))

		desc.insert(0, "=" * 50)
		desc.append("=" * 50)

		print "\n".join(desc)



task_mgr = TaskManager.instance()


# ----------------------------------------------------------
# 机器人任务测试接口
# ----------------------------------------------------------
def test_task(key, count = 10):
	"""让指定数量的机器人执行某任务"""
	task_mgr.do_task(key, count)

def release_task(key, count = 0):
	"""终止指定数量的任务，count是0表示终止
	所有指定的任务"""
	task_mgr.release_task(key, count)

def release_all_tasks():
	"""终止所有任务"""
	task_mgr.release_all_tasks()

def ls_task(key = None):
	"""显示任务情况"""
	task_mgr.ls_task(key)



#############################################
#BigWorld.globalData["AntiRobotVerify_rate"] = value
