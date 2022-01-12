# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)����ʩ����λ��

import BigWorld
import csdefine
import csstatus
from SpellBase.HomingSpell import HomingSpellBuff
import Love3

class Spell_power_catch( HomingSpellBuff ):
	"""
	ϵͳ����
	����һ��AreaRestrictTransducer��entity(���幦��entity)
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		HomingSpellBuff.__init__( self )
		self.buff = 0					# ��������ʱ��


	def init( self, dictData ):
		"""
		��ȡ��������
		@param dictData:	��������
		@type dictData:	python dictData
		"""
		HomingSpellBuff.init( self, dictData )
		self._buffID = int( dictData["param4"] )
		HomingSpellBuff.init( self, dictData )



	def onInterrupted( self, caster, reason ):
		"""
		�������ܱ���ϻص�
		"""
		HomingSpellBuff.onInterrupted( self, caster, reason )
		if reason == csstatus.SKILL_INTERRUPTED_BY_SPELL_3:
			Love3.g_skills[self._buffID].receiveLinkBuff( None, caster )


	def canInterruptSpell( self, reason ):
		"""
		�ɷ񱻸�ԭ����
		"""
		return reason != csstatus.SKILL_INTERRUPTED_BY_SPELL_2

