# -*- coding: gb18030 -*-
#
# ����Ŀͻ��˼��� 2009-01-10 SongPeifang & LinQing
#
from Spell_Item import Spell_Item
import GUIFacade
import BigWorld
import random
import csdefine
import csstatus

class Spell_322399001( Spell_Item ):
	"""
	����Ŀͻ��˼���
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell_Item.init( self, dict )
		self._fishingRange = int( dict[ "param3" ] )		# ���뺣�߶�Զ���Ե���

	def rotate( self, caster ):
		"""
		ת��������Դ󺣣�ʵ���Ͼ�����Ժ��߲��õ�����Entity��
		"""
		# ��ȡ�������ߵ�һЩ��������Entity
		entities = caster.entitiesInRange( self._fishingRange, cnd = lambda ent : ent.__class__.__name__ == "SpecialHideEntity" )
		if len( entities ) < 1:
			return
		index = random.randint( 0, len( entities ) - 1 )
		# ����ЩEntity�������һ�������ת��
		specialHideEntity = entities[index]
		new_yaw = ( specialHideEntity.position - caster.position ).yaw
		# yaw������10��ʱ��ת��
		if abs( caster.yaw - new_yaw ) > 0.0:
			caster.turnaround( specialHideEntity.matrix, None )

	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�
		"""
		entities = caster.entitiesInRange( self._fishingRange, cnd = lambda ent : ent.__class__.__name__ == "SpecialHideEntity" )
		if len( entities ) < 1:
			# �ж�����Ƿ������ڿɵ����������
			return csstatus.SKILL_CAST_NOT_SUN_FISH_PLACE
		return Spell_Item.useableCheck( self, caster, target)

	def interrupt( self, caster, reason ):
		"""
		�жϵ���
		@type	speller 	: entity
		@param	speller 	: ����ʩ����
		"""
		player = BigWorld.player()
		if player.id != caster.id:
			return
		Spell_Item.interrupt( self, caster, reason )
		if reason != csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 or caster.getState() == csdefine.ENTITY_STATE_DEAD:
			# ��������Ҫ�رյ�����棬��������ж�ԭ���ǵ���Ͳ���Ҫ��
			GUIFacade.onFishingEnd( caster )
			caster.end_body_changing( "" )

	def intonate( self, caster, intonateTime, targetObject ):
		"""
		���ż�������������Ч����
		"""
		player = BigWorld.player()
		if player.id == caster.id:
			self.rotate( caster )	# ת�򺣱�
		Spell_Item.intonate( self, caster, intonateTime, targetObject )