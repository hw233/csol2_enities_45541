# -*- coding: gb18030 -*-

"""
Spell�����ࡣ
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
		��python dict����SkillBase
		"""
		Spell.__init__( self )
		self.speed = None
		self.yaw = None
		self.param4 = []
		self.allPlayerFlag = False

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
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
		self.param3 = str( dict["param3"] )	#����
		
		param4 = dict["param4"].split(";")
		if len( param4 ) > 0:
			if param4[0] != "":
				self.param4 = [ int(i) for i in dict["param4"][0].split("|")]  	#�¼�ID
		if len( param4 ) > 1:
			self.allPlayerFlag = int( param4[1] ) 	#�Ƿ����н��ܵ��Ŀͻ��˶�����
		
		
	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
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
		�ƶ���Ŀ�������ص�
		"""
		player = BigWorld.player()
		if player is None: return
		#����ת��
		if self.yaw:
			BigWorld.dcursor().yaw = self.yaw #���ת��
			camera = rds.worldCamHandler.cameraShell  #�����ת��
			camera.setYaw( self.yaw + math.pi, True )
		
		player.setActionState( Action.ASTATE_CONTROL )
		player.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT)
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", True )
		#player.switchFlyWater( False )
		if self.speed:
			player.setSpeed(self.speed)
		if self.param3 != "":
			rds.actionMgr.playAction( BigWorld.player().model, self.param3, 0.0, None )
			
		if self.param4 != 0:	#���ž�ͷ�¼�
			rds.cameraEventMgr.triggerByClass( self.param4 )

#�����ƶ������󲥷Ŷ����ʹ����ͻ��˾�ͷ�¼�modify by wuxo 2012-2-27 