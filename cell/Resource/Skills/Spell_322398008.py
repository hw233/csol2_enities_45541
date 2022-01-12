# -*- coding: gb18030 -*-


import Const

from bwdebug import *
from Spell_Item import Spell_Item
from Love3 import g_honorItemZhaocai
import csdefine
import ItemTypeEnum
import csstatus

class Spell_322398008( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )


	def receive( self, caster, receiver ):
		"""
		virtual method.
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		# ����caster���ϵı�����Ʒ�������Ҽ��ϻ�õ���Ʒ
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "�������滻��player( %s )'s item is None.uid:%i." % ( caster.getName(), uid ) )
			return
		
		dropType		= caster.queryTemp( "Honor_dropType" )
		dropInstance 	= caster.queryTemp( "Honor_dropInstance" )
		
		
		if dropType == Const.LUCKY_BOX_DROP_MONEY:
			caster.addMoney( dropInstance, csdefine.CHANGE_MONEY_YYD_BOX )
		elif dropType == Const.LUCKY_BOX_DROP_POTENTIAL:
			caster.addPotential( dropInstance, csdefine.CHANGE_POTENTIAL_YYD_BOX )
		elif dropType == Const.LUCKY_BOX_DROP_EXP:
			caster.addExp( dropInstance, csdefine.CHANGE_EXP_YYD_BOX )
		else:
			dropInstance.setBindType( ItemTypeEnum.CBT_PICKUP )
			caster.addItem( dropInstance, csdefine.ADD_ITEM_YYD_BOX )


	def useableCheck( self, caster, target ):
		"""
		��Ҫ��һ���ո�ſ��Դ�ʥ�����ӡ������޷������Ʒ
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		dropType, dropInstance = g_honorItemZhaocai.getDropData( item.getLevel() )
		
		if dropType in [Const.LUCKY_BOX_DROP_NORMAL_ITEM, Const.HONOR_ITEM]:
			if caster.checkItemsPlaceIntoNK_( [dropInstance] ) != csdefine.KITBAG_CAN_HOLD:
				caster.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
				return False
		caster.setTemp( "Honor_dropType", dropType )
		caster.setTemp( "Honor_dropInstance", dropInstance )

		return Spell_Item.useableCheck( self, caster, target )