# -*- coding: gb18030 -*-


from bwdebug import *
import time
import BigWorld
import event.EventCenter as ECenter
from ChatFacade import chatFacade
import csdefine
import Const

class StatisticItem:
	"""
	基本统计类
	"""
	def __init__( self ):
		self.totalDamage = 0
		self.spellInfo = {}
		self.startTime = time.time()

	def getTotalDamage( self ):
		return self.totalDamage

	def getSpellInfo( self ):
		"""
		"""
		return self.spellInfo

	def makeDamage( self, spellName, value ):
		"""
		统计产生伤害
		"""
		self.totalDamage += value
		if spellName not in self.spellInfo:
			self.spellInfo[spellName] = { "damage":value, "useDegree":1 }
		else:
			self.spellInfo[spellName]["damage"] += value
			self.spellInfo[spellName]["useDegree"] += 1

	def getDPS( self ):
		lastTime = time.time() - self.startTime
		if lastTime <= 0:return 0
		return self.totalDamage / lastTime

	def getDescript( self ):
		"""
		获得字符串描述
		"""
		return str( self.totalDamage ) + str( self.spellInfo )


class PlayerStatisticItem( StatisticItem ):
	def __init__( self ):
		StatisticItem.__init__( self )
		self.petStatisticInfo = {}
		self.petID = 0			#当前出战宠物id

	def getPetTotalDamage( self, petID ):
		"""
		"""
		try:
			return self.petStatisticInfo[petID].getTotalDamage()
		except KeyError:
			return 0

	def getPetDPS( self, petID ):
		"""
		获取指定宠物的dps
		"""
		try:
			return self.petStatisticInfo[petID].getDPS()
		except KeyError:
			return 0

	def getPetSpellInfo( self, petID ):
		"""
		获得宠物的技能伤害信息
		"""
		try:
			return self.petStatisticInfo[petID].getSpellInfo()
		except KeyError:
			return {}

	def makePetDamage( self, petID, spellName, damageValue ):
		"""
		产生宠物伤害
		"""
		if self.petID != petID:
			self.petID = petID
		if petID not in self.petStatisticInfo:
			self.petStatisticInfo[petID] = StatisticItem()
		self.petStatisticInfo[petID].makeDamage( spellName, damageValue )

	def hasPet( self, petID ):
		return petID in self.petStatisticInfo

	def removePet( self, petID ):
		try:
			del self.petStatisticInfo[petID]
		except KeyError:
			pass
	
	def getTotalDamage( self ):
		if self.petID in self.petStatisticInfo:
			return StatisticItem.getTotalDamage( self ) + self.getPetTotalDamage( self.petID )
		else:
			return StatisticItem.getTotalDamage( self )
	
	def getDPS( self ):
		if self.petID in self.petStatisticInfo:
			return StatisticItem.getDPS( self ) + self.getPetDPS( self.petID )
		else:
			return StatisticItem.getDPS( self )

class Broadcast:
	"""
	伤害统计发布
	"""
	def __init__( self, parent ):
		"""
		"""
		# 这里设置parent是为了在发布结束时告诉发布机的使用者，
		# 发布机的使用者可能会引用了发布机有可能造成交叉引用
		# 因此在发布机的实例引用者销毁之前要销毁把引用的实例释放。
		self.parent = parent

		self.receiver = ""	# 接收对象
		self.channel = csdefine.CHAT_CHANNEL_NEAR	# 频道
		self.msgList = []		# 要发布的消息列表
		self.timer = 0		# 每一条消息的timerID
		self.broadcasting = False	# 是否在发布中

	def __call__( self, channel, msgList, receiver ):
		if self.broadcasting:
			DEBUG_MSG( "------>>>正在发布消息中。。" )
			return
		if len( msgList ) == 0:
			DEBUG_MSG( "------>>>没有消息发布。。" )
			return
		self.broadcasting = True
		self.receiver = receiver		# 接收对象
		self.msgList = msgList
		self.channel = channel		# 频道
		self.__send()

	def __send( self ):
		"""
		"""
		DEBUG_MSG( "--->>>self.msgList[0]", self.msgList[0] )
		tempMsgs = self.msgList
		chatFacade.sendChannelMessage( self.channel, tempMsgs.pop(), self.receiver )
		if len( tempMsgs ) != 0:
			self.timer = BigWorld.callback( Const.STA_BROADCAST_INTERVAL, self.__send )
		else:
			self.receiver = ""	# 接收对象
			self.channel = csdefine.CHAT_CHANNEL_NEAR	# 频道
			tempMsgs = self.msgList		# 要发布的消息列表
			self.timer = 0		# 每一条消息的timerID
			self.broadcasting = False	# 是否在发布中

	def dispose( self ):
		"""
		清理工作
		"""
		BigWorld.cancelCallback( self.timer )
		self.timer = 0		# 每一条消息的timerID
		self.receiver = ""	# 接收对象
		self.channel = csdefine.CHAT_CHANNEL_NEAR	# 频道
		self.msgList = []		# 要发布的消息列表

class DamageStatisticMgr:
	"""
	伤害数据统计管理器
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert DamageStatisticMgr._instance is None, "Instance had already existed!!!"
		self.switch = False		# 是否开启统计
		self.totalDamage = 0	# 总伤害
		self.startTime = 0		# 开始时间
		self.statistic = {}		# 统计表
		self.damages = {}

	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = DamageStatisticMgr()
		return self._instance

	def start( self ):
		"""
		"""
		self.switch = True
		self.startTime = time.time()
		self.damages = {}

	def stop( self ):
		"""
		"""
		self.switch = False		# 是否开启统计
		self.totalDamage = 0	# 总伤害
		self.startTime = 0		# 开始时间
		self.statistic = {}		# 统计表

	def restart( self ):
		"""
		重新统计统计数据
		"""
		self.totalDamage = 0			# 总伤害
		self.startTime = time.time()		# 开始时间
		self.statistic = {}				# 统计表
		self.damages = {}

	def receiveDamage( self, spell, caster, target, damageType, damageValue ):
		"""
		客户端的所有伤害信息都会接收，根据需要取舍

		需要的数据：此技能伤害、玩家伤害、宠物伤害、宠物技能伤害、开始统计时间
		总伤害 = 玩家伤害+宠物伤害
		玩家秒伤害 = 玩家伤害/统计时间
		宠物秒伤害 = 宠物伤害/统计时间
		"""
		if not self.switch:
			return
		playerID = 0
		petID = 0
		casterName = ""
		player = BigWorld.player()
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			playerID = caster.id
			casterName = caster.getName()
			if playerID != player.id:	# 如果不是自己
				if not player.isInTeam():
					return
				if not player.isTeamMember( caster.id ):	# 不是队友
					return
			self.totalDamage += damageValue
			if not playerID in self.statistic:
				self.statistic[playerID] = PlayerStatisticItem()
			self.statistic[playerID].makeDamage( spell.getName(), damageValue )
			DEBUG_MSG( "--->>>spell(%s), caster(%s), target(%s), damageType(%i), damageValue(%i)." % ( spell.getName(), caster.getName(), target.getName(), damageType, damageValue ) )
		elif caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			petOwner = caster.getOwner()
			if petOwner is None:
				return
			petID = caster.id
			playerID = petOwner.id
			casterName = petOwner.getName()
			if player.id != playerID:
				if not player.isInTeam():
					return
				if not player.isTeamMember( playerID ):	# 不是队友
					return
			self.totalDamage += damageValue
			if playerID not in self.statistic:
				self.statistic[playerID] = PlayerStatisticItem()
			self.statistic[playerID].makePetDamage( caster.id, spell.getName(), damageValue )
			DEBUG_MSG( "--->>>spell(%s), caster(%s), target(%s), damageType(%i), damageValue(%i)." % ( spell.getName(), petOwner.getName(), target.getName(), damageType, damageValue ) )
		self.setDamageMsg( playerID )
		ECenter.fireEvent( "EVT_ON_RECEIVE_DAMAGE_STATIST", playerID )

	def setDamageMsg( self, playerID ):
		damageStatis = self.statistic.get( playerID, None )
		if damageStatis is None:return
		player = BigWorld.entities.get( playerID, None )
		if player is None:return
		playerName = player.getName()
		singleDamage = damageStatis.getTotalDamage()	 	#个体总伤害量
		singleDps = damageStatis.getDPS()					#个体DPS
		if statisticInstance.totalDamage <= 0:return
		damageRatio = float( singleDamage )/self.totalDamage				#个体伤害百分比
		self.damages[playerName] = [playerName, singleDamage, singleDps, damageRatio]

	def getBroadcastMsgList( self ):
		"""
		"""
		msgList = []
		for item in self.statistic.itervalues():
			msgList.append( item.getDescript() )
		DEBUG_MSG( "---->>>msgList", msgList )
		return msgList

statisticInstance = DamageStatisticMgr.instance()
