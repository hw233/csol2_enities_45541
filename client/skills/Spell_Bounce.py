# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *
from SpellBase import *
import csdefine
from gbref import rds
import csarithmetic
import Math
import math
from gbref import rds
from Function import Functor


class Spell_Bounce( Spell ):
	"""
	�����ﴴ��ʱ ��Ҫ����ҵ���
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )


	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		���ܼ��ܴ���
		
		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		# ������Ч����
		self._skillAE( BigWorld.player(), target, casterID, damageType, damage  )

	def _skillAE( self, player, target, casterID, damageType, damage ):
		"""
		���ܲ����˺�ʱ�Ķ���Ч���ȴ���
		@param player:			����Լ�
		@type player:			Entity
		@param target:			Spellʩ�ŵ�Ŀ��Entity
		@type target:			Entity
		@param caster:			Buffʩ���� ����ΪNone
		@type castaer:			Entity
		@param damageType:		�˺�����
		@type damageType:		Integer
		@param damage:			�˺���ֵ
		@type damage:			Integer
		"""
		if target.id == BigWorld.player().id:
			BigWorld.callback( 0.1, Functor( self.moveOut, casterID ) )
			
	def moveOut( self, casterID ):
		caster = BigWorld.entities.get( casterID )
		target = BigWorld.player()
		if caster:
			caster.isCloseCollide( True )
			s1 = caster.getBoundingBox().z / 2
			s2 = caster.getBoundingBox().x / 2
			radius = math.sqrt( s1*s1 + s2*s2 )
			disP = target.position - caster.position
			dis = radius - disP.length
			if dis < 0: return
			yaw = target.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			dstPos = target.position + direction * dis
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, endDstPos+(0,2,0), endDstPos-(0,2,0) )
			def __onMoveOver( success ):
				target.stopMove()
				caster.isCloseCollide( False )
				caster.openCollide()
				rds.skillEffect.interrupt( target )#��Ч�ж�
				if not  success:
					DEBUG_MSG( "player move is failed." )
			target.moveToDirectly( endDstPos, __onMoveOver )
		else:	
			BigWorld.callback( 0.1, Functor( self.moveOut, casterID ) )


	def hit( self, skillID, target ):
		"""
		�����ܻ�����
		@param skillID:			����ID��
		@type skillID:			INT
		@param target:			Spellʩ�ŵ�Ŀ��Entity
		@type target:			Entity
		"""
		if target is None:
			return
		if target.actionStateMgr( ):
			weaponType = target.getWeaponType()
			vehicleType = 0
			if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				vehicleType = target.vehicleType
			actionNames = rds.spellEffect.getHitAction( skillID, weaponType, vehicleType )
			target.playActions( actionNames )


