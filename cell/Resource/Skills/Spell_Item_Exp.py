# -*- coding: gb18030 -*-


import Const

from bwdebug import *
from Spell_Item import Spell_Item
from Love3 import g_itemDropLuckyBoxZhaocai
import csdefine
import csstatus

class Spell_Item_Exp( Spell_Item ):
	"""
	��Ʒ���ܣ��вƱ���
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
			ERROR_MSG( "Exp Item��player( %s )'s item is None.uid:%i." % ( caster.getName(), uid ) )
			return

		caster.addExp( item.getExp(), csdefine.CHANGE_EXP_JUE_DI_FAN_JI )
		