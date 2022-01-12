# -*- coding: gb18030 -*-
#
# $Id: QTReward.py,v 1.54 2008-09-03 10:47:27 qilan Exp $

"""
"""

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from Resource.QuestLoader import QuestsFlyweight
from Resource.QuestRewardFromTableLoader import QuestRewardFromTableLoader		# ����������������Ϊ�������
import csdefine
import csconst
import items
import struct
import random
import cPickle
import BigWorld
import csstatus
import Const
import time
import ItemTypeEnum
import sys
import math
from items.ItemDropLoader import ItemDropInWorldLoader
g_itemDropInWorld = ItemDropInWorldLoader.instance()
g_questRewardFromTable = QuestRewardFromTableLoader.instance()
import Love3
from CrondScheme import *
from DaohengLoader import DaohengLoader
g_daoheng = DaohengLoader.instance()

TITLE_XIUCAI = 30				#��ųƺ�
TITLE_JUREN = 31				#���˳ƺ�
TITLE_JINSHI = 32				#��ʿ�ƺ�
TITLE_TANHUA = 33				#̽���ƺ�
TITLE_BANGYAN = 34				#���۳ƺ�
TITLE_ZHUANGYUAN = 35			#״Ԫ�ƺ�

ITEM_FUBI_ID = 	50201914		#����ID

# ӳ������ű���ʵ��������
# ��ӳ����Ҫ���ڴ������г�ʼ��ʵ��ʱʹ��
# key = Ŀ�������ַ�����ȡ�Ը����͵�������;
# value = �̳���QTReward���࣬���ڸ�������ʵ��������Ķ���
quest_reward_type_maps = {}

def MAP_QUEST_REWARD_TYPE( classObj ):
	"""
	ӳ������Ŀ��������ʵ��������
	"""
	quest_reward_type_maps[classObj.__name__] = classObj

def createReward( strType ):
	"""
	��������ʵ��

	@return: instance of QTReward or derive from it
	@type:   QTReward
	"""
	try:
		return quest_reward_type_maps[strType]()
	except KeyError:
		ERROR_MSG( "can't create instance by %s type." % strType )
		return None



# ------------------------------------------------------------>
# Abstract class
# ------------------------------------------------------------>
class QTReward:
	m_type = csdefine.QUEST_REWARD_NONE
	def __init__( self , *args ):
		pass

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: ��ʼ������,������ʽ��ÿ��ʵ���Լ��涨
		@type  section: string
		"""
		pass

	def type( self ):
		"""
		ȡ�ý�������
		"""
		return self.m_type

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		return []

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������
		"""
		return ""

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not playerEntity.wallow_getLucreRate(): # �������Ϊ0���򲻽���
			playerEntity.client.onStatusMessage( csstatus.ANTI_INDULGENCE_STATE_SICK, "" )
			return False
		return True


# ------------------------------------------------------------>
# QTRewardMoney
# ------------------------------------------------------------>
class QTRewardMoney( QTReward ):

	m_type = csdefine.QUEST_REWARD_MONEY

	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		gameYield = playerEntity.wallow_getLucreRate()
		money = self._amount * gameYield
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_QTREWARDMONEY )
		return [cschannel_msgs.GMMGR_JIN_QIAN  + str(self._amount * gameYield) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )


# ------------------------------------------------------------>
# QTRewardMoneyByTemp
# ------------------------------------------------------------>
class QTRewardMoneyByTemp( QTReward ):

	m_type = csdefine.QUEST_REWARD_MONEY
	"""
	�����������60%������
	1-2����Ա������ɣ�80%������
	3-5����Ա������ɣ�100%������
	6-9����Ա������ɣ�120%������
	10�����ϳ�Ա������ɣ�150%������
	"""
	# rewardRate = { 1:0.6, 2:0.6, 3:1.0, 4:1.0, 5:1.0, 6:1.2, 7:1.2, 8:1.2, 9:1.2 }

	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )
		self._rewardRata = eval( section.readString( "param2" ) )
		self._overRate = section.readFloat( "param3" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		gameYield = playerEntity.wallow_getLucreRate()
		rate = 0.0
		num = playerEntity.queryTemp( "tongDartMembers", 0 )
		#if num is None:
		#	return [cschannel_msgs.GMMGR_JIN_QIAN  + "0" ]
		if not num in self._rewardRata and num > 0:
			rate = self._overRate
		else:
			rate = self._rewardRata[num]
		money = int( self._amount * gameYield * rate )
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_QTREWARDMONEY )
		# ����ɰ������ʱ�����ڰ����Ի�ð���ʽ������ʽ�����ֵ���ڴ�ͷ����һ�ý�Ǯ������50%�� 
		playerEntity.tong_addMoney( money/2, csdefine.TONG_CHANGE_MONEY_QTREWARDTONGMONEY  )
		return [cschannel_msgs.GMMGR_JIN_QIAN  + str(money) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		gameYield = playerEntity.wallow_getLucreRate()
		num = playerEntity.queryTemp( "tongDartMembers")
		rate = 1
		if num is not None:
			if not num in self._rewardRata and num > 0:
				rate = self._overRate
			else:
				rate = self._rewardRata[num]
				
		money = int( self._amount * gameYield * rate )
		return struct.pack( "=bi", self.type(), money )

# ------------------------------------------------------------>
# QTRewardMultiMoney
# ------------------------------------------------------------>
class QTRewardMultiMoney( QTRewardMoney ):
	"""
	�౶��Ǯ���������� 5��10�� x 2
	"""

	m_type = csdefine.QUEST_REWARD_MULTI_MONEY

	def __init__( self ,*args ):
		self._multiFlag = 1
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		gameYield = playerEntity.wallow_getLucreRate()
		money = self._amount * gameYield * self._multiFlag
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_QTREWARDMONEY )
		msg = [cschannel_msgs.GMMGR_JIN_QIAN  + str(self._amount * gameYield) ]
		if self._multiFlag > 1:
			msg = [cschannel_msgs.GMMGR_JIN_QIAN  + str(self._amount * gameYield) + " x " + str( int( self._multiFlag ) ) ]
		return msg

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		multi_rewards = 1
		if playerEntity.queryTemp( 'multi_rewards', 1 ) != 1:
			multi_rewards = playerEntity.queryTemp( 'multi_rewards', 1 )
		elif playerEntity.has_quest( questID ):
			multi_rewards = playerEntity.questsTable[questID].query( 'multi_rewards', 1 )
		self._multiFlag = multi_rewards
		return struct.pack( "=bib", self.type(), self._amount, self._multiFlag )


# ------------------------------------------------------------>
# QTRewardDeposit
# ------------------------------------------------------------>
class QTRewardDeposit( QTReward ):
	m_type = csdefine.QUEST_REWARD_DEPOSIT
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		gameYield = playerEntity.wallow_getLucreRate()
		money = self._amount * gameYield
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_DEPOSIT_RETURN )
		return [cschannel_msgs.QUEST_INFO_3  + str(self._amount * gameYield) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )


# ------------------------------------------------------------>
# QTTongContributeNormal
# ------------------------------------------------------------>
class QTTongContributeNormal( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_CONTRIBUTE_NORMAL
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.tong_addContribute( self._amount )
		return [cschannel_msgs.QUEST_INFO_4  + str(self._amount) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )

class QTRewardRobDartMoney( QTRewardMoney ):

	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		money = playerEntity.questsTable[questID].query( 'Rob_Money', 0 )
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_QTREWARDROBDARTMONEY )
		return [cschannel_msgs.GMMGR_JIN_QIAN  + str(money) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

class QTRewardMerchantMoney( QTRewardMoney ):
	m_type = csdefine.QUEST_REWARD_MERCHANT_MONEY
	def __init__( self ,*args ):
		pass

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )			#����Ѻ��
		self.str = section.readString( "param2" )			#��������
		self.yinpiaoValue = section.readInt( "param3" )		#������Ʊ���
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		gameYield = playerEntity.wallow_getLucreRate()
		yinpiaoValue = self.yinpiaoValue
		money = ( yinpiaoValue - self._amount ) * gameYield 
		rMoney = ( self._amount +  ( yinpiaoValue - self._amount ) ) * gameYield
		
		if money < 0:
			ERROR_MSG( "QTRewardMerchantMoney do failed questID(%s), value(%i, %i)" % (str(questID), money, rMoney) )
			money = 0
			rMoney = 0
		
		playerEntity.addMoney( rMoney, csdefine.CHANGE_MONEY_QTREWARDMERCHANTMONEY )
		playerEntity.tong_addMoney( money, csdefine.TONG_CHANGE_MONEY_QTREWARDMERCHANTMONEY )
		return [cschannel_msgs.GMMGR_JIN_QIAN  + str( rMoney )]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=b", self.type()) + self.str

# ------------------------------------------------------------>
# QTRewardItemItems
# ------------------------------------------------------------>
class QTRewardItems( QTReward ):
	m_type = csdefine.QUEST_REWARD_ITEMS
	def __init__( self, *args ):
		"""
		��ʼ��������Ϣ
		"""
		self._rewardItemsInfo = []		#
		if len( args ) > 0:
			for e in xrange(0, len(args), 2):
				self._rewardItemsInfo.append( ( args[e], args[e+1], args[e+2], args[e+3], args[e+4] ) )

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: itemID, amount
		@type  section: pyDataSection
		"""
		try:
			for	node in section.values():
				if not node.has_key( "itemID" ):
					raise KeyError
				self.add(node.readInt( "itemID" ), node.readInt( "amount" ), node.readInt("param1"), node.readInt("param2"), node.readString("param3") )
		except KeyError:
			# QTRewardQuestPartCompleted���ָ��Ͻ����п����õ���Ʒ������������Ҫ��������Ĳ�����ʽ add by cwl
			self.add(section.readInt( "param1" ), section.readInt( "param2" ), section.readInt("param3"), section.readInt("param4"), section.readString("param5") )
			

	def add( self , itemID, itemAmount, isBind, ownerLevel, schemeInfo ):
		"""
		���һ���µĽ���
		@param   rewardInstance: һ����ģ�����κ�һ�ֽ�����ʵ��
		@type    rewardInstance: reward instance
		"""
		if itemAmount <= 0:
			itemAmount = 1
		self._rewardItemsInfo.append( ( itemID, itemAmount, isBind, ownerLevel, schemeInfo  ) )

	def getCount( self ):
		"""
		��ȡ�˰� �����Ľ�����Ŀ
		"""
		return len(self._rewardItemsInfo)

	def getItems( self , playerEntity, questID ):
		"""
		virtual method
		ȡ�ý�����Ʒ
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: Items
		@rtype:  CItemBase Instances
		"""
		_rewardItems = []
		for itemID, amount, isBind, ownerLevel, schemeInfo in self._rewardItemsInfo:
			item = items.instance().createDynamicItem( itemID, amount )
			if isBind:
				item.setBindType( ItemTypeEnum.CBT_PICKUP )
			if ownerLevel:
				item.set( "level", playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level ) )
			if schemeInfo != "":
				try:
					cmd,presistMinute = schemeInfo.split("|")
					presistMinute = int( presistMinute )
					scheme = Scheme()
					scheme.init( cmd )
					year, month, day, hour, minute = time.localtime( time.time() - presistMinute * 60 )[:5]
					nextTime = scheme.calculateNext( year, month, day, hour, minute )
					if nextTime > time.time():
						continue
				except:
					ERROR_MSG("QTRewardItems: scheme config(%s) was wrong!"%schemeInfo )
					continue
			_rewardItems.append( item )
		return _rewardItems

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not QTReward.check( self, playerEntity, questID = 0 ):
			return False

		return playerEntity.checkItemsPlaceIntoNK_( self.getItems( playerEntity, questID ) ) == csdefine.KITBAG_CAN_HOLD

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		infoList = []
		for item in  self.getItems( playerEntity, questID ):
			playerEntity.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTREWARDITEMS )
			infoList.append(item.name())
		return infoList

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		info = []
		for i in self._rewardItemsInfo:
			if i[3] != 0:		#Ҫ����Ʒ�ȼ�������ҽ�����ʱ�ĵȼ�
				info.append( ( i[0], i[1], i[2], playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level ), i[4] ) )
				continue
			info.append( i )
		s = cPickle.dumps( info, 2 )
		return struct.pack( "=b", self.type()) + s




class QTRewardItemsFromRoleLevel( QTRewardItems ):
	"""
	������ҽ�����ȼ������ý�����Ʒ�ȼ��������ҽ�����ȼ�û�м�¼����ʹ����ҵȼ�
	"""
	m_type = csdefine.QUEST_REWARD_ITEMS_FROM_ROLE_LEVEL
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		infoList = []
		for itemID, amount, isBind, ownerLevel,schemeInfo  in self._rewardItemsInfo:
			item = items.instance().createDynamicItem( itemID, amount )
			if isBind:
				item.setBindType( ItemTypeEnum.CBT_PICKUP )
			if ownerLevel:
				item.set( "level", playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level ) )
			playerEntity.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTREWARDITEMS )
			infoList.append(item.name())
		return infoList

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		rewardItemsInfo = []
		for itemID, amount, isBind, ownerLevel,schemeInfo in self._rewardItemsInfo:
			rewardItemsInfo.append( [itemID, amount, isBind, playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level ),  schemeInfo ] )
		s = cPickle.dumps( rewardItemsInfo, 2 )
		return struct.pack( "=b", self.type()) + s



# ------------------------------------------------------------>
# QTRewardItemItemsQuality
# ------------------------------------------------------------>
class QTRewardItemsQuality( QTReward ):
	m_type = csdefine.QUEST_REWARD_ITEMS_QUALITY
	def __init__( self, *args ):
		"""
		��ʼ��������Ϣ
		"""
		if len( args ) > 0:
			self._amount = args[0]
			self._level = args[1]
			self._quality = args[2]
			self._descript = args[3]

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: itemID, amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )
		self._level = section.readInt( "param2" )
		self._quality = section.readInt( "param3" )
		self._descript = section.readString( "param4" )

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not QTReward.check( self, playerEntity, questID = 0 ):
			return False
		return playerEntity.getNormalKitbagFreeOrderCount() >= self._amount

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		infoList = []
		level = random.randint( self._level - 9, self._level )
		itemList = g_itemDropInWorld.getItemByClass( self._quality, level, playerEntity.getClass() )

		for e in xrange( self._amount ):
			itemID = random.choice( itemList )
			item = items.instance().createDynamicItem( itemID , 1 )
			item.setQuality( self._quality )

			prefix = ItemTypeEnum.CPT_FABULOUS
			if self._quality != ItemTypeEnum.CQT_GREEN:
				preList = ItemTypeEnum.CPT_NO_GREEN
				prefix = random.choice( ItemTypeEnum.CPT_GREEN )
			item.setPrefix( prefix )
			item.createRandomEffect()
			item.setBindType( ItemTypeEnum.CBT_PICKUP, playerEntity )	# ��
			playerEntity.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTREWARDITEMS )
			infoList.append( item.name() )
		return infoList

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=b", self.type()) + self._descript


# ------------------------------------------------------------>
# QTRewardChooseItems
# ------------------------------------------------------------>
class QTRewardChooseItems( QTRewardItems ):
	"""
	��Ʒ��ѡһ
	"""
	m_type = csdefine.QUEST_REWARD_CHOOSE_ITEMS
	def __init__( self, *args ):
		"""
		"""
		QTRewardItems.__init__( self, *args )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		items = self.getItems( playerEntity, questID )
		playerEntity.addItemAndRadio( items, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTREWARDCHOOSEITEMS )
		return [ item.name() for item in items ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not QTReward.check( self, playerEntity, questID = 0 ):
			return False
		return playerEntity.checkItemsPlaceIntoNK_( self.getItems( playerEntity, questID ) ) == csdefine.KITBAG_CAN_HOLD

	def getItems( self , playerEntity, questID ):
		"""
		virtual method
		ȡ�ý�����Ʒ
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: Items
		@rtype:  CItemBase Instances
		"""
		selectindex = playerEntity.queryTemp( "RewardItemChoose" , 0 )
		itemInfo = self._rewardItemsInfo[ selectindex ]
		try:
			item = items.instance().createDynamicItem( itemInfo[0], itemInfo[1] )
			if itemInfo[2]:
				item.setBindType( ItemTypeEnum.CBT_PICKUP )
		except:
			ERROR_MSG( "Error Index(%i)!" %  selectindex)
			return []
		return  [item]


# ------------------------------------------------------------>
# QTRewardRndItems
# ------------------------------------------------------------>
class QTRewardRndItems( QTRewardItems ):
	m_type = csdefine.QUEST_REWARD_RANDOM_ITEMS
	def __init__( self, *args ):
		"""
		"""
		self._rewardItemsRate = []
		if len( args ) > 0:
			for e in xrange(0, len(args), 3):
				item = items.instance().createDynamicItem( args[e], args[e+1] )
				self._rewardItemsRate.append( (item, args[e+2]) )

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: ���±�
		@type  section: pyDataSection
		"""
		for	node in section.values():
			self.addRndItem( node.readInt( "itemID" ), node.readInt( "amount" ), node.readFloat( "rate" ), node.readInt( "group" ) )

	def addRndItem( self, itemID, itemAmount, rate, group ):
		"""
		"""
		if itemAmount > 0:
			self._rewardItemsRate.append( ( itemID, itemAmount, rate, group ) )

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def getItems( self, playerEntity, questID  ):
		"""
		virtual method
		ȡ�ý�����Ʒ
		@return: Items
		@rtype:  CItemBase Instances
		"""
		tempItems = []
		index = self.generateIndex()
		for i in index:
			try:
				item = items.instance().createDynamicItem( i[0], i[1] )
				tempItems.append( item )
			except:
				ERROR_MSG( "Error Index(%i)!" %  i)
				continue
		return tempItems

	def generateIndex( self ):
		"""
		"""
		index = []
		groups = []
		for itemID, itemAmount, rate, group in self._rewardItemsRate:
			porb = random.random()
			if porb <= rate and not group in groups:
				index.append( (itemID, itemAmount) )
				groups.append( group )
		return index

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		infoList = []
		tempItems = self.getItems( playerEntity, questID )
		for i in tempItems:
			playerEntity.addItemAndRadio( i.new(), ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTREWARDRNDITEMS )
			infoList.append( i.name() )
		return infoList

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		dataList = [ (e[0], e[1]) for e in self._rewardItemsRate ]
		s = cPickle.dumps( dataList, 2 )
		return struct.pack( "=b", self.type()) + s


# ------------------------------------------------------------>
# QTRewardExp
# ------------------------------------------------------------>
class QTRewardExp( QTReward ):
	m_type = csdefine.QUEST_REWARD_EXP
	def __init__( self ,*args ):
		self._amount = 0
		self._owner = 0
		if len( args ) > 0:
			self._amount = args[0]

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._owner = owner
		self._amount = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.addExp( self.calculate( playerEntity ), csdefine.CHANGE_EXP_QTREWARD )
		return [cschannel_msgs.QUEST_INFO_5  + str(self._amount)]

	def calculate( self, playerEntity ):
		"""
		���㾭��

		@rtype: int
		"""
		# ���ڲ߻���ǰû�д���������˸�Ϊֱ�ӷ���
		return int(self._amount)

		if self._owner == 0:return self._amount
		lvl = playerEntity.level - self._owner.getLevel()
		if lvl <= 3:
			exp = self._amount
		elif lvl <= 6:
			exp = self._amount / 2
		else:
			exp = self._amount / 10
		return int(exp)

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self.calculate( playerEntity ) )

class QTRewardExpDart( QTRewardExp ):
	"""
	���ھ��齱��
	"""
	m_type = csdefine.QUEST_REWARD_EXP_TONG_DART
	def calculate( self, playerEntity ):
		"""
		���㾭��

		@rtype: int
		"""
		point = playerEntity.query( "dartStartMapPoint", -1 )
		if point == -1:
			dartPointDict = eval( BigWorld.getSpaceDataFirstForKey( playerEntity.spaceID, csconst.SPACE_SPACEDATA_DART_POINT ) )
			if playerEntity.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ):
				point = dartPointDict[csdefine.ROLE_FLAG_XL_DARTING]
			else:
				point = dartPointDict[csdefine.ROLE_FLAG_CP_DARTING]
		else:
			point = playerEntity.query( "dartStartMapPoint" )
		return self._amount * ( 1 + ( point - csconst.DART_INITIAL_POINT ) / 100.0 )

# ------------------------------------------------------------>
# QTRewardMultiExp
# ------------------------------------------------------------>
class QTRewardMultiExp( QTRewardExp ):
	"""
	�౶���ﾭ�齱�������� 8000 x 3
	"""
	m_type = csdefine.QUEST_REWARD_MULTI_EXP

	def __init__( self ,*args ):
		self._amount = 0
		self._owner = 0
		self._multiFlag = 1
		if len( args ) > 0:
			self._amount = args[0]

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.addExp( self.calculate( playerEntity ) * self._multiFlag, csdefine.CHANGE_EXP_QTREWARD )
		msg = [ cschannel_msgs.QUEST_INFO_5  + str(self._amount) ]
		if self._multiFlag > 1:
			msg = [ cschannel_msgs.QUEST_INFO_5  + str(self._amount) + " x " + str( int( self._multiFlag ) ) ]
		return msg

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		multi_rewards = 1
		if playerEntity.queryTemp( 'multi_rewards', 1 ) != 1:
			multi_rewards = playerEntity.queryTemp( 'multi_rewards', 1 )
		elif playerEntity.has_quest( questID ):
			multi_rewards = playerEntity.questsTable[questID].query( 'multi_rewards', 1 )
		self._multiFlag = multi_rewards
		return struct.pack( "=bib", self.type(), self.calculate( playerEntity ), multi_rewards )


# ------------------------------------------------------------>
# QTRewardPetExp
# ------------------------------------------------------------>
class QTRewardPetExp( QTRewardExp ):
	m_type = csdefine.QUEST_REWARD_PET_EXP

	def do( self, playerEntity, questID ):
		"""
		"""
		quest = playerEntity.getQuest( questID )
		if quest.getType() != csdefine.QUEST_TYPE_NONE or quest.getStyle() == csdefine.QUEST_STYLE_LOOP_GROUP:
			level = playerEntity.getLevel()
		else:
			level  = quest.getLevel()

		actPet = playerEntity.pcg_getActPet()
		if actPet :
			actPet.entity.addQuestEXP( self._amount, level )
		return [cschannel_msgs.QUEST_INFO_5  + str(self._amount)]


# ------------------------------------------------------------>
# QTRewardMultiPetExp
# ------------------------------------------------------------>
class QTRewardMultiPetExp( QTRewardMultiExp ):
	"""
	�౶���ﾭ�齱�������� 3000 x 2
	"""
	m_type = csdefine.QUEST_REWARD_MULTI_PET_EXP

	def do( self, playerEntity, questID ):
		"""
		"""
		quest = playerEntity.getQuest( questID )
		if quest.getType() != csdefine.QUEST_TYPE_NONE or quest.getStyle() == csdefine.QUEST_STYLE_LOOP_GROUP:
			level = playerEntity.getLevel()
		else:
			level  = quest.getLevel()

		actPet = playerEntity.pcg_getActPet()
		if actPet :
			actPet.entity.addQuestEXP( self._amount * self._multiFlag, level )
		msg = cschannel_msgs.QUEST_INFO_5  + str( self._amount )
		if self._multiFlag > 1:
			msg = cschannel_msgs.QUEST_INFO_5  + str( self._amount ) + " x " + str( int( self._multiFlag ) )
		return msg


# ------------------------------------------------------------>
# QTRewardPercentageExp
# ------------------------------------------------------------>
class QTRewardPercentageExp( QTRewardExp ):
	"""
	"""
	def __init__( self ,*args ):
		self._baseExp = 0
		self._increasePercentage = 0
		self._specialFlag = ""
		assert False, "��ʱδʹ�ò�ʵ��"

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		format: baseExp, increasePercentage, specialFlag, maxTimes
		format: int, float, string, int

		example: 100, 0.1, rq1, 10
		��ʾ����rq1��ֵ��ÿ������10%����rq1 == 0��exp == 100�� rq1 == 1ʱ��exp == 100 * 1.1���������ƣ��������10������ͷ����
		rq1�Ǽ�¼��������ϵ���ʱ��־��

		@param section: format: baseExp, increasePercentage, specialFlag, maxTimes
		@type  section: pyDataSection
		"""
		# phw: ��ʱδʹ�ò�ʵ��
		assert False, "��ʱδʹ�ò�ʵ��"
		v = section.asString.split( "," )
		self._baseExp = int( v[0] )
		self._increasePercentage = float( v[1] )
		self._specialFlag = v[2].strip( "\t \n\r" )
		self._maxTimes = v[3]

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		exp = self.calculate( playerEntity )
		playerEntity.addExp( exp, csdefine.CHANGE_EXP_QTREWARDPERCENTAGEEXP )
		return [cschannel_msgs.QUEST_INFO_6  + str(exp)]

	def calculate( self, playerEntity ):
		"""
		���㾭��

		@rtype: int
		"""
		try:
			d = playerEntity.getMapping()["questSpecialFlag"]
		except KeyError:
			d = {}
			playerEntity.getMapping()["questSpecialFlag"] = d
		if d.has_key( self._specialFlag ):
			d[self._specialFlag] += 1
		else:
			d[self._specialFlag] = 1
		f = d[self._specialFlag] - 1
		if f >= self._maxTimes:
			d[self._specialFlag] = 0
		f = 1 + f * self._increasePercentage

		return int( self._baseExp * f )

# ------------------------------------------------------------>
# QTRewardTitle
# ------------------------------------------------------------>
from TitleMgr import TitleMgr
g_titleLoader = TitleMgr.instance()
class QTRewardTitle( QTReward ):
	m_type = csdefine.QUEST_REWARD_TITLE
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._title = args[0]
		else:
			self._title = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: ��ʼ������,������ʽ��ÿ��ʵ���Լ��涨
		@type  section: pyDataSection
		"""
		self._title = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.addTitle( self._title )
		return []

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._title )

# ------------------------------------------------------------>
# QTRewardPotential
# ------------------------------------------------------------>
class QTRewardPotential( QTReward ):
	m_type = csdefine.QUEST_REWARD_POTENTIAL
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._potential = args[0]
		else:
			self._potential = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: ��ʼ������,������ʽ��ÿ��ʵ���Լ��涨
		@type  section: pyDataSection
		"""
		self._potential = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.addPotential( self._potential )
		return []

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.potential >= csconst.ROLE_POTENTIAL_UPPER: #���Ǳ���Ѿ��������ޣ������������
			playerEntity.statusMessage( csstatus.ACCOUNT_CANT_GAIN_POTENTIAL )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._potential )

# ------------------------------------------------------------>
# QTRewardSkill
# ------------------------------------------------------------>
class QTRewardSkill( QTReward ):
	m_type = csdefine.QUEST_REWARD_SKILL
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._skillID = args[0]
		else:
			self._skillID = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: ��ʼ������,������ʽ��ÿ��ʵ���Լ��涨
		@type  section: pyDataSection
		"""
		self._skillID = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.addSkill( self._skillID )
		return []

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=b", self.type() ) + str( self._skillID )

# ------------------------------------------------------------>
# QTRewardRelationMoney
# ------------------------------------------------------------>
class QTRewardRelationMoney( QTRewardMoney ):
	m_type = csdefine.QUEST_REWARD_MONEY
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		return []

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )

# ------------------------------------------------------------>
# QTRewardRelationExp
# ------------------------------------------------------------>
class QTRewardRelationExp( QTRewardExp ):
	"""
	���齱����ʽ:
	if g <= w:
		exp = baseExp * ( 0.5 + ( g - 1 )*0.1 + ( c - 1 )*0.05 ) * 2
	else:
		exp = baseExp * ( 0.5 + ( g - 1 )*0.1 + ( c - 1 )*0.05 )

	exp: ������ֵ��
	baseExp:  ��������
	w:	˫����������
	g:	�����ɵ�������
	c:	��ҵ�ǰ�ǵڼ��Σ�����
	l:  ��ǰ������ȼ�(���ڼ��� baseExp )
	"""

	m_type = csdefine.QUEST_REWARD_RELATION_EXP
	def __init__( self ,*args ):
		self._amount = 0
		self._owner = 0
		self._doubleExpFlag = False
		if len( args ) > 0:
			self._amount = args[0]

	def init( self, param1, param2 ):
		"""
		"""
		self.w = param2				# ˫����������
		self.baseExpDatas = param1	# ����������Ϣ��
		self.baseExp = 0			# ��������

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		exp = self.calcRewardExp( playerEntity, questID )
		playerEntity.addExp( int( exp ), csdefine.CHANGE_EXP_QTREWARDRELATIONEXP )
		return [cschannel_msgs.QUEST_INFO_5  + str(int(exp))]

	def calcRewardExp( self, playerEntity, questID ):
		"""
		����do��ʱ�򣬸���ҼӶ��پ���
		"""
		exp = 0
		g = playerEntity.getGroupQuestCount( questID ) + 1
		c = playerEntity.getSubQuestCount( questID )
		l = playerEntity.getQuest( playerEntity.questsTable[questID].query( 'subQuestID' )).getLevel()
		
		exp = csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_LOOP_QUEST_30_59, l, c, g )
		if g <= self.w:
			exp *= 2
			
		return exp

	def calcShowClientExp( self, playerEntity, questID ):
		"""
		������ʾ���ͻ��˿������Ӧ�üӵľ���
		ע�⣬��ʾ���ͻ��˵ľ��飬��doʱ��ľ������������
		��ʾ��ʱ��cҪ��1����ɵ�ʱ��Ͳ��ü�1��
		��Ϊ��ɵ�ʱ��ִ�е�do��ʱ���Ѿ��ӹ�1��
		"""
		g = playerEntity.getGroupQuestCount( questID ) + 1
		c = playerEntity.getSubQuestCount( questID ) + 1									#��ɺ�Ĵ���
		l = playerEntity.getQuest( playerEntity.questsTable[questID].query( 'subQuestID' )).getLevel()
		
		exp = csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_LOOP_QUEST_30_59, l, c, g )
		if g <= self.w:
			self._doubleExpFlag = True
			exp *= 2
		else:
			self._doubleExpFlag = False
			
		return exp

	def transferForClient( self, playerEntity, questID ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		exp = self.calcShowClientExp( playerEntity, questID )
		return struct.pack( "=bib", self.type(), int(exp), self._doubleExpFlag )


# ------------------------------------------------------------>
# QTRewardRelationPetExp
# ------------------------------------------------------------>
class QTRewardRelationPetExp( QTRewardRelationExp ):
	"""
	��������ﾭ�齱����ʽ:
	exp = ���ݹ�ʽ����������þ����1/4
	"""

	m_type = csdefine.QUEST_REWARD_RELATION_PET_EXP

	def __init__( self ,*args ):
		QTRewardRelationExp.__init__( self ,*args )

	def init( self, param1, param2 ):
		"""
		"""
		QTRewardRelationExp.init( self, param1, param2 )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		quest = playerEntity.getQuest( questID )
		if quest.getType() != csdefine.QUEST_TYPE_NONE or quest.getStyle() == csdefine.QUEST_STYLE_LOOP_GROUP:
			level = playerEntity.getLevel()
		else:
			level  = quest.getLevel()

		exp = self.calcRewardExp( playerEntity, questID ) / 4
		actPet = playerEntity.pcg_getActPet()
		if actPet :
			actPet.entity.addQuestEXP( exp, level )
			return [cschannel_msgs.QUEST_INFO_5  + str(int(exp))]
		else:
			return [ cschannel_msgs.QUEST_INFO_7 ]

	def transferForClient( self, playerEntity, questID ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		exp = self.calcShowClientExp( playerEntity, questID ) / 4
		return struct.pack( "=bib", self.type(), int(exp), self._doubleExpFlag )

# ------------------------------------------------------------>
# QTRewardRndItems
# ------------------------------------------------------------>
class QTRewardFixedRndItems( QTRewardItems ):
	m_type = csdefine.QUEST_REWARD_FIXED_RANDOM_ITEMS
	def __init__( self, *args ):
		"""
		"""
		self._rewardItemsFixedRate = []
		self.showItem = False
		self.str = ""
		if len( args ) > 0:
			for e in xrange(0, len(args), 4):
				#item = items.instance().createDynamicItem( args[e], args[e+1] )
				self._rewardItemsFixedRate.append( (args[e], args[e+1] , args[e+2], args[e+3], args[e+4]) )
				self.str = args[e+4]


	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: ���±�
		@type  section: pyDataSection
		"""
		tempParam = 0.0
		for	node in section.values():
			self.addRndItem( node.readInt( "itemID" ), node.readInt( "amount" ), tempParam, node.readFloat( "param1" ), node.readInt( "param3" ) )	# ���ӽ��������� 2009-07-17 SPF
			tempParam = node.readFloat( "param1" )
			self.str = node.readString("param2")
			flag = node.readInt("param4")
			if flag and flag == 1:
				self.showItem = True

	def addRndItem( self, itemID, itemAmount, rateDown, rateUp, bindType ):
		"""
		"""
		if itemAmount > 0:
			#item = items.instance().createDynamicItem( itemID, itemAmount )
			self._rewardItemsFixedRate.append( ( itemID, itemAmount, rateDown, rateUp, bindType ) )

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		"""��ΪĿǰ���������������ؼ������ֱ�ӷ���return True
		index = self.generateIndex()
		playerEntity.setTemp( "RewardRnd_Index" , self.generateIndex() )
		for i in index:
			if not self._rewards[i][1].check( playerEntity ):
				playerEntity.removeTemp( "RewardRnd_Index" )
				return False
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def getItems( self , playerEntity, questID ):
		"""
		virtual method
		ȡ�ý�����Ʒ
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: Items
		@rtype:  CItemBase Instances
		"""
		tempItems = []
		index = self.generateIndex( playerEntity )
		for i in index:
			try:
				tempItems.append( i )
			except:
				ERROR_MSG( "Error Index(%i)!" %  i)
				continue
		return tempItems

	def generateIndex( self, playerEntity ):
		"""
		"""
		index = []
		prob = random.random() * 100.0
		for i in self._rewardItemsFixedRate:
			if prob > i[2] and prob <= i[3]:
				item = items.instance().createDynamicItem( i[0], i[1] )
				if i[4] != 0:
					item.setBindType( i[4], playerEntity )
				index.append( item )
		return index

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		infoList = []
		_rewardItems = self.getItems( playerEntity, questID )
		for i in _rewardItems:
			playerEntity.addItemAndRadio( i, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTREWARDFIXEDRNDITEMS )
			infoList.append( i.name() )
		return infoList


	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		if self.showItem:		# ��ֵΪTrue����ʾ������Ʒ������ֻ��ʾ�����������
			dataList = [ (e[0], e[1]) for e in self._rewardItemsFixedRate ]
			s = cPickle.dumps( dataList, 2 )
			return struct.pack( "=bi", self.type(), 1 ) + s
		else:
			return struct.pack( "=bi", self.type(), 0 ) + self.str
		#return struct.pack( "=bi", self.type(), self.str )


# ------------------------------------------------------------>
# QTRewardPrestige
# ------------------------------------------------------------>
class QTRewardPrestige( QTReward ):
	m_type = csdefine.QUEST_REWARD_PRESTIGE
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._prestigeID = args[0]
			self._value = args[1]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._prestigeID = section.readInt( "param1" )			#����ID
		self._value		 = section.readInt( "param2" )			#����ֵ

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.addPrestige( self._prestigeID, self._value )
		if playerEntity.getQuest(questID).getType() == csdefine.QUEST_TYPE_DART or playerEntity.getQuest(questID).getType() == csdefine.QUEST_TYPE_MEMBER_DART:
			if self._prestigeID == csconst.FACTION_XL:
				BigWorld.globalData['DartManager'].add( playerEntity.getName(), 'sm_dartCreditXinglong', self._value )
			if self._prestigeID == csconst.FACTION_CP:
				BigWorld.globalData['DartManager'].add( playerEntity.getName(), 'sm_dartCreditChangping', self._value )
		elif playerEntity.getQuest(questID).getType() == csdefine.QUEST_TYPE_ROB:
			if self._prestigeID == csconst.FACTION_XL:
				BigWorld.globalData['DartManager'].add( playerEntity.getName(), 'sm_dartNotoriousXinglong', self._value )
			if self._prestigeID == csconst.FACTION_CP:
				BigWorld.globalData['DartManager'].add( playerEntity.getName(), 'sm_dartNotoriousChangping', self._value )

		return [cschannel_msgs.QUEST_INFO_8+ str(self._prestigeID),  cschannel_msgs.QUEST_INFO_9  + str(self._value) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		dataList = [ (self._prestigeID, self._value)]

		s = cPickle.dumps( dataList, 2 )
		return struct.pack( "=b", self.type() ) + s


# ------------------------------------------------------------>
# QTRewardPrestigeTong
# ------------------------------------------------------------>
class QTRewardPrestigeTong( QTReward ):
	m_type = csdefine.QUEST_REWARD_PRESTIGE
	"""
	�����������60%������
	1-2����Ա������ɣ�80%������
	3-5����Ա������ɣ�100%������
	6-9����Ա������ɣ�120%������
	10�����ϳ�Ա������ɣ�150%������
	"""
	# rewardRate = { 1:0.6, 2:0.6, 3:1.0, 4:1.0, 5:1.0, 6:1.2, 7:1.2, 8:1.2, 9:1.2 }
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._prestigeID = args[0]
			self._value = args[1]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._prestigeID = section.readInt( "param1" )			#����ID
		self._value		 = section.readInt( "param2" )			#����ֵ
		self._rewardRata = eval( section.readString( "param3" ) )
		self._overRate = section.readFloat( "param4" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		rate = 0.0
		num = playerEntity.queryTemp( "tongDartMembers" )
		if num is None:
			return [cschannel_msgs.QUEST_INFO_8+ "0",  cschannel_msgs.QUEST_INFO_9  + "0" ]
		if not num in self._rewardRata and num > 0:
			rate = self._overRate
		else:
			rate = self._rewardRata[num]
		value = int( self._value * rate )
		playerEntity.addPrestige( self._prestigeID, value )
		if playerEntity.getQuest(questID).getType() == csdefine.QUEST_TYPE_DART or playerEntity.getQuest(questID).getType() == csdefine.QUEST_TYPE_MEMBER_DART:
			if self._prestigeID == csconst.FACTION_XL:
				BigWorld.globalData['DartManager'].add( playerEntity.getName(), 'sm_dartCreditXinglong', value )
			if self._prestigeID == csconst.FACTION_CP:
				BigWorld.globalData['DartManager'].add( playerEntity.getName(), 'sm_dartCreditChangping', value )
		elif playerEntity.getQuest(questID).getType() == csdefine.QUEST_TYPE_ROB:
			if self._prestigeID == csconst.FACTION_XL:
				BigWorld.globalData['DartManager'].add( playerEntity.getName(), 'sm_dartNotoriousXinglong', value )
			if self._prestigeID == csconst.FACTION_CP:
				BigWorld.globalData['DartManager'].add( playerEntity.getName(), 'sm_dartNotoriousChangping', value )
		return [cschannel_msgs.QUEST_INFO_8+ str(self._prestigeID),  cschannel_msgs.QUEST_INFO_9  + str(value) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		dataList = [ (self._prestigeID, self._value)]

		s = cPickle.dumps( dataList, 2 )
		return struct.pack( "=b", self.type() ) + s


# ------------------------------------------------------------>
# QTRewardTongContribute
# ------------------------------------------------------------>
class QTTongContribute( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_CONTRIBUTE
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

		self.count = 0 # �����������
		self.mult = 0  # ��������

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def setAmount( self, amount ):
		self._amount = amount

	def setExtraParam( self, *args ):
		self.count = args[0]
		self.mult = args[1]

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		amount = self._amount
		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			amount *= self.mult
		playerEntity.tong_addContribute( amount )
		return [cschannel_msgs.QUEST_INFO_4  + str(amount) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		_doubleExpFlag = False
		amount = self._amount
		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		playerEntity.getGroupQuestCount( questID ) + \
		playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			amount *= self.mult
			_doubleExpFlag = True
		return struct.pack( "=bib", self.type(), amount, _doubleExpFlag )


# ------------------------------------------------------------>
# QTRewardTongBuildVal
# ------------------------------------------------------------>
class QTRewardTongBuildVal( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_BUILDVAL
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

		self.count = 0 # �����������
		self.mult = 0  # ��������

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def setExtraParam( self, *args ):
		self.count = args[0]
		self.mult = args[1]

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		amount = self._amount
		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			amount *= self.mult
		#playerEntity.tong_addBuildVal( amount )
		return [cschannel_msgs.QUEST_INFO_10  + str(amount) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		_doubleExpFlag = False
		amount = self._amount
		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			amount *= self.mult
			_doubleExpFlag = True
		return struct.pack( "=bib", self.type(), amount, _doubleExpFlag )

# ------------------------------------------------------------>
# QTRewardTongMoney
# ------------------------------------------------------------>
class QTRewardTongMoney( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_MONEY
	# ���ڰ���ʽ���Ҫͨ���������ã��������ǰ��չ�ʽ�����ʽ�ֵ��
	def __init__( self ,*args ):
		self.count = 0 # �����������
		self.mult = 0  # ��������

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		pass

	def setExtraParam( self, *args ):
		self.count = args[0]
		self.mult = args[1]

	def getAmount( self, playerEntity, questID ):
		"""
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%questID, playerEntity.level )
		g = playerEntity.getGroupQuestCount( questID ) + 1
		baseMoney = QuestsFlyweight.instance().getSecondMoneyByLevel( questLevel ) * 45
		if baseMoney is None:
			return
		money = baseMoney * ( 0.55 + ( g - 1 ) * 0.1 )

		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			money *= self.mult

		return int( money )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		money = self.getAmount( playerEntity, questID )
		
		if money < 0:
			ERROR_MSG( "QTRewardTongMoney do failed! questID(%s), value(%i)" % (str(questID), money) )
			money = 0
		
		playerEntity.tong_addMoney( money, csdefine.TONG_CHANGE_MONEY_QTREWARDTONGMONEY  )
		return [cschannel_msgs.QUEST_INFO_11  + str( self.getAmount( playerEntity, questID ) ) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%questID, playerEntity.level )
		_doubleExpFlag = False
		g = playerEntity.getGroupQuestCount( questID ) + 1
		baseMoney = QuestsFlyweight.instance().getSecondMoneyByLevel( questLevel ) * 45
		if baseMoney is None:
			return
		money = baseMoney * ( 0.55 + ( g - 1 ) * 0.1 )

		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			money *= self.mult
			_doubleExpFlag = True
		return struct.pack( "=bib", self.type(), int( money ), _doubleExpFlag )

# ------------------------------------------------------------>
# QTRewardRoleLevelMoney
# ------------------------------------------------------------>
class QTRewardRoleLevelMoney( QTReward ):
	m_type = csdefine.QUEST_REWARD_ROLE_LEVEL_MONEY
	# ���ڰ���ʽ���Ҫͨ���������ã��������ǰ��չ�ʽ�����ʽ�ֵ��
	def __init__( self ,*args ):
		self.count = 0 # �����������
		self.mult = 0  # ��������

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		pass

	def setExtraParam( self, *args ):
		self.count = args[0]
		self.mult = args[1]

	def getAmount( self, playerEntity, questID ):
		"""
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%questID, playerEntity.level )
		g = playerEntity.getGroupQuestCount( questID ) + 1
		baseMoney = QuestsFlyweight.instance().getSecondMoneyByLevel( questLevel ) * 45
		if baseMoney is None:
			return
		money = baseMoney * ( 0.55 + ( g - 1 ) * 0.1 )

		# ��Ǯ����˫��
		#playerEntity.addMoney( int( money ) )
		#total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		#        playerEntity.getGroupQuestCount( questID ) + \
		#        playerEntity.getSubQuestCount( questID ) + 1
		#if self.count > 0 and self.count >=  total:
		#	money *= self.mult

		return int( money )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		money = self.getAmount( playerEntity, questID )
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_QTREWARDROLELEVELMONEY  )
		return [cschannel_msgs.GMMGR_JIN_QIAN  + str( self.getAmount( playerEntity, questID ) ) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%questID, playerEntity.level )
		_doubleExpFlag = False
		g = playerEntity.getGroupQuestCount( questID ) + 1
		baseMoney = QuestsFlyweight.instance().getSecondMoneyByLevel( questLevel ) * 45
		if baseMoney is None:
			return
		money = baseMoney * ( 0.55 + ( g - 1 ) * 0.1 )

		#total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		#        playerEntity.getGroupQuestCount( questID ) + \
		#        playerEntity.getSubQuestCount( questID ) + 1
		#if self.count > 0 and self.count >=  total:
		#	amount *= self.mult
		#	_doubleExpFlag = True
		return struct.pack( "=bib", self.type(), int( money ), _doubleExpFlag )

# ------------------------------------------------------------>
# QTRewardExpFromRoleLevel
# ------------------------------------------------------------>
class QTRewardExpFromRoleLevel( QTReward ):
	"""
	���鹫ʽΪ����������*(0.55+(a-1)*0.1)������a��С����
	��������Ϊ����ɫ�ӵ�һ��ʱ�ĵȼ���Ӧ���뾭��*45

	���齱����ʽ:
	if g <= w:
		exp = baseExp * ( 0.55 + ( g - 1 )*0.1 ) * 2
	else:
		exp = baseExp * ( 0.55 + ( g - 1 )*0.1 )

	exp: ������ֵ��
	baseExp:  ��������
	w:	˫����������
	g:	�����ɵ�������
	"""
	m_type = csdefine.QUEST_REWARD_EXP_FROM_ROLE_LEVEL
	def __init__( self ,*args ):
		self.count = 0 # ���������
		self.mult = 0  # ��������
		self._doubleExpFlag = False

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		pass

	def getAmount( self, playerEntity, questID ):
		"""
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%questID, playerEntity.level )
		g = playerEntity.getSubQuestCount( questID )
		# ���ﲻ��1��ԭ���ǣ��������ʱ���Ƚ������������Ĵ�����ʱCount�Ѿ���1�ˡ�
		#c = playerEntity.getSubQuestCount( questID )
		#l = playerEntity.getQuest( playerEntity.questsTable[questID].query( 'subQuestID' )).getLevel()

		baseExp = QuestsFlyweight.instance().getSecondExpByLevel( questLevel ) * 63
		if baseExp is None:
			return
		if g < self.count:
			exp = baseExp * ( 0.5 + ( g - 1 ) * 0.1 ) * 1
		else:
			exp = baseExp * ( 0.5 + ( g - 1 )*0.1 )

		#exp = playerEntity.level * 100
		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			exp *= self.mult
		return int( exp )

	def setExtraParam( self, *args ):
		self.count = args[0]
		self.mult = args[1]

	def getTransClientAmount( self, playerEntity, questID ):
		"""
		�����ʾ�ڿͻ����ϵĳ��ﾭ��
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%questID, playerEntity.level )
		exp = 0
		self._doubleExpFlag = False
		g = playerEntity.getSubQuestCount( questID ) + 1
		baseExp = QuestsFlyweight.instance().getSecondExpByLevel( questLevel ) * 63
		if baseExp is None:
			return
		if g < self.count:
			exp = baseExp * ( 0.5 + ( g - 1 ) * 0.1 ) * 1
		else:
			exp = baseExp * ( 0.5 + ( g - 1 )*0.1 )

		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			exp *= self.mult
			self._doubleExpFlag = True
		return exp

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		exp = self.getAmount( playerEntity, questID )
		playerEntity.addExp( exp, csdefine.CHANGE_EXP_QTREWARDEXPFROMROLELEVEL )
		return [cschannel_msgs.QUEST_INFO_5  + str( exp )]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		exp = self.getTransClientAmount( playerEntity, questID )
		return struct.pack( "=bib", self.type(), int( exp ), self._doubleExpFlag )


# ------------------------------------------------------------>
# QTRewardPetExpFromRoleLevel
# ------------------------------------------------------------>
class QTRewardPetExpFromRoleLevel( QTRewardExpFromRoleLevel ):
	"""
	���鹫ʽΪ��QTRewardExpFromRoleLevel��������Ҿ����1/4
	"""
	m_type = csdefine.QUEST_REWARD_PET_EXP_FROM_ROLE_LEVEL

	def __init__( self ,*args ):
		QTRewardExpFromRoleLevel.__init__( self ,*args )

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		QTRewardExpFromRoleLevel.init( self, owner, section )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		exp = self.getAmount( playerEntity, questID ) / 4
		quest = playerEntity.getQuest( questID )
		if quest.getType() != csdefine.QUEST_TYPE_NONE or quest.getStyle() == csdefine.QUEST_STYLE_LOOP_GROUP:
			level = playerEntity.getLevel()
		else:
			level  = quest.getLevel()

		actPet = playerEntity.pcg_getActPet()
		if actPet :
			actPet.entity.addQuestEXP( exp, level )
		return [ cschannel_msgs.QUEST_INFO_5  + str( exp ) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		exp = self.getTransClientAmount( playerEntity, questID ) / 4
		return struct.pack( "=bib", self.type(), int( exp ), self._doubleExpFlag )

# ------------------------------------------------------------>
# QTRewardSecondPercentExp �뾭��ӳ�
# ------------------------------------------------------------>
class QTRewardSecondPercentExp( QTReward ):
	m_type = csdefine.QUEST_REWARD_EXP_SECOND_PERCENT
	def __init__( self ,*args ):
		"""
		�뾭��ӳ�
		"""
		if len( args ) > 0:
			self._percent = args[0]
		else:
			self._percent = 1.0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._percent = section.readFloat( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		exp = self.calculate( playerEntity )
		playerEntity.addExp( exp, csdefine.CHANGE_EXP_QTREWARDSECONDPERCENTEXP )
		return [cschannel_msgs.QUEST_INFO_5  + str(exp)]

	def calculate( self, playerEntity ):
		"""
		���㾭��

		@rtype: int
		"""
		baseExp = QuestsFlyweight.instance().getSecondExpByLevel( playerEntity.level ) * self._percent
		return int(baseExp)

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%questID, playerEntity.level )
		exp = QuestsFlyweight.instance().getSecondExpByLevel( questLevel ) * self._percent
		return struct.pack( "=bi", self.type(), int( exp ) )


# ------------------------------------------------------------>
# QTRewardPetSecondPercentExp �뾭��ӳ�(����)
# ------------------------------------------------------------>
class QTRewardPetSecondPercentExp( QTRewardSecondPercentExp ):

	m_type = csdefine.QUEST_REWARD_PET_EXP_SECOND_PERCENT

	def __init__( self ,*args ):
		"""
		�뾭��ӳ�
		"""
		QTRewardSecondPercentExp.__init__( self ,*args )

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		QTRewardSecondPercentExp.init( self, owner, section )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		quest = playerEntity.getQuest( questID )
		level = 0
		if quest.getType() != csdefine.QUEST_TYPE_NONE or quest.getStyle() == csdefine.QUEST_STYLE_LOOP_GROUP:
			level = playerEntity.getLevel()
		else:
			level  = quest.getLevel()

		exp = self.calculate( playerEntity ) / 4
		actPet = playerEntity.pcg_getActPet()
		if actPet :
			actPet.entity.addQuestEXP( exp, level )
		return [ cschannel_msgs.QUEST_INFO_5  + str( exp ) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%questID, playerEntity.level )
		exp = QuestsFlyweight.instance().getSecondExpByLevel( questLevel ) * self._percent / 4
		return struct.pack( "=bi", self.type(), int( exp ) )


# ------------------------------------------------------------>
# QTRewardIETitle �ƾٳƺŽ���
# ------------------------------------------------------------>
class QTRewardIETitle( QTRewardTitle ):
	m_type = csdefine.QUEST_REWARD_IE_TITLE
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		task = None
		quest = playerEntity.getQuest( questID )
		for t in playerEntity.questsTable._quests[questID]._tasks.itervalues():
			if t.getType() == csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION:
				task = t
				break
		iRight = int ( task.str1 )
		iFinish = task.val1
		titleName = g_titleLoader.getName( self._title )
		examName = quest._title[8:12]	# ��ǰ���������硰���ԡ������ԡ���
		nextExam = ""
		nextDate = ""
		dianShi = False
		if examName == cschannel_msgs.QUEST_INFO_12:
			nextExam = cschannel_msgs.QUEST_INFO_13
			nextDate = cschannel_msgs.QUEST_INFO_14
		elif examName == cschannel_msgs.QUEST_INFO_13:
			nextExam = cschannel_msgs.QUEST_INFO_15
			nextDate = cschannel_msgs.QUEST_INFO_16
		elif examName == cschannel_msgs.QUEST_INFO_15:
			dianShi = True

		# �ش���ȷ����60%���ܻ�óƺ�
		if iRight * 1.0 / iFinish < 0.6 and not dianShi:
			playerEntity.statusMessage( csstatus.IE_ANSWER_FAILED_TITLE, nextExam )
			return []

		playerEntity.addTitle( self._title )
		localTime = time.localtime()
		xiucaiLimit = ( 0, 0, 0, 0 )	# ��ųƺ����ʱ��Ϊ��������12��0��0��(��һ0��0��0��)
		jurenLimit = ( 5, 0, 0, 0 )	# ���˳ƺ����ʱ��Ϊ��������12��0��0�루����0��0��0�룩
		otherLimit = ( 6, 0, 0, 0 )	# ��ʿ��״Ԫ�����ۡ�̽���ƺ����ʱ��Ϊ��������12��0��0�루����0��0��0�룩
		if self._title in [ TITLE_XIUCAI, TITLE_JUREN, TITLE_JINSHI, TITLE_TANHUA, TITLE_BANGYAN, TITLE_ZHUANGYUAN ]:
			limitTime = ( 0,0 )
			if self._title == TITLE_XIUCAI:
				limitTime = xiucaiLimit
			elif self._title == TITLE_JUREN:
				limitTime = jurenLimit
			else:
				limitTime = otherLimit

			seconds = limitTime[3] - localTime[5]
			minutes = limitTime[2] - localTime[4]
			hour = limitTime[1] - localTime[3]
			day = limitTime[0] - localTime[6]
			if seconds < 0:
				seconds += 60
				minutes -= 1
			if minutes < 0:
				minutes += 60
				hour -= 1
			if hour < 0:
				hour += 24
				day -= 1
			if day < 0:
				day += 7
			interval = day * 24 * 3600 + hour * 3600 + minutes * 60 + seconds
			playerEntity.setTitleLimitTime( self._title, interval )

		playerEntity.selectTitle( playerEntity.id, self._title )
		if examName != cschannel_msgs.QUEST_INFO_15:
			playerEntity.statusMessage( csstatus.IE_ANSWER_GAINED_TITLE, playerEntity.playerName, titleName, nextExam, nextDate, nextExam )
		return []


# ------------------------------------------------------------>
# QTRewardExpFromTable
# ------------------------------------------------------------>
class QTRewardExpFromTable( QTReward ):
	m_type = csdefine.QUEST_REWARD_EXP
	def __init__( self ,*args ):
		pass

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		pass

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.addExp( self.calculate( playerEntity, questID ), csdefine.CHANGE_EXP_QTREWARDEXPFROMTABLE )
		return [cschannel_msgs.QUEST_INFO_5  + str( self.calculate( playerEntity, questID ) )]

	def calculate( self, playerEntity, questID ):
		"""
		���㾭��

		@rtype: int
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level )
		try:
			exp = int( g_questRewardFromTable.get( str( questID ) )[questLevel]['exp'] )
		except KeyError:
			INFO_MSG( "level %i don't in table" % playerEntity.level )	# û����Ӧ�ȼ�������
			return 1

		return exp

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self.calculate( playerEntity, str( questID ) ) )


# ------------------------------------------------------------>
# QTRewardMoneyFromTable
# ------------------------------------------------------------>
class QTRewardMoneyFromTable( QTReward ):
	m_type = csdefine.QUEST_REWARD_MONEY
	def __init__( self ,*args ):
		pass

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		pass

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		money = self.calculate( playerEntity, questID )
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_QTREWARDMONEYFROMTABLE )
		return [cschannel_msgs.GMMGR_JIN_QIAN  + str(self.calculate( playerEntity, questID )) ]

	def calculate( self, playerEntity, questID ):
		"""
		���㾭��

		@rtype: int
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level )
		try:
			money = int( g_questRewardFromTable.get( str( questID ) )[questLevel]['money'] )
		except KeyError:
			INFO_MSG( "level %i don't in table" % questLevel )	# û����Ӧ�ȼ�������
			return 1

		return money

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		nearMax = playerEntity.testAddMoney( self.calculate( playerEntity, questID ) )
		if playerEntity.iskitbagsLocked():	# ����������by����
			playerEntity.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return False
		if  nearMax > 0:	#������Я���Ľ�Ǯ��������������Ʒ��Ǯ�ѵ�����
			playerEntity.statusMessage( csstatus.CIB_MONEY_OVERFLOW )		#֪ͨ���
			return False
		elif nearMax == 0:
			playerEntity.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )		#֪ͨ���
			return False
		else:
			return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self.calculate( playerEntity, questID ) )

# ------------------------------------------------------------>
# QTRewardRandomItemFromTable
# ------------------------------------------------------------>
class QTRewardRandomItemFromTable( QTReward ):
	m_type = csdefine.QUEST_REWARD_RANDOM_ITEM_FROM_TABLE
	def __init__( self, *args ):
		"""
		��ʼ��������Ϣ
		"""
		self.str = ""
		self.count = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: itemID, amount
		@type  section: pyDataSection
		"""
		self.count  = section.readInt( "param1" )	# ������Ʒ����
		self.str = section.readString( "param2" )	# ������ʾ

	def getCount( self ):
		"""
		��ȡ�˰� �����Ľ�����Ŀ
		"""
		return self.count

	def getItems( self , playerEntity, questID ):
		"""
		virtual method
		ȡ�ý�����Ʒ
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: Items
		@rtype:  CItemBase Instances
		"""
		return playerEntity.queryTemp( "tempQTRewardRandomItemFromTable", [] )

	def add( self , playerEntity, questID ):
		"""
		���һ���µĽ���
		@param   rewardInstance: һ����ģ�����κ�һ�ֽ�����ʵ��
		@type    rewardInstance: reward instance
		"""
		questLevel = playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level )
		itemList = []
		for e in xrange( self.count ):
			rnd = random.randint( 1, 100 )
			keys = g_questRewardFromTable.get( str( questID ) )[questLevel]['items'].keys()
			keys.sort()
			if len( keys ) < 1:
				return
			for key in keys:
				if key >= rnd:
					break

			itemID = g_questRewardFromTable.get( str( questID ) )[questLevel]['items'][key]
			item = items.instance().createDynamicItem( itemID )
			itemList.append( item )
		playerEntity.setTemp( "tempQTRewardRandomItemFromTable", itemList )		# ��¼��Ʒ��ʱ����

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not QTReward.check( self, playerEntity, questID = 0 ):
			return False
		self.add( playerEntity, questID )
		return playerEntity.checkItemsPlaceIntoNK_( playerEntity.queryTemp( "tempQTRewardRandomItemFromTable", [] ) ) == csdefine.KITBAG_CAN_HOLD

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		infoList = []
		for e in playerEntity.queryTemp( "tempQTRewardRandomItemFromTable", [] ):
			playerEntity.addItemAndRadio( e.new(), ItemTypeEnum.ITEM_GET_QUEST,reason =  csdefine.ADD_ITEM_QTREWARDRANDOMITEMFROMTABLE )
			infoList.append(e.name())
		return infoList

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=b", self.type()) + self.str


class QTRewardSpecialTongBuildVal( QTRewardTongBuildVal ):
	"""
	������������İ�Ὠ��Ƚ���
	"""
	m_type = csdefine.QUEST_REWARD_SPECIAL_TONG_BUILDVAL
	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )
		self._moreAmount = section.readInt( "param2" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		singleCount = playerEntity.getSubQuestCount( questID )
		if singleCount != 0 and singleCount %10 == 0:
			amount = self._moreAmount
		else:
			amount = self._amount
		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			amount *= self.mult
		#playerEntity.tong_addBuildVal( amount )
		return [cschannel_msgs.QUEST_INFO_10  + str(amount) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		_doubleExpFlag = False
		singleCount = playerEntity.getSubQuestCount( questID ) + 1
		if singleCount != 0 and singleCount %10 == 0:
			amount = self._moreAmount
		else:
			amount = self._amount
		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			amount *= self.mult
			_doubleExpFlag = True
		return struct.pack( "=bib", self.type(), amount, _doubleExpFlag )



class QTRewardFuBiItems( QTRewardItems ):
	"""
	�����Ҫ�Ǹ���������ʹ�õĸ��ҽ���
	"""
	m_type = csdefine.QUEST_REWARD_FUBI_ITEMS
	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: itemID, amount
		@type  section: pyDataSection
		"""
		self.add( ITEM_FUBI_ID, section.readInt( "param1" ), 0, 0)


# ------------------------------------------------------------>
# QTRewardChooseItemsAndBind
# ------------------------------------------------------------>
class QTRewardChooseItemsAndBind( QTRewardChooseItems ):
	"""
	��Ʒ��ѡһ
	"""
	m_type = csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND
	def __init__( self, *args ):
		"""
		"""
		QTRewardChooseItems.__init__( self, *args )

	def getItems( self , playerEntity, questID ):
		"""
		virtual method
		ȡ�ý�����Ʒ
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: Items
		@rtype:  CItemBase Instances
		"""
		selectindex = playerEntity.queryTemp( "RewardItemChoose" , 0 )
		itemInfo = self._rewardItemsInfo[ selectindex ]
		try:
			item = items.instance().createDynamicItem( itemInfo[0], itemInfo[1] )
			item.setBindType( ItemTypeEnum.CBT_PICKUP )
		except:
			ERROR_MSG( "Error Index(%i)!" %  selectindex)
			return []
		return  [item]


# ------------------------------------------------------------>
# QTRewardTongFeteItems
# ------------------------------------------------------------>
class QTRewardTongFete( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_FETE
	def __init__( self, *args ):
		"""
		��ʼ��������Ϣ
		"""
		pass


	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: itemID, amount
		@type  section: pyDataSection
		"""
		pass


	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not QTReward.check( self, playerEntity, questID = 0 ):
			return False
		return True

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		order = playerEntity.queryTemp( "questOrder", 0 )
		playerEntity.setTemp( "FeteRewardGiveItemOrder", order )
		awarder = Love3.g_rewards.fetch( csdefine.RCG_TONG_FETE, playerEntity )							# awarder���ǽ���ʵ��
		awarder.award( playerEntity, csdefine.ADD_ITEM_QUEST )														# reason�Ǹ�������ԭ��
		return []

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		s = cPickle.dumps( [], 2 )
		return struct.pack( "=b", self.type()) + s


# ------------------------------------------------------------>
# QTRewardTongContribute
# ------------------------------------------------------------>
class QTRewardTongContribute( QTReward ):
	"""
	��ṱ�׽���
	"""
	m_type = csdefine.QUEST_REWARD_TONG_CONTRIBUTE

	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		gameYield = playerEntity.wallow_getLucreRate()
		contr = int( self._amount * gameYield )
		playerEntity.tong_addContribute( contr )
		
		return [cschannel_msgs.GMMGR_BANG_GONG  + str(contr) ]

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )


# ------------------------------------------------------------>
# QTRewardTongActionVal
# ------------------------------------------------------------>
class QTRewardTongActionVal( QTReward ):
	"""
	����ж�������
	"""
	m_type = csdefine.QUEST_REWARD_TONG_ACTIONVAL

	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

		self.count = 0 # �����������
		self.mult = 0  # ��������

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )
		
	def setExtraParam( self, *args ):
		self.count = args[0]
		self.mult = args[1]	#
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		amount = self._amount
		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		        playerEntity.getGroupQuestCount( questID ) + \
		        playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			amount *= self.mult
		
		gameYield = playerEntity.wallow_getLucreRate()
		actionVal = int( amount * gameYield )
		#playerEntity.tong_addActionVal( actionVal )
		return [cschannel_msgs.QUEST_INFO_51  + str( actionVal ) ]

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		_doubleExpFlag = False
		amount = self._amount
		total = ( playerEntity.getGroupQuestCount( questID ) ) * \
		playerEntity.getGroupQuestCount( questID ) + \
		playerEntity.getSubQuestCount( questID ) + 1
		if self.count > 0 and self.count >=  total:
			amount *= self.mult
			_doubleExpFlag = True
		return struct.pack( "=bib", self.type(), amount, _doubleExpFlag )

# ------------------------------------------------------------>
# QTRewardCampMorale
# ------------------------------------------------------------>
class QTRewardCampMorale( QTReward ):
	"""
	��Ӫʿ��
	"""
	m_type = csdefine.QUEST_REWARD_CAMP_MORALE
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.camp_addMorale( playerEntity.getCamp(), self._amount )
		return [cschannel_msgs.QUEST_INFO_52  + str( self._amount ) ]
		
	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )
		
class QTRewardCampHonour( QTReward ):
	"""
	��Ӫ����
	"""
	m_type = csdefine.QUEST_REWARD_CAMP_HONOUR
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.camp_addHonour( self._amount )
		return [cschannel_msgs.QUEST_INFO_53  + str( self._amount ) ]
	
	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )

# ------------------------------------------------------------>
# QTRewardDaoheng
# ------------------------------------------------------------>
class QTRewardDaoheng( QTReward ):
	"""
	���н���
	"""
	m_type = csdefine.QUEST_REWARD_DAOHENG

	def __init__( self ,*args ):
		"""
		��ʼ��������Ϣ
		"""
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		adjust_param = Const.DAOHENG_AMEND_RATE
		n = float( playerEntity.getDaoheng() ) / g_daoheng.get( playerEntity.getLevel())  # �߻�Ҫ�󣬲���nȡ��ҵ���ֵ/��ǰ�ȼ���Ӧ�ı�׼����ֵ
		rate  =  adjust_param /(math.log( ( 1 + adjust_param ), math.e ) * pow( ( 1+ adjust_param ), n ) ) 
		daoheng = rate * self._amount
		daoheng =  max( 1, daoheng )
		playerEntity.addDaoheng( daoheng, csdefine.ADD_DAOHENG_REASON_QUEST )

		return [cschannel_msgs.QUEST_INFO_54  + str( daoheng ) ]

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )
		
# ------------------------------------------------------------>
# QTRewardMoneyFromRoleLevel
# ------------------------------------------------------------>
class QTRewardRateMoneyFromRoleLevel( QTRewardMoney ):
	"""
	��Ӫ���������ҵȼ���һ�����ʻ�ý�Ǯ����
	"""
	m_type = csdefine.QUEST_REWARD_RATE_MONEY_FROM_ROLE_LEVEL
	
	def __init__( self ,*args ):
		"""
		��ʼ��������Ϣ
		"""
		if len( args ) > 0:
			self._rate = args[0]
		else:
			self._rate = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._rate = section.readFloat( "param1" )
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		money = self.calculate( playerEntity, questID )
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_QTREWARDMONEY )
		
		pType = csdefine.ACTIVITY_PARENT_TYPE_QUEST
		aType = 0
		action = csdefine.ACTIVITY_ACTION_REWARD_MONEY
		return [cschannel_msgs.GMMGR_JIN_QIAN  + str(money) ]
		
	def calculate( self, playerEntity, questID ):
		"""
		"""
		playerLevel = playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level )
		money = ( 100 * playerLevel * ( 1.5 ** ( 0.1 * playerLevel - 1 ) ) ) * self._rate
		return money

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self.calculate( playerEntity, questID ) ) 
		
# ------------------------------------------------------------>
# QTRewardExpFromRoleLevel
# ------------------------------------------------------------>
class QTRewardRateExpFromRoleLevel( QTRewardExp ):
	"""
	��Ӫ���������ҵȼ���һ�����ʻ�þ��齱��
	"""
	m_type = csdefine.QUEST_REWARD_RATE_EXP_FROM_ROLE_LEVEL
	
	def __init__( self ,*args ):
		"""
		��ʼ��������Ϣ
		"""
		if len( args ) > 0:
			self._rate = args[0]
		else:
			self._rate = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._rate = section.readFloat( "param1" )
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		exp = self.calculate( playerEntity, questID )
		playerEntity.addExp( exp, csdefine.CHANGE_EXP_QTREWARD )
		return [cschannel_msgs.QUEST_INFO_5  + str(exp)]
		
	def calculate( self, playerEntity, questID ):
		"""
		"""
		playerLevel = playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level )
		exp = ( 175 * ( playerLevel ** 1.5 ) + 460 ) * self._rate
		return exp

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self.calculate( playerEntity, questID ) ) 
		
#-------------------------------------------------------------------
# QTRewardQuestPartCompleted
#-------------------------------------------------------------------
class QTRewardQuestPartCompleted( QTReward ):
	"""
	���һ��������Ŀ��Ҫ���Ľ���
	"""
	m_type = csdefine.QUEST_REWARD_RATE_QUEST_PART_COMPLETED
	
	def __init__( self, *args ):
		self._sonRewardInstances = {}
		
	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: ���±�
		@type  section: pyDataSection
		"""
		for node in section.values():
			typeStr = node.readString( "type" )
			if typeStr == "QTRewardRelationExp":
				typeStr = "QTRewardExp"
			reward = createReward( typeStr )
			reward.init( owner, node )
			requestTaskNum = node.readInt( "taskNum" )
			if not self._sonRewardInstances.has_key( requestTaskNum ):
				self._sonRewardInstances[ requestTaskNum ] = [ reward ]
			else:
				self._sonRewardInstances[ requestTaskNum ].append( reward )
	
	def getItems( self , playerEntity, questID ):
		tempItems = []
		for reward in self._sonRewardInstances.values():
			if hasattr( reward, "getItems" ):
				tempItems.extend( reward.getItems( playerEntity, questID ) )
		return tempItems
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		completeTaskNum = 0
		resultList = []
		tasks = playerEntity.getQuestTasks( questID ).getTasks()
		for task in tasks.itervalues():
			if task.isCompleted( playerEntity ):
				completeTaskNum += 1
		for reward in self._sonRewardInstances.get( completeTaskNum ):
			if hasattr( reward, "getItems" ):				# Quest��reward_���Ѿ�������Ʒ��������������޳�
				continue
			resultList.extend( reward.do( playerEntity, questID ) )
		return resultList
		
	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		resultStr = ""
		for taskNum, sonRewards in self._sonRewardInstances.iteritems():
			for reward in sonRewards:																				# ��������ʽ
				sonStr = struct.pack( "=i", taskNum ) + reward.transferForClient( playerEntity, questID )			#|----|------|------------------|------|------------------|
				resultStr += struct.pack( "=i", len( sonStr ) ) + sonStr											#|type| len1 | taskNum + reward1| len2 | taskNum + reward2|
																													#|----|------|------------------|------|------------------|
		return struct.pack( "=b", self.type() ) + resultStr
		
# ------------------------------------------------------------>
# QTRewardMoney
# ------------------------------------------------------------>
class QTRewardMoneyFromQuestQuality( QTRewardMoney ):

	m_type = csdefine.QUEST_REWARD_MONEY_FROM_REWARD_QUEST_QUALITY

	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		money = self.calculate( playerEntity, questID )
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_QTREWARDMONEY )
		return [cschannel_msgs.GMMGR_JIN_QIAN  + str( money ) ]

	def calculate( self, playerEntity, questID ):
		"""
		�����Ǯ

		@rtype: int
		"""
		# ���ڲ߻���ǰû�д���������˸�Ϊֱ�ӷ���
		quality = playerEntity.query( "rewardQuestQuality_%i"%int( questID ), 1 )
		money = self._amount * quality
		return int( money )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self.calculate( playerEntity, questID ) )

# ------------------------------------------------------------>
# QTRewardExp
# ------------------------------------------------------------>
class QTRewardExpFromQuestQuality( QTRewardExp ):
	m_type = csdefine.QUEST_REWARD_EXP_FROM_REWARD_QUEST_QUALITY
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		exp = self.calculate( playerEntity, questID )
		playerEntity.addExp( exp, csdefine.CHANGE_EXP_QTREWARD )
		return [ cschannel_msgs.QUEST_INFO_5 + str( exp ) ]

	def calculate( self, playerEntity, questID ):
		"""
		���㾭��

		@rtype: int
		"""
		# ���ڲ߻���ǰû�д���������˸�Ϊֱ�ӷ���
		quality = playerEntity.query( "rewardQuestQuality_%i"%int( questID ), 1 )
		exp = self._amount * quality
		return int( exp )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self.calculate( playerEntity, questID ) )

# ------------------------------------------------------------>
# QTRewardTongNomalMoney
# ------------------------------------------------------------>
class QTRewardTongNomalMoney( QTReward ):
	"""
	����Ǯ����
	"""
	m_type = csdefine.QUEST_REWARD_TONG_NOMAL_MONEY
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.tong_addMoney( self._amount, csdefine.TONG_CHANGE_MONEY_QTREWARD )
		return [ cschannel_msgs.QUEST_INFO_11 + str( self._amount ) ]

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )

# ------------------------------------------------------------>
# QTRewardTongExp
# ------------------------------------------------------------>
class QTRewardTongExp( QTReward ):
	"""
	��ᾭ�齱��
	"""
	m_type = csdefine.QUEST_REWARD_TONG_EXP
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._amount = args[0]
		else:
			self._amount = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: amount
		@type  section: pyDataSection
		"""
		self._amount = section.readInt( "param1" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		tongMailbox = playerEntity.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.addExp( self._amount, csdefine.TONG_CHANGE_EXP_QTREWARD )
		return [ cschannel_msgs.QUEST_INFO_56 + str( self._amount ) ]

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=bi", self.type(), self._amount )
		

# ------------------------------------------------------------>
# QTRewardItemsFromClass
# ------------------------------------------------------------>
class QTRewardItemsFromClass( QTReward ):
	m_type = csdefine.QUEST_REWARD_ITEMS_FROM_CLASS
	def __init__( self, *args ):
		"""
		��ʼ��������Ϣ
		"""
		self._rewardItemsInfo = []

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: format: itemID, amount
		@type  section: pyDataSection
		"""
		try:
			for	node in section.values():
				if not node.has_key( "itemID" ):
					raise KeyError
				self.add(node.readInt( "itemID" ), node.readInt( "amount" ), node.readInt("playerClass"), node.readInt("param1"), node.readInt("param2"), node.readString("param3") )
		except KeyError:
			# QTRewardQuestPartCompleted���ָ��Ͻ����п����õ���Ʒ������������Ҫ��������Ĳ�����ʽ add by cwl
			self.add(section.readInt( "param1" ), section.readInt( "param2" ), section.readInt("param3"), section.readInt("param4"), section.readString("param5"), section.readInt("param6") )
			

	def add( self , itemID, itemAmount, playerClass, isBind, ownerLevel, schemeInfo ):
		"""
		���һ���µĽ���
		@param   rewardInstance: һ����ģ�����κ�һ�ֽ�����ʵ��
		@type    rewardInstance: reward instance
		"""
		if itemAmount <= 0:
			itemAmount = 1
		self._rewardItemsInfo.append( ( itemID, itemAmount, playerClass, isBind, ownerLevel, schemeInfo  ) )


	def getItems( self , playerEntity, questID ):
		"""
		virtual method
		ȡ�ý�����Ʒ
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: Items
		@rtype:  CItemBase Instances
		"""
		_rewardItems = []
		for itemID, amount, playerClass, isBind, ownerLevel, schemeInfo in self._rewardItemsInfo:
			if hasattr( playerEntity, "getClass" ):
				if playerEntity.getClass() == playerClass:
					item = items.instance().createDynamicItem( itemID, amount )
					if isBind:
						item.setBindType( ItemTypeEnum.CBT_PICKUP )
					if ownerLevel:
						item.set( "level", playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level ) )
					if schemeInfo != "":
						try:
							cmd,presistMinute = schemeInfo.split("|")
							presistMinute = int( presistMinute )
							scheme = Scheme()
							scheme.init( cmd )
							year, month, day, hour, minute = time.localtime( time.time() - presistMinute * 60 )[:5]
							nextTime = scheme.calculateNext( year, month, day, hour, minute )
							if nextTime > time.time():
								continue
						except:
							ERROR_MSG("QTRewardItems: scheme config(%s) was wrong!"%schemeInfo )
							continue
					_rewardItems.append( item )
		return _rewardItems

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not QTReward.check( self, playerEntity, questID = 0 ):
			return False

		return playerEntity.checkItemsPlaceIntoNK_( self.getItems( playerEntity, questID ) ) == csdefine.KITBAG_CAN_HOLD

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		infoList = []
		for item in  self.getItems( playerEntity, questID ):
			playerEntity.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QTREWARDITEMS )
			infoList.append(item.name())
		return infoList

	def getItemByClass( self, playerEntity ):
		"""
		�������ְҵѡ��Ҫ������ͻ��˵�����
		"""
		_rewardItemsInfo = []
		for itemID, amount, playerClass, isBind, ownerLevel, schemeInfo in self._rewardItemsInfo:
			if hasattr( playerEntity, "getClass" ):
				if playerEntity.getClass() == playerClass:
					_rewardItemsInfo.append( ( itemID, amount, playerClass, isBind, ownerLevel, schemeInfo  ) )
		return _rewardItemsInfo

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		info = []
		for i in self.getItemByClass( playerEntity ):
			if i[4] != 0:		#Ҫ����Ʒ�ȼ�������ҽ�����ʱ�ĵȼ�
				info.append( ( i[0], i[1], i[2], i[3], playerEntity.query( "recordQuestLevel_%i"%int(questID), playerEntity.level ), i[5] ) )
				continue
			info.append( i )
		s = cPickle.dumps( info, 2 )
		return struct.pack( "=b", self.type()) + s
		
# ------------------------------------------------------------>
# QTRewardSkillFromClass
# ------------------------------------------------------------>
class QTRewardSkillFromClass( QTReward ):
	m_type = csdefine.QUEST_REWARD_SKILL_FROM_CLASS
	def __init__( self ,*args ):
		if len( args ) > 0:
			self._skillID = args[0]
		else:
			self._skillID = 0

	def init( self, owner, section ):
		"""
		@param   owner: ��ǰѡ���ӵ����(����)ʵ��
		@type    owner: Quest
		@param section: ��ʼ������,������ʽ��ÿ��ʵ���Լ��涨
		@type  section: pyDataSection
		"""
		self._skillID1 = section.readInt( "param1" )
		self._skillID2 = section.readInt( "param2" )
		self._skillID3 = section.readInt( "param3" )
		self._skillID4 = section.readInt( "param4" )

	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		playerEntity.addSkill( self.getSkillByClass( playerEntity ) )
		return []

	def getSkillByClass( self, playerEntity ):
		"""
		�������ְҵ��ò�ͬ�ļ���
		"""
		if hasattr( playerEntity, "getClass" ):
			if playerEntity.getClass() == csdefine.CLASS_FIGHTER:
				return self._skillID1
			elif playerEntity.getClass() == csdefine.CLASS_SWORDMAN:
				return self._skillID2
			elif playerEntity.getClass() == csdefine.CLASS_ARCHER:
				return self._skillID3
			elif playerEntity.getClass() == csdefine.CLASS_MAGE:
				return self._skillID4
		else:
			return self._skillID1

	def check( self, playerEntity, questID = 0 ):
		"""
		����Ƿ�����ȷִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QTReward.check( self, playerEntity, questID = 0 )

	def transferForClient( self, playerEntity, questID = 0 ):
		"""
		�ѵ�ǰֵת���ɿͻ�����Ҫ��������

		@return: string
		"""
		return struct.pack( "=b", self.type() ) + str( self.getSkillByClass( playerEntity ) )

# ------------------------------------------------------------>
# QTReward Solts ר�ý�������
# ------------------------------------------------------------>	
class QTRewardMoneySlots( QTRewardMoney ):
	m_type = csdefine.QUEST_REWARD_SOLTS_MONEY
	def __init__( self ,*args ):
		QTRewardMoney.__init__( self ,*args )
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		gameYield = playerEntity.wallow_getLucreRate()
		multiple = playerEntity.getQuestSlotsMultiple()
		money = self._amount * gameYield * multiple
		playerEntity.addMoney( money, csdefine.CHANGE_MONEY_QTREWARDMONEY )
		return [cschannel_msgs.GMMGR_JIN_QIAN  + str( money ) ]
	

class QTRewardExpSlots( QTRewardExp ):
	m_type = csdefine.QUEST_REWARD_SOLTS_EXP
	def __init__( self, *args ):
		QTRewardExp.__init__( self, *args )
	
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		multiple = playerEntity.getQuestSlotsMultiple()
		exp = self.calculate( playerEntity ) * multiple
		playerEntity.addExp( exp, csdefine.CHANGE_EXP_QTREWARD )
		return [cschannel_msgs.QUEST_INFO_5  + str(exp)]


class QTRewardPotentialSolts( QTRewardPotential ):
	m_type = csdefine.QUEST_REWARD_SOLTS_POTENTIAL
	def __init__( self, *args ):
		QTRewardPotential.__init__( self, *args )
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		multiple = playerEntity.getQuestSlotsMultiple()
		potential = self._potential * multiple
		playerEntity.addPotential( potential )
		return []

class QTRewardDaohengSolts( QTRewardDaoheng ):
	m_type = csdefine.QUEST_REWARD_SOLTS_DAOHENG
	def __init__( self, *args ):
		QTRewardDaoheng.__init__( self, *args )
		
	def do( self, playerEntity, questID ):
		"""
		ִ�н���

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		return type:		 �ɹ���õĽ�����Ʒ��list
		"""
		adjust_param = Const.DAOHENG_AMEND_RATE
		n = float( playerEntity.getDaoheng() ) / g_daoheng.get( playerEntity.getLevel())  # �߻�Ҫ�󣬲���nȡ��ҵ���ֵ/��ǰ�ȼ���Ӧ�ı�׼����ֵ
		rate  =  adjust_param /(math.log( ( 1 + adjust_param ), math.e ) * pow( ( 1+ adjust_param ), n ) ) 
		multiple = playerEntity.getQuestSlotsMultiple() #ȡ���ϻ��������ı���
		daoheng = rate * self._amount * multiple
		daoheng =  max( 1, daoheng )
		playerEntity.addDaoheng( daoheng, csdefine.ADD_DAOHENG_REASON_QUEST )

		return [cschannel_msgs.QUEST_INFO_54  + str( daoheng ) ]
		
# ע�������
MAP_QUEST_REWARD_TYPE( QTRewardMoney )			# amount
MAP_QUEST_REWARD_TYPE( QTRewardMoneyByTemp )
MAP_QUEST_REWARD_TYPE( QTRewardDeposit )
MAP_QUEST_REWARD_TYPE( QTRewardItems )			# itemID, amount
MAP_QUEST_REWARD_TYPE( QTRewardChooseItems )
MAP_QUEST_REWARD_TYPE( QTRewardRndItems )
MAP_QUEST_REWARD_TYPE( QTRewardExp )			# amount
MAP_QUEST_REWARD_TYPE( QTRewardPercentageExp )	# baseExp, increasePercentage, specialFlag, maxTimes
MAP_QUEST_REWARD_TYPE( QTRewardTitle )			# titleID
MAP_QUEST_REWARD_TYPE( QTRewardSkill )			# skillID
MAP_QUEST_REWARD_TYPE( QTRewardPotential )		# amount
MAP_QUEST_REWARD_TYPE( QTRewardRelationMoney )
MAP_QUEST_REWARD_TYPE( QTRewardRelationExp )
MAP_QUEST_REWARD_TYPE( QTRewardFixedRndItems )
MAP_QUEST_REWARD_TYPE( QTRewardPrestige )
MAP_QUEST_REWARD_TYPE( QTRewardPrestigeTong )
MAP_QUEST_REWARD_TYPE( QTRewardMerchantMoney )
MAP_QUEST_REWARD_TYPE( QTTongContribute )
MAP_QUEST_REWARD_TYPE( QTRewardTongBuildVal )
MAP_QUEST_REWARD_TYPE( QTRewardTongMoney )
MAP_QUEST_REWARD_TYPE( QTRewardExpFromRoleLevel )
MAP_QUEST_REWARD_TYPE( QTRewardSecondPercentExp )
MAP_QUEST_REWARD_TYPE( QTTongContributeNormal )
MAP_QUEST_REWARD_TYPE( QTRewardRoleLevelMoney )
MAP_QUEST_REWARD_TYPE( QTRewardPetExp )
MAP_QUEST_REWARD_TYPE( QTRewardIETitle )
MAP_QUEST_REWARD_TYPE( QTRewardExpFromTable )
MAP_QUEST_REWARD_TYPE( QTRewardMoneyFromTable )
MAP_QUEST_REWARD_TYPE( QTRewardRandomItemFromTable )
MAP_QUEST_REWARD_TYPE( QTRewardRelationPetExp )			#
MAP_QUEST_REWARD_TYPE( QTRewardPetExpFromRoleLevel )	#
MAP_QUEST_REWARD_TYPE( QTRewardPetSecondPercentExp )	# �뾭��ӳ�(����)
MAP_QUEST_REWARD_TYPE( QTRewardMultiExp )				# �౶���ﾭ�齱��
MAP_QUEST_REWARD_TYPE( QTRewardMultiPetExp )			# �౶���ﾭ�齱��
MAP_QUEST_REWARD_TYPE( QTRewardMultiMoney )				# �౶��Ǯ����
MAP_QUEST_REWARD_TYPE(QTRewardItemsQuality)
MAP_QUEST_REWARD_TYPE(QTRewardSpecialTongBuildVal)
MAP_QUEST_REWARD_TYPE(QTRewardFuBiItems)
MAP_QUEST_REWARD_TYPE(QTRewardChooseItems)
MAP_QUEST_REWARD_TYPE(QTRewardTongFete)
MAP_QUEST_REWARD_TYPE(QTRewardItemsFromRoleLevel)
MAP_QUEST_REWARD_TYPE( QTRewardExpDart )
MAP_QUEST_REWARD_TYPE( QTRewardTongActionVal )
MAP_QUEST_REWARD_TYPE( QTRewardCampMorale )
MAP_QUEST_REWARD_TYPE( QTRewardCampHonour )
MAP_QUEST_REWARD_TYPE( QTRewardDaoheng )
MAP_QUEST_REWARD_TYPE( QTRewardRateMoneyFromRoleLevel )
MAP_QUEST_REWARD_TYPE( QTRewardRateExpFromRoleLevel )
MAP_QUEST_REWARD_TYPE( QTRewardQuestPartCompleted )
MAP_QUEST_REWARD_TYPE( QTRewardMoneyFromQuestQuality )
MAP_QUEST_REWARD_TYPE( QTRewardExpFromQuestQuality )
MAP_QUEST_REWARD_TYPE( QTRewardTongNomalMoney )
MAP_QUEST_REWARD_TYPE( QTRewardTongExp )
MAP_QUEST_REWARD_TYPE( QTRewardItemsFromClass )
MAP_QUEST_REWARD_TYPE( QTRewardSkillFromClass )
MAP_QUEST_REWARD_TYPE( QTRewardMoneySlots )
MAP_QUEST_REWARD_TYPE( QTRewardExpSlots )
MAP_QUEST_REWARD_TYPE( QTRewardPotentialSolts )
MAP_QUEST_REWARD_TYPE( QTRewardDaohengSolts )

#
# $Log: not supported by cvs2svn $
# Revision 1.53  2008/08/22 07:15:25  songpeifang
# ������������ʱ��key������Ϊstring
#
# Revision 1.52  2008/08/22 06:28:39  songpeifang
# �����������Ľ���
#
# Revision 1.51  2008/08/20 10:41:06  zhangdengshan
# �������;���ת��Ϊ����
#
# Revision 1.50  2008/08/15 09:17:15  zhangyuxing
# ������������
#
# Revision 1.49  2008/08/09 03:07:37  zhangyuxing
# no message
#
# Revision 1.48  2008/08/09 01:51:15  wangshufeng
# ��Ʒid���͵�����STRING -> INT32,��Ӧ�������롣
#
# Revision 1.47  2008/07/30 05:53:16  zhangyuxing
# getGroupQuestDegree ����Ϊ�� getGroupCount
# getGroupQuestCount  ����Ϊ�� getSubQuestCount
#
# Revision 1.46  2008/07/28 01:10:02  zhangyuxing
# ���ӻ����齱����ʽ
#
# Revision 1.45  2008/07/01 03:07:23  zhangyuxing
# ������Ʒ���뱳������ʧ�ܵ�״̬
#
# Revision 1.44  2008/06/27 01:13:33  zhangyuxing
# no message
#
# Revision 1.43  2008/03/28 03:39:38  zhangyuxing
# �޸� �̶���������Ĳ���ʵ��
#
# Revision 1.42  2008/03/18 06:27:17  zhangyuxing
# ȥ��һ�� getItem �Ĵ������
#
# Revision 1.41  2008/01/30 05:33:55  zhangyuxing
# �̶���������������ȡֵ��Χ�� 1-100 ��Ϊ 0-1�� ������ȡ������
#
# Revision 1.40  2008/01/30 02:48:27  zhangyuxing
# ���ӣ���ӹ̶����������
#
# Revision 1.39  2008/01/29 03:11:14  phw
# method modified: QTRewardExp::calculate(), adjust calculate mode.
#
# Revision 1.38  2008/01/09 03:05:50  zhangyuxing
# �������ֽ�������
# QTRewardRelationMoney
# QTRewardRelationExp
# ��Ҫ���ڴ�������Ĺ������������飬��Ǯ��
#
# Revision 1.37  2007/12/06 09:53:08  phw
# ������û����ȷ��ȡ�������ݵ�bug
#
# Revision 1.36  2007/12/06 07:45:36  phw
# ��֪�������˻���ʲôԭ���transferForClient()�Ļ��б�ʽ��
# �����¸�Ϊ�����ַ�����ʽ��
#
# Revision 1.35  2007/12/06 01:23:47  zhangyuxing
# �ָ���֮ǰ���ͽ�����Ʒ��ʱ�� ʹ�� �б���Ϊ���ء�
#
# Revision 1.34  2007/12/05 06:58:45  phw
# �޸���transferForClient()�ķ���ֵ����
# �޸��˹̶���Ʒ����init()�����ĳ�ʼ����ʽ
#
# Revision 1.33  2007/12/04 09:30:11  fangpengjun
# zhangyuxing���һ������޸�����Ʒ�����������
#
# Revision 1.32  2007/12/04 02:59:05  zhangyuxing
# �޸�BUG����Ʒ�����ķ��ظĻ�Ϊ �ַ����б�
#
# Revision 1.31  2007/12/04 02:10:42  phw
# added: MAP_QUEST_REWARD_TYPE( QTRewardPotential )
#
# Revision 1.30  2007/11/28 03:10:15  zhangyuxing
# �޸�����Ʒ���������ļ��ķ�ʽ
#
# Revision 1.29  2007/11/26 01:47:04  zhangyuxing
# ������ �޸��˽�����Ʒ����̳й�ϵ���Լ���Ʒ��Ϊ����������б�
# ������ԭ���Ľ�����Ʒʵ��
# ԭ�еĽӿ�ʹ�÷�ʽ��û�иı�
#
# Revision 1.28  2007/11/20 06:46:32  phw
# method modified: QTRewardItem.__init__(), �������±����������
#
# Revision 1.27  2007/11/02 03:59:56  phw
# ��ԭ����__init__.py�е�ʵ��������Ϊ��ģ���Լ�������
#
# Revision 1.26  2007/06/14 09:59:20  huangyongwei
# ���������˺궨��
#
# Revision 1.25  2007/05/05 08:19:15  phw
# whrandom -> random
#
# Revision 1.24  2007/03/12 06:24:04  kebiao
# �޸��˽�����ʾ�ĸ�ʽ
#
# Revision 1.23  2007/03/12 01:35:15  kebiao
# �ı�do�ӿ���ִ���꽱���󷵻�����������Ϣ�б�
#
# Revision 1.22  2007/03/07 02:20:57  kebiao
# ����������һЩ��ƷID�߻�һʱ���ܸ���������һЩ��������˵���Ʒ���ͽ�����Ϣʱ�Ĵ�����
#
# Revision 1.21  2007/03/05 09:06:45  kebiao
# ��
# raise "item '%s' not found." % itemID
# �ĳ� �����������������(��Ϊ�ܶ�����߻���û����ȷ��ƷID)
# ERROR_MSG( "%s: item not found." % itemID )
#
# Revision 1.20  2007/02/27 00:39:03  kebiao
# ������չ����Ʒģ��
# QTRewardItemEx
#
# Revision 1.19  2007/02/26 01:26:48  kebiao
# ����������������ý���ʵ����do��ɸ��ԵĽ�������
#
# Revision 1.18  2007/02/07 07:12:20  kebiao
# ����
# QTRewardItemPacket
# QTRewardChooseItems
# QTRewardRndItems
# QTRewardPotential
#
# Revision 1.17  2006/12/21 10:15:12  phw
# ��Ʒ��ص��ڳ�ʼ��ʱ�Ͱ���ƷIDת��ΪСд
#
# Revision 1.16  2006/09/19 08:10:28  chenzheming
# no message
#
# Revision 1.15  2006/08/28 00:57:24  chenzheming
# no message
#
# Revision 1.14  2006/08/28 00:32:47  chenzheming
# no message
#
# Revision 1.13  2006/08/18 07:50:28  phw
# no message
#
# Revision 1.12  2006/08/11 02:58:36  phw
# no message
#
# Revision 1.11  2006/08/09 08:35:33  phw
# ����ģ��ItemDataList��Ϊ����items
#
# Revision 1.10  2006/08/05 08:31:55  phw
# �޸Ľӿڣ�
#     �޸����ж���Ʒ���Ե�ֱ�ӷ���Ϊʹ�ýӿڷ���
#
# Revision 1.9  2006/04/06 06:50:26  phw
# ���뽱�����ܺͼ�����Ҫ�ж�
#
# Revision 1.8  2006/04/03 07:29:20  phw
# ������Ʒ�������ȷ����
#
# Revision 1.7  2006/03/28 10:08:03  phw
# class QTRewardTitle: to class QTRewardTitle( QTReward ):
#
# Revision 1.6  2006/03/28 10:01:08  phw
# ����QTRewardTitle.transferForClient()ʹ�ò����ڵ�����
#
# Revision 1.5  2006/03/22 02:28:38  phw
# ����Ʒ���������������ʧ����־
#
# Revision 1.4  2006/03/10 05:14:44  phw
# ����transferForClient()�������ڰ��ڷ�����������ת���ɼ򵥵���client����ʾ�Ľ�������
#
# Revision 1.3  2006/03/06 09:55:56  phw
# chang QTRewardItems to QTRewardItem
#
# Revision 1.2  2006/01/24 03:34:05  phw
# no message
#
# Revision 1.1  2006/01/24 02:20:50  phw
# no message
#
#
