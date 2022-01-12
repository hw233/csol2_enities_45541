# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemHP.py,v 1.10 2008-08-14 06:11:09 songpeifang Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus
from Spell_ItemHP import Spell_ItemHP

class Spell_ItemHP_TriggerEvent( Spell_ItemHP ):
	"""
	使用：立刻恢复自身生命值1960点。
	"""
	def __init__( self ):
		"""
		这个类和父类从功能上来说是一样的，与之不同的是：这个类在技能被成功使用之后会触发一个QTTaskEventTrigger
		用来完成诸如：成功使用某个技能多少次才能完成一个任务之类的奇怪应用
		by mushuang
		"""
		Spell_ItemHP.__init__( self )
		self.questID = 0
		self.taskIdx = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_ItemHP.init( self, dict )
		self.questID = int( dict[ "param1" ] )
		self.taskIdx = int( dict[ "param2" ] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell_ItemHP.receive( self, caster, receiver )
		
		# 触发玩家身上的任务
		if caster.hasTaskIndex( self.questID, self.taskIdx ):
			caster.questTaskIncreaseState( self.questID, self.taskIdx )