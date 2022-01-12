# -*- coding:gb18030 -*-

from Spell_Item import Spell_Item
import csstatus
from bwdebug import *

class Spell_344029( Spell_Item ):
	"""
	������Ұ﹩
	"""
	def __init__( self ):
		Spell_Item.__init__( self )
		self.tongContribute = 0
		
	def init( self, data ):
		Spell_Item.init( self, data )
		self.tongContribute = int( data["param1"] ) if len( data["param1"] ) else 0
		
	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		roleEntity = target.getObject()
		if roleEntity is None or not hasattr( roleEntity, "tong_addContribute" ):
			ERROR_MSG( "targetEnity( %s ) is not Role" % roleEntity.getName() )
			return csstatus.SKILL_CANT_CAST_ENTITY
		if not roleEntity.isJoinTong():
			return csstatus.SKILL_ITEM_ADD_NOT_TONG_ATTRIBUTE
		return Spell_Item.useableCheck( self, caster, target )
		
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
		receiver.tong_addContribute( self.tongContribute )
		Spell_Item.receive( self, caster, receiver )