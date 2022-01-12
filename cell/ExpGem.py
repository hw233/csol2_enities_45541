# -*- coding: gb18030 -*-
#
# $Id: ExpGem.py,v 1.2 2008-09-02 01:53:46 wangshufeng Exp $

"""
角色经验石，15:31 2008-7-21，wsf
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


# 不同级别的玩家，代练增加的经验百分比不同，目前还用不到，以后有可能用到。
LEVEL_MAP_PERCENT	= {}


class BaseExpGem:
	def __init__( self, index ):
		self.index = index


	def updateAttr( self, attrName, value, owner = None ):
		"""
		统一更新属性值的函数
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
	角色领取经验石
	"""
	def __init__( self, index = 0 ):
		BaseExpGem.__init__( self, index )
		self.limitTime = 0
		self.timerID = 0


	def getAttrsDict( self ):
		"""
		重载基类的相关函数
		"""
		tempDict = BaseExpGem.getAttrsDict( self )
		tempDict[ "index" ] = self.getAttr( "index" )
		tempDict[ "limitTime" ] = self.getAttr( "limitTime" )
		tempDict[ "timerID" ] = self.getAttr( "timerID" )
		return tempDict


	def load( self, owner, limitTime ):
		"""
		加载宝石
		"""
		self.limitTime = limitTime
		owner.roleCommonGem.append( self )

		# 玩家物理法术攻击力上升2%
		owner.damage_min_percent += 0.02
		owner.damage_max_percent += 0.02
		owner.magic_damage_percent += 0.02
		owner.calcDamageMin()
		owner.calcDamageMax()
		owner.calcMagicDamage()
		owner.client.gem_loadComGem( self.index )	# 通知客户端
		#owner.statusMessage()


	def offload( self, owner ):
		"""
		卸载宝石
		"""
		# 玩家物理法术攻击力下降2%
		owner.damage_min_percent -= 0.02
		owner.damage_max_percent -= 0.02
		owner.magic_damage_percent -= 0.02
		owner.calcDamageMin()
		owner.calcDamageMax()
		owner.calcMagicDamage()
		owner.cancel( self.timerID )
		owner.client.gem_offload( self.index )	# 通知客户端
		owner.roleCommonGem.remove( self )
		#owner.statusMessage()


class TrainExpGem( BaseExpGem ):
	"""
	角色代练经验石
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
		给代练宝石充代练时间
		"""
		remainTime += self.remainTime
		if remainTime > csconst.GEM_PET_COMMON_VALUE_UPPER:
			return csstatus.PET_TRAIN_CHARGE_FAIL_TIME_SLOPOVER
		else:
			self.updateAttr( "remainTime", remainTime, owner )
			return csstatus.PET_TRAIN_CHARGE_SUCCESS

	def startTrain( self, trainType, owner ):
		"""
		开始代练
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
		停止代练
		"""
		if not self.isInTrain():
			return
		trainType = self.getAttr( "trainType" )
		self.updateAttr( "trainType", 0, owner )	# 设置trainType为0,表示停止代练
		self.updateAttr( "startTime", 0, owner )
		owner.statusMessage( csstatus.ROLE_TRAIN_STOP_SUCCESS, self.__cc_strTranTypes[trainType] )
		
	def isTraining( self ):
		"""
		用来判断是否正在代练
		"""
		return self.getAttr( "trainType" ) != 0


	def onRoleLevelUp( self, owner ):
		"""
		玩家升级通知
		"""
		if not self.isInTrain():
			return
		self.update( owner )			# 更新正在代练的经验石数据，通知客户端整理表现


	def update( self, owner ):
		"""
		更新代练宝石数据
		"""
		trainTime = time.time() - self.updateTime
		# 有可能出现此情况，因为updateTime是上一次服务器运行时的time.time()时间，怀疑再次启动的time.time()小于上次的updateTime
		# trainTime < 0会造成玩家代练经验为负值，此处停止玩家代练，写错误日志。18:29 2009-11-4，wsf
		if trainTime < 0:
			ERROR_MSG( "玩家( %s )代练宝石时间异常：服务器时间( %s ),上次更新时间( %s )" % ( owner.getName(), int( time.time() ), self.updateTime ) )
			self.stopTrain( owner )
			return
		percent = expGemDataMgr.getExpByLevel( owner.level )
		self.updateTime = time.time()	# 最近一次更新时间，不需要通知客户端，仅在服务器使用
		remainTime = self.remainTime - trainTime
		if remainTime < 0:
			trainTime = self.remainTime
		startTime = self.startTime
		trainType = self.trainType
		if self.trainType == csdefine.PET_TRAIN_TYPE_HARD:
			percent = percent * csconst.GEM_WORK_HARD_RATE
			remainTime = self.remainTime - 2 * trainTime
		if remainTime <= 0:				# 宝石剩余代练时间耗完
			remainTime = 0
			startTime = 0
			trainType = 0
			self.updateAttr( "startTime", startTime, owner )
			self.updateAttr( "trainType", trainType, owner )	# 如果无剩余时间，那么停止代练
			
		#maxExp = RLevelEXP.getEXPMax( owner.level )
		exp = self.exp + trainTime * percent
		if exp >= csconst.GEM_PET_COMMON_VALUE_UPPER:					#经验不能累计超过10亿
			exp = csconst.GEM_PET_COMMON_VALUE_UPPER
		self.updateAttr( "remainTime", remainTime, owner )
		self.updateAttr( "exp", exp, owner )


	def giveExp( self, owner, value ):
		"""
		玩家汲取经验
		"""
		if self.exp <= 0 or value <= 0:
			#owner.statusMessage( )	定义消息
			return
		owner.addExp( value, csdefine.CHANGE_EXP_TRAINEXPGEM )
		self.updateAttr( "exp", self.exp - value , owner )


	def isInTrain( self ):
		"""
		判断是否在代练中
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