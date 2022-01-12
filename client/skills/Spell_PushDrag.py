# -*- coding:gb18030 -*-

"""
Spell������
"""
from SpellBase.Spell import Spell
from bwdebug import *
import BigWorld
import Math
import Define

class Spell_PushDrag( Spell ):
	"""
    ������Ҽ以�������ֵ��� 
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		Spell.__init__( self )
		self.targetMoveDistance = 0.0				# ˮƽ���߷�����ƶ�λ�ƣ�Ϊ����ʾ������Ŀ����ˮƽ���������������ף���Ϊ�����ʾ������Ŀ����ˮƽ�������ͷ��߷������������ף�����0��ֱ������ʩ������ǰ

	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		if dict["param1"]:
			self.targetMoveDistance = float( dict["param1"] )

	def cast( self, caster, targetObject ):
		"""
		virtual method.
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		target = targetObject.getObject()
		if target.id == BigWorld.player().id:
			def moveOver( success ):
				target.stopMove()
				if not  success:
					DEBUG_MSG( "player move is failed." )
			direction = Math.Vector3( target.position ) - Math.Vector3( caster.position )	   # �õ�ˮƽ���ߵ�����
			direction.normalise()					# ��õ�λ����

			# ����������ʼλ����ʩ����λ�øպ���ͬһ��������
			if direction == Math.Vector3():
				direction = Math.Vector3( caster.position )
				direction.normalise()

			# �õ�������Ŀ���
			if self.targetMoveDistance == 0.0:
				dstPos = caster.position
			else:
				dstPos = target.position + direction * self.targetMoveDistance
			dstPos = Math.Vector3( dstPos )
			if target.isMoving():
				target.stopMove()
				target.moveToDirectly( dstPos, moveOver )
			else:
				target.moveToDirectly( dstPos, moveOver )
