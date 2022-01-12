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
	����ͳ����
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
		ͳ�Ʋ����˺�
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
		����ַ�������
		"""
		return str( self.totalDamage ) + str( self.spellInfo )


class PlayerStatisticItem( StatisticItem ):
	def __init__( self ):
		StatisticItem.__init__( self )
		self.petStatisticInfo = {}
		self.petID = 0			#��ǰ��ս����id

	def getPetTotalDamage( self, petID ):
		"""
		"""
		try:
			return self.petStatisticInfo[petID].getTotalDamage()
		except KeyError:
			return 0

	def getPetDPS( self, petID ):
		"""
		��ȡָ�������dps
		"""
		try:
			return self.petStatisticInfo[petID].getDPS()
		except KeyError:
			return 0

	def getPetSpellInfo( self, petID ):
		"""
		��ó���ļ����˺���Ϣ
		"""
		try:
			return self.petStatisticInfo[petID].getSpellInfo()
		except KeyError:
			return {}

	def makePetDamage( self, petID, spellName, damageValue ):
		"""
		���������˺�
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
	�˺�ͳ�Ʒ���
	"""
	def __init__( self, parent ):
		"""
		"""
		# ��������parent��Ϊ���ڷ�������ʱ���߷�������ʹ���ߣ�
		# ��������ʹ���߿��ܻ������˷������п�����ɽ�������
		# ����ڷ�������ʵ������������֮ǰҪ���ٰ����õ�ʵ���ͷš�
		self.parent = parent

		self.receiver = ""	# ���ն���
		self.channel = csdefine.CHAT_CHANNEL_NEAR	# Ƶ��
		self.msgList = []		# Ҫ��������Ϣ�б�
		self.timer = 0		# ÿһ����Ϣ��timerID
		self.broadcasting = False	# �Ƿ��ڷ�����

	def __call__( self, channel, msgList, receiver ):
		if self.broadcasting:
			DEBUG_MSG( "------>>>���ڷ�����Ϣ�С���" )
			return
		if len( msgList ) == 0:
			DEBUG_MSG( "------>>>û����Ϣ��������" )
			return
		self.broadcasting = True
		self.receiver = receiver		# ���ն���
		self.msgList = msgList
		self.channel = channel		# Ƶ��
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
			self.receiver = ""	# ���ն���
			self.channel = csdefine.CHAT_CHANNEL_NEAR	# Ƶ��
			tempMsgs = self.msgList		# Ҫ��������Ϣ�б�
			self.timer = 0		# ÿһ����Ϣ��timerID
			self.broadcasting = False	# �Ƿ��ڷ�����

	def dispose( self ):
		"""
		������
		"""
		BigWorld.cancelCallback( self.timer )
		self.timer = 0		# ÿһ����Ϣ��timerID
		self.receiver = ""	# ���ն���
		self.channel = csdefine.CHAT_CHANNEL_NEAR	# Ƶ��
		self.msgList = []		# Ҫ��������Ϣ�б�

class DamageStatisticMgr:
	"""
	�˺�����ͳ�ƹ�����
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert DamageStatisticMgr._instance is None, "Instance had already existed!!!"
		self.switch = False		# �Ƿ���ͳ��
		self.totalDamage = 0	# ���˺�
		self.startTime = 0		# ��ʼʱ��
		self.statistic = {}		# ͳ�Ʊ�
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
		self.switch = False		# �Ƿ���ͳ��
		self.totalDamage = 0	# ���˺�
		self.startTime = 0		# ��ʼʱ��
		self.statistic = {}		# ͳ�Ʊ�

	def restart( self ):
		"""
		����ͳ��ͳ������
		"""
		self.totalDamage = 0			# ���˺�
		self.startTime = time.time()		# ��ʼʱ��
		self.statistic = {}				# ͳ�Ʊ�
		self.damages = {}

	def receiveDamage( self, spell, caster, target, damageType, damageValue ):
		"""
		�ͻ��˵������˺���Ϣ������գ�������Ҫȡ��

		��Ҫ�����ݣ��˼����˺�������˺��������˺������＼���˺�����ʼͳ��ʱ��
		���˺� = ����˺�+�����˺�
		������˺� = ����˺�/ͳ��ʱ��
		�������˺� = �����˺�/ͳ��ʱ��
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
			if playerID != player.id:	# ��������Լ�
				if not player.isInTeam():
					return
				if not player.isTeamMember( caster.id ):	# ���Ƕ���
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
				if not player.isTeamMember( playerID ):	# ���Ƕ���
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
		singleDamage = damageStatis.getTotalDamage()	 	#�������˺���
		singleDps = damageStatis.getDPS()					#����DPS
		if statisticInstance.totalDamage <= 0:return
		damageRatio = float( singleDamage )/self.totalDamage				#�����˺��ٷֱ�
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
