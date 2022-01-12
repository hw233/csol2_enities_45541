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
		���ñ�ʯ��timerID
		"""
		self.__timerID = timerID


	def getTimerID( self ):
		"""
		���ñ�ʯ��timerID
		"""
		return self.__timerID


	def load( self, owner, limitTime ):
		"""
		װ�ر�ʯ�������ڴ���һЩ����
		"""
		self.__limitTime = limitTime	# �����ݽ���server�õ�
		owner.client.ptn_loadComGem( self.getIndex() )

	def offload( self, owner ):
		"""
		ж�±�ʯ
		"""
		self.__timerID = 0
		owner.client.ptn_offloadComGem( self.getIndex() )	# ֪ͨ�ͻ���


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
		��������ʯ�����ʱ��
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
		�������֪ͨ
		"""
		if self.__remainTime <= 0:
			#debug�����ڴ���״̬
			return

		if self.__trainType == csdefine.PET_TRAIN_TYPE_NONE:	# ���ڴ���״̬
			return

		self.flush( owner )			# �������ڴ����ľ���ʯ���ݣ�֪ͨ�ͻ����������


	def flush( self, owner ):
		"""
		���´�����ʯ����
		"""
		percent = expGemDataMgr.getExpByLevel( owner.level )
		trainTime = time.time() - self.__updateTime
		self.__updateTime = time.time()	# ���һ�θ���ʱ�䣬����Ҫ֪ͨ�ͻ��ˣ����ڷ�����ʹ��
		remainTime = self.__remainTime - trainTime
		if remainTime < 0:
			trainTime = self.__remainTime
		startTime = self.__startTime
		trainType = self.__trainType
		if self.__trainType == csdefine.PET_TRAIN_TYPE_HARD:
			percent = percent * csconst.GEM_WORK_HARD_RATE
			remainTime = self.__remainTime - 2 * trainTime
		if self.isInTrain() and remainTime <= 0:				# ��ʯʣ�����ʱ�����
			remainTime = 0
			startTime = 0
			trainType = 0
			self.updateAttr( "startTime", startTime, owner )
			self.updateAttr( "trainType", trainType, owner )	# �����ʣ��ʱ�䣬��ôֹͣ����

		#maxExp = RLevelEXP.getEXPMax( owner.level )
		exp = int( self.__exp + trainTime * percent )
		if exp >= csconst.GEM_PET_COMMON_VALUE_UPPER:					#���鲻���ۼƳ���10��
			exp = csconst.GEM_PET_COMMON_VALUE_UPPER
		self.updateAttr( "remainTime", remainTime, owner )
		self.updateAttr( "exp", exp, owner )


	def isInTrain( self ):
		"""
		�ж��Ƿ��ڴ�����
		"""
		return self.__startTime > 0



# --------------------------------------------------------------------
# instance for packing
# --------------------------------------------------------------------
commonGemInstance = CommonGem()
trainGemInstance = TrainGem()
