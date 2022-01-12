# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffNormal.py,v 1.10 2008-07-04 03:50:57 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
import csconst
from Spell_BuffNormal import Spell_BuffNormal

class Spell_BuffNormal_TriggerEvent( Spell_BuffNormal ):
	"""
	�����͸���ӹ�������˵��һ���ģ���֮��ͬ���ǣ�������ڼ��ܱ��ɹ�ʹ��֮��ᴥ��һ��QTTaskEventTrigger
	����������磺�ɹ�ʹ��ĳ�����ܶ��ٴβ������һ������֮������Ӧ��
	by mushuang
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )
		self.questID = 0
		self.taskIdx = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		self.questID = int( dict[ "param1" ] )
		self.taskIdx = int( dict[ "param2" ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		Spell_BuffNormal.receive( self, caster, receiver )
		
		# ����������ϵ�����
		if caster.hasTaskIndex( self.questID, self.taskIdx ):
			caster.questTaskIncreaseState( self.questID, self.taskIdx )
		
