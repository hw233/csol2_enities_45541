# -*- coding: gb18030 -*-

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
from gbref import rds
import csarithmetic
import Math
import math

class Spell_PullAndBite( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		# ������λ������
		self.targetMoveSpeed = 0.0
		#����ʩ���߾���
		self.disToCaster  = 2.0

	def init( self, data ):
		"""
		"""
		Spell.init( self, data )
		self.disToCaster     = float( data["param1"] )
		self.targetMoveSpeed = float( data["param2"] )
		
		
	def receiveSpell( self, target, casterID, damageType, damage  ):
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#�����������ԭ���� �ڷ�������һ��entity����һ��entityʩ�� ���������ǿ��ĵ�ʩ���ߵ�
				#���ͻ��˿��ܻ���Ϊĳԭ�� �磺�����ӳ� ���ڱ���û�и��µ�AOI�е��Ǹ�ʩ����entity����
				#��������ִ��� written by kebiao.  2008.1.8
				return
		# ������Ч����
		self._skillAE( player, target, caster, damageType, damage  )
		
	def _skillAE( self, player, target, caster, damageType, damage ):
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
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return
		id = self.getID()
		if caster:
			self.hit( id, target )
			rds.skillEffect.playHitEffects( caster, target, id )
		rds.skillEffect.playCameraEffects( caster, target, id )
		#�����ǰĿ�괦�ڰ���״̬�����������λ��
		if target.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY| csdefine.EFFECT_STATE_FIX ) > 0:
			return
		#�������˴�һ��Ŀ��ʱ�ı����ж�
		if target.beHomingCasterID != 0 and target.beHomingCasterID != caster.id : return
		
		dis = ( target.position - caster.position ).length
		if target.__class__.__name__ == "PlayerRole" and self.targetMoveSpeed and dis > self.disToCaster:
			yaw = ( caster.position - target.position ).yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			direction.normalise()
			dstPos = target.position + direction * ( dis - self.disToCaster )
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, target.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( target.spaceID, endDstPos+(0,3,0), endDstPos-(0,3,0) )
			
			def __onMoveOver( success ):
				target.stopMove()
				if not  success:
					DEBUG_MSG( "player move is failed." )
			target.moveToDirectly( endDstPos, __onMoveOver )
	
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
