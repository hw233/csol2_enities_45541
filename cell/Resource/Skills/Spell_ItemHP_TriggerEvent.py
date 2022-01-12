# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemHP.py,v 1.10 2008-08-14 06:11:09 songpeifang Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus
from Spell_ItemHP import Spell_ItemHP

class Spell_ItemHP_TriggerEvent( Spell_ItemHP ):
	"""
	ʹ�ã����ָ̻���������ֵ1960�㡣
	"""
	def __init__( self ):
		"""
		�����͸���ӹ�������˵��һ���ģ���֮��ͬ���ǣ�������ڼ��ܱ��ɹ�ʹ��֮��ᴥ��һ��QTTaskEventTrigger
		����������磺�ɹ�ʹ��ĳ�����ܶ��ٴβ������һ������֮������Ӧ��
		by mushuang
		"""
		Spell_ItemHP.__init__( self )
		self.questID = 0
		self.taskIdx = 0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemHP.init( self, dict )
		self.questID = int( dict[ "param1" ] )
		self.taskIdx = int( dict[ "param2" ] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		Spell_ItemHP.receive( self, caster, receiver )
		
		# ����������ϵ�����
		if caster.hasTaskIndex( self.questID, self.taskIdx ):
			caster.questTaskIncreaseState( self.questID, self.taskIdx )