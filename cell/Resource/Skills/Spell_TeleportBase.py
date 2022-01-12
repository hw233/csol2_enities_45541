# -*- coding: gb18030 -*-
#
# $Id: Spell_TeleportBase.py,v 1.1 2009-09-21 04:04:50 pengju Exp $

"""
���ͼ��ܻ�����
"""
import BigWorld
import csstatus
import csdefine
from SpellBase import *
import Const

class Spell_TeleportBase( Spell ):
	"""
	���ͼ��ܻ�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

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
		# ��ҵ�ǰ���ܿ��ƣ����ܴ���
		if not caster.controlledBy :
			return csstatus.SKILL_CANT_USE_IN_LOSE_CONTROL

		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB

		#Я��������Ʒ������ʹ��
		if caster.hasMerchantItem() or caster.hasFlag( csdefine.ROLE_FLAG_BLOODY_ITEM ):
			return csstatus.MERCHANT_ITEM_CANT_FLY

		# ����з�������buff
		if len( caster.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return csstatus.SKILL_CANT_CAST

		#�ڼ����в��ܴ���
		if caster.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			return csstatus.SPACE_MISS_LEAVE_PRISON
		if caster.getCurrentSpaceType() == csdefine.SPACE_TYPE_TONG_TURN_WAR:
			return csstatus.SKILL_CANT_CAST

		# ��ֹ����ԭ���µĲ���ʩ��
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
			return csstatus.SKILL_CANT_CAST
		return Spell.useableCheck( self, caster, target )

# $Log: not supported by cvs2svn $
#