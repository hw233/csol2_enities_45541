# -*- coding: gb18030 -*-
#
# $Id: PetStorage.py,v 1.10 2008-06-19 07:44:27 fangpengjun Exp $

"""
this module implements pet storage interface.

2007/07/01: writen by huangyongwei
2007/10/24: according to the new version, it is rewriten by huangyongwei
"""

import BigWorld
import csdefine
import csconst
import csstatus
import Const
from Time import Time
import event.EventCenter as ECenter
from cscollections import MapList

class PetStorage :
	def __init__( self ) :
		self.__endTime = 0
		self.__requireCBID = 0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getStoredPetsDict( self, petList ) :
		pets = MapList()
		for pet in petList :
			pets[pet["databaseID"]] = StorePet( pet["databaseID"], pet["name"], pet["level"], pet["species"], pet["modelNumber"] )
		return pets


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		self.base.pst_updateClient()

	# -------------------------------------------------
	def pst_storePet( self, dbid ) :
		self.cell.pst_storePet( dbid )

	def pst_takePet( self, dbid ) :
		self.cell.pst_takePet( dbid )

	# ---------------------------------------
	def pst_getEndTime( self ) :
		return self.__endTime

	# ----------------------------------------------------------------
	# define methods
	# ----------------------------------------------------------------
	def pst_openHire( self, objectID ) :
		"""
		打开仓库租赁对话框，选择要租赁的仓库类型
		"""
		try :
			entity = BigWorld.entities[objectID]
			ECenter.fireEvent( "EVT_ON_PST_OPEN_STORAGE_TENANCY", objectID )
		except KeyError, err :
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )

	def pst_onHireResult( self, success ) :
		"""
		租用仓库返回结果
		"""
		ECenter.fireEvent( "EVT_ON_PST_STORAGE_TENANCY_RESULT", success )

	# -------------------------------------------------
	def pst_onOpen( self, stype, overdue, petList ) :
		"""
		defined method
		打开仓库回调
		"""
		maxCount = csconst.pst_storeCount[stype]
		petDict = self.__getStoredPetsDict( petList )
		ECenter.fireEvent( "EVT_ON_PST_OPEN_PET_STORAGE", stype, overdue, petDict )

	# -------------------------------------------------
	def pst_onUpdateHireTime( self, endTime ) :
		"""
		defined method
		租用一个仓库
		"""
		BigWorld.cancelCallback( self.__requireCBID )
		self.__endTime = endTime
		ahead = max( 1, endTime - Time.time() - 10 )
		ECenter.fireEvent( "EVT_ON_PST_OPEN_STORAGE_TIME", ahead )
		self.__requireCBID = BigWorld.callback( ahead, self.base.pst_updateClient )

	# -------------------------------------------------
	def pst_onStoredPet( self, storePet ) :
		"""
		defined method
		存储一个宠物回调
		"""
		ECenter.fireEvent( "EVT_ON_PST_STORED_PET", storePet )

	def pst_onTakenPet( self, dbid ) :
		"""
		define method
		取出一个宠物回调
		"""
		ECenter.fireEvent( "EVT_ON_PST_TAKEN_PET", dbid )

class StorePet:
	def __init__( self, dbid, name, level, species, modelNumber ):
		self.dbid = dbid
		self.name = name
		self.level = level
		self.species = species
		self.modelNumber = modelNumber

