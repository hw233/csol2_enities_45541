# -*- coding: gb18030 -*-
#
# $Id: BDuffFacade.py,v 1.20 2008-08-25 11:00:55 qilan Exp $

import BigWorld
from bwdebug import *
from event.EventCenter import *
from guis import util
from ItemsFactory import BuffItem
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from ItemsFactory import ItemInfo


# --------------------------------------------------------------------
# implement facade class
# --------------------------------------------------------------------
class BDuffFacade :
	__roleBDuffInfos = []
	__roleBuffInfos = []
	__roleDuffInfos = []

	@classmethod
	def reset( SELF ) :
		SELF.__roleBDuffInfos = []
		SELF.__roleBuffInfos = []
		SELF.__roleDuffInfos = []


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def getBDuffInfos( SELF ) :
		return SELF.__roleBDuffInfos

	@classmethod
	def setBDuffInfos( SELF , index, info , isMalignant ) :
		if isMalignant:
			SELF.__roleDuffInfos[index] = info
		else:
			SELF.__roleBuffInfos[index] = info
		SELF.__roleBDuffInfos[index] = info

	# -------------------------------------------------
	@classmethod
	def addBuff( SELF, buffData ) :
		buffInfo = BuffItem( buffData )
		SELF.__roleBuffInfos.append( buffInfo )
		SELF.__roleBDuffInfos.append( buffInfo )
		return buffInfo

	@classmethod
	def addDuff( SELF, duffData ) :
		duffInfo = BuffItem( duffData )
		SELF.__roleDuffInfos.append( duffInfo )
		SELF.__roleBDuffInfos.append( duffInfo )
		return duffInfo

	# ---------------------------------------
	@classmethod
	def removeBuff( SELF, index ) :
		for buffInfo in SELF.__roleBDuffInfos:
			if buffInfo.buffIndex == index:
				SELF.__roleBuffInfos.remove( buffInfo )
				SELF.__roleBDuffInfos.remove( buffInfo )
				return buffInfo
		return None

	@classmethod
	def removeDuff( SELF, index ) :
		for buffInfo in SELF.__roleBDuffInfos:
			if buffInfo.buffIndex == index:
				SELF.__roleDuffInfos.remove( buffInfo )
				SELF.__roleBDuffInfos.remove( buffInfo )
				return buffInfo
		return None

	@classmethod
	def updateBuff( SELF, index, buffData ) :
		try :
			for buffInfo in SELF.__roleBDuffInfos:
				if buffInfo.buffIndex == index:
					buffInfo.__init__( buffData )
					return buffInfo
		except :
			pass
		return None

# --------------------------------------------------------------------
# called by client base
# --------------------------------------------------------------------
def onAddBuff( entityID, buffData ) :
	"""
	add buff to the character
	@type			entityID : int32
	@param			entityID : id of character
	@type			buffInfo : dict
	@param 			buffInfo : { id : int16, endTime : int32 }
	"""
	if entityID == BigWorld.player().id :
		info = BDuffFacade.addBuff( buffData )
		fireEvent( "EVT_ON_ROLE_ADD_BUFF", info )

def onAddDuff( entityID, duffData ) :
	"""
	add duff to the character
	@type			entityID : int32
	@param			entityID : id of character
	@type			duffInfo : dict
	@param 			duffInfo : { id : int16, endTime : int32 }
	"""
	if entityID == BigWorld.player().id :
		info = BDuffFacade.addDuff( duffData )
		fireEvent( "EVT_ON_ROLE_ADD_DUFF", info )

# -------------------------------------------
def onRemoveBuff( entityID, index ) :
	"""
	remove buff from charcter
	@type			entityID : int32
	@param			entityID : id of character
	@type			index	 : int
	@param 			index	 : index of buffinfo
	"""
	if entityID == BigWorld.player().id :
		info = BDuffFacade.removeBuff( index )
		if info is None : return
		fireEvent( "EVT_ON_ROLE_REMOVE_BUFF", info )

def onRemoveDuff( entityID, index ) :
	"""
	remove buff from character
	@type			entityID : int32
	@param			entityID : id of character
	@type			index	 : int
	@param 			index	 : index of buffinfo
	"""
	if entityID == BigWorld.player().id :
		info = BDuffFacade.removeDuff( index )
		if info is None : return
		fireEvent( "EVT_ON_ROLE_REMOVE_DUFF", info )

def onUpdateBDuffData( entityID, index, newbuffData , isMalignant ):
	"""
	add persistent time of buff or duff
	@type			entityID : int32
	@param			entityID : id of character
	@type			buffInfo : dict
	@param 			buffInfo : { id : int16, endTime : int32 }
	"""
	if entityID == BigWorld.player().id :
		info = BDuffFacade.updateBuff( index, newbuffData )
		#BDuffFacade.setBDuffInfos( index, info , isMalignant )
		fireEvent( "EVT_ON_ROLE_UPDATE_BUFF", info )


# --------------------------------------------------------------------
# called by ui
# --------------------------------------------------------------------
def getBDuffCount() :
	"""
	how many buff/duff icons to show at a time
	@rtype					: int
	@return					: the number of buff/duff icons to show at a time
	"""
	return 10


def getWarningTime() :
	"""
	how long the warning will last
	@rtype					: float
	@return					: how long the warning will last
	"""
	return 20.0

def removeBuff( buffInfo ) :
	try :
		index = BDuffFacade.getBDuffInfos().index( buffInfo )
		BigWorld.player().requestRemoveBuff( buffInfo.buffIndex )
	except :
		DEBUG_MSG( "buff is not exist! you can't remove it" )

