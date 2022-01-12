# -*- coding: gb18030 -*-

#edit by wuxo 2011-9-20
"""
Spell技能类。实现客户端NPC说话、播动作、播放镜头（一开始就控制玩家）
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
import Define
from gbref import rds
import Action
import Const
import event.EventCenter as ECenter

class Spell_questComplete( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )
		self.playTarget = None		#目标
		self.npcs = []     #隐藏的npc的classname
		self.entities = []
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict["param1"] == "":
			self.param1 = ()
		else:
			self.param1 = eval( dict["param1"] ) 	#NPC说话表现
		if dict["param2"] == "":
			self.param2 = ()
		else:
			self.param2 = eval( dict["param2"] ) 	#NPC动作播放
		if dict["param3"] == "":
			self.param3 = ()
			self.npcs = []
		else:
			param3 = dict["param3"].split(";")
			self.param3 = eval( param3[0] ) 	#镜头播放，是否隐藏NPC
			if len(param3) > 1:
				self.npcs = param3[1:]
			
	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		player = BigWorld.player()
		target = targetObject.getObject()
		self.playTarget = target
		
		#增加一开始就控制玩家客户端并隐藏Ui
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", 0 )
		if player:
			player.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT )
			player.addControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA,Define.CONTROL_FORBID_ROLE_CAMERA_EVENT )
		
		if self.playTarget != None:	#NPC说话
			if len(self.param1) == 2 and self.param1[1] >= 0:
				BigWorld.callback(self.param1[1],self.playNPCSay)
			if len(self.param2) == 2 and self.param2[1] >= 0:
				model = self.playTarget.getModel()
				rds.actionMgr.playAction( model, self.param2[0], self.param2[1], None )
		if caster.id == player.id:	#只在自己的客户端播放镜头
			if len(self.param3) == 4 and self.param3[2] >= 0:
				BigWorld.callback(self.param3[2], self.playCamera)
	
	def playNPCSay(self):
		"""
		nPC说话
		"""
		self.playTarget.onSay( self.playTarget.getName(), self.param1[0] )
		
	
	def playCamera( self ):
		"""
		播放镜头
		"""
		rds.cameraEventMgr.trigger( self.param3[0] )
		p = BigWorld.player()
		for en in p.entitiesInRange( 50 ):
			if hasattr( en, "className" ) and en.className in self.npcs:
				self.entities.append(en)
		
		if self.param3[1] == 1:
			self.entities.append(p)
		
		for e in self.entities:
			e.setVisibility( False )
		
		if self.param3[3] > 0:	#隐藏多久
			BigWorld.callback( self.param3[3], self.showTargetModdel )	

	def showTargetModdel( self ):
		"""
		显示目标模型
		"""
		for e in self.entities:
			e.setVisibility( True )
			