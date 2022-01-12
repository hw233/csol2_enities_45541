# -*- coding: gb18030 -*-


import Const

from bwdebug import *
from Spell_Item import Spell_Item
import csdefine
import csstatus
import csconst

class Spell_Reward_Quest_Item( Spell_Item ):
	"""
	��Ʒ���ܣ�ˢ����������
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
			ERROR_MSG( "RewardQuest Item��player( %s )'s item is None.uid:%s." % ( caster.getName(), uid ) )
			return

		if item.id == csconst.REWARD_QUEST_LOW_ITEM:
			receiver.rewardQuestItemRefresh( 1, csdefine.REWARD_QUEST_LOW_ITEM_REFRESH )
		elif item.id == csconst.REWARD_QUEST_HIGH_ITEM:
			receiver.rewardQuestItemRefresh( 1, csdefine.REWARD_QUEST_HIGH_ITEM_REFRESH )
