# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import csdefine
from Spell_BuffNormal import Spell_ItemBuffNormal


class Spell_111006( Spell_ItemBuffNormal ):
	"""
	��Ŀ�굥λ����൱��������ֵ����xx%���˺�
	"""
	def __init__( self ):
		"""
		"""
		Spell_ItemBuffNormal.__init__( self )
		self.param = []
		self.damage = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )
		self.param1 = int( dict["param1"] if len( dict["param1"] ) > 0 else 10 )  / 100.0  # �˺��ٷֱ�
		self.param2 = dict["param2"]   													   # �˺�Ŀ���б�

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
		target = target.getObject()
		# Ŀ��Ѫ������10%����ʩ��
		if target.HP <= target.HP_Max * self.param1:
			return csstatus.SKILL_TARGET_IS_GOING_TO_DIE
		List = self.param2.split("|")
		for i in List:
			self.param.append(i)
		# ֻ�ܶ�ָ����Ŀ��ʩ��
		if not target.className in self.param:
			return csstatus.SKILL_INVALID_ENTITY
		# ��ֹ����ԭ���µĲ���ʩ��
		if caster.actionSign( csdefine.ACTION_FORBID_USE_ITEM ):
			if caster.getState() == csdefine.ENTITY_STATE_PENDING:
				return csstatus.CIB_MSG_PENDING_CANT_USE_ITEM
			return csstatus.CIB_MSG_TEMP_CANT_USE_ITEM
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY
		return csstatus.SKILL_GO_ON

	def calReduceDamage( self,caster, receiver ):
		"""
		����ʵ�ʼ�����
		�ȼ����� = (�����ȼ�-�ط��ȼ�)*4% 
		ʵ�ʼ���=MAX(�ط���������-�����Ƶ�����-�ȼ�����,0) 
		"""
		disLevel = 0
		if caster.level  > receiver.level:
			disLevel = ( caster.level - receiver.level ) * 0.04
		
		return max( receiver.reduce_role_damage - caster.add_role_damage - disLevel, 0.0 )
	
	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		if caster.isReal():
			Spell_ItemBuffNormal.receive( self, caster, receiver )

		self.damage = int( receiver.HP_Max * self.param1 )
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		self.damag *= rm

		receiver.receiveDamage( caster.id, self, csdefine.DAMAGE_TYPE_PHYSICS_NORMAL, self.damage )