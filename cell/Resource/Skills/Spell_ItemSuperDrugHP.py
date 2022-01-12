# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemSuperDrugHP.py,v 1.2 2008-09-01 09:15:53 huangdong Exp $


from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus
import csdefine


class Spell_ItemSuperDrugHP( Spell_ItemCure ):
	"""
	ʹ�ã��ۻ��ָ�һ��������HP
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemCure.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		# ����Ч��ֵӦ����casterΪrealʱ���в�����item��ʹ��Ч����������Ч��Ҫ�Ӹ�receiver����ʱ�豣֤receiver��real
		# ����һ��hadReceived��ǣ�receive��һ��ִ��ʱ��casterΪreal����ʱ����hadReceivedΪTrue������item��ʹ��Ч����
		# ����ǵڶ��ν���receve( ͨ��receiveOnReal )��hadReceived�����˲��ٶ�caster���д���
		# ��˾Ͳ���۳������Ʒ����ʹ��Ч����19:27 2009-11-4��wsf
		stringKey = str( self.getID() ) + str( caster.id )
		hadReceived = False
		if receiver.isReal():
			hadReceived = receiver.queryTemp( stringKey, False )
		if caster and caster.isReal() and not hadReceived:
			Spell_ItemCure.receive( self, caster, receiver )
			item = caster.getByUid( caster.queryTemp( "item_using" ) )
			receiver.setTemp( "buffcurPoint", min( self._effect_max, item.getCurrPoint() ) )
			self.payItemPoint_HP( caster, receiver)
		if not hadReceived:
			receiver.setTemp( stringKey, True )
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.removeTemp( stringKey )
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

	def payItemPoint_HP( self , caster, receiver ):
		"""
		����ָ�HP��Ӧ�ÿ۳��ĵ���
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		lostHp = receiver.HP_Max - receiver.HP
		curHP = max( self._effect_min, lostHp )
		curHP = min( self._effect_max, curHP )
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