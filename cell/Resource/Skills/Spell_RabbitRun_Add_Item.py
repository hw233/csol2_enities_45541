# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)����ʩ����λ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *

from Spell_Rabbit_Run import Spell_Rabbit_Run

ITEM_IDs = [50101141]
import random
import items
g_items = items.instance()

class Spell_RabbitRun_Add_Item( Spell_Rabbit_Run ):
	"""
	ϵͳ����
	����һ��AreaRestrictTransducer��entity(���幦��entity)
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Rabbit_Run.__init__( self )
		self.param1 = 0		#��ƷID


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Rabbit_Run.init( self, dict )
		self.param1 = int( dict["param1"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		item = g_items.createDynamicItem( self.param1 , 1 )
		receiver.addItem( item, csdefine.ADD_ITEM_RABBIT_RUN )
		Spell_Rabbit_Run.receive( self, caster, receiver )