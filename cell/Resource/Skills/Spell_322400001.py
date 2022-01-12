# -*- coding: gb18030 -*-

from bwdebug import *
from Spell_Item import Spell_Item
import csdefine


class Spell_322400001( Spell_Item ):
	"""
	��Ʒ����ļ���
	��һ��ʹ�ô����������Ǯ�Ĺ��ܣ�
	�ڶ���ʹ����ʹ���߻���Ӧ��Ǯ��
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


	def updateItem( self, caster ):
		"""
		������Ʒ
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return

		if item.query( "hide_money", 0 ) == 0:	# ����������ûǮ�������ǵ�һ��ʹ�ã�����Ҫ������Ʒ
			caster.removeTemp( "item_using" )
			return

		caster.removeTemp( "item_using" )
		item.onSpellOver( caster )


	def receive( self, caster, receiver ):
		"""
		���շ���
		"""
		uid  = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		isCharge = item.query( "hide_money", 0 ) > 0
		if not isCharge:	# ��������ûǮ��֪ͨ��ҳ�ֵ
			receiver.client.couple_requestChargeHongbao( item.order )
			return

		receiver.addMoney( item.query( "hide_money" ), csdefine.CHANGE_MONEY_REDPACKAGE  )