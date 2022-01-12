# -*- coding: gb18030 -*-
#实现触发镜头
#edit by wuxo 2012-4-24
import BigWorld
from gbref import rds
from Spell_Item import Spell_Item

class Spell_QuestItem_Position( Spell_Item ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置 
		@type dict:				python dict
		"""
		Spell_Item.init( self, dict )
		
		if dict["param5"] != "":
			self.param5 = [ int(i) for i in dict["param5"].split("|")]
		else:
			self.param5 = []
		
		
	def cast( self, caster, targetObject ):
		player = BigWorld.player()
		target = targetObject.getObject()
		if target == player and len(self.param5) != 0 :
			rds.cameraEventMgr.triggerByClass( self.param5 )
		Spell_Item.cast( self, caster, targetObject )
			