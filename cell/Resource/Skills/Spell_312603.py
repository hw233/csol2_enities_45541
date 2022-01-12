# -*- coding: gb18030 -*-
#
# $Id: Spell_Dispersion.py,v 1.26 2008-08-14 01:11:36 kebiao Exp $

"""
��ɢ������
"""

from SpellBase import *
from Resource import DispersionTable
import csdefine
import csstatus

class Spell_312603( Spell ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		#self._dispelType = []
		self._triggerBuffInterruptCode = []							# �ü��ܴ�����Щ��־���ж�ĳЩBUFF
		
	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		
		self._dispelAmount = int( dict.get( "param1" , 0 ) )			# ������ɢ���� DispelAmount
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
				
	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method.
		���ܷ���֮ǰ��Ҫ��������
		"""
		# ĥ��
		#caster.equipAbrasion()
		pass

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell.useableCheck( self, caster, target )
		
	def canDispel( self, caster, receiver, buffData ):
		"""
		�ɷ���ɢ
		"""
		skill = buffData["skill"]
		if skill.getLevel() <= self.getCastTargetLevelMax():
			if skill.cancelBuff( self._triggerBuffInterruptCode ):
				return True		
		return False
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# ��ɢĿ�����ϵ�buff
		rmb = []
		count = 0
		for index, buff in enumerate( receiver.getBuffs() ):
			if self.canDispel( caster, receiver, buff ):
				rmb.append( index )
				count += 1
				if count >= self._dispelAmount:
					break

		# ����
		rmb.reverse()
		for index in rmb:
			receiver.removeBuff( index, self._triggerBuffInterruptCode )