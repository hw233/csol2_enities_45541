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
		拾取地面处理
		@type		point: Vector3
		@param		point: 有待拾取地面的点
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
		清空navigate相关的事件
		"""
		self.__navPath = []

	def __getNavPath( self ):
		"""
		获取从self.position(不包括此点)到self.spawnPos为原点self.radius范围内的目的点(包括此点),
		有Vector3组成的list路径.没有路径时,返回空list
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
		根据不同配置,查找一个合适的AI处理函数,没有合适的函数时,返回None
		"""
		if not hasattr( self, 'radius'):
			return None
		if self.radius < 1.0:		# 半径小于1米就没有移动的意义了（很难表现移动的意义）
			return None

		#暂定方案:优先考虑巡逻行为,其次navigate随机移动行为,接着时随机移动行为
		#保留这些行为事件,方便以后扩展或配置AI事件用
		if hasattr( self, "patrolPathNode" ) and hasattr( self, "patrolList" ):
			if len( self.patrolPathNode ) > 0 and self.patrolList is not None:
				return self.__eventPatrol

		if self.__useNavEvent:
			return self.__eventNavigate

		return self.__eventPromenade

	def __eventNavigate( self ):
		"""
		采用navigate数据进行移动
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
		执行一个新的巡逻行为
		@param  startNode:  patrolPathNode 开始出发的点
		@type   startNode:  string
		@param  patrolList: PatrolPath实例
		@type   patrolList: PATROL_PATH
		"""
		if not self.patrolList.isReady():	# 如果资源还没有被加载 那么返回True 等数据准备好了再巡逻
			BigWorld.callback( 1, self.onSeekNotify )
			return True

		# 得到下一个连接点
		patrolInfo = self.patrolList.nodesTraversableFrom( self.patrolPathNode )
		patrolCount = len( patrolInfo )

		if patrolCount == 1:
			# 如果只有一个连接点 ( 通常是单向连点 或者双向连点的一个分支末端的返回点 )
			#self.setTemp( "Patrol_gotoNode", patrolInfo[ 0 ][ 0 ] )
			self.Patrol_OldNode = self.patrolPathNode
			self.patrolPathNode = patrolInfo[ 0 ][ 0 ]
			distance = ( self.position - patrolInfo[ 0 ][ 1 ] ).length
			timeout = 1.5 * distance / self.walkSpeed
			self.moveTo(  patrolInfo[ 0 ][ 1 ], self.onSeekNotify )
		elif patrolCount >= 2:
			# 这里通常是多向连点
			patrolInfoList = list( patrolInfo )
			while patrolCount > 0:
				idx = random.randint( 0, patrolCount - 1 )
				if patrolInfoList[ idx ][ 0 ] in [ self.patrolPathNode, self.Patrol_OldNode ]:	#不能为当前点和上一次的点
					patrolInfoList.pop( idx )
					patrolCount -= 1
					continue
				#self.setTemp( "Patrol_gotoNode", patrolInfoList[ idx ][ 0 ] )
				self.Patrol_OldNode = self.patrolPathNode
				self.patrolPathNode = patrolInfoList[ idx ][ 0 ]
				self.moveTo(  patrolInfoList[ idx ][ 1 ], self.onSeekNotify )
				break
		else:
			# 这里通常可能是一个单向连点的末端 无法找到下一个点了
			return False
		return True

	def __eventPromenade( self ):
		"""
		随机移动.PS:需要SIMPLE_PHYSICS的物理支持,否则会嵌入模型或者地表里面
		"""
		# 计算移动的目标位置
		x = self.spawnPos.x + random.uniform( -self.radius, self.radius )
		z = self.spawnPos.z + random.uniform( -self.radius, self.radius )
		y = self.spawnPos.y

		# 找出目标位置的高度,以避免移动到地底下面去
		collide = BigWorld.collide( self.spaceID, ( x, y + 10, z ), ( x, y - 10, z ) )
		if collide is None:
			self.onPdSeekNotify( False )
			return
		y = collide[0].y

		# 计算超时
		pos = Math.Vector3( x,y,z )
		distance = ( self.position - (x,y,z) ).length
		timeout = 1.5 * distance / self.walkSpeed
		# 计算yaw
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
		创建entity的filter模块
		"""
		return BigWorld.AvatarDropFilter()	# 代替AvatarFilter

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
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
		self.spawnPos = Math.Vector3( self.position )		# 复制并记录自己的出生点
		GameObject.onCacheCompleted( self )

		# 经测试，在1.8.6.8版中，直接初始化physics已经不再崩溃。
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
		if not self.inWorld:	# 在某些情况下确实会出此问题(bw1868)
			BigWorld.callback( 1.0, self.initProfile )
			return
		BigWorld.controlEntity( self, True )

		self.physics = ONLYMOVE_PHYSICS									#defined in keys.py
		self.physics.lodDistance = 60.0									#默认值为60m
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
		自由走动完成后通报
		"""
		if state == False:
			self.__clearNavEvent()
		self.updateVelocity( False )
		self.thinkTimerID = BigWorld.callback( random.uniform( 1, 10 ), self.think )


	def think( self ):
		"""
		"""
		if not self.inWorld:	# 在某些情况下此问题确实会发生(bw1868)
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
	# 移动到指定坐标
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
		# 计算yaw
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
		创建模型
		"""
		# 获取模型
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
		
	def __onModelLoad( self, event, model ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		self.setModel( model, event )

		# 设置action match,确保模型改变不会影响 ActionMatch
		am = self.am
		if am.owner != None: am.owner.delMotor( am )
		self.model.motors = ( am, )

		# 获取该模型的随即动作
		self.getRandomActions()

		# 动态模型的放大必须在置 action match 之后做，否则会被复原
		self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )

	def getRandomActions( self ):
		"""
		get the random actions.
		because the random actions have unfixed amount
		so I get the actions from random1,random2....if unsuccessful and return
		获取随机动作，由于随机动作数量不固定，
		获取随机动作从random1开始，random2,random3....获取失败则返回
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
		#获取随机动作的数量
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
		# 如果已不在视野则过滤
		if not self.inWorld: return
		self.am.matchCaps = [Define.CAPS_DEFAULT]

	def onBored( self, actionName ):
		"""
		此回调用于播放随机动作
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""
		if actionName != "stand": return
		self.playRandomAction()
		# 当一个动作开始播放时 fuse 会重置为0
		# 引擎似乎有bug，有时候并没有重置 fuse 这个属性，现在在这里重置
		self.am.fuse = 0
		# 每通知一次 onBored  引擎会自动把 patience 设为一个负值??
		# 只有重置 patience 值 才能连续的不停调用 onBored 方法
		self.am.patience = random.random() * 6 + 6.0

# Creature.py
