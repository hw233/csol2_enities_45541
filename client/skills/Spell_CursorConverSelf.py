# -*- coding: gb18030 -*-

"""
Spell�����ࡣ
"""
import BigWorld
import Math
import gbref
from SpellBase import *
import csstatus
from Spell_Cursor import Spell_Cursor
import SkillTargetObjImpl
from Function import Functor

"""
��ǰ��귽���λ�ý���ʩ��
"""
class Spell_CursorConverSelf( Spell_Cursor ):
	def __init__( self ):
		"""
		"""
		Spell_Cursor.__init__( self )
	
	def spell( self, caster, target ):
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( caster )
		Spell_Cursor.spell(self, caster, spellTarget)
	
	def validTarget( self, caster, target ):
		return csstatus.SKILL_GO_ON

class Spell_CursorMultAttack( Spell_CursorConverSelf ):
	# ��귽��ֶ���˺�
	def __init__( self ):
		Spell_CursorConverSelf.__init__( self )

	def init( self, dict ):
		Spell_CursorConverSelf.init( self, dict )
		self._attackCount = int( dict[ "param1" ] )
		if self._attackCount <= 0: self._attackCount = 1
	
	def receiveSpell( self, target, casterID, damageType, damage ):
		"""
		���ܼ��ܴ���
		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#�����������ԭ���� �ڷ�������һ��entity����һ��entityʩ�� ���������ǿ��ĵ�ʩ���ߵ�
				#���ͻ��˿��ܻ���Ϊĳԭ�� �磺�����ӳ� ���ڱ���û�и��µ�AOI�е��Ǹ�ʩ����entity����
				#��������ִ��� written by kebiao.  2008.1.8
				return
		else:
			caster = None

		count = 1
		if damage > 0:
			p2 = damage
			param2 /= self._attackCount
			if target.HP < p2:
				count = target.HP / damage + 1
			else:
				count = self._attackCount
		# ������Ч����
		self._skillAE( player, target, caster, damageType, damage  )
		self.showSkillInfo( count, player, target, casterID, damageType, damage  )

	def showSkillInfo( self, attackCount, player, target, casterID, param1, param2 ):
		"""
		# �˺���Ϣ��ʾ
		"""
		if target.isAlive():
			target.onReceiveDamage( casterID, self, param1, param2 )							# ϵͳ��Ϣ
			if attackCount > 1:
				BigWorld.callback( 0.3, Functor( self.showSkillInfo, attackCount - 1, player, target, casterID, param1, param2 ) )
