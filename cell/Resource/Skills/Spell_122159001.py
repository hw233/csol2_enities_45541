# -*- coding: gb18030 -*-
#
# 2009-02-03 ���巼
#

from Spell_BuffNormal import Spell_BuffNormal
from SpellBase import *
import csstatus
import csconst
import time
import csdefine
import ECBExtend

class Spell_122159001( Spell_BuffNormal ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )

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
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# ������������ͻ��߳������ͻ����ڳ������ڣ����͵�ʵ����д���
		if not ( receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) ):
			return

		currSunBathAreaCount = receiver.queryTemp( "sun_bath_area_count", 0 ) + 1
		receiver.setTemp( "sun_bath_area_count", currSunBathAreaCount )
		if currSunBathAreaCount <= 1:
			if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				receiver.statusMessage( csstatus.ROLE_ENTER_SUN_BATH_MAP )
			self.receiveLinkBuff( receiver, receiver )

		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.actCounterInc( csdefine.ACTION_FORBID_PK )	# ��ֹ���PK�ı��
			date = time.localtime()[2]
			if receiver.sunBathDailyRecord.date != date:
				receiver.sunBathDailyRecord.date = date
				receiver.sunBathDailyRecord.sunBathCount = 0
				receiver.sunBathDailyRecord.prayCount = 0
			receiver.setTemp( "ADD_SUN_BATH_COUNT_TIMER_ID", receiver.addTimer( 1, 10, ECBExtend.ADD_SUN_BATH_COUNT ) )
			# �չ�ԡ����Ĺ�ʽ�� ��Ҽ��� + 23
			increaseEXP = receiver.level + 23
			receiver.setTemp( "clean_sun_bath_exp", increaseEXP )
			actPet = receiver.pcg_getActPet()
			if actPet :														# ������Я���г�������
				actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )		# ���ջ�֮
