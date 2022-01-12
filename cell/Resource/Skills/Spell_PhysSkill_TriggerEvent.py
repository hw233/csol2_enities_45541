# -*- coding: gb18030 -*-
#
# $Id: Spell_PhysSkill.py,v 1.18 2008-09-04 07:46:27 kebiao Exp $

"""
持续性效果
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
import SkillTargetObjImpl
from Spell_PhysSkill import Spell_PhysSkill

class Spell_PhysSkill_TriggerEvent( Spell_PhysSkill ):
	"""
	这个类和父类从功能上来说是一样的，与之不同的是：这个类在技能被成功使用之后会触发一个QTTaskEventTrigger
	用来完成诸如：成功使用某个技能多少次才能完成一个任务之类的奇怪应用
	by mushuang
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill.__init__( self )
		self.questID = 0
		self.taskIdx = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
		self.questID = int ( dict[ "param1" ] )
		self.taskIdx = int( dict[ "param2" ] )
	
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell_PhysSkill.receive( self, caster, receiver )
		
		# 触发玩家身上的任务
		if caster.hasTaskIndex( self.questID, self.taskIdx ):
			caster.questTaskIncreaseState( self.questID, self.taskIdx )


