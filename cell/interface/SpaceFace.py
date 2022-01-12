# -*- coding: gb18030 -*-
#
# $Id: SpaceFace.py,v 1.15 2008-08-30 09:21:16 yangkai Exp $

"""
Player Cell for SPACE Face
2007/07/19: tidied up by huangyongwei
"""

from bwdebug import *
import BigWorld
import Language
from ECBExtend import *
import csconst
import csstatus
import csdefine
import Const
import Math
import math
import utils
from ObjectScripts.GameObjectFactory import g_objFactory
from MsgLogger import g_logger

from ObjectScripts.SpaceCopy  import SpaceCopy

ILLEGALITY_POSITION_Y_AXIS = -99999

# player id, space name, time
TELEPORT_KEY = "SPACE WATCH DOG: %s.[player id %i, player name %s, space %s, at %f]"

# 假设位面传送结束后，前进了1秒的距离
GUESS_TIME = 1

class SpaceFace:
	"""
	player in cell
	"""
	def __init__( self ):
		pass


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onEnterSpace_( self ):
		"""
		当玩家进入某空间，该方法被调用
		"""
		self.spaceType = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		print "++++++ entering space!"
		print TELEPORT_KEY % ("player entered space", self.id, self.getName(), self.spaceType, BigWorld.time())
		spaceBase = self.getCurrentSpaceBase()

		try:
			cellMailbox = BigWorld.entities[spaceBase.id]
		except KeyError:
			cellMailbox = spaceBase.cell
		space = g_objFactory.getObject( self.spaceType )
		cellMailbox.onEnter( self.base, space.packedSpaceDataOnEnter( self ) )

	def onLeaveSpace_( self ):
		"""
		当玩家离开某空间，该方法被调用
		"""
		# 取得entity当前所在的space的space entity base
		# 如果找到了则返回相应的base，找不到则返回.
		# 找不到的原因通常是因为space处于destoryed中，而自己还没有收到转移通知或destroy.
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % self.spaceID]
		except KeyError:
			return

		try:
			cellMailbox = BigWorld.entities[spaceBase.id]
		except KeyError:
			cellMailbox = spaceBase.cell

		# 如果在不同地图传送将会结束切磋
		if self.qieCuoState in [ csdefine.QIECUO_READY, csdefine.QIECUO_FIRE ]:
			self.loseQieCuo()
		elif self.qieCuoState in [ csdefine.QIECUO_INVITE, csdefine.QIECUO_BEINVITE ] :
			self.replyQieCuo( self.id, self.qieCuoTargetID, False )

		space = g_objFactory.getObject( self.spaceType )
		cellMailbox.onLeave( self.base, space.packedSpaceDataOnLeave( self ) )

	# -------------------------------------------------
	def onEnterArea( self ) :
		"""
		同地图跳转后被调用
		hyw--2008.10.08
		"""
		pass

	def onLeaveArea( self ):
		"""
		同地图跳转前被调用
		hyw--2008.10.08
		"""
		pass

	def onGotoSpaceBefore( self, spaceName ):
		"""
		传送前调用
		"""
		pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def gotoForetime( self ):
		"""
		define method.
		传送到过去的位置
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD:	# 在任何副本中，只要是系统自动传送玩家出副本的情况，对于未复活的玩家以最普通的复活方式复活到复活绑定点
			self.reviveOnCity()
			self.setTemp( "role_die_teleport", True ) 	#设置临时死亡标记
		else:
			self.setTemp( "ignoreFullRule", True )		# 设置一个标记， 在多线地图中忽略满线的规则， 避免在副本中无法被传出的现象
			self.gotoSpace( self.lastSpaceType, self.lastSpacePosition, self.direction )
			self.removeTemp( "ignoreFullRule" )

	def gotoEnterPos( self ):
		"""
		define method.
		传送到进入副本的位置
		"""
		self.setTemp( "ignoreFullRule", True )
		self.gotoSpace( self.lastSpaceType, self.lastSpacePosition, self.direction )
		self.removeTemp( "ignoreFullRule" )
		if self.state == csdefine.ENTITY_STATE_DEAD:
			self.reviveActivity()

	# ----------------------------------------------------------------
	# callback methods
	# ----------------------------------------------------------------
	def enterSpaceNotify( self ):
		"""
		defined method.
		内部接口，不允许重载
		进入space检测
		"""
		self.onEnterSpace_()
		# 未决BUFF
		self.spellTarget( csconst.PENDING_SKILL_ID, self.id )
		# 如果源spaceID与目标spaceID相等，肯定有地方出错了
		assert self.popTemp( "enter_spaceID" ) != self.spaceID

	def enterPlanesNotify(self):
		"""
		defined method.
		内部接口，不允许重载
		进入位面通知
		"""
		self.onEnterSpace_()

	def requestTeleport( self, exposed ):
		"""
		define method.
		客户端请求传送
		"""
		if exposed != self.id:
			return
		rtInfos = self.queryTemp( "requestTeleport", None )
		if rtInfos:
			rtInfosL = rtInfos.split(";")
			map = rtInfosL[0]
			pos = Math.Vector3( eval(rtInfosL[1]) )
			dire = Math.Vector3( eval(rtInfosL[2]) )
			self.gotoSpace( map, pos, dire )
		self.removeTemp( "requestTeleport" )

	def requestFlash( self, exposed, pos ):
		"""
		exposed method.
		客户端请求闪现
		"""
		if exposed != self.id:
			return
		flashInfo = self.queryTemp( "SPELL_FLASH", 0.0 )
		if flashInfo > 0.0:
			if self.position.flatDistTo( pos ) <= flashInfo:
				self.openVolatileInfo()
				self.position = pos
		self.removeTemp( "SPELL_FLASH" )

	# ----------------------------------------------------------------
	# defination methods
	# ----------------------------------------------------------------
	def gotoSpace( self, spaceName, position, direction ):
		"""
		define method.
		进入空间
		作用：
			根据spaceName，查找到要进入的空间信息，根据空间需要的条件，从cell里收集条件(领域条件和同一条件)，
			然后调用base的enterSpace入口，将条件传过去
		@type 			spaceName : string
		@param 			spaceName : 空间名，空间的关键字
		@type 			position  : vector3
		@param 			position  : 目标位置
		@type 			direction : vector3
		@param 			direction : 方向
		"""
		INFO_MSG( spaceName, position, direction )

		#由于spaceScript包括了domain和spaceNormal的一些接口 所以此处直接获取该 领域名称的脚本直接进行domain的相关检查
		spaceObj = g_objFactory.getObject( spaceName )				# 2007.12.14: modified by hyw
		if spaceObj is None :
			ERROR_MSG( "objectScript can't found. %s" % spaceName )
			return

		# 检测离开space条件是否满足
		currSpaceObj = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		result = currSpaceObj.checkDomainLeaveEnable( self )
		if result != csstatus.SPACE_OK:
			INFO_MSG( "leave domain condition different:", result )
			self.client.spaceMessage( result )
			return

		# 检测进入space条件是否满足
		result = spaceObj.checkDomainIntoEnable( self )
		if result == csstatus.SPACE_OK:
			self.onGotoSpaceBefore( spaceName )
			self.base.enterSpace( spaceName, position, direction, spaceObj.packedDomainData( self ) )
			spaceType = spaceObj.getSpaceType()
			try:
				g_logger.actJoinEnterSpaceLog( spaceType, csdefine.ACTIVITY_JOIN_ROLE, self.databaseID, self.level, self.getName() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		else:
			INFO_MSG( "into domain condition different:", result )
			self.client.spaceMessage( result )

	def gotoPlane( self, spaceName, position, direction ):
		"""
		Define method.
		请求进入位面空间。此种进入方式没有传送进度加载，所以目标位置必须是player客户端周围已经加载的chunk，即是以player为中心的9宫格。

		这里需注意，如果没有指定position，那么使用玩家当前的position来作为目标position，避免使用客户端提供的position。
		"""
		DEBUG_MSG( "player( %s ) request goto plane( %s )." % ( self.getName(), spaceName ) )
		print TELEPORT_KEY % ("player request goto plane", self.id, self.getName(), spaceName, BigWorld.time())
		# 不允许进行同地图位面传送
		assert spaceName != self.spaceType

		if position.y <= ILLEGALITY_POSITION_Y_AXIS:	# 暂时使用y值小于等于ILLEGALITY_POSITION_Y_AXIS表示位置无效
			position = self.postion
		self.setTemp( "gotoPlane", True )
		self.gotoSpace( spaceName, position, direction )	# 与普通方式进入空间保持一致，在底层实现上plane与space是一样的概念
		self.removeTemp( "gotoPlane" )

	def teleportToPlanes( self, position, direction, cellMailBox, planesID ):
		"""
		defined method.
		作用：传送到指定位面space，调用玩家自身的功能，让其进入指定空间。
		注：由于底层的teleport()没有完成回调，因此我们需要自己模拟。

		@type     position: vector3
		@param    position: 目标位置
		@type    direction: vector3
		@param   direction: 方向
		@type  cellMailBox: MAILBOX
		@param cellMailBox: 用于定位需要跳转的目标space，此mailbox可以是任意的有效的cell mailbox
		"""
		DEBUG_MSG( "player( %s ) teleport to plane( %s ) at %f" % ( self.getName(), self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), BigWorld.time() ) )
		print TELEPORT_KEY % ("player teleporting to plane", self.id, self.getName(), "N/A", BigWorld.time())

		self.onLeaveSpace_()
		currSpaceObj = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		if not isinstance(currSpaceObj, SpaceCopy):# 主线地图才保存最后进入地图
			self.lastSpaceType = self.spaceType
			self.lastSpacePosition = self.position

		self.setTemp( "enter_spaceID", self.spaceID )

		self.client.planeSpacePrepare()		# warnning : you have to do this before teleport to plane, or client will fail in smooth into the plane.Any question,pls contact wangshufeng.11:03 2014-1-4
		# You can send a method call after they do a teleport,
		# that's kinda the standard thing,
		# it'll get forwarded and queued on the real entity's destination.
		# The teleport might fail though,
		# if it does, onTeleportFailure gets called before any such queued method does.
		# So you can set a flag in onTeleportFailure and check for that in the queued method.
		#self.volatileInfo = VOLATILE_INFO_CLOSED
		if self.popTemp("MOVE_INTO_PLANE", False):
			print "------->>> move into plane at pos", position
			#prev_pos = position
			#position = self.guessPlaneEnterPos(position, direction)
			#print "------->>> guess destination", position
			#print "------->>> origin yaw %f, guess yaw %f" % (direction[-1], (position - prev_pos).yaw)
		self.systemCastSpell( Const.TELEPORT_PLANE_SKILLID  )	# 把服务器速度的验证设置为一个足够大的值，保证客户端的位置验证在位面传送时间内都是合法的，通过buff来控制topSpeed改变的时间
		self.planesID = planesID
		self.teleport( cellMailBox, position, direction )
		self.enterPlanesNotify()	# 此方法必须在teleport后面，且必须在defs中定义。

	def guessPlaneEnterPos(self, position, direction):
		"""
		@param position:
		@param direction:
		@return:
		"""
		global GUESS_TIME
		yaw = direction[-1]

		guessMove = GUESS_TIME * self.move_speed
		xm = guessMove * math.sin(yaw)
		zm = guessMove * math.cos(yaw)

		guessDest = Math.Vector3(position)
		guessDest.x += xm
		guessDest.z += zm

		guessDest = utils.navpolyToGround(self.spaceID, guessDest, 3.0, 3.0)
		properDest = self.canNavigateTo(guessDest, guessMove * 2)

		if properDest is None:
			origin = Math.Vector3(position)
			properDest = Math.Vector3(guessDest)
			origin.y += 0.5
			properDest.y = origin.y
			collision = BigWorld.collide(self.spaceID, origin, properDest)

			if collision:
				properDest = collision[0]
				xm = 0.5 * math.sin(yaw)
				zm = 0.5 * math.cos(yaw)
				properDest.x -= xm
				properDest.z -= zm

		return utils.navpolyToGround(self.spaceID, properDest, 3.0, 3.5)

	def gotoSpaceLineNumber( self, space, lineNumber, position, direction = (0, 0 ,0) ):
		"""
		define method.
		传送到x线场景， 一些支持多线的space如果想指定传送到第几线，必须使用这个接口进行传送
		使用gotoSpace也可以， 但到底被传送到哪个线由space负载平衡来决定。
			@param space		:	目的场景标识
			@type space			:	string
			@param lineNumber	:	线的号码
			@type space			:	uint
			@param position		:	目的场景位置
			@type position		:	vector3
			@param direction	:	出现时方向
			@type direction		:	vector3
		"""
		self.setTemp( "lineNumber", lineNumber )
		self.gotoSpace( space, position, direction )
		self.removeTemp( "lineNumber" )

	def teleportToSpace( self, position, direction, cellMailBox, dstSpaceID ):
		"""
		defined method.
		作用：传送到指定space，调用玩家自身的功能，让其进入指定空间。
		注：由于底层的teleport()没有完成回调，因此我们需要自己模拟。
			由于传送目标有“相同地图”传送和“不同地图”传送两种，
			因此，在模拟的时候有两个问题需要解决：
				- 传送目标是相同地图
				- 传送目标不是相同地图
			老实说，有了dstSpaceID以后，感觉很怪，但当前没有更好的解决方案了。

		@type     position: vector3
		@param    position: 目标位置
		@type    direction: vector3
		@param   direction: 方向
		@type  cellMailBox: MAILBOX
		@param cellMailBox: 用于定位需要跳转的目标space，此mailbox可以是任意的有效的cell mailbox
		@type   dstSpaceID: int32
		@param  dstSpaceID: 目标地图的spaceID，这个值主要用来确认目标地图与当前地图是否是同一地图用。
		"""
		entity = BigWorld.entities.get( cellMailBox.id, None )

		# 如果entity找不到，且没有提供目标spaceID，我们认为这是错误的用法。
		assert entity is not None or dstSpaceID >= 0

		# 传送时不应该有掉落伤害,所以将“开始掉落的高度”重置为要传送到的位置的高度 by mushuang
		self.fallDownHeight = position[ 1 ]

		# 能在当前 cellapp 找到指定的 entity 且两个 entity 在同一个 space 里，是相同地图传送
		# 目标spaceID与当前地图的spaceID相同，是相同地图传送
		isSameSpace = ( ( entity is not None and entity.spaceID == self.spaceID ) or ( dstSpaceID == self.spaceID ) )
		self.planesID = 0
		if isSameSpace:
			self.onLeaveArea()
			self.direction = direction # 由于引擎的teleport同地图传送不会修改朝向的问题，所以这里手动的修改传送的朝向
			self.teleport( None, position, direction )
			self.onEnterArea()
		else:
			self.onLeaveSpace_()
			currSpaceObj = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
			if not isinstance(currSpaceObj, SpaceCopy):# 主线地图才保存最后进入地图
				self.lastSpaceType = self.spaceType
				self.lastSpacePosition = self.position

			self.setTemp( "enter_spaceID", self.spaceID )	# 没啥用，主要用来验证

			# You can send a method call after they do a teleport,
			# that's kinda the standard thing,
			# it'll get forwarded and queued on the real entity's destination.
			# The teleport might fail though,
			# if it does, onTeleportFailure gets called before any such queued method does.
			# So you can set a flag in onTeleportFailure and check for that in the queued method.
			self.teleport( cellMailBox, position, direction )
			self.enterSpaceNotify()	# 此方法必须在teleport后面，且必须在defs中定义。

	def onTeleportFailure( self ):
		"""
		This method is called on a real entity when a teleport() call for that entity fails.
		This can occur if the nearby entity mailbox passed into teleport() is stale,
		meaning that the entity that it points to no longer exists on the destination CellApp pointed to by the mailbox.
		"""
		ERROR_MSG( "id %i(%s) teleport failure. current space id %i, space name %s, position" % ( self.id, self.getName(), self.spaceID, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) ), self.position )

	def requestInitSpaceSkill( self, exposed ):
		# 请求初始经副本技能
		# Exposed mothods
		if exposed != self.id:
			return

		currSpaceObj = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		currSpaceObj.requestInitSpaceSkill( self )

	def isCurrSpaceCanFly( self ):
		"""
		判断当前空间是否可以飞行
		"""
		spaceLabel =BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		return g_objFactory.getObject( spaceLabel ).canFly

	def isCurrSpaceCanVehicle( self ):
		"""
		判断当前空间是否可以召唤骑宠
		"""
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		return g_objFactory.getObject( spaceLabel ).canVehicle

	def onSpaceCopyTeleport( self, actType, spaceLabel, pos, direction, isFirstEnter ):
		"""
		define method
		传入已开副本
		"""
		if self.isActivityCanNotJoin( actType ) and isFirstEnter:
			self.statusMessage( csstatus.SPACE_COOY_YE_WAI_CHALLENGE_FULL )
		else:
			self.gotoSpace( spaceLabel, pos, direction )

	# ----------------------------------------------------------------
	# plane space
	# ----------------------------------------------------------------
	def enterPlane(self, planeType):
		self.gotoPlane(planeType, self.position, self.direction)

	def leavePlane(self):
		self.gotoPlane(self.lastSpaceType, self.position, self.direction)

	def telportToPlaneEntry(self, srcEntityID):
		"""
		Exposed method
		"""
		if srcEntityID != self.id:
			return

		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_WM:
			ERROR_MSG("%s isn't in wm space type but %s currentlly." %
				(self.getName(), self.getCurrentSpaceType()))
			return

		if self.state != csdefine.ENTITY_STATE_FREE:
			ERROR_MSG("%s is not in free state currentlly but %s" %
				(self.getName(), self.state))
			return

		DEBUG_MSG("%s request to teleport to plane entry of wm %s" %
			(self.getName(), self.spaceType))

		space_script = g_objFactory.getObject(self.spaceType)
		space_script.telportRoleToEntry(self)
