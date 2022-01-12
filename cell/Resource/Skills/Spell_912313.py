# -*- coding: gb18030 -*-

from bwdebug import *
from Spell_Item import Spell_Item
from Spell_TeleportBase import Spell_TeleportBase
import csstatus
import csconst
import csdefine
import BigWorld

 
class Spell_912313( Spell_Item ):
	"""
	����õ�壺�����Ѻö�
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		
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
	
		
		
		state = Spell_Item.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:	# �ȼ��cooldown������
			return state
			
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		
		# �Ѻöȵ������Ӷ�Ŀ����ж� by mushuang		
		targetEntity = target.getObject()
		
	
		# if Ŀ�겻����� :
		if not targetEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			return csstatus.FRIEND_ITEM_USED_ONLY_ON_FRIEND
			
		# if Ŀ�����Լ� 
		if caster.id == targetEntity.id :
			return csstatus.FRIEND_ITEM_USED_ONLY_ON_FRIEND
		
		# if �ж����A��ʹ���ߣ������B���Ѻù�ϵ
		caster.setTemp( "addFriendlyRequesting", True )
		caster.setTemp( "addFriendlyName",targetEntity.getName() )
		caster.base.rlt_checkAddFriendyValue( target.getObject().databaseID )
		return state
		
	def onSpellInterrupted( self, caster ):
		"""
		��ʩ�������ʱ��֪ͨ��
		��Ϻ���Ҫ��һЩ����
		"""
		Spell_Item.onSpellInterrupted( self, caster )
		caster.removeTemp( "addFriendlyRequesting" )
		
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
		caster.removeTemp( "addFriendlyRequesting" )
		casterName = caster.getName()
		receiverName = receiver.getName()
		caster.base.addItemFriendlyValue( receiver.databaseID, self._effect_max )
		receiver.base.addItemFriendlyValue( caster.databaseID, self._effect_max )
		itemName = caster.getByUid( caster.queryTemp( "item_using" ) ).name()
		caster.statusMessage( csstatus.FRIEND_ITEM_ADD_VALUE_SUCCESS, receiverName, itemName, receiverName, self._effect_max )
		receiver.client.onStatusMessage( csstatus.FRIEND_ITEM_BE_ADDED_VALUE_SUCCESS, "(\'%s\', \'%s\', \'%s\', %i)" % ( casterName, itemName, casterName, self._effect_max ) )
		