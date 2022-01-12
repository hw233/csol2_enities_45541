# -*- coding: gb18030 -*-
#
# $Id: Spell_PhysSkill.py,v 1.18 2008-09-04 07:46:27 kebiao Exp $

"""
������Ч��
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
import SkillTargetObjImpl
from Spell_PhysSkill import Spell_PhysSkill2
from Spell_Magic import Spell_Magic
from Spell_DirectDamage import Spell_DirectPhyDamage

class Spell_DirectPhyDamage_TriggerEvent( Spell_DirectPhyDamage ):
	"""
	Ԫ���˺�����
	"""
	def __init__( self ):
		"""
		�����͸���ӹ�������˵��һ���ģ���֮��ͬ���ǣ�������ڼ��ܱ��ɹ�ʹ��֮��ᴥ��һ��QTTaskEventTrigger
		����������磺�ɹ�ʹ��ĳ�����ܶ��ٴβ������һ������֮������Ӧ��
		by mushuang
		"""
		Spell_DirectPhyDamage.__init__( self )
		self.questID = 0
		self.taskIdx = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_DirectPhyDamage.init( self, dict )
		self.questID = int( dict[ "param1" ] )
		self.taskIdx = int( dict[ "param2" ] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		Spell_DirectPhyDamage.receive( self, caster, receiver )
		
		# ����������ϵ�����
		if caster.hasTaskIndex( self.questID, self.taskIdx ):
			caster.questTaskIncreaseState( self.questID, self.taskIdx )

