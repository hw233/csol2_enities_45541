# -*- coding: gb18030 -*-
#
# $Id: ExpGem.py,v 1.1 2008-08-01 11:17:43 wangshufeng Exp $

"""
角色经验石，15:31 2008-7-21，wsf
"""

import time
import csdefine
import csstatus
import csconst
import random
from bwdebug import *
import event.EventCenter as ECenter
import BigWorld

# 不同级别的玩家，代练增加的经验百分比不同，目前还用不到，以后有可能用到。
LEVEL_MAP_PERCENT	= {}

TRAIN_UPDATE_TIME = 5			# 每5分钟向服务器请求更新数据


class BaseExpGem:
	def __init__( self ):
		pass


	# ----------------------------------------------------------------
	# update or query attribute methods
	# ----------------------------------------------------------------
	def onUpdateAttr( self, attrName, value ) :
		"""
		it will be called when an attribute is updated by server
		@type				attrName : str
		@param				attrName : attribute name
		@type				value	 : all python type
		@param				value	 : attribute value
		@return						 : None
		"""
		if hasattr( self, attrName ):
			oldValue = getattr( self, attrName )
			setattr( self, attrName, value )
		notifier = getattr( self, "set_" + attrName, None )
		if notifier is not None:
			notifier( oldValue )


	# ----------------------------------------------------------------
	# packle / unpackle methods
	# ----------------------------------------------------------------
	def getDictFromObj( self, obj ):
		return {}

	def createObjFromDict( self, dict ):
		gem = self.__class__()
		for attrName, value in dict.items():
			gem.onUpdateAttr( attrName, value )
		return gem

	def isSameType( self, gem ) :
		return isinstance( gem, BaseExpGem )


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
		return getattr( self, attrName )


class CommonExpGem( BaseExpGem ):
	"""
	角色领取经验石
	"""
	def __init__( self ):
		BaseExpGem.__init__( self )
		self.index = 0
		self.limitTime = 0


	def set_index( self, oldValue ):
		"""
		玩家租用经验石后，此数据会更新，此数据有更新时通知界面且输出系统提示：成功租用。
		"""
		#BigWorld.player().statusMessge()
	#	DEBUG_MSG( "---->>>value,oldValue", self.index, oldValue )
		pass

#	def set_limitTime( self, oldValue ):
#		"""
#		"""
#		DEBUG_MSG( "---->>>limitTime,oldValue", self.limitTime, oldValue )
#		ECenter.fireEvent( "EVT_ON_COMMON_GEM_LIMILTED", self.index, self.limitTime )


class TrainExpGem( BaseExpGem ):
	"""
	角色代练经验石
	"""
	def __init__( self ):
		BaseExpGem.__init__( self )
		self.index = -1
		self.trainType = 0
		self.remainTime = 0
		self.startTime = 0
		self.exp = 0

		self.CBID = 0


	def startUpdateTimer( self ):
		"""
		开始要求服务器更新的timer
		"""
		self.stopUpdateTimer()
		self.requestUpdate()


	def stopUpdateTimer( self ):
		"""
		停止更新timer
		"""
		BigWorld.cancelCallback( self.CBID )


	def requestUpdate( self ):
		"""
		请求服务器更新
		"""
		BigWorld.player().cell.gem_updateTrain()
		self.CBID = BigWorld.callback( TRAIN_UPDATE_TIME, self.requestUpdate )


	def set_trainType( self, oldValue ):
		"""
		when the train type is changed by server it will be called
		"""
		if self.trainType > 0:
			self.startUpdateTimer()
		else:
			self.stopUpdateTimer()	# 如果结束代练，那么停止timer
		ECenter.fireEvent( "EVT_ON_PLAYER_TRAIN_TYPE_CHANGED", self.trainType )


	def set_remainTime( self, oldValue ):
		"""
		when the remanentTime is changed by server it will be called
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_REMAIN_TRAIN_TIME_CHANGED", self.remainTime )
#		ECenter.fireEvent( "EVT_ON_PLAYER_REMAIN_TRAIN_POINT_CHANGED", self.remanentPoints )


	def set_exp( self, oldValue ) :
		"""
		when the exp is changed by server it will be called
		"""
		if oldValue == self.exp : return
		ECenter.fireEvent( "EVT_ON_PLAYER_TRAIN_EXP_CHANGED", self.exp )


	def inTraining( self ):
		"""
		代练宝石是否在代练状态
		"""
		return self.getAttr( "trainType" ) != csdefine.PET_TRAIN_TYPE_NONE

# --------------------------------------------------------------------
# instance for packing
# --------------------------------------------------------------------
commonGemInstance = CommonExpGem()
trainGemInstance = TrainExpGem()

#
# $log:v$
#