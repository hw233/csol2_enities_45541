# -*- coding: gb18030 -*-
#
# $Id: QuestReward.py,v 1.17 2008-08-22 06:26:29 songpeifang Exp $

"""
"""

import BigWorld
import csdefine
import items
import struct
import skills as Skill
import config.client.labels.QuestReward as lbDatas
from bwdebug import *
import cPickle

from TitleMgr import TitleMgr
titleMgr = TitleMgr.instance()

# ------------------------------------------------------------>
# Abstract class
# ------------------------------------------------------------>
class QTReward:
	m_type = csdefine.QUEST_REWARD_NONE
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		pass

	def type( self ):
		"""
		ȡ�ý�������
		"""
		return self.m_type

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return ""

	def countable( self ) :
		"""
		�ý����Ƿ�������
		"""
		return False


# ------------------------------------------------------------>
# QTRewardMoney
# ------------------------------------------------------------>
class QTRewardMoney( QTReward ):
	m_type = csdefine.QUEST_REWARD_MONEY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args
		self._multiFlag = 1

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )


# ------------------------------------------------------------>
# QTRewardMultiMoney
# ------------------------------------------------------------>
class QTRewardMultiMoney( QTRewardMoney ):
	m_type = csdefine.QUEST_REWARD_MULTI_MONEY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		argsTupple = struct.unpack( "=bib", args )
		self._amount = argsTupple[1]
		self._multiFlag = argsTupple[2]

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		if self._multiFlag > 1:
			return str( self._amount ) + " x " + str( self._multiFlag )
		else:
			return str( self._amount )


# ------------------------------------------------------------>
# QTRewardDeposit
# ------------------------------------------------------------>
class QTRewardDeposit( QTReward ):
	m_type = csdefine.QUEST_REWARD_DEPOSIT
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )


# ------------------------------------------------------------>
# QTRewardMoney
# ------------------------------------------------------------>
class QTRewardMerchantMoney( QTReward ):
	m_type = csdefine.QUEST_REWARD_MERCHANT_MONEY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self.str = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return self.str


# ------------------------------------------------------------>
# QTRewardRelationMoney
# ------------------------------------------------------------>
class QTRewardRelationMoney( QTRewardMoney ):
	m_type = csdefine.QUEST_REWARD_RELATION_MONEY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )


# ------------------------------------------------------------>
# QTRewardItems
# ------------------------------------------------------------>
class QTRewardItems( QTReward ):
	m_type = csdefine.QUEST_REWARD_ITEMS
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		l = cPickle.loads(args)

		self._items = []
		tempItem = None

		for i in l:
			item = items.instance().createDynamicItem( i[0] , i[1] )
			if i[4] != "":
				item.set( "schemeInfo", i[4] )
			if i[3]:
				item.set( "level", i[3] )
			self._items.append( item )

	def getName(self, index):
		"""
		��ȡ��Ʒ����
		"""
		return self._items[index].name()

	def getIcon(self, index):
		"""
		��ȡ��Ʒ���ͼ��
		"""
		return self._items[index].icon()

	def getDescription(self, index):
		"""
		���ؽ�����ص�����
		"""
		return self._items[index].description( BigWorld.player() )
		#return "item"

	def countable( self ) :
		"""
		�ý����Ƿ�������
		"""
		return True

	def getAmount(self, index) :
		"""
		��ȡ��Ʒ����
		"""
		return self._items[index].getAmount()


# ------------------------------------------------------------>
# QTRewardItems
# ------------------------------------------------------------>
class QTRewardItemsFromRoleLevel( QTReward ):
	m_type = csdefine.QUEST_REWARD_ITEMS_FROM_ROLE_LEVEL
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		l = cPickle.loads(args)

		self._items = []
		tempItem = None

		for i in l:
			item = items.instance().createDynamicItem( i[0] , i[1] )
			if i[2]:
				item.setBindType( ItemTypeEnum.CBT_PICKUP )
			if i[3]:
				item.set( "level", i[3] )
			self._items.append( item )

# ------------------------------------------------------------>
# QTRewardItemsQuality
# ------------------------------------------------------------>
class QTRewardItemsQuality( QTReward ):
	m_type = csdefine.QUEST_REWARD_ITEMS_QUALITY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self.str = args

	def type( self ):
		"""
		ȡ�ý�������
		"""
		return self.m_type

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return self.str

	def countable( self ) :
		"""
		�ý����Ƿ�������
		"""
		return False

# ------------------------------------------------------------>
# QTRewardChooseItems
# ------------------------------------------------------------>
class QTRewardChooseItems( QTRewardItems ):
	"""
	��ѡһ����
	"""
	m_type = csdefine.QUEST_REWARD_CHOOSE_ITEMS
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		QTRewardItems.__init__( self, args )


# ------------------------------------------------------------>
# QTRewardRndItems
# ------------------------------------------------------------>
class QTRewardRndItems( QTRewardItems ):
	"""
	�������
	"""
	m_type = csdefine.QUEST_REWARD_RANDOM_ITEMS
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		l = cPickle.loads(args)
		self._items = []
		for i in l:
			item = items.instance().createDynamicItem( i[0] , i[1] )
			self._items.append( item )
		

	def getName(self, index):
		"""
		��ȡ��Ʒ����
		"""
		return self._items[index].name()

	def getIcon(self, index):
		"""
		��ȡ��Ʒ���ͼ��
		"""
		return self._items[index].icon()

	def getDescription(self, index):
		"""
		���ؽ�����ص�����
		"""
		return self._items[index].description( BigWorld.player() )

	def countable( self ) :
		"""
		�ý����Ƿ�������
		"""
		return True


# ------------------------------------------------------------>
# QTRewardFixedRndItems
# ------------------------------------------------------------>
class QTRewardFixedRndItems( QTRewardItems ):
	"""
	�̶���Ʒ�������
	"""
	m_type = csdefine.QUEST_REWARD_FIXED_RANDOM_ITEMS
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		headLen = struct.calcsize( "=i" )
		flag = struct.unpack( "=i", args[:headLen] )[0]
		
		if flag == 0:					# ���ַ�Ϊ0��ʾ����ʾ��Ʒ��ֻ��ʾ�����������
			self.isItem = False
			self.str = args[headLen:]
		else:							# ������ʾ��Ʒ
			self.isItem = True
			l = cPickle.loads( args[headLen:] )
			self._items = []
			for i in l:
				item = items.instance().createDynamicItem( i[0] , i[1] )
				self._items.append( item )


# ------------------------------------------------------------>
# QTRewardExp
# ------------------------------------------------------------>
class QTRewardExp( QTReward ):
	m_type = csdefine.QUEST_REWARD_EXP
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args
		self._multiFlag = 1

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )

class QTRewardExpDart( QTRewardExp ):
	"""
	���ھ��齱��
	"""
	m_type = csdefine.QUEST_REWARD_EXP_TONG_DART

# ------------------------------------------------------------>
# QTRewardMultiExp
# ------------------------------------------------------------>
class QTRewardMultiExp( QTRewardExp ):
	m_type = csdefine.QUEST_REWARD_MULTI_EXP
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		argsTupple = struct.unpack( "=bib", args )
		self._amount = argsTupple[1]
		self._multiFlag = argsTupple[2]

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		if self._multiFlag > 1:
			return str( self._amount ) + " x " + str( self._multiFlag )
		else:
			return str( self._amount )


# ------------------------------------------------------------>
# QTRewardPetExp
# ------------------------------------------------------------>
class QTRewardPetExp( QTRewardExp ):
	m_type = csdefine.QUEST_REWARD_PET_EXP
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args
		self._multiFlag = 1

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )


# ------------------------------------------------------------>
# QTRewardMultiPetExp
# ------------------------------------------------------------>
class QTRewardMultiPetExp( QTRewardMultiExp ):

	m_type = csdefine.QUEST_REWARD_MULTI_PET_EXP

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return QTRewardMultiExp.getDescription( self )


# ------------------------------------------------------------>
# QTRewardRelationExp
# ------------------------------------------------------------>
class QTRewardRelationExp( QTReward ):
	m_type = csdefine.QUEST_REWARD_RELATION_EXP
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		argsTupple = struct.unpack( "=bib", args )
		self._amount = argsTupple[1]
		self._doubleExpFlag = argsTupple[2]
	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		if self._doubleExpFlag:
			return str( self._amount/2) + " x 2"
		else:
			return str( self._amount )


# ------------------------------------------------------------>
# QTRewardRelationPetExp
# ------------------------------------------------------------>
class QTRewardRelationPetExp( QTRewardRelationExp ):
	"""
	��������ﾭ�齱��
	"""
	m_type = csdefine.QUEST_REWARD_RELATION_PET_EXP

	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		QTRewardRelationExp.__init__( self, args )


# ------------------------------------------------------------>
# QTRewardPotential
# ------------------------------------------------------------>
class QTRewardPotential( QTReward ):
	m_type = csdefine.QUEST_REWARD_POTENTIAL
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )


# ------------------------------------------------------------>
# QTRewardTitle
# ------------------------------------------------------------>
class QTRewardTitle( QTReward ):
	m_type = csdefine.QUEST_REWARD_IE_TITLE
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._title = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return titleMgr.getName( self._title )


# ------------------------------------------------------------>
# QTRewardIETitle
# ------------------------------------------------------------>
class QTRewardIETitle( QTRewardTitle ):
	m_type = csdefine.QUEST_REWARD_IE_TITLE
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._title = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return titleMgr.getName( self._title )


# ------------------------------------------------------------>
# QTRewardSkill
# ------------------------------------------------------------>
class QTRewardSkill( QTReward ):
	m_type = csdefine.QUEST_REWARD_SKILL
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._skillID = int( args )
		self._skill = Skill.getSkill( self._skillID )

	def getName( self ) :
		"""
		��ȡ��������
		"""
		return self._skill.getName()

	def getIcon( self ) :
		"""
		��ȡ�������ܵ����ͼ��
		"""
		return self._skill.getIcon()

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		sk = self._skill
		return [sk.getName(), str( sk.getLevel() ) + lbDatas.LEVEL, sk.getDescription()]


# ------------------------------------------------------------>
# QTRewardMoney
# ------------------------------------------------------------>
class QTRewardPrestige( QTReward ):
	m_type = csdefine.QUEST_REWARD_PRESTIGE
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""

		l = cPickle.loads(args)

		self._prestigeID = l[0][0]
		self._amount = l[0][1]

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )


# ------------------------------------------------------------>
# QTRewardTongContribute
# ------------------------------------------------------------>
class QTTongContribute( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_CONTRIBUTE
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		argsTupple = struct.unpack( "=bib", args )
		self._amount = argsTupple[1]
		self._doubleExpFlag = argsTupple[2]

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		if self._doubleExpFlag:
			return str( self._amount/2) + " x 2"
		else:
			return str( self._amount )


# ------------------------------------------------------------>
# QTRewardTongBuildVal
# ------------------------------------------------------------>
class QTRewardTongBuildVal( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_BUILDVAL
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		argsTupple = struct.unpack( "=bib", args )
		self._amount = argsTupple[1]
		self._doubleExpFlag = argsTupple[2]

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		if self._doubleExpFlag:
			return str( self._amount/2) + " x 2"
		else:
			return str( self._amount )


# ------------------------------------------------------------>
# QTRewardTongMoney
# ------------------------------------------------------------>
class QTRewardTongMoney( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_MONEY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		argsTupple = struct.unpack( "=bib", args )
		self._amount = argsTupple[1]
		self._doubleExpFlag = argsTupple[2]

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		if self._doubleExpFlag:
			return str( self._amount/2) + " x 2"
		else:
			return str( self._amount )


# ------------------------------------------------------------>
# QTRewardExpFromRoleLevel
# ------------------------------------------------------------>
class QTRewardExpFromRoleLevel( QTReward ):
	m_type = csdefine.QUEST_REWARD_EXP_FROM_ROLE_LEVEL
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		argsTupple = struct.unpack( "=bib", args )
		self._amount = argsTupple[1]
		self._doubleExpFlag = argsTupple[2]

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		if self._doubleExpFlag:
			return str( self._amount/2) + " x 2"
		else:
			return str( self._amount )


# ------------------------------------------------------------>
# QTRewardPetExpFromRoleLevel
# ------------------------------------------------------------>
class QTRewardPetExpFromRoleLevel( QTRewardExpFromRoleLevel ):

	m_type = csdefine.QUEST_REWARD_PET_EXP_FROM_ROLE_LEVEL

	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		QTRewardExpFromRoleLevel.__init__( self, args )

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return QTRewardExpFromRoleLevel.getDescription( self )


# ------------------------------------------------------------>
# QTRewardRoleLevelMoney
# ------------------------------------------------------------>
class QTRewardRoleLevelMoney( QTReward ):
	m_type = csdefine.QUEST_REWARD_ROLE_LEVEL_MONEY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		argsTupple = struct.unpack( "=bib", args )
		self._amount = argsTupple[1]
		self._doubleExpFlag = argsTupple[2]

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		if self._doubleExpFlag:
			return str( self._amount/2) + " x 2"
		else:
			return str( self._amount )


# ------------------------------------------------------------>
# QTRewardSecondExp �뾭��ӳ�
# ------------------------------------------------------------>
class QTRewardSecondPercentExp( QTReward ):
	m_type = csdefine.QUEST_REWARD_EXP_SECOND_PERCENT
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )


# ------------------------------------------------------------>
# QTRewardPetSecondPercentExp �뾭��ӳ�
# ------------------------------------------------------------>
class QTRewardPetSecondPercentExp( QTRewardSecondPercentExp ):

	m_type = csdefine.QUEST_REWARD_PET_EXP_SECOND_PERCENT

	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		QTRewardSecondPercentExp.__init__( self, args )

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return QTRewardSecondPercentExp.getDescription( self )


# ------------------------------------------------------------>
# QTTongContributeNormal
# ------------------------------------------------------------>
class QTTongContributeNormal( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_CONTRIBUTE_NORMAL
	def __init__( self ,args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )


# ------------------------------------------------------------>
# QTRewardRandomItemFromTable
# ------------------------------------------------------------>
class QTRewardRandomItemFromTable( QTRewardItems ):
	"""
	�����Ʒ��������ȡ��
	"""
	m_type = csdefine.QUEST_REWARD_RANDOM_ITEM_FROM_TABLE
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self.str = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return self.str


class QTRewardSpecialTongBuildVal( QTRewardTongBuildVal ):
	m_type = csdefine.QUEST_REWARD_SPECIAL_TONG_BUILDVAL
	def __init__( self, args ):
		"""
		"""
		QTRewardTongBuildVal.__init__( self, args )


class QTRewardFuBiItems( QTRewardItems ):
	m_type = csdefine.QUEST_REWARD_FUBI_ITEMS
	def __init__( self, args ):
		"""
		"""
		QTRewardItems.__init__( self, args )


class QTRewardChooseItemsAndBind( QTRewardChooseItems ):
	m_type = csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND
	def __init__( self, args ):
		"""
		"""
		QTRewardItems.__init__( self, args )


# ------------------------------------------------------------>
# QTRewardTongFete
# ------------------------------------------------------------>
class QTRewardTongFete( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_FETE
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		QTReward.__init__( self, args )

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return self.str1

class QTRewardTongActionVal( QTReward ):
	m_type = csdefine.QUEST_REWARD_TONG_ACTIONVAL
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		argsTupple = struct.unpack( "=bib", args )
		self._amount = argsTupple[1]
		self._doubleExpFlag = argsTupple[2]

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		if self._doubleExpFlag:
			return str( self._amount/2) + " x 2"
		else:
			return str( self._amount )
			
# ------------------------------------------------------------>
# QTRewardCampMorale
# ------------------------------------------------------------>
class QTRewardCampMorale( QTReward ):
	"""
	��Ӫʿ��
	"""
	m_type = csdefine.QUEST_REWARD_CAMP_MORALE
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )

# ------------------------------------------------------------>
# QTRewardCampHonour
# ------------------------------------------------------------>
class QTRewardCampHonour( QTReward ):
	"""
	��Ӫ����
	"""
	m_type = csdefine.QUEST_REWARD_CAMP_HONOUR
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )
	
# ------------------------------------------------------------>
# QTRewardDaoheng ������н���
# ------------------------------------------------------------>			
class QTRewardDaoheng( QTReward ):
	m_type = csdefine.QUEST_REWARD_DAOHENG
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )

#-------------------------------------------------------------------
# QTRewardQuestPartCompleted
#-------------------------------------------------------------------
class QTRewardQuestPartCompleted( QTReward ):
	"""
	���һ��������Ŀ��Ҫ���Ľ���
	"""
	m_type = csdefine.QUEST_REWARD_RATE_QUEST_PART_COMPLETED
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self.sonRewards = {}
		headLen = struct.calcsize( "=i" )
		lenStartIndex = 0
		while( lenStartIndex < len( args ) ):
			lenEndIndex = lenStartIndex + headLen
			nodeLen = struct.unpack( "=i", args[ lenStartIndex : lenEndIndex ] )[0]
			nodeStream = args[ lenEndIndex : lenEndIndex + nodeLen ]
			self._createReward( nodeStream )
			lenStartIndex = lenEndIndex + nodeLen
	
	def _createReward( self, stream ):
		"""
		�����������д����ӽ���
		"""
		headLen = struct.calcsize( "=i" )
		taskNum = struct.unpack( "=i", stream[:headLen] )[0]
		instance = createByStream( stream[headLen:] )
		if not self.sonRewards.has_key( taskNum ):
			self.sonRewards[ taskNum ] = [ instance ]
		else:
			self.sonRewards[ taskNum ].append( instance )

#---------------------------------------------------------------
#QTRewardRateMoneyFromRoleLevel
#---------------------------------------------------------------
class QTRewardRateMoneyFromRoleLevel( QTReward ):
	"""
	��Ӫ���������ҵȼ���һ�����ʻ�ý�Ǯ����
	"""
	m_type = csdefine.QUEST_REWARD_RATE_MONEY_FROM_ROLE_LEVEL
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )

#---------------------------------------------------------------
#QTRewardRateMoneyFromRoleLevel
#---------------------------------------------------------------
class QTRewardRateExpFromRoleLevel( QTReward ):
	"""
	��Ӫ���������ҵȼ���һ�����ʻ�þ��齱��
	"""
	m_type = csdefine.QUEST_REWARD_RATE_EXP_FROM_ROLE_LEVEL
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )
		
#---------------------------------------------------------------
#QTRewardMoneyFromQuestQuality
#---------------------------------------------------------------
class QTRewardMoneyFromQuestQuality( QTRewardMoney ):
	"""
	���������������Ʒ�ʸ�����Ӧ��Ǯ����
	"""
	m_type = csdefine.QUEST_REWARD_MONEY_FROM_REWARD_QUEST_QUALITY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )
		
#---------------------------------------------------------------
#QTRewardExpFromQuestQuality
#---------------------------------------------------------------
class QTRewardExpFromQuestQuality( QTRewardExp ):
	"""
	���������������Ʒ�ʸ�����Ӧ���齱��
	"""
	m_type = csdefine.QUEST_REWARD_EXP_FROM_REWARD_QUEST_QUALITY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )

#---------------------------------------------------------------
#QTRewardRateMoneyFromRoleLevel
#---------------------------------------------------------------
class QTRewardTongNomalMoney( QTReward ):
	"""
	����Ǯ����
	"""
	m_type = csdefine.QUEST_REWARD_TONG_NOMAL_MONEY
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )

#---------------------------------------------------------------
#QTRewardTongExp
#---------------------------------------------------------------
class QTRewardTongExp( QTReward ):
	"""
	��ᾭ�齱��
	"""
	m_type = csdefine.QUEST_REWARD_TONG_EXP
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		self._amount = args

	def getDescription( self ):
		"""
		���ؽ�����ص�����
		"""
		return str( self._amount )
		
# ------------------------------------------------------------>
# QTRewardItemsFromClass
# ------------------------------------------------------------>
class QTRewardItemsFromClass( QTRewardItems ):
	m_type = csdefine.QUEST_REWARD_ITEMS_FROM_CLASS
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		QTRewardItems.__init__( self, args )
		
# ------------------------------------------------------------>
# QTRewardSkillFromClass
# ------------------------------------------------------------>
class QTRewardSkillFromClass( QTRewardSkill ):
	m_type = csdefine.QUEST_REWARD_SKILL_FROM_CLASS
	def __init__( self, args ):
		"""
		��ʼ��,������ʽ�Լ�����
		"""
		QTRewardSkill.__init__( self, args )

# ------------------------------------------------------------>
# QTReward Solts ר�ý�������
# ------------------------------------------------------------>	
class QTRewardMoneySlots( QTRewardMoney ):
	m_type = csdefine.QUEST_REWARD_SOLTS_MONEY
	def __init__( self ,args ):
		QTRewardMoney.__init__( self ,args )

class QTRewardExpSlots( QTRewardExp ):
	m_type = csdefine.QUEST_REWARD_SOLTS_EXP
	def __init__( self, args ):
		QTRewardExp.__init__( self, args )

class QTRewardPotentialSolts( QTRewardPotential ):
	m_type = csdefine.QUEST_REWARD_SOLTS_POTENTIAL
	def __init__( self, args ):
		QTRewardPotential.__init__( self, args )
		
class QTRewardDaohengSolts( QTRewardDaoheng ):
	m_type = csdefine.QUEST_REWARD_SOLTS_DAOHENG
	def __init__( self, args ):
		QTRewardDaoheng.__init__( self, args )
		
#---------------------------------------------------------------------
G_MAP_TYPE2CLASS = {
						csdefine.QUEST_REWARD_EXP		 				: QTRewardExp,			# ��������
						csdefine.QUEST_REWARD_ITEMS	 					: QTRewardItems,		# ������Ʒ
						csdefine.QUEST_REWARD_MONEY						: QTRewardMoney,		# ������Ǯ
						csdefine.QUEST_REWARD_TITLE						: QTRewardTitle,		# �����ƺ�
						csdefine.QUEST_REWARD_IE_TITLE					: QTRewardIETitle,		# �����ƺ�
						csdefine.QUEST_REWARD_SKILL						: QTRewardSkill,		# ��������
						csdefine.QUEST_REWARD_CHOOSE_ITEMS				: QTRewardChooseItems,	# ��ѡһ����
						csdefine.QUEST_REWARD_RANDOM_ITEMS				: QTRewardRndItems,		# �������
						csdefine.QUEST_REWARD_POTENTIAL					: QTRewardPotential,	# Ǳ�ܵ㽱��
						csdefine.QUEST_REWARD_PRESTIGE					: QTRewardPrestige,
						csdefine.QUEST_REWARD_FIXED_RANDOM_ITEMS		: QTRewardFixedRndItems,
						csdefine.QUEST_REWARD_RELATION_EXP				: QTRewardRelationExp,
						csdefine.QUEST_REWARD_MERCHANT_MONEY			: QTRewardMerchantMoney,
						csdefine.QUEST_REWARD_TONG_CONTRIBUTE			: QTTongContribute,
						csdefine.QUEST_REWARD_TONG_BUILDVAL				: QTRewardTongBuildVal,
						csdefine.QUEST_REWARD_TONG_MONEY				: QTRewardTongMoney,
						csdefine.QUEST_REWARD_EXP_FROM_ROLE_LEVEL		: QTRewardExpFromRoleLevel,
						csdefine.QUEST_REWARD_EXP_SECOND_PERCENT		: QTRewardSecondPercentExp,
						csdefine.QUEST_REWARD_TONG_CONTRIBUTE_NORMAL	: QTTongContributeNormal,
						csdefine.QUEST_REWARD_ROLE_LEVEL_MONEY			: QTRewardRoleLevelMoney,
						csdefine.QUEST_REWARD_PET_EXP					: QTRewardPetExp,
						csdefine.QUEST_REWARD_RELATION_PET_EXP			: QTRewardRelationPetExp,
						csdefine.QUEST_REWARD_PET_EXP_FROM_ROLE_LEVEL	: QTRewardPetExpFromRoleLevel,
						csdefine.QUEST_REWARD_PET_EXP_SECOND_PERCENT	: QTRewardPetSecondPercentExp,
						csdefine.QUEST_REWARD_RANDOM_ITEM_FROM_TABLE	: QTRewardRandomItemFromTable,
						csdefine.QUEST_REWARD_DEPOSIT					: QTRewardDeposit,
						csdefine.QUEST_REWARD_MULTI_EXP					: QTRewardMultiExp,
						csdefine.QUEST_REWARD_MULTI_PET_EXP				: QTRewardMultiPetExp,
						csdefine.QUEST_REWARD_MULTI_MONEY				: QTRewardMultiMoney,
						csdefine.QUEST_REWARD_ITEMS_QUALITY				: QTRewardItemsQuality,
						csdefine.QUEST_REWARD_SPECIAL_TONG_BUILDVAL		: QTRewardSpecialTongBuildVal,
						csdefine.QUEST_REWARD_FUBI_ITEMS				: QTRewardFuBiItems,
						csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND		: QTRewardChooseItemsAndBind,
						csdefine.QUEST_REWARD_TONG_FETE					: QTRewardTongFete,
						csdefine.QUEST_REWARD_ITEMS_FROM_ROLE_LEVEL		: QTRewardItemsFromRoleLevel,
						csdefine.QUEST_REWARD_EXP_TONG_DART				: QTRewardExpDart,	# ���ھ��齱��
						csdefine.QUEST_REWARD_TONG_ACTIONVAL			: QTRewardTongActionVal,	# ����ж�������
						csdefine.QUEST_REWARD_DAOHENG					: QTRewardDaoheng,	# ���н���
						csdefine.QUEST_REWARD_CAMP_MORALE				: QTRewardCampMorale,
						csdefine.QUEST_REWARD_CAMP_HONOUR				: QTRewardCampHonour,
						csdefine.QUEST_REWARD_RATE_QUEST_PART_COMPLETED	: QTRewardQuestPartCompleted,
						csdefine.QUEST_REWARD_RATE_MONEY_FROM_ROLE_LEVEL: QTRewardRateMoneyFromRoleLevel,
						csdefine.QUEST_REWARD_RATE_EXP_FROM_ROLE_LEVEL	: QTRewardRateExpFromRoleLevel,
						csdefine.QUEST_REWARD_MONEY_FROM_REWARD_QUEST_QUALITY	: QTRewardMoneyFromQuestQuality,	#���������Ǯ����
						csdefine.QUEST_REWARD_EXP_FROM_REWARD_QUEST_QUALITY	: QTRewardExpFromQuestQuality,	#���������齱��
						csdefine.QUEST_REWARD_TONG_NOMAL_MONEY			: QTRewardTongNomalMoney,	# ����Ǯ����
						csdefine.QUEST_REWARD_TONG_EXP					: QTRewardTongExp,			# ��ᾭ�齱��
						csdefine.QUEST_REWARD_ITEMS_FROM_CLASS			: QTRewardItemsFromClass,	# �������ְҵ���費ͬ��Ʒ����
						csdefine.QUEST_REWARD_SKILL_FROM_CLASS			: QTRewardSkillFromClass,	# �������ְҵ������ͬ����
						csdefine.QUEST_REWARD_SOLTS_MONEY				: QTRewardMoneySlots,		# �����ϻ�����������������Ǯ
						csdefine.QUEST_REWARD_SOLTS_EXP					: QTRewardExpSlots,			# �����ϻ�������������������
						csdefine.QUEST_REWARD_SOLTS_POTENTIAL			: QTRewardPotentialSolts,	# �����ϻ���������������Ǳ��ֵ
						csdefine.QUEST_REWARD_SOLTS_DAOHENG				: QTRewardDaohengSolts,		# �����ϻ�������������������ֵ
					}

TYPE_REWARDS_1 = [ csdefine.QUEST_REWARD_ITEMS,
					csdefine.QUEST_REWARD_ITEMS_QUALITY,
					csdefine.QUEST_REWARD_CHOOSE_ITEMS,
					csdefine.QUEST_REWARD_RANDOM_ITEMS,
					csdefine.QUEST_REWARD_SKILL,
					csdefine.QUEST_REWARD_FIXED_RANDOM_ITEMS,
					csdefine.QUEST_REWARD_MERCHANT_MONEY,
					csdefine.QUEST_REWARD_RANDOM_ITEM_FROM_TABLE,
					csdefine.QUEST_REWARD_PRESTIGE,
					csdefine.QUEST_REWARD_FUBI_ITEMS,
					csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND,
					csdefine.QUEST_REWARD_TONG_FETE,
					csdefine.QUEST_REWARD_ITEMS_FROM_ROLE_LEVEL,
					csdefine.QUEST_REWARD_RATE_QUEST_PART_COMPLETED,
					csdefine.QUEST_REWARD_ITEMS_FROM_CLASS,
					csdefine.QUEST_REWARD_SKILL_FROM_CLASS,
				]

TYPE_REWARDS_2 = [ csdefine.QUEST_REWARD_RELATION_EXP,
					csdefine.QUEST_REWARD_RELATION_PET_EXP,
					csdefine.QUEST_REWARD_TONG_CONTRIBUTE,
					csdefine.QUEST_REWARD_TONG_BUILDVAL,
					csdefine.QUEST_REWARD_TONG_MONEY,
					csdefine.QUEST_REWARD_EXP_FROM_ROLE_LEVEL,
					csdefine.QUEST_REWARD_PET_EXP_FROM_ROLE_LEVEL,
					csdefine.QUEST_REWARD_ROLE_LEVEL_MONEY,
					csdefine.QUEST_REWARD_MULTI_EXP,
					csdefine.QUEST_REWARD_MULTI_PET_EXP,
					csdefine.QUEST_REWARD_MULTI_MONEY,
					csdefine.QUEST_REWARD_SPECIAL_TONG_BUILDVAL,
					csdefine.QUEST_REWARD_TONG_ACTIONVAL
				]


def createByStream( stream ):
	"""
	ͨ��һ���ַ�������������

	@return: instance of QTReward
	@rtype:  QTReward
	"""
	head = "=b"
	headLen = struct.calcsize( "=b" )
	type = struct.unpack( head, stream[:headLen] )[0]

	try:
		classType = G_MAP_TYPE2CLASS[type]
	except KeyError, errstr:
		ERROR_MSG( errstr )
		return None
	if type in TYPE_REWARDS_1:
		c = classType( stream[headLen:] )
	elif type in TYPE_REWARDS_2:
		c = classType( stream )
	else:
		c = classType( struct.unpack( "=bi", stream )[1] )
	return c


# --------------------------------------------------------------------
#
# $Log: not supported by cvs2svn $
# Revision 1.16  2008/08/15 09:20:02  zhangyuxing
# ������������
#
# Revision 1.15  2008/07/19 01:56:26  wangshufeng
# �ƺ�ϵͳ��ص���
#
# Revision 1.14  2008/01/30 02:53:34  zhangyuxing
# no message
#
# Revision 1.13  2007/12/29 02:20:14  phw
# method modified: QTRewardPotential::__init__(), self._potential -> self._amount
#
# Revision 1.12  2007/12/04 09:29:29  fangpengjun
# zhangyuxing���һ������޸�����Ʒ�����������
#
# Revision 1.11  2007/11/26 01:51:12  zhangyuxing
# �޸ģ� ��QTRewardItem ��Ϊ�� QTRewardItems, ͬʱ��������ݽṹ��
# ���ֺͷ�����һ�£���ʹ����Ʒ�б�
# ���⣬����������������Ʒ���ݣ�����ͽ����ʽҲ�����޸�
#
# Revision 1.10  2007/06/14 10:32:35  huangyongwei
# ������ȫ�ֺ궨��
#
# Revision 1.9  2007/02/07 07:15:47  kebiao
# ���·�ʽ�޸��˽�����Ʒ����
#
# Revision 1.8  2007/01/08 03:46:25  huangyongwei
# return "icons/%s.dds" % self._item.query( "icon" )
# --->
# return self._item.icon()
#
# ����Ʒͼ�������·���ŵ���Ʒ����,�����õ��ĵط���Ҫ����
#
# Revision 1.7  2006/12/29 07:13:50  huangyongwei
# 1��TitleReward �� SkillReward ���Ǽ̳л���
# 2���ڸ��ֽ���ʵ��������˽�������Ľӿ�
#
# Revision 1.6  2006/08/09 08:31:33  phw
# ����ģ��ItemDataList��Ϊ����items
#
# Revision 1.5  2006/08/05 08:16:05  phw
# �޸Ľӿ�:
#     QTRewardItems::__init__()
#     �޸����ж���Ʒ���Ե�ֱ�ӷ���Ϊʹ�ýӿڷ���
#
# Revision 1.4  2006/04/06 06:50:00  phw
# ���뽱������
#
# Revision 1.3  2006/04/03 07:38:36  phw
# ����ʹ�ò����ڵı�����
#
# Revision 1.2  2006/04/03 07:28:39  phw
# ����������Ʒ��������������ȷ����
#
# Revision 1.1  2006/03/14 09:27:21  phw
# ���ʹӷ���������������������
#
# --------------------------------------------------------------------