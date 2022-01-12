# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemSuperDrugHP.py,v 1.2 2008-09-01 09:15:53 huangdong Exp $


from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus
import csdefine


class Spell_Item_CuryPercent_HP( Spell_ItemCure ):
	"""
	ʹ�ã��ۻ��ָ�һ��������HP,ÿ�ΰ��ٷֱȻָ�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemCure.__init__( self )

	def init( self, dictDat ):
		"""
		��ȡ��������
		@param dictDat:	��������
		@type dictDat:	python dictDat
		"""
		Spell_ItemCure.init( self, dictDat )
		self._effect_max = dictDat[ "EffectMax" ]		# �����ڵײ� self._effect_max ֵ���� self._effect_min ��ǿ�Ƶ��� self._effect_min �����������¸�ֵ

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		uid = caster.queryTemp( "item_using" )

		if caster.isReal() and not caster.queryTemp( uid, False ):
			Spell_ItemCure.receive( self, caster, receiver )
			uid = caster.queryTemp( "item_using" )
			item = caster.getByUid( uid )
			receiver.setTemp( "buffcurPoint", min( int( receiver.HP_Max / 100.0 * self._effect_max ) + self._effect_min, item.getCurrPoint() ) )
			self.payItemPoint_HP( caster, receiver, item)

		if not receiver.isReal():
			caster.setTemp( uid, True)						# ֮���Խ��ж��ظ������ݼ�¼��cast���ϣ�����Ϊ����cast�϶�Ϊreal ����receiveOnReal��ʱ�� ��ֵһ�����޸��ˡ�
			receiver.receiveOnReal( caster.id, self )
			return

		caster.setTemp( uid, False )						# setTemp����Զ���޸�
		curPoint = receiver.popTemp( "buffcurPoint", 0 )
		self.cureHP( caster, receiver, curPoint )

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
		targetEntity = target.getObject()
		if targetEntity.HP == targetEntity.HP_Max:
			return csstatus.SKILL_CURE_NONEED
		if targetEntity.getEntityType() == csdefine.ENTITY_TYPE_PET and targetEntity.level < int( self.getParam5Data() ):
			return csstatus.SKILL_ITEM_NOT_READY
		return Spell_ItemCure.useableCheck( self, caster, target)

	def payItemPoint_HP( self, caster, receiver, item ):
		"""
		����ָ�HP��Ӧ�ÿ۳��ĵ���
		"""
		lostHp = receiver.HP_Max - receiver.HP
		effect = int( receiver.HP_Max / 100.0 * self._effect_max ) + self._effect_min
		curHP = max( self._effect_min, lostHp )
		curHP = min( effect, curHP )
		if item:
			item.setTemp("sd_usePoint",curHP)

	def calcDelay( self, caster, target ):
		"""
		virtual method.
		ȡ���˺��ӳ�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: float(��)
		"""
		return 0.0