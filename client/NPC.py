# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.83 2008-02-20 04:11:34 zhangyuxing Exp $

"""
Base class for all NPC
NPC基类
"""

import BigWorld
from bwdebug import *
import GUIFacade
from Monster import Monster
import csdefine
import event.EventCenter as ECenter
from gbref import rds
import Define
import Const

ACTION_MAPS = {	"walk" 			: [ "ride_walk", "crossleg_walk"],
				"run" 			: [ "ride_run", "crossleg_run" ],
				"stand"			: [ "ride_stand", "crossleg_stand" ],
					}

class NPC( Monster ):
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )
		self.setSelectable( True )

	# ----------------------------------------------------------------
	def enterWorld( self ):
		"""
		This method is called when the entity enter the world
		"""
		Monster.enterWorld( self )

	def leaveWorld( self ):
		"""
		This method is called when the entity leaves the world
		"""
		Monster.leaveWorld( self )

	def onTargetFocus( self ):
		"""
		目标焦点事件
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
		Monster.onTargetFocus( self )

	# Quitting as target
	def onTargetBlur( self ):
		"""
		离开目标事件
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		Monster.onTargetBlur( self )

	def isInteractionRange( self, entity ):
		"""
		判断一个entity是否在自己的交互范围内
		"""
		return self.position.flatDistTo( entity.position ) < self.getRoleAndNpcSpeakDistance()

	# ----------------------------------------------------------------
	# 模型相关
	# ----------------------------------------------------------------

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		创建模型
		继承 Monster.createModel
		"""
		Monster.createModel( self, event )

	def onModelChange( self, oldModel, newModel ):
		"""
		模型更换通知
		"""
		if newModel is None: return
		Monster.onModelChange( self, oldModel, newModel )
		if self.className == Const.MASTER_NPC_CLASSNAME:	# 城主雕像模型默认动作stand_1
			rds.actionMgr.playAction( newModel, Const.MODEL_ACTION_STAND_1 )

#----------------------------------------------------
	def setVoiceDelate( self ):
		"""
		NPC发音延时控制
		"""
		self.voiceBan = True
		self.voiceTimerID = BigWorld.callback( 3.0, self.onVoiceDelateComplete )

	def onVoiceDelateComplete( self ):
		"""
		NPC发音延时结束
		"""
		self.voiceTimerID = 0
		self.voiceBan = False


# NPC.py
