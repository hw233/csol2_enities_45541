# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemDispersion.py,v 1.26 8:56 2010-7-15 jinagyi Exp $

"""
��Ʒ���� ��ɢ������
"""

from Spell_Item import Spell_Item
from Resource import DispersionTable
import csdefine
import csstatus


class Spell_ItemDispersion( Spell_Item ):
	"""
		սʿ�б�����ɢ�� :1
		��ʦ��ѣ����ɢ�� :2
		�����м�����ɢ�� :3
		�����л�˯��ɢ�� :4			
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )
		#self._dispelType = []
		self._triggerBuffInterruptCode = []							# �ü��ܴ�����Щ��־���ж�ĳЩBUFF
		
	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		
		self._dispelAmount = int( dict.get( "param1" , 0 ) )			# ������ɢ���� DispelAmount
		"""
		��ɢ����
		սʿ�б�����ɢ�� :EFFECT_STATE_VERTIGO
		��ʦ��ѣ����ɢ�� :EFFECT_STATE_VERTIGO
		�����м�����ɢ�� :EFFECT_STATE_VERTIGO
		�����л�˯��ɢ�� :EFFECT_STATE_VERTIGO		
		"""
		type = dict.get( "param2" , "" )
		if len( type ) > 0:
			self._effectType = eval( "csdefine." + type )				
		else:
			self._effectType = -1
			
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
			
		if self._effectType != csdefine.EFFECT_STATE_VERTIGO and caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if self._effectType != csdefine.EFFECT_STATE_SLEEP and caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if self._effectType != csdefine.EFFECT_STATE_HUSH_MAGIC and caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell_Item.useableCheck( self, caster, target )
		
	def canDispel( self, caster, receiver, buffData ):
		"""
		�ɷ���ɢ
		"""
		skill = buffData["skill"]
		if skill.getLevel() < self.getLevel():# ֻ����ɢ���Լ�����׵�BUFF
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
		receiver.clearBuff( self._triggerBuffInterruptCode )