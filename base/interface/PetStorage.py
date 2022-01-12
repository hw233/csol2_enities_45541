# -*- coding: gb18030 -*-
#
# $Id: PetStorage.py,v 1.5 2008-07-02 06:29:07 kebiao Exp $

"""
this module implements pet cage interface.

2007/11/27: writen by huangyongwei
"""

import time
import cschannel_msgs
import ShareTexts as ST
import csdefine
import csconst
import csstatus
from bwdebug import *
from MsgLogger import g_logger
from PetEpitome import queryPets
from PetFormulas import formulas
import sys

class PetStorage :
	def __init__( self ) :
		pass

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getStoredPet( self, dbid ) :
		"""
		从仓库中获取指定 DBID 的宠物
		"""
		for storedPet in self.__storedPets :
			if storedPet["databaseID"] == dbid :
				return storedPet
		return None

	def __removeStoredPet( self, dbid ) :
		"""
		删除仓库中指定 DBID 的宠物
		"""
		storedPet = self.__getStoredPet( dbid )
		if storedPet is None :
			ERROR_MSG( "pet %i is not in storage!" % dbid )
		else :
			self.__storedPets.remove( storedPet )

	# -------------------------------------------------
	def __getStatus( self ) :
		"""
		获取仓库租用剩余时间状态
		"""
		self.__flushStatus()
		if self.__endTime == 0 :
			return csdefine.PET_STORE_STATUS_NONE
		elif time.time() > self.__endTime :
			return csdefine.PET_STORE_STATUS_OVERDUE
		return csdefine.PET_STORE_STATUS_HIRING

	def __flushStatus( self ) :
		"""
		更新时间状态
		"""
		if self.__endTime == 0 :
			self.cell.pst_onStatusChanged( csdefine.PET_STORE_STATUS_NONE )
		elif time.time() > self.__endTime :
			if len( self.__storedPets ) == 0 :
				self.__endTime = 0
				self.cell.pst_onStatusChanged( csdefine.PET_STORE_STATUS_NONE )
			else :
				self.cell.pst_onStatusChanged( csdefine.PET_STORE_STATUS_OVERDUE )
			if not self.__notified and hasattr( self, "client" ) :
				self.statusMessage( csstatus.PET_STORAGE_OVERDUE )
				self.__notified = True
		else :
			self.cell.pst_onStatusChanged( csdefine.PET_STORE_STATUS_HIRING )
			self.client.pst_onUpdateHireTime( self.__endTime )

	def pst_hire( self, stype, times ) :
		"""
		租用一个仓库
		"""
		status = self.__getStatus()
		if status == csdefine.PET_STORE_STATUS_HIRING :
			self.statusMessage( csstatus.PET_STORAGE_HIRE_FAIL_HIRED )
			self.client.pst_onHireResult( 0 )
			self.cell.pst_onEndOperating()
			return

		gold = formulas.getStorageCost( stype, times )
		if self.payGold( gold, csdefine.CHANGE_GOLD_PST_HIRE ) :
			self.__stype = stype
			self.__endTime = time.time() + csconst.PST_HOLD_DAYS * 24 * 3600*times
			self.__notified = False
			self.client.pst_onHireResult( 1 )
			self.__flushStatus()

			if stype == csdefine.PET_STORE_TYPE_LARGE :
				self.statusMessage( csstatus.PET_STORAGE_HIRE_LARGE_SUCCESS, csconst.pst_storeCount[stype], csconst.PST_HOLD_DAYS*times )
			else :
				self.statusMessage( csstatus.PET_STORAGE_HIRE_SMALL_SUCCESS, csconst.pst_storeCount[stype], csconst.PST_HOLD_DAYS*times )
		else :
			self.statusMessage( csstatus.PET_STORAGE_HIRE_FAIL_LACK_GOLD )
			self.client.pst_onHireResult( 0 )
		self.cell.pst_onEndOperating()


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def pst_open( self ) :
		"""
		打开仓库
		"""
		overdue = self.__getStatus() == csdefine.PET_STORE_STATUS_OVERDUE
		self.client.pst_onOpen( self.__stype, overdue, self.__storedPets )

	def pst_storePet( self, dbid ) :
		"""
		defined method
		存储宠物
		"""
		status = self.__getStatus()
		if status == csdefine.PET_STORE_STATUS_NONE :
			HACK_MSG( "player %i try to store pet to storage before hiring!" % self.databaseID )
		elif status == csdefine.PET_STORE_STATUS_OVERDUE :
			self.statusMessage( csstatus.PET_STORE_PET_FAIL_OVERDUE )
		elif len( self.__storedPets ) >= csconst.pst_storeCount[self.__stype] :
			self.statusMessage( csstatus.PET_STORE_PET_FAIL_FULLED )
		elif self.pcg_getPetEpitome( dbid ) is None :
			self.statusMessage( csstatus.PET_STORE_PET_FAIL_NOT_EXIST )
		elif self.pcg_isActivePet( dbid ) :
			self.statusMessage( csstatus.PET_STORE_PET_FAIL_CONJURED )
		else :
			epitome = self.pcg_removePet_( dbid, csdefine.DELETEPET_PETSTORE )
			storedPet = epitome.getStoredPetDict()
			self.__storedPets.append( storedPet )
			self.client.pst_onStoredPet( storedPet )
			self.statusMessage( csstatus.PET_STORE_PET_SUCCESS )
			try:
				g_logger.petStorageAddLog( self.databaseID, self.getName(), dbid, epitome.getAttr("uname") )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

		self.cell.pst_onEndOperating()

	def pst_takePet( self, dbid ) :
		"""
		define method
		从仓库中去除宠物
		"""
		status = self.__getStatus()
		if status == csdefine.PET_STORE_STATUS_NONE :
			HACK_MSG( "player %i try to take out pet from storage before hiring!" % self.databaseID  )
			self.cell.pst_onEndOperating()
			return
		if self.__getStoredPet( dbid ) is None :
			self.statusMessage( csstatus.PET_TAKE_PET_FAIL_NOT_EXIT )
			self.cell.pst_onEndOperating()
			return

		def onQueryPet( success, epitomes ) :
			if not success :
				self.statusMessage( csstatus.PET_TAKE_PET_FAIL_UNKNOW )
				self.cell.pst_onEndOperating()
			elif len( epitomes ) == 0 :
				self.statusMessage( csstatus.PET_TAKE_PET_FAIL_NOT_EXIT )
				self.cell.pst_onEndOperating()
			else :
				epitome = epitomes[dbid]
				self.pcg_addPet_( epitome, csdefine.ADDPET_TAKEPETFROMBANK )
				self.__removeStoredPet( dbid )
				self.client.pst_onTakenPet( dbid )
				self.statusMessage( csstatus.PET_TAKE_PET_SUCCESS )
				self.cell.pst_onEndOperating()
				try:
					g_logger.petStorageTakeLog( self.databaseID, self.getName(), dbid, epitome.getAttr("uname") )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
		queryPets( self.databaseID, [dbid], onQueryPet )


	def set_storageEndTime( self, remainTime ):
		"""
		define method
		设置宠物仓库有效时间
		"""
		if self.__getStatus() == csdefine.PET_STORE_STATUS_NONE:
			return
		if self.__endTime == -1:
			return

		self.__endTime = time.time() + remainTime


	# ----------------------------------------------------------------
	# exposed mehtods
	# ----------------------------------------------------------------
	def pst_updateClient( self ) :
		"""
		</Exposed>
		申请向客户端更新租用时间
		"""
		self.__flushStatus()

	def pst_hireStorage( self, stype, times ):
		"""
		</Exposed>
		租用一个仓库
		@param				stype : MACRO DEFINATION( UINT8 )
		@param				stype : 仓库类型（在 csdefine 中定义）
		"""
		cost = formulas.getStorageCost( stype, times )
		if self.getUsableGold() < cost :
			self.statusMessage( csstatus.PET_STORAGE_HIRE_FAIL_LACK_GOLD )
		else :
			self.pst_hire( stype, times )
