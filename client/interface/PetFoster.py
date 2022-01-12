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
		self.pft_dstPetEpitome = None		# �Է�ѡ��ķ�ֳ��������
		self.pft_endProcreateTimerList = []	# ��ֳ����timer�б�


	def leaveWorld( self ):
		for cbid in self.pft_endProcreateTimerList:
			BigWorld.cancelCallback( cbid )
		self.pft_endProcreateTimerList = []

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getProcreatePets( self ) :
		"""
		��ȡ�ɷ�ֳ�ĳ���  epitome
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
		EntityCache�������
		"""
		pass
		#self.base.pft_updateClient()

	def pft_getRemainTime( self ) :
		"""
		��ȡ��ֳʣ��ʱ��
		"""
		return max( 0, self.__endTime - Time.time() )

	def pft_dstChangeState( self, dstState ):
		"""
		Define method.
		�Է���ֳ����״̬�ı�

		@param dstState : �Է��ķ�ֳ����״̬��INT8
		"""
		ECenter.fireEvent( "EVT_ON_PETFOSTER_DST_STATE_CHANGE", dstState )
		DEBUG_MSG( "---->>>dstState", dstState )

	def pft_dstPetChanged( self, petEpitome ):
		"""
		Define method.
		�Է��ı������ڷ�ֳ�ĳ��

		@param petEpitome : ��������
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
		���ճ��ﷱֳ����ʱ��

		@param endTime : ���ﷱֳ����ʱ��
		@type endTime : INT32
		"""
		now = Time.time()
		if now - csconst.PET_PROCREATE_OVERDUE_TIME > endTime:
			self.statusMessage( csstatus.PET_PROCREATE_GET_OVERDUE )
			self.pft_remind( playerDBID )	# ������ڣ�֪ͨ����������
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
		��ֳʱ�䵽�����������֪ͨ2�����뷱ֳ����ҡ�
		"""
		self.statusMessage( csstatus.PET_PROCREATE_END )
		self.base.pft_remind( dstPlayerDBID )
