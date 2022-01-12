# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.83 2008-02-20 04:11:34 zhangyuxing Exp $

"""
Base class for all NPC
NPC����
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
	NPC����
	"""
	def __init__( self ):
		"""
		��ʼ��
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
		Ŀ�꽹���¼�
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
		Monster.onTargetFocus( self )

	# Quitting as target
	def onTargetBlur( self ):
		"""
		�뿪Ŀ���¼�
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		Monster.onTargetBlur( self )

	def isInteractionRange( self, entity ):
		"""
		�ж�һ��entity�Ƿ����Լ��Ľ�����Χ��
		"""
		return self.position.flatDistTo( entity.position ) < self.getRoleAndNpcSpeakDistance()

	# ----------------------------------------------------------------
	# ģ�����
	# ----------------------------------------------------------------

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ��
		�̳� Monster.createModel
		"""
		Monster.createModel( self, event )

	def onModelChange( self, oldModel, newModel ):
		"""
		ģ�͸���֪ͨ
		"""
		if newModel is None: return
		Monster.onModelChange( self, oldModel, newModel )
		if self.className == Const.MASTER_NPC_CLASSNAME:	# ��������ģ��Ĭ�϶���stand_1
			rds.actionMgr.playAction( newModel, Const.MODEL_ACTION_STAND_1 )

#----------------------------------------------------
	def setVoiceDelate( self ):
		"""
		NPC������ʱ����
		"""
		self.voiceBan = True
		self.voiceTimerID = BigWorld.callback( 3.0, self.onVoiceDelateComplete )

	def onVoiceDelateComplete( self ):
		"""
		NPC������ʱ����
		"""
		self.voiceTimerID = 0
		self.voiceBan = False


# NPC.py
