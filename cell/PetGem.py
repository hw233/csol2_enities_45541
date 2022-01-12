# -*- coding: gb18030 -*-
#
# $Id: PetGem.py,v 1.8 2008-09-02 01:53:46 wangshufeng Exp $

"""
implement gem used by pet

2007/11/14: writen by huangyongwei
"""
import Language
import time
import random
import inspect
import csdefine
import csstatus
import csconst
import ECBExtend
import ShareTexts
from bwdebug import *
from PetFormulas import formulas
from LevelEXP import RoleLevelEXP as RLevelEXP
from ExpGemDataMgr import expGemDataMgr


class BaseGem :
	def __init__( self, index ) :
		self.__index = index


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def updateAttr( self, attrName, value, owner = None ) :
		for cs in inspect.getmro( self.__class__ ) :
			fullName = "_%s__%s" % ( cs.__name__, attrName )
			if not hasattr( self, fullName ) : continue
			setattr( self, fullName, value )
			break
		if owner is not None :
			owner.client.ptn_onUpdateGemAttr( self.__index, attrName, value )


	# ----------------------------------------------------------------
	# mehtods for packing / unpacking
	# ----------------------------------------------------------------
	def getAttrsDict( self ) :
		return { "index": self.__index }

	# ---------------------------------------
	def getDictFromObj( self, gem ) :
		return gem.getAttrsDict()

	def createObjFromDict( self, dict ) :
		gem = self.__class__()
		for attrName, value in dict.items() :
			gem.updateAttr( attrName, value )
		return gem

	def isSameType( self, obj ) :
		return isinstance( obj, BaseGem )


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
		for cs in inspect.getmro( self.__class__ ) :
			fullName = "_%s__%s" % ( cs.__name__, attrName )
			if not hasattr( self, fullName ) : continue
			return getattr( self, fullName )
		ERROR_MSG( "attribute __%s is not exist!" % attrName )
		return getattr( self, fullName )

	def getIndex( self ) :
		"""
		get the gem's index in the role's gems bag, this attribute value is set when a gem is created by role
		@rtype					: UINT8
		@return					: the gem's index
		"""
		return self.__index


# --------------------------------------------------------------------
# implement common gem class
# --------------------------------------------------------------------
class CommonGem( BaseGem ) :
	def __init__( self, index = 0 ) :
		BaseGem.__init__( self, index )
		self.__limitTime = 0
		self.__timerID = 0

	# ----------------------------------------------------------------
	# mehtods for packing / unpacking
	# ----------------------------------------------------------------
	def getAttrsDict( self ) :
		dict = BaseGem.getAttrsDict( self )
		#dict["index"] = self.getAttr( "index" )
		dict["limitTime"] = self.getAttr( "limitTime" )
		dict["timerID"] = self.getAttr( "timerID" )
		return dict


	def setTimerID( self, timerID ):
		"""
		设置宝石的timerID
		"""
		self.__timerID = timerID


	def getTimerID( self ):
		"""
		设置宝石的timerID
		"""
		return self.__timerID


	def load( self, owner, limitTime ):
		"""
		装载宝石，可以在此做一些事情
		"""
		self.__limitTime = limitTime	# 此数据仅在server用到
		owner.client.ptn_loadComGem( self.getIndex() )

	def offload( self, owner ):
		"""
		卸下宝石
		"""
		self.__timerID = 0
		owner.client.ptn_offloadComGem( self.getIndex() )	# 通知客户端


# --------------------------------------------------------------------
# implement train gem class
# --------------------------------------------------------------------
class TrainGem( BaseGem ) :
	__cc_strTranTypes = {}
	__cc_strTranTypes[csdefine.PET_TRAIN_TYPE_COMMON]	= ShareTexts.PET_TRAIN_TYPE_COMMON
	__cc_strTranTypes[csdefine.PET_TRAIN_TYPE_HARD]		= ShareTexts.PET_TRAIN_TYPE_HARD

	def __init__( self ) :
		BaseGem.__init__( self, -1 )
		self.__trainType = csdefine.PET_TRAIN_TYPE_NONE
		self.__startTime = 0
		self.__remainTime = 0
		self.__updateTime = 0
		self.__exp = 0


	# ----------------------------------------------------------------
	# mehtods for packing / unpacking
	# ----------------------------------------------------------------
	def getAttrsDict( self ) :
		dict = BaseGem.getAttrsDict( self )
		dict["trainType"] = self.__trainType
		dict["startTime"] = self.__startTime
		dict["remainTime"] = self.__remainTime
		dict["updateTime"] = self.__updateTime
		dict["exp"] = self.__exp
		return dict


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __inTraining( self ) :
		return self.getAttr( "trainType" ) != csdefine.PET_TRAIN_TYPE_NONE


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getEXP( self, owner ) :
		"""
		get exp stores in the gem
		@type				owner : BigWorld.Entity
		@param				owner : entity of the role the gem belong to
		@rtype					  : INT32
		@return					  : exp value stores in the gem
		"""
		#self.flush( owner )
		return self.__exp


	# -------------------------------------------------
	def charge( self, remainTime, owner ) :
		"""
		给代练宝石充代练时间
		"""
		remainTime += self.__remainTime
		if remainTime > csconst.GEM_PET_COMMON_VALUE_UPPER:
			return csstatus.PET_TRAIN_CHARGE_FAIL_TIME_SLOPOVER
		self.updateAttr( "remainTime", remainTime, owner )
		return csstatus.PET_TRAIN_CHARGE_SUCCESS


	def startTrain( self, trainType, owner ) :
		"""
		start auto training
		@type			trainType : MACRO DEFINATION
		@param			trainType : common train or hard train defined in csdefine.py
		@type			owner	  : BigWorld.Entity
		@param			owner	  : entity of the role the gem belong to
		@return					  : None
		"""
		#if not self.isActivated() :
		#	HACK_MSG( "player %i try to charge train gem in not activated status!" )
		#elif self.__inTraining() :
		#	owner.statusMessage( csstatus.PET_TRAIN_FAIL_IN_TRIAN )
		#elif trainType != csdefine.PET_TRAIN_TYPE_COMMON and \
		#	trainType != csdefine.PET_TRAIN_TYPE_HARD :
		#		ERROR_MSG( "error train type!" )
		if self.__remainTime <= 0:
			owner.statusMessage( csstatus.PET_TRAIN_FAIL_NO_TRAIN_TIME )
		else :
			now = time.time()
			self.__updateTime = now
			self.updateAttr( "trainType", trainType, owner )
			self.updateAttr( "startTime", now, owner )
			owner.statusMessage( csstatus.PET_TRAIN_START_SUCCESS, self.__cc_strTranTypes[trainType] )


	def stopTrain( self, owner ) :
		"""
		stop training
		@type				owner : BigWorld.Entity
		@param				owner : entity of the role the gem belong to
		@return					  : None
		"""
		if not self.__inTraining() :
			owner.statusMessage( csstatus.PET_TRAIN_STOP_FAIL_NOT_IN_TRAIN )
			return
		self.flush( owner )
		trainType = self.getAttr( "trainType" )
		self.updateAttr( "trainType", csdefine.PET_TRAIN_TYPE_NONE, owner )
		self.updateAttr( "startTime", 0, owner )
		owner.statusMessage( csstatus.PET_TRAIN_STOP_SUCCESS, self.__cc_strTranTypes[trainType] )


	def subtractEXP( self, value, owner ) :
		"""
		subtract EXP, it is called to feed pet with exp
		@type				value : INT32
		@param					  : exp value
		@type				owner : BigWorld.Entity
		@param				owner : entity of the role the gem belong to
		@return					  : None
		"""
		self.updateAttr( "exp", self.__exp - value, owner )


	def onRoleLevelUp( self, owner ):
		"""
		玩家升级通知
		"""
		if self.__remainTime <= 0:
			#debug，不在代练状态
			return

		if self.__trainType == csdefine.PET_TRAIN_TYPE_NONE:	# 不在代练状态
			return

		self.flush( owner )			# 更新正在代练的经验石数据，通知客户端整理表现


	def flush( self, owner ):
		"""
		更新代练宝石数据
		"""
		percent = expGemDataMgr.getExpByLevel( owner.level )
		trainTime = time.time() - self.__updateTime
		self.__updateTime = time.time()	# 最近一次更新时间，不需要通知客户端，仅在服务器使用
		remainTime = self.__remainTime - trainTime
		if remainTime < 0:
			trainTime = self.__remainTime
		startTime = self.__startTime
		trainType = self.__trainType
		if self.__trainType == csdefine.PET_TRAIN_TYPE_HARD:
			percent = percent * csconst.GEM_WORK_HARD_RATE
			remainTime = self.__remainTime - 2 * trainTime
		if self.isInTrain() and remainTime <= 0:				# 宝石剩余代练时间耗完
			remainTime = 0
			startTime = 0
			trainType = 0
			self.updateAttr( "startTime", startTime, owner )
			self.updateAttr( "trainType", trainType, owner )	# 如果无剩余时间，那么停止代练

		#maxExp = RLevelEXP.getEXPMax( owner.level )
		exp = int( self.__exp + trainTime * percent )
		if exp >= csconst.GEM_PET_COMMON_VALUE_UPPER:					#经验不能累计超过10亿
			exp = csconst.GEM_PET_COMMON_VALUE_UPPER
		self.updateAttr( "remainTime", remainTime, owner )
		self.updateAttr( "exp", exp, owner )


	def isInTrain( self ):
		"""
		判断是否在代练中
		"""
		return self.__startTime > 0



# --------------------------------------------------------------------
# instance for packing
# --------------------------------------------------------------------
commonGemInstance = CommonGem()
trainGemInstance = TrainGem()
