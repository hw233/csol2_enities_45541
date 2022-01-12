# -*- coding: gb18030 -*-
#
# $Id: ExpGem.py,v 1.2 2008-09-02 01:53:46 wangshufeng Exp $

"""
��ɫ����ʯ��15:31 2008-7-21��wsf
"""
import Language
import cschannel_msgs
import ShareTexts as ST
import time
import csdefine
import csstatus
import csconst
import random
from bwdebug import *
import ECBExtend
from LevelEXP import RoleLevelEXP as RLevelEXP
from ExpGemDataMgr import expGemDataMgr
from MsgLogger import g_logger


# ��ͬ�������ң��������ӵľ���ٷֱȲ�ͬ��Ŀǰ���ò������Ժ��п����õ���
LEVEL_MAP_PERCENT	= {}


class BaseExpGem:
	def __init__( self, index ):
		self.index = index


	def updateAttr( self, attrName, value, owner = None ):
		"""
		ͳһ��������ֵ�ĺ���
		"""
		if hasattr( self, attrName ):
			setattr( self, attrName, value )
		if owner:
			owner.client.onUpdateRoleGem( self.index, attrName, value )


	# ----------------------------------------------------------------
	# mehtods for packing / unpacking
	# ----------------------------------------------------------------
	def getAttrsDict( self ) :
		return {}

	# ---------------------------------------
	def getDictFromObj( self, gem ):
		return gem.getAttrsDict()

	def createObjFromDict( self, dict ):
		gem = self.__class__()
		for attrName, value in dict.items():
			gem.updateAttr( attrName, value )
		return gem

	def isSameType( self, obj ) :
		return isinstance( obj, BaseExpGem )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getAttr( self, attrName ) :
		"""
		get attribute of the gem
		@type				attrName : str
		@param				attrName : attribute name
		@rtype						 : whichever python type
		@return						 : the attribute value you want to get
		"""
		if hasattr( self, attrName ):
			return getattr( self, attrName )
		ERROR_MSG( "attribute %s is not exist!" % attrName )


class CommonExpGem( BaseExpGem ):
	"""
	��ɫ��ȡ����ʯ
	"""
	def __init__( self, index = 0 ):
		BaseExpGem.__init__( self, index )
		self.limitTime = 0
		self.timerID = 0


	def getAttrsDict( self ):
		"""
		���ػ������غ���
		"""
		tempDict = BaseExpGem.getAttrsDict( self )
		tempDict[ "index" ] = self.getAttr( "index" )
		tempDict[ "limitTime" ] = self.getAttr( "limitTime" )
		tempDict[ "timerID" ] = self.getAttr( "timerID" )
		return tempDict


	def load( self, owner, limitTime ):
		"""
		���ر�ʯ
		"""
		self.limitTime = limitTime
		owner.roleCommonGem.append( self )

		# �������������������2%
		owner.damage_min_percent += 0.02
		owner.damage_max_percent += 0.02
		owner.magic_damage_percent += 0.02
		owner.calcDamageMin()
		owner.calcDamageMax()
		owner.calcMagicDamage()
		owner.client.gem_loadComGem( self.index )	# ֪ͨ�ͻ���
		#owner.statusMessage()


	def offload( self, owner ):
		"""
		ж�ر�ʯ
		"""
		# ����������������½�2%
		owner.damage_min_percent -= 0.02
		owner.damage_max_percent -= 0.02
		owner.magic_damage_percent -= 0.02
		owner.calcDamageMin()
		owner.calcDamageMax()
		owner.calcMagicDamage()
		owner.cancel( self.timerID )
		owner.client.gem_offload( self.index )	# ֪ͨ�ͻ���
		owner.roleCommonGem.remove( self )
		#owner.statusMessage()


class TrainExpGem( BaseExpGem ):
	"""
	��ɫ��������ʯ
	"""
	__cc_strTranTypes = {}
	__cc_strTranTypes[csdefine.GEM_WORK_NORMAL]	= cschannel_msgs.ROLE_INFO_10
	__cc_strTranTypes[csdefine.GEM_WORK_HARD]		= cschannel_msgs.ROLE_INFO_11
	def __init__( self, index = -1 ):
		BaseExpGem.__init__( self, index )
		self.trainType = 0
		self.startTime = 0
		self.remainTime = 0
		self.updateTime = 0
		self.exp = 0


	def getAttrsDict( self ):
		tempDict = BaseExpGem.getAttrsDict( self )
		tempDict[ "trainType" ] = self.getAttr( "trainType" )
		tempDict[ "startTime" ] = self.getAttr( "startTime" )
		tempDict[ "remainTime" ] = self.getAttr( "remainTime" )
		tempDict[ "updateTime" ] = self.getAttr( "updateTime" )
		tempDict[ "exp" ] = self.getAttr( "exp" )
		return tempDict

	def charge( self, remainTime, owner ):
		"""
		��������ʯ�����ʱ��
		"""
		remainTime += self.remainTime
		if remainTime > csconst.GEM_PET_COMMON_VALUE_UPPER:
			return csstatus.PET_TRAIN_CHARGE_FAIL_TIME_SLOPOVER
		else:
			self.updateAttr( "remainTime", remainTime, owner )
			return csstatus.PET_TRAIN_CHARGE_SUCCESS

	def startTrain( self, trainType, owner ):
		"""
		��ʼ����
		"""
		if self.remainTime <= 0:
			owner.statusMessage( csstatus.PET_TRAIN_FAIL_NO_TRAIN_TIME )
			return
		
		if self.isTraining():
			owner.statusMessage( csstatus.GEM_IS_TRAINING )
			return
		
		now = time.time()
		self.updateAttr( "trainType", trainType, owner )
		self.updateAttr( "startTime", now, owner )
		self.updateTime = now
		owner.statusMessage( csstatus.ROLE_START_SUCCESS, self.__cc_strTranTypes[trainType] )

		try:
			g_logger.roleTrainingsLog( owner.databaseID, owner.getName(), trainType )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def stopTrain( self, owner ):
		"""
		ֹͣ����
		"""
		if not self.isInTrain():
			return
		trainType = self.getAttr( "trainType" )
		self.updateAttr( "trainType", 0, owner )	# ����trainTypeΪ0,��ʾֹͣ����
		self.updateAttr( "startTime", 0, owner )
		owner.statusMessage( csstatus.ROLE_TRAIN_STOP_SUCCESS, self.__cc_strTranTypes[trainType] )
		
	def isTraining( self ):
		"""
		�����ж��Ƿ����ڴ���
		"""
		return self.getAttr( "trainType" ) != 0


	def onRoleLevelUp( self, owner ):
		"""
		�������֪ͨ
		"""
		if not self.isInTrain():
			return
		self.update( owner )			# �������ڴ����ľ���ʯ���ݣ�֪ͨ�ͻ����������


	def update( self, owner ):
		"""
		���´�����ʯ����
		"""
		trainTime = time.time() - self.updateTime
		# �п��ܳ��ִ��������ΪupdateTime����һ�η���������ʱ��time.time()ʱ�䣬�����ٴ�������time.time()С���ϴε�updateTime
		# trainTime < 0�������Ҵ�������Ϊ��ֵ���˴�ֹͣ��Ҵ�����д������־��18:29 2009-11-4��wsf
		if trainTime < 0:
			ERROR_MSG( "���( %s )������ʯʱ���쳣��������ʱ��( %s ),�ϴθ���ʱ��( %s )" % ( owner.getName(), int( time.time() ), self.updateTime ) )
			self.stopTrain( owner )
			return
		percent = expGemDataMgr.getExpByLevel( owner.level )
		self.updateTime = time.time()	# ���һ�θ���ʱ�䣬����Ҫ֪ͨ�ͻ��ˣ����ڷ�����ʹ��
		remainTime = self.remainTime - trainTime
		if remainTime < 0:
			trainTime = self.remainTime
		startTime = self.startTime
		trainType = self.trainType
		if self.trainType == csdefine.PET_TRAIN_TYPE_HARD:
			percent = percent * csconst.GEM_WORK_HARD_RATE
			remainTime = self.remainTime - 2 * trainTime
		if remainTime <= 0:				# ��ʯʣ�����ʱ�����
			remainTime = 0
			startTime = 0
			trainType = 0
			self.updateAttr( "startTime", startTime, owner )
			self.updateAttr( "trainType", trainType, owner )	# �����ʣ��ʱ�䣬��ôֹͣ����
			
		#maxExp = RLevelEXP.getEXPMax( owner.level )
		exp = self.exp + trainTime * percent
		if exp >= csconst.GEM_PET_COMMON_VALUE_UPPER:					#���鲻���ۼƳ���10��
			exp = csconst.GEM_PET_COMMON_VALUE_UPPER
		self.updateAttr( "remainTime", remainTime, owner )
		self.updateAttr( "exp", exp, owner )


	def giveExp( self, owner, value ):
		"""
		��Ҽ�ȡ����
		"""
		if self.exp <= 0 or value <= 0:
			#owner.statusMessage( )	������Ϣ
			return
		owner.addExp( value, csdefine.CHANGE_EXP_TRAINEXPGEM )
		self.updateAttr( "exp", self.exp - value , owner )


	def isInTrain( self ):
		"""
		�ж��Ƿ��ڴ�����
		"""
		return self.startTime > 0


# --------------------------------------------------------------------
# instance for packing
# --------------------------------------------------------------------
commonGemInstance = CommonExpGem()
trainGemInstance = TrainExpGem()

#
# $log:$
#