# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)����ʩ����λ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *

from Spell_BuffNormal import Spell_BuffNormal

import random
import items
g_items = items.instance()

class Spell_Add_Item( Spell_BuffNormal ):
	"""
	������������һ����Ʒ1,����һ����������Ʒ1��ȡһ����Ʒ2
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )
		self.param1 = 0		#��Ʒ1 ID
		self.param2 = 1		#��Ʒ1 ����
		self.param3 = 0		#��Ʒ2 ID


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		self.param1 = int( dict["param1"] )
		self.param2 = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 )
		self.param3 = int( dict["param3"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		item = g_items.createDynamicItem( self.param1 )
		if item == None:
			Spell_BuffNormal.receive( self, caster, receiver )
			return
		receiver.addItem( item, csdefine.ADD_ITEM_REQUESTADDITEM )
		receiver.queryItemFromBagAndAddItem( self.param1, self.param2, self.param3 )
		Spell_BuffNormal.receive( self, caster, receiver )
		