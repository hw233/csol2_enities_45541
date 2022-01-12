# -*- coding: gb18030 -*-

import random
import BigWorld
import Math
import csdefine
import csstatus
import keys
import Define
import Const
import gbref
import Action

from SlaveMonster import SlaveMonster
from gbref import rds
from UnitSelect import UnitSelect
from VehicleHelper import isFlying


ACTION_MAPS = {	"walk" 			: ["ride_walk", "crossleg_walk"],
				"run" 			: ["ride_run", "crossleg_run"],
				"stand" 		: ["ride_stand", "crossleg_stand"],
				"jump_begin" 	: ["ride_jump_begin", "crossleg_jump_begin"],
				"jump_process" 	: ["ride_jump_process", "crossleg_jump_process"],
				"jump_end" 		: ["ride_jump_end", "crossleg_jump_end"],
				}
NODE_NAME = "HP_pan_01"

class SlaveDart( SlaveMonster, Action.Action ):
	"""
	�ڳ�
	"""
	def __init__( self ):
		SlaveMonster.__init__( self )
		Action.Action.__init__( self )
		self.attachModel = None
		self.rideCount = 0
		self.disDartPlayerID = 0
		self.modelType = Define.VEHICLE_MODEL_PAN

	# --------------------------------------------------
	# Engine Callback Methods
	# --------------------------------------------------
	def enterWorld( self ):
		"""
		"""
		self.setSelectable( True )

		if self.isRideOwner:
			self.onMountEntity( self.ownerID, 0 )

		SlaveMonster.enterWorld( self )

	def leaveWorld( self ):
		"""
		"""
		SlaveMonster.leaveWorld( self )
	
	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return BigWorld.AvatarFilter()

	def rideOwner( self ):
		"""
		�������ڳ��ص�
		"""
		self.rideCount += 1
		if BigWorld.player().model is not None:
			self.mountEntity( BigWorld.player(), 0 )
			self.rideCount = 0

		if self.rideCount < 20:
			BigWorld.callback( 0.2, self.rideOwner )

	def mountEntity( self, player, order ):
		"""
		"""
		# �ϳ�֮ǰҪ���������
		if player.isJumping():			#����״̬�£����������ڳ�
			return
		if player.vehicleModelNum:
			player.statusMessage( csstatus.DART_FORBID_VEHICLE )
			return
		self.cell.mountEntity( player.id, 0 )

	def disMountEntity( self, player ):
		"""
		"""
		player.resetPhysics()
		self.cell.disMountEntity( player.id )
		self.physics = keys.DUMMY_PHYSICS

	def onMountEntity( self, playerID, order ):
		"""
		define method
		"""
		if BigWorld.player().id == playerID:
			BigWorld.player().physics = keys.DUMMY_PHYSICS
			self.resetPhysics()
			pivotPosition = Const.CAMERA_PROVITE_OFFSET_TO_SLAVEDART
			minDistance = 	Const.CAMERA_MIN_DISTANCE_TO_SLAVEDART
			rds.worldCamHandler.cameraShell.setEntityTarget( self )
			rds.worldCamHandler.cameraShell.adjustToTarget( True, -0.8, pivotPosition, minDistance, 20 )

		if self.model is None: return

		role = BigWorld.entities.get( playerID )
		if role is None: return
		model = role.model
		if model is None: return
		role.setModel( None )

		model.OnActionStart = role.onActionStart

		self.model.OnActionStart = self.onActionStart
		self.model.visible = True

		rds.effectMgr.linkObject( self.model, NODE_NAME, model )
		self.onActionStart( "stand" )

	def onDisMountEntity( self, playerID, order ):
		"""
		define method
		"""
		self.onEndAutoRun( False )
		if self.model is None: return

		self.model.OnActionStart = None

		rModel = self.getAttachModel()
		rds.effectMgr.linkObject( self.model, NODE_NAME, None )

		role = BigWorld.entities.get( playerID )
		if role is None: return
		if rModel:
			role.setModel( rModel )
		else:
			role.createEquipModel()

	def getAttachModel( self, order = 0 ):
		"""
		��ȡ�ڳ��ϸ��ص�ģ��
		"""
		if self.model is None: return
		nodeName = NODE_NAME.replace("HP_", "")
		rModel = getattr( self.model, nodeName )
		return rModel

	def updateAttachModel( self, model ):
		"""
		�����ڳ��ϸ��ص�ģ��
		"""
		if self.model is None: return
		oldModel = self.getAttachModel()
		if oldModel: oldModel.OnActionStart = None
		rds.effectMgr.linkObject( self.model, NODE_NAME, model )
		self.onActionStart( "stand" )

	def resetPhysics( self ):
		"""
		"""
		self.physics = keys.STANDARD_PHYSICS
		self.physics.velocity = ( 0.0, 0.0, 0.0 )
		self.physics.velocityMouse = "Direction"
		self.physics.angular = 0
		self.physics.angularMouse = "MouseX"
		self.physics.collide = 1
		self.physics.fall = True
		self.physics.modelWidth = 0.4
		self.physics.modelDepth = 0.3
		self.physics.modelHeight = 2.5   #ͳһ�߶ȣ�����ĳЩ�����½�ɫͽ�������Ͻϵ͵�"��ͨ����"���Թ�ȥ������ɫ���Ͻϸߵ�"��ͨ����"�޷���ȥ
		self.physics.scrambleHeight = 0.5

		self.physics.isMovingNotifier = None
		self.setSpeed( self.move_speed )

	def set_move_speed( self, oldSpeed ):
		if self.isRideOwner:
			self.setSpeed( self.move_speed )

	def onActionStart( self, actionName ):
		"""
		���ģ�Ͷ����ص�
		"""
		if actionName not in ACTION_MAPS: return
		roleActionName = ACTION_MAPS[actionName][1]
		rds.actionMgr.playAction( self.getAttachModel(), roleActionName )

	def canControl( self ):
		return True

	def moveForward( self, isDown ):
		"""
		�����ǰ�ƶ�
		@param	isDown : ����Զ��尴��״̬
		@type		isDown : Bool
		"""
		if not self.canControl(): return

		self.updateDirection( Action.DIRECT_FORWARD, isDown )
		if isDown:
			#�������Ծ״̬Ҫ����Ƿ�������������ǰ��
			if self.physics.jumpState == 1 or self.physics.jumpState == 0 :
				vec = self.physics.velocity
				self.physics.velocity = ( vec[0], vec[1], self.move_speed )
				return True
			elif self.physics.jumpState == 2 :
				return True
		else:
			#�������Ծ״̬�������ٶ�
			if self.physics.jumpState != -1:
				return True
		self.flushAction()

	def moveBack( self, isDown ):
		"""
		�������ƶ�
		@param	isDown : ����Զ��尴��״̬
		@type		isDown : Bool
		"""
		if not self.canControl(): return
		self.updateDirection( Action.DIRECT_BACKWARD, isDown )
		if self.physics.jumpState != -1: return
		self.flushAction()

	def moveLeft( self, isDown ):
		"""
		��������ƶ�
		@param	isDown : ����Զ��尴��״̬
		@type		isDown : Bool
		"""
		if not self.canControl(): return
		self.updateDirection( Action.DIRECT_LEFT, isDown )
		if self.physics.jumpState != -1: return
		self.flushAction()

	def moveRight( self, isDown ):
		"""
		��������ƶ�
		@param	isDown : ����Զ��尴��״̬
		@type		isDown : Bool
		"""
		if not self.canControl(): return
		self.updateDirection( Action.DIRECT_RIGHT, isDown )
		if self.physics.jumpState != -1: return
		self.flushAction()

	def moveToCursor( self ):
		"""
		������ƶ�
		"""
		if not self.canControl(): return False
		if self.physics.jumpState != -1: return False
		toPos = gbref.cursorToDropPoint()						# ������갴�´�����ά����
		if toPos is None: return False
		self.setActionState( Action.ASTATE_DEST )
		if self.moveTo( toPos, self.__onMoveToOver ):
			UnitSelect().showMoveGuider( toPos )
		return True

	def __onMoveToOver( self, success ):
		"""
		when move to a position this method will called at seekCallback method
		"""
		UnitSelect().hideMoveGuider()

	def setCameraPivotPosition( self, order ):
		"""
		����λ����������ͷ��ƫ�Ƹ߶ȵ�
		"""
		# ��ȡ����ͷ
		camera = BigWorld.camera()
		camera.target = self.matrix
		# ��ȡ����ͷƫ�Ƹ߶�
		if self.model is None: return
		nodeName = "HP_title"
		if nodeName is None: return
		node = rds.effectMgr.accessNode( self.model, nodeName )
		if node is None: return
		y = ( Math.Matrix( node ).applyToOrigin() - self.position ).y
		# Ҫ��y < 0 ��������Ĭ�ϸ߶ȡ�
		if y <= 0:y = 1.8
		camera.pivotPosition = ( 0.0, y, 0.0 )


	def autoMoveForward( self ):
		"""
		�Զ���ǰ�ƶ�
		"""
		if self.isActionState( Action.ASTATE_AUTOFORWARD ) :
			self.setActionState( Action.ASTATE_CONTROL )
			self.stopMove()
		else :
			self.setActionState( Action.ASTATE_AUTOFORWARD )
			BigWorld.dcursor().yaw = BigWorld.camera().direction.yaw
			self.startMove()
		self.flushAction()

	def onCameraDirChanged( self, direction ):
		"""
		��������ƶ�֪ͨ
		"""
		if not self.canControl(): return
		if self.physics.jumpState != -1: return
		Action.Action.onCameraDirChanged( self, direction )


	def getRandomActions( self ):
		"""
		get the random actions.
		because the random actions have unfixed amount
		so I get the actions from random1,random2....if unsuccessful and return
		��ȡ���������������������������̶���
		��ȡ���������random1��ʼ��random2,random3....��ȡʧ���򷵻�
		"""
		if self.model is None: return
		#the range(1,10) is  provisional, because I can't find more than 2 randomActions for a entity
		for index in range(1,10):
			actName = "random"+str( index )
			if self.model.hasAction( actName ):
				self.randomActions.append( actName )
			else:
				return

	def playRandomAction( self ):
		"""
		play random Action
		"""
		#��ȡ�������������
		randomActionCount = len( self.randomActions )
		if randomActionCount == 0:
				return
		elif randomActionCount == 1:
			self.am.matchCaps = [ Define.CAPS_RANDOM, Define.CAPS_INDEX25 ]
		else:
			index = random.randint( 0, randomActionCount - 1 )
			caps = Define.CAPS_INDEX25 + index
			self.am.matchCaps = [Define.CAPS_RANDOM, caps]

		BigWorld.callback( 0.1, self.onOneShoot )


	def onBored( self, actionName ):
		"""
		�˻ص����ڲ����������
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""
		# ���action �ǿ�ʱ������fuse�����¿�ʼ��ʱ
		if actionName is None: self.am.fuse = 0
		if actionName != "stand": return
		self.playRandomAction()
		# ��һ��������ʼ����ʱ fuse ������Ϊ0
		# �����ƺ���bug����ʱ��û������ fuse ������ԣ���������������
		self.am.fuse = 0
		# ÿ֪ͨһ�� onBored  ������Զ��� patience ��Ϊһ����ֵ??
		# ֻ������ patience ֵ ���������Ĳ�ͣ���� onBored ����
		self.am.patience = random.random() * 6 + 6.0


	def jumpBegin( self ):
		"""
		"""
		pass


	def handleMouseShape( self ):
		"""
		������궯��
		"""
		
		player = BigWorld.player()

		if isFlying( player ):
			rds.ccursor.set( "normal" )
			return

		# 30����ұ���
		if player.pkState == csdefine.PK_STATE_PROTECT:
			rds.ccursor.set( "normal" )
			return

		if player.actionSign( csdefine.ACTION_FORBID_PK ):
			rds.ccursor.set( "normal" )
			return

		if player.pkMode == csdefine.PK_CONTROL_PROTECT_PEACE:
			rds.ccursor.set( "normal" )
			return

		if BigWorld.entities.has_key( self.ownerID ):
			owner = BigWorld.entities[self.ownerID]

		else:
			rds.ccursor.set( "attack" )
			return

		# ���entity�Ƕ���
		if player.isTeamMember( owner ):
			rds.ccursor.set( "normal" )
			return

		# ����ҵ�pkģʽ�Ǽ���ģʽ����entity�Ǽ����Ա
		if player.pkMode == csdefine.PK_CONTROL_PROTECT_KIN and player.family_dbID != 0 and ( owner.family_dbID == player.family_dbID ):
			rds.ccursor.set( "normal" )
			return

		# ����ҵ�pkģʽ�ǰ��ģʽ����entity�ǰ���Ա
		if player.sysPKMode and player.sysPKMode == csdefine.PK_CONTROL_PROTECT_TONG and player.tong_dbID != 0 and ( owner.tong_dbID == player.tong_dbID ):
			rds.ccursor.set( "normal" )
			return

		if player == owner:
			rds.ccursor.set( "normal" )
			return

		rds.ccursor.set( "attack" )

	def onStartAutoRun( self, position ):
		"""
		�Զ�Ѱ·��ʼ
		"""
		BigWorld.player().onStartAutoRun( position )

	def onEndAutoRun( self, state ):
		"""
		�����Զ�Ѱ·
		"""
		player = BigWorld.player()
		player.endAutoRun( state )
		player.stopMove()
		self.stopMove()

	def getNodeName( self, order ):
		"""
		����ָ��λ�û�����ģ�͵İ󶨵���
		���ݲ߻��������󶨵��2�࣬
		һ����HP_hip_*��һ���� HP_pan_*
		����2�಻�ܹ���
		return String/None
		"""
		return None

	def isSlaveDart( self ):
		"""
		������Ƿ����ڳ�
		"""
		return True

	def handleKeyEvent( self, isDown, key, mods ):
		"""
		"""
		return False