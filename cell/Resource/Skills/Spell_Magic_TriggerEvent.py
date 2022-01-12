# -*- coding: gb18030 -*-
#
# $Id: Spell_Magic.py,v 1.21 2008-09-04 07:46:27 kebiao Exp $

"""
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
from Spell_PhysSkill import Spell_PhysSkill
import SkillTargetObjImpl
from Spell_Magic import Spell_Magic

class Spell_Magic_TriggerEvent( Spell_Magic ):
	"""
	�������弼��
	"""
	def __init__( self ):
		"""
		�����͸���ӹ�������˵��һ���ģ���֮��ͬ���ǣ�������ڼ��ܱ��ɹ�ʹ��֮��ᴥ��һ��QTTaskEventTrigger
		����������磺�ɹ�ʹ��ĳ�����ܶ��ٴβ������һ������֮������Ӧ��
		by mushuang
		"""
		Spell_Magic.__init__( self )
		self.questID = 0
		self.taskIdx = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self.questID = int( dict[ "param1" ] )
		self.taskIdx = int( dict[ "param2" ] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		Spell_Magic.receive( self, caster, receiver )
		
		# ����������ϵ�����
		if caster.hasTaskIndex( self.questID, self.taskIdx ):
			caster.questTaskIncreaseState( self.questID, self.taskIdx )
