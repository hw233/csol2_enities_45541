# -*- coding: gb18030 -*-
#
# $Id: PetFoster.py,v 1.8 2008-07-21 02:55:50 huangyongwei Exp $

"""
This module implements the pet entity.

2007/11/26 : writen by huangyongwei
"""

import BigWorld
import csdefine
import csconst
import csstatus
import event.EventCenter as ECenter
from PetFormulas import formulas
from Time import Time
from Function import Functor
from bwdebug import *


class PetFoster :
	def __init__( self ) :
		self.__requireCBID = 0
		self.__endTime = 0
		self.__notifyTime = 0
		self.pft_dstPetEpitome = None		# 对方选择的繁殖宠物数据
		self.pft_endProcreateTimerList = []	# 繁殖结束timer列表


	def leaveWorld( self ):
		for cbid in self.pft_endProcreateTimerList:
			BigWorld.cancelCallback( cbid )
		self.pft_endProcreateTimerList = []

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getProcreatePets( self ) :
		"""
		获取可繁殖的宠物  epitome
		"""
		petEpitomes = []
		for epitome in self.pcg_getPetEpitomes().itervalues() :
			if epitome.conjured :
				continue
			if not formulas.isHierarchy( epitome.species, csdefine.PET_HIERARCHY_INFANCY1 ) :
				continue
			if epitome.level < csconst.PET_PROCREATE_MIN_LEVEL :
				continue
			petEpitomes.append( epitome )
		return petEpitomes

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		pass
		#self.base.pft_updateClient()

	def pft_getRemainTime( self ) :
		"""
		获取繁殖剩余时间
		"""
		return max( 0, self.__endTime - Time.time() )

	def pft_dstChangeState( self, dstState ):
		"""
		Define method.
		对方繁殖操作状态改变

		@param dstState : 对方的繁殖操作状态，INT8
		"""
		ECenter.fireEvent( "EVT_ON_PETFOSTER_DST_STATE_CHANGE", dstState )
		DEBUG_MSG( "---->>>dstState", dstState )

	def pft_dstPetChanged( self, petEpitome ):
		"""
		Define method.
		对方改变了用于繁殖的宠物。

		@param petEpitome : 宠物数据
		@type petEpitome : PET_EPITOME
		"""
		self.pft_dstPetEpitome = petEpitome
		ECenter.fireEvent( "EVT_ON_PETFOSTER_DST_PETEPITOME_CHANGE", petEpitome )

	def set_procreateState( self, oldValue ):
		"""
		"""
		DEBUG_MSG( "---->>>oldValue, newValue", oldValue, self.procreateState )
		ECenter.fireEvent( "EVT_ON_PETFOSTER_PROCREATE_STATE", oldValue, self.procreateState )

	def pft_receivePetProcreationInfo( self, playerDBID, endTime ):
		"""
		Define method.
		接收宠物繁殖到期时间

		@param endTime : 宠物繁殖到期时间
		@type endTime : INT32
		"""
		now = Time.time()
		if now - csconst.PET_PROCREATE_OVERDUE_TIME > endTime:
			self.statusMessage( csstatus.PET_PROCREATE_GET_OVERDUE )
			self.pft_remind( playerDBID )	# 宠物过期，通知服务器更新
		elif now > endTime:
			self.statusMessage( csstatus.PET_PROCREATE_END )
		else:
			self.pft_endProcreateTimerList.append( BigWorld.callback( max( 10.0, endTime - Time.time() ), Functor( self.pft_remind, playerDBID ) ) )
			remainTime = endTime - Time.time()
			remainHours = remainTime/3600
			remMins = ( remainTime%3600 )/60
			ECenter.fireEvent( "EVT_ON_PETFOSTER_REMAIN_TIME", remainTime )

	def pft_remind( self, dstPlayerDBID ):
		"""
		繁殖时间到，请求服务器通知2个参与繁殖的玩家。
		"""
		self.statusMessage( csstatus.PET_PROCREATE_END )
		self.base.pft_remind( dstPlayerDBID )
