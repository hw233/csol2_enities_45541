# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemSuperDrugMP.py,v 1.2 2008-09-01 09:15:58 huangdong Exp $


from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus
import csdefine


class Spell_Item_CuryPercent_MP( Spell_ItemCure ):
	"""
	ʹ�ã��ۻ��ָ�һ��������MP,ÿ�ΰ��ٷֱȻָ�
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
		self._effect_max = dictDat[ "EffectMax" ]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		uid = caster.queryTemp( "item_using" )
		hasReceived = False

		if caster.isReal() and not caster.queryTemp( uid, False ):
			Spell_ItemCure.receive( self, caster, receiver )
			uid = caster.queryTemp( "item_using" )
			item = caster.getByUid( uid )
			receiver.setTemp( "buffcurPoint", min( int( receiver.MP_Max / 100.0 * self._effect_max ) + self._effect_min , item.getCurrPoint() ) )
			self.payItemPoint_MP( caster, receiver, item )

		if not receiver.isReal():
			caster.setTemp( uid, True)						# ֮���Խ��ж��ظ������ݼ�¼��cast���ϣ�����Ϊ����cast�϶�Ϊreal ����receiveOnReal��ʱ�� ��ֵһ�����޸��ˡ�
			receiver.receiveOnReal( caster.id, self )
			return

		caster.setTemp( uid, False )						# setTemp����Զ���޸�
		curPoint = receiver.popTemp( "buffcurPoint", 0 )
		self.cureMP( caster, receiver, curPoint )


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
		if targetEntity.MP == targetEntity.MP_Max:
			return csstatus.SKILL_CURE_NONEED
		if targetEntity.getEntityType() == csdefine.ENTITY_TYPE_PET and targetEntity.level < int( self.getParam5Data() ):
			return csstatus.SKILL_ITEM_NOT_READY
		return Spell_ItemCure.useableCheck( self, caster, target)

	def payItemPoint_MP( self , caster, receiver, item):
		"""
		����ָ�MP��Ӧ�ÿ۳��ĵ���
		"""
		lostMp = receiver.MP_Max - receiver.MP
		effect = int( receiver.MP_Max / 100.0 * self._effect_max ) + self._effect_min
		curMP = max( self._effect_min, lostMp )
		curMP = min( effect, curMP )
		if item:
			item.setTemp("sd_usePoint",curMP)

	def calcDelay( self, caster, target ):
		"""
		virtual method.
		ȡ���˺��ӳ�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: float(��)
		"""
		return 0.0