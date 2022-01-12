# -*- coding: gb18030 -*-
#
# $Id: PetGem.py,v 1.19 2008-08-01 11:18:35 wangshufeng Exp $

"""
implement gem used by pet

2007/11/14: writen by huangyongwei
"""

import Language
import time
import inspect
import BigWorld
import csdefine
import csconst
import csstatus
from PetFormulas import formulas
import event.EventCenter as ECenter
from bwdebug import *

class BaseGem :
	def __init__( self, index ) :
		self.__index = index

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
		fullName = None
		for cs in inspect.getmro( self.__class__ ) :
			name = "_%s__%s" % ( cs.__name__, attrName )
			if hasattr( self, name ) :
				fullName = name
				break
		if fullName is not None :
			oldValue = getattr( self, fullName )
			setattr( self, fullName, value )
			notifier = getattr( self, "set_" + attrName, None )
			if notifier is not None :
				notifier( oldValue )

	def getAttr( self, attrName ) :
		"""
		get attribute of gem
		@type				attrName : str
		@param				attrName : attribute name
		@rtype						 : all python type
		@return						 : attribute value
		"""
		for cs in inspect.getmro( self.__class__ ) :
			fullName = "_%s__%s" % ( cs.__name__, attrName )
			if not hasattr( self, fullName ) : continue
			return getattr( self, fullName )
		ERROR_MSG( "attribute '__%s' is not exist!" % attrName )
		return getattr( self, fullName )

	# ----------------------------------------------------------------
	# packle / unpackle methods
	# ----------------------------------------------------------------
	def getDictFromObj( self, obj ) :
		return {}

	def createObjFromDict( self, dict ) :
		gem = self.__class__()
		for attrName, value in dict.items() :
			gem.onUpdateAttr( attrName, value )
		return gem

	def isSameType( self, gem ) :
		return isinstance( gem, BaseGem )

	@property
	def index( self ) :
		"""
		get the index of gem
		@rtype				: int
		@return				: the index of gem
		"""
		return self.__index


# --------------------------------------------------------------------
# implement common gem class
# --------------------------------------------------------------------
class CommonGem( BaseGem ) :
	def __init__( self, index = 0 ) :
		BaseGem.__init__( self, index )
		self.limitTime = 0


# --------------------------------------------------------------------
# implement train gem class
# --------------------------------------------------------------------
class TrainGem( BaseGem ) :
	def __init__( self ) :
		BaseGem.__init__( self, -1 )
		self.__trainType = csdefine.PET_TRAIN_TYPE_NONE
		self.__remainTime = 0
		self.__startTime = 0
		self.__exp = 0

		self.__flushCBID = 0

	def set_trainType( self, old ) :
		"""
		when the train type is changed by server it will be called
		"""
		if self.type > 0:
			self.startCycleFlush()
		else:
			self.stopCycleFlush()	# 如果结束代练，那么停止timer
		ECenter.fireEvent( "EVT_ON_PET_TRAIN_TYPE_CHANGED", self.type )

	def set_remainTime( self, old ) :
		"""
		when the remanentTime is changed by server it will be called
		"""
		ECenter.fireEvent( "EVT_ON_PET_REMAIN_TRAIN_TIME_CHANGED", self.remainTime )
		ECenter.fireEvent( "EVT_ON_PET_REMAIN_TRAIN_POINT_CHANGED", self.remainPoints )


	def set_exp( self, old ) :
		"""
		when the exp is changed by server it will be called
		"""
		if old == self.EXP : return
		ECenter.fireEvent( "EVT_ON_PET_TRAIN_EXP_CHANGED", self.EXP )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def EXP( self ) :
		"""
		exp stories in the gem
		"""
		return self.__exp

	@property
	def remainTime( self ) :
		"""
		remanent train time
		"""
		return self.__remainTime

	@property
	def remainPoints( self ) :
		"""
		remanent train points
		"""
		return formulas.getTrainPoints( self.__remainTime )

	@property
	def inTraining( self ) :
		"""
		indicate whether the gem is in training status
		"""
		return self.getAttr( "trainType" ) != csdefine.PET_TRAIN_TYPE_NONE

	@property
	def type( self ):
		"""
		train type
		"""
		return self.__trainType

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __cycleFlush( self ) :
		self.flush()
		self.__flushCBID = BigWorld.callback( 5, self.__cycleFlush )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def flush( self ) :
		"""
		calculate exp value it is valid in training status
		@return					: None
		"""
		BigWorld.player().cell.ptn_flushTrain()

	def startCycleFlush( self ) :
		"""
		require server the update gem's attributes each minute
		@return					: None
		"""
		self.stopCycleFlush()
		self.__cycleFlush()

	def stopCycleFlush( self ) :
		"""
		require server stop sending gem's attributes to client
		@return					: None
		"""
		BigWorld.cancelCallback( self.__flushCBID )

	# -------------------------------------------------
	def charge( self, gold ) :
		"""
		pay gold to get auto training time
		@type				gold : UINT32
		@param				gold : game point
		@return					 : None
		"""
		player = BigWorld.player()
		if player.gold < gold :
			player.statusMessage( csstatus.PET_TRAIN_CHARGE_FAIL_LACK_GOLD )
		else :
			player.base.ptn_trainCharge( gold )

	def startTrain( self, trainType ) :
		"""
		start to auto train
		@trainType				: MACRO DEFINATION
		@trainType				: common train or hard train defined in csdefine.py
		@return					: None
		"""
		player = BigWorld.player()
		if self.inTraining :
			player.statusMessage( csstatus.PET_TRAIN_FAIL_IN_TRIAN )
		elif self.__remainTime <= 0 :
			player.statusMessage( csstatus.PET_TRAIN_FAIL_NO_TRAIN_TIME )
		else :
			player.cell.ptn_stratTrain( trainType )

	def stopTrain( self ) :
		"""
		stop training
		@return					: None
		"""
		player = BigWorld.player()
		if not self.inTraining :
			player.statusMessage( csstatus.PET_TRAIN_STOP_FAIL_NOT_IN_TRAIN )
		else :
			player.cell.ptn_stopTrain()

	def feedPet( self, dbid, value ) :
		"""
		feed pet with exp
		@type			dbid  : INT64
		@param			dbid  : the pet database id which you want to feed
		@type			value : INT32
		@param			value : exp
		@return				  : None
		"""
		BigWorld.player().cell.ptn_feedPetEXP( dbid, value )

# --------------------------------------------------------------------
# instance for packing
# --------------------------------------------------------------------
commonGemInstance = CommonGem()
trainGemInstance = TrainGem()



#
# $Log: not supported by cvs2svn $
#
#
#