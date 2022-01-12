# -*- coding: gb18030 -*-

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
import Define
import Math
from gbref import rds
import Action
import Const
import math
import event.EventCenter as ECenter

class Spell_122285( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )
		self.speed = None
		self.yaw = None
		self.param4 = []
		self.allPlayerFlag = False

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		param1 =  dict["param1"].split(";")
		self.param1 = Math.Vector3( eval( param1[0] ) )
		if len( param1 ) == 2:
			self.yaw = float(param1[1])
		if dict["param2"] != "":
			self.param2 = float( dict["param2"] ) 
		else:
			self.param2 = 0
		self.param3 = str( dict["param3"] )	#动作
		
		param4 = dict["param4"].split(";")
		if len( param4 ) > 0:
			if param4[0] != "":
				self.param4 = [ int(i) for i in dict["param4"][0].split("|")]  	#事件ID
		if len( param4 ) > 1:
			self.allPlayerFlag = int( param4[1] ) 	#是否所有接受到的客户端都播放
		
		
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
		if self.allPlayerFlag:
			self.playAction()
		else:
			if target.id == player.id:
				self.playAction()
		
	def playAction( self ):
		player = BigWorld.player()
		player.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT )
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", False )
		player.setActionState( Action.ASTATE_DEST )
		#player.switchFlyWater( True )
		if self.param2 != 0:
			self.speed = player.move_speed
			player.setSpeed(self.param2)
		player.moveToPos( self.param1, self.__onMoveOver1 )
		BigWorld.callback( 1.0, self.__jumpBegin )

	def __jumpBegin( self ):
		"""
		"""
		player = BigWorld.player()
		if player is None: return
		if not player.isMoving(): return
		if not player.onWaterArea:
			BigWorld.callback( 0.1, self.__jumpBegin )
			return

		if player.getJumpState() != Const.STATE_JUMP_DEFAULT:
			BigWorld.callback( 0.1, self.__jumpBegin )
			return

		player.jumpBegin()
		BigWorld.callback( 0.1, self.__jumpBegin )

	def __onMoveOver1( self, success ):
		"""
		移动到目标点结束回调
		"""
		player = BigWorld.player()
		if player is None: return
		#设置转向
		if self.yaw:
			BigWorld.dcursor().yaw = self.yaw #玩家转向
			camera = rds.worldCamHandler.cameraShell  #摄像机转向
			camera.setYaw( self.yaw + math.pi, True )
		
		player.setActionState( Action.ASTATE_CONTROL )
		player.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT)
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", True )
		#player.switchFlyWater( False )
		if self.speed:
			player.setSpeed(self.speed)
		if self.param3 != "":
			rds.actionMgr.playAction( BigWorld.player().model, self.param3, 0.0, None )
			
		if self.param4 != 0:	#播放镜头事件
			rds.cameraEventMgr.triggerByClass( self.param4 )

#增加移动结束后播放动作和触发客户端镜头事件modify by wuxo 2012-2-27 