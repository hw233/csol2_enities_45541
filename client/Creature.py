# -*- coding: gb18030 -*-

# $Id: Creature.py,v 1.15 2008-08-01 08:13:06 zhangyuxing Exp $


"""
"""

import random
import Math
import BigWorld
import csdefine
import Define
from bwdebug import *
from keys import *
from interface.GameObject import GameObject
from gbref import rds
from Function import Functor
from navigate import NavDataMgr

# --------------------------------------------------------------------
# implement preview role
# --------------------------------------------------------------------
class Creature( GameObject ) :
	def __init__( self ) :
		GameObject.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_MISC
		self.setSelectable( False )
		self.Patrol_OldNode = None
		self.__navPath = []		#nav path
		self.__useNavEvent = False
		self.__AIFn = None		#point to the ai function, PS: Function Type: def __funName( self ):
		self.thinkTimerID = -1

	def __findDropPoint( self, point ):
		"""
		ʰȡ���洦��
		@type		point: Vector3
		@param		point: �д�ʰȡ����ĵ�
		"""
		testPos = Math.Vector3( point )
		testPos.y += 3
		dp = BigWorld.findDropPoint( self.spaceID, testPos )
		if dp is not None:
			testPos.y = dp[0].y
		else:
			testPos.y = point.y
		return testPos

	def __clearNavEvent( self ):
		"""
		���navigate��ص��¼�
		"""
		self.__navPath = []

	def __getNavPath( self ):
		"""
		��ȡ��self.position(�������˵�)��self.spawnPosΪԭ��self.radius��Χ�ڵ�Ŀ�ĵ�(�����˵�),
		��Vector3��ɵ�list·��.û��·��ʱ,���ؿ�list
		"""
		dstPos = Math.Vector3( self.spawnPos.x + random.uniform( -self.radius, self.radius ),
				self.spawnPos.y,
				self.spawnPos.z + random.uniform( -self.radius, self.radius ) )
		srcPos = self.position
		goalPosLst = NavDataMgr.instance().canNavigateTo( srcPos, dstPos )
		if len( goalPosLst ) <= 0:
			return []
		return NavDataMgr.instance().simpleFindPath( srcPos, goalPosLst[0] )

	def __getAIFn( self ):
		"""
		���ݲ�ͬ����,����һ�����ʵ�AI������,û�к��ʵĺ���ʱ,����None
		"""
		if not hasattr( self, 'radius'):
			return None
		if self.radius < 1.0:		# �뾶С��1�׾�û���ƶ��������ˣ����ѱ����ƶ������壩
			return None

		#�ݶ�����:���ȿ���Ѳ����Ϊ,���navigate����ƶ���Ϊ,����ʱ����ƶ���Ϊ
		#������Щ��Ϊ�¼�,�����Ժ���չ������AI�¼���
		if hasattr( self, "patrolPathNode" ) and hasattr( self, "patrolList" ):
			if len( self.patrolPathNode ) > 0 and self.patrolList is not None:
				return self.__eventPatrol

		if self.__useNavEvent:
			return self.__eventNavigate

		return self.__eventPromenade

	def __eventNavigate( self ):
		"""
		����navigate���ݽ����ƶ�
		"""
		if len( self.__navPath ) == 0:
			self.__navPath = self.__getNavPath()

		if len( self.__navPath ) == 0:
			self.onPdSeekNotify( False )
			return

		dstPos = self.__findDropPoint( self.__navPath.pop( 0 ) )
		timeout = 1.5 * dstPos.distTo( self.position ) / self.walkSpeed
		yaw = ( dstPos - self.position ).yaw
		self.physics.seek( ( dstPos.x, dstPos.y, dstPos.z,yaw ), timeout, 10, self.onPdSeekNotify )
		self.updateVelocity( True )

	def __eventPatrol( self ):
		"""
		ִ��һ���µ�Ѳ����Ϊ
		@param  startNode:  patrolPathNode ��ʼ�����ĵ�
		@type   startNode:  string
		@param  patrolList: PatrolPathʵ��
		@type   patrolList: PATROL_PATH
		"""
		if not self.patrolList.isReady():	# �����Դ��û�б����� ��ô����True ������׼��������Ѳ��
			BigWorld.callback( 1, self.onSeekNotify )
			return True

		# �õ���һ�����ӵ�
		patrolInfo = self.patrolList.nodesTraversableFrom( self.patrolPathNode )
		patrolCount = len( patrolInfo )

		if patrolCount == 1:
			# ���ֻ��һ�����ӵ� ( ͨ���ǵ������� ����˫�������һ����֧ĩ�˵ķ��ص� )
			#self.setTemp( "Patrol_gotoNode", patrolInfo[ 0 ][ 0 ] )
			self.Patrol_OldNode = self.patrolPathNode
			self.patrolPathNode = patrolInfo[ 0 ][ 0 ]
			distance = ( self.position - patrolInfo[ 0 ][ 1 ] ).length
			timeout = 1.5 * distance / self.walkSpeed
			self.moveTo(  patrolInfo[ 0 ][ 1 ], self.onSeekNotify )
		elif patrolCount >= 2:
			# ����ͨ���Ƕ�������
			patrolInfoList = list( patrolInfo )
			while patrolCount > 0:
				idx = random.randint( 0, patrolCount - 1 )
				if patrolInfoList[ idx ][ 0 ] in [ self.patrolPathNode, self.Patrol_OldNode ]:	#����Ϊ��ǰ�����һ�εĵ�
					patrolInfoList.pop( idx )
					patrolCount -= 1
					continue
				#self.setTemp( "Patrol_gotoNode", patrolInfoList[ idx ][ 0 ] )
				self.Patrol_OldNode = self.patrolPathNode
				self.patrolPathNode = patrolInfoList[ idx ][ 0 ]
				self.moveTo(  patrolInfoList[ idx ][ 1 ], self.onSeekNotify )
				break
		else:
			# ����ͨ��������һ�����������ĩ�� �޷��ҵ���һ������
			return False
		return True

	def __eventPromenade( self ):
		"""
		����ƶ�.PS:��ҪSIMPLE_PHYSICS������֧��,�����Ƕ��ģ�ͻ��ߵر�����
		"""
		# �����ƶ���Ŀ��λ��
		x = self.spawnPos.x + random.uniform( -self.radius, self.radius )
		z = self.spawnPos.z + random.uniform( -self.radius, self.radius )
		y = self.spawnPos.y

		# �ҳ�Ŀ��λ�õĸ߶�,�Ա����ƶ����ص�����ȥ
		collide = BigWorld.collide( self.spaceID, ( x, y + 10, z ), ( x, y - 10, z ) )
		if collide is None:
			self.onPdSeekNotify( False )
			return
		y = collide[0].y

		# ���㳬ʱ
		pos = Math.Vector3( x,y,z )
		distance = ( self.position - (x,y,z) ).length
		timeout = 1.5 * distance / self.walkSpeed
		# ����yaw
		yaw = ( pos - self.position ).yaw

		self.physics.seek( ( x,y,z,yaw ), timeout, 10, self.onPdSeekNotify )
		self.updateVelocity( True )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		prerep = []
		path = rds.npcModel.getModelSources( self.modelNumber )
		prerep.extend( path )
		return prerep

	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return BigWorld.AvatarDropFilter()	# ����AvatarFilter

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if not self.inWorld:
			return

		self.am = BigWorld.ActionMatcher( self )
		self.am.matchCaps = [Define.CAPS_DEFAULT,]
		self.am.boredNotifier = self.onBored
		self.am.patience = random.random() * 6 + 6.0
		self.am.fuse = random.random() * 6 + 6.0
		# about model
		self.randomActions = []
		self.createModel( Define.MODEL_LOAD_ENTER_WORLD )
		self.spawnPos = Math.Vector3( self.position )		# ���Ʋ���¼�Լ��ĳ�����
		GameObject.onCacheCompleted( self )

		# �����ԣ���1.8.6.8���У�ֱ�ӳ�ʼ��physics�Ѿ����ٱ�����
		self.initProfile()

	def leaveWorld( self ):
		"""
		This method is called when the entity leaves the world
		"""
		if self.thinkTimerID != -1:
			BigWorld.cancelCallback( self.thinkTimerID )
		if not self.clonedEntity:
			return
		GameObject.leaveWorld( self )
		BigWorld.controlEntity( self, False )


	def onTargetFocus( self ) :
		"""
		when the mouse enter my body, it will be called
		"""
		pass

	def onTargetBlur( self ) :
		"""
		when the mouse leave my body, it will be called
		"""
		pass

	def onTargetClick( self, sender ) :
		"""
		when the left mouse button click in my body, it will be called
		"""
		pass

	def initProfile( self ) :
		"""
		set me as control entity
		"""
		if not self.inWorld:	# ��ĳЩ�����ȷʵ���������(bw1868)
			BigWorld.callback( 1.0, self.initProfile )
			return
		BigWorld.controlEntity( self, True )

		self.physics = ONLYMOVE_PHYSICS									#defined in keys.py
		self.physics.lodDistance = 60.0									#Ĭ��ֵΪ60m
		self.__useNavEvent = True

		self.physics.userDirected = False
		#self.physics.velocity = ( 0.0, 0.0, 0.0 )
		#self.physics.velocityMouse = "Direction"
		#self.physics.angular = 0
		#self.physics.angularMouse = "MouseX"
		self.physics.collide = True
		self.physics.gravity = 10
		self.physics.fall = True
		self.physics.isMovingNotifier = self.onMovingNotify
		self.__AIFn = self.__getAIFn()
		if callable( self.__AIFn ):
			self.thinkTimerID = BigWorld.callback( random.uniform( 2, 10 ), self.think )

	def onMovingNotify( self, isMoving ) :
		"""
		it is called whenever the entity transitions between moving and not moving or from not moving to moving.
		"""
		if not self.inWorld: return
		if self.model is None: return
		if not self.model.inWorld: return

		for actionName in self.model.queue:
			rds.actionMgr.stopAction( self.model, actionName )

	def onSeekNotify( self, state ) :
		"""
		@param state: which is 1 if the seek succeeded, 0 otherwise.
		"""
		self.updateVelocity( False )
		self.think()

	def onPdSeekNotify( self, state ):
		"""
		�����߶���ɺ�ͨ��
		"""
		if state == False:
			self.__clearNavEvent()
		self.updateVelocity( False )
		self.thinkTimerID = BigWorld.callback( random.uniform( 1, 10 ), self.think )


	def think( self ):
		"""
		"""
		if not self.inWorld:	# ��ĳЩ����´�����ȷʵ�ᷢ��(bw1868)
			self.thinkTimerID = BigWorld.callback( random.uniform( 1, 10 ), self.think )
			return
		if callable( self.__AIFn ):
			self.__AIFn()

	def stopMove( self ) :
		"""
		template method.
		stop moving
		@return				: None
		"""
		self.__clearNavEvent()
		if self.physics.seeking:
			self.physics.seek( None, 0, 0, None )
		self.physics.stop()

	# --------------------------------------------------
	# �ƶ���ָ������
	# --------------------------------------------------
	def moveTo( self, position, callback = None ) :
		"""
		seek to anywhere
		@type		position 		: tuple
		@param		position 		: destination position
		@type		nearby			: float
		@param		nearby			: how far close to the psotion
		@return				 		: None
		"""
		distance = ( position - self.position ).length
		timeout = 1.5 * distance / self.walkSpeed
		# ����yaw
		position = Math.Vector3( position )
		yaw = ( position - self.position ).yaw
		self.physics.seek( ( position[0],position[1],position[2],yaw ), timeout, 10,  callback )
		self.updateVelocity(True)

	def updateVelocity( self, isMove ):
		"""
		"""
		if not isMove:
			self.physics.velocity = ( 0, 0, 0 )
			return

		self.physics.velocity = ( 0, 0, self.walkSpeed )

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		����ģ��
		"""
		# ��ȡģ��
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
		
	def __onModelLoad( self, event, model ):
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
		self.setModel( model, event )

		# ����action match,ȷ��ģ�͸ı䲻��Ӱ�� ActionMatch
		am = self.am
		if am.owner != None: am.owner.delMotor( am )
		self.model.motors = ( am, )

		# ��ȡ��ģ�͵��漴����
		self.getRandomActions()

		# ��̬ģ�͵ķŴ�������� action match ֮����������ᱻ��ԭ
		self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )

	def getRandomActions( self ):
		"""
		get the random actions.
		because the random actions have unfixed amount
		so I get the actions from random1,random2....if unsuccessful and return
		��ȡ���������������������������̶���
		��ȡ���������random1��ʼ��random2,random3....��ȡʧ���򷵻�
		"""
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

	def onOneShoot( self ):
		"""
		<oneShot>
		Setting this to TRUE means that the Action Matcher will not continue
		playing that action past one cycle of it, if it is no longer triggered,
		but a <cancel> section was keeping it active.
		"""
		# ����Ѳ�����Ұ�����
		if not self.inWorld: return
		self.am.matchCaps = [Define.CAPS_DEFAULT]

	def onBored( self, actionName ):
		"""
		�˻ص����ڲ����������
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""
		if actionName != "stand": return
		self.playRandomAction()
		# ��һ��������ʼ����ʱ fuse ������Ϊ0
		# �����ƺ���bug����ʱ��û������ fuse ������ԣ���������������
		self.am.fuse = 0
		# ÿ֪ͨһ�� onBored  ������Զ��� patience ��Ϊһ����ֵ??
		# ֻ������ patience ֵ ���������Ĳ�ͣ���� onBored ����
		self.am.patience = random.random() * 6 + 6.0

# Creature.py
