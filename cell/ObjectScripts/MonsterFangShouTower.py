# -*- coding: gb18030 -*-
#
# $Id: $

import BigWorld
import csdefine
import Const
from bwdebug import DEBUG_MSG
from Monster import Monster


class MonsterFangShouTower(Monster):
	"""
	���ظ���������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		Monster.initEntity( self, selfEntity )
		selfEntity.effectStateInc( csdefine.EFFECT_STATE_ALL_NO_FIGHT )
		
		if not selfEntity.getCurrentSpaceType() == csdefine.SPACE_TYPE_FANG_SHOU :
			return
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			currentArea = self.getCurrentFangShouArea( selfEntity.position )
			spaceBase.cell.remoteScriptCall( "onFangShouTowerCreate", ( currentArea, selfEntity.id ) )
	
	def getCurrentFangShouArea( self, pos ) :
		"""
		��ȡ��ǰ���ڷ��ظ�������
		"""
		z = pos.z
		currentArea = ""
		if z > Const.COPY_FANG_SHOU_AERA_POS_Z_FIRST :
			currentArea = Const.COPY_FANG_SHOU_AREA_FIRST
		elif z > Const.COPY_FANG_SHOU_AERA_POS_Z_SECOND :
			currentArea = Const.COPY_FANG_SHOU_AREA_SECOND
		elif z > Const.COPY_FANG_SHOU_AERA_POS_Z_THRID :
			currentArea = Const.COPY_FANG_SHOU_AREA_THRID
		else :
			currentArea = Const.COPY_FANG_SHOU_AREA_FORTH
		return currentArea