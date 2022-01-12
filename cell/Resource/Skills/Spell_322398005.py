# -*- coding: gb18030 -*-

import Const
import csdefine
from bwdebug import *
from Spell_Item import Spell_Item
from Love3 import g_itemDropLuckyBoxJinbao
import csstatus

class Spell_322398005( Spell_Item ):
	"""
	��Ʒ���ܣ���������
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
			ERROR_MSG( "�������У�player( %s )'s item is None.uid:%s." % uid )
			return

		dropType, dropInstance = g_itemDropLuckyBoxJinbao.getDropData( item.getLevel() )

		if dropType == Const.LUCKY_BOX_DROP_MONEY:
			caster.addMoney( dropInstance, csdefine.CHANGE_MONEY_LUCKYBOXJINBAO )
		elif dropType == Const.LUCKY_BOX_DROP_POTENTIAL:
			caster.addPotential( dropInstance, csdefine.CHANGE_POTENTIAL_JINBAO )
		elif dropType == Const.LUCKY_BOX_DROP_EXP:
			caster.addExp( dropInstance, csdefine.CHANGE_EXP_LUCKYBOXJINBAO )
		else:
			caster.addItem( dropInstance, csdefine.ADD_ITEM_LUCKYBOXJINBAO )
		
	def useableCheck( self, caster, target ):
		"""
		��Ҫ��һ���ո�ſ��Դ򿪱��С������޷������Ʒ
		"""
		if caster.getNormalKitbagFreeOrderCount() < 1:
			return csstatus.SKILL_USE_ITEM_NEED_ONE_BLANK
		return Spell_Item.useableCheck( self, caster, target )
		