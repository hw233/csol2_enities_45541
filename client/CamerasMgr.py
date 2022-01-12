# -*- coding: gb18030 -*-
#
# $Id: CamerasMgr.py,v 1.28 2008-09-03 01:40:23 huangyongwei Exp $
#
"""
implement cameras, it moved from love3.py
2007/09/18: created by huangyongwei
2008/03/13: modified FLCShell by huangyongwei
			add methods: setMatrixTarget / setEntityTarget / setCameraPos
2008/08/22: rebuilded by huangyongwei
			removed CameraMgr singleton class due to phw's desirability
2009.06.23: add RCCamHandler class
"""

import math
import weakref
import BigWorld
import GUI
import Math
import csarithmetic as arithmetic
from AbstractTemplates import Singleton
from bwdebug import *
import csdefine
from keys import *
from Action import Action
from gbref import rds
from ShortcutMgr import shortcutMgr
import Const
import csol
import Define

# --------------------------------------------------------------------
# implement base camera shell class
# --------------------------------------------------------------------
class CAMShell( object ) :
	cc_per_angle_in_radian_ = math.pi / 180			# 1°的弧度值

	def __init__( self, camera ) :
		assert self.__class__ != CAMShell, "CAMShell is an abstract class!"
		self.camera_ = camera						# 相机
		self.targetEntity_ = None					# 相机绑定的 entity


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def camera( self ) :
		"""
		获取相机
		"""
		return self.camera_

	@property
	def targetEntity( self ) :
		"""
		相机绑定的目标
		"""
		if self.targetEntity_ is None :
			return None
		return self.targetEntity_()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def handle_( self, dx, dy, dz ) :
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setEntityTarget( self, entity ) :
		"""
		self.camera_.target = entity.matrix
		此处使用 EntityPosProvider 来提供座标的原因是防止 camera 受到 direction 的影响
		EntityPosProvider 过滤了 direction，仅使用 target matrix 的 translation 部分
		@type			entity : BigWorld.Entity
		@param			entity : target entity
		@return				   : None
		"""
		if entity is None :
			self.targetEntity_ = None
		else :
			self.targetEntity_ = weakref.ref( entity )
		self.camera_.target = BigWorld.EntityPosProvider( entity )


# --------------------------------------------------------------------
# implement flexible camera shell
# --------------------------------------------------------------------
class FLCShell( CAMShell ) :
	"""
	camera      target                  lookAt
	|-----------|-----------------------|---------

	            ^
	prePos      | target
	------------+----------
				|( 0, 0 )
				|

	preferredPos 是假设目标在（0，0）点后，相机的位置（也就是相机相对目标的位置）
	viewOffset 是相机观察点到目标的偏移，同样是假设目标在（0，0）点
	"""
	def __init__( self ) :
		camera = BigWorld.FlexiCam()
		CAMShell.__init__( self, camera )
		self.minRadius = 0.5									# min radius relative to target
		self.maxRadius = 16.0									# max radius relative to target
		self.minYaw = 0.0										# min yaw value of the camera
		self.maxYaw = 2 * math.pi								# max yaw value of the camera
		self.minPitch = math.pi / 2								# min pitch value of the camera
		self.maxPitch = 188.0 * self.cc_per_angle_in_radian_	# max pitch value of the camera

		# -----------------------------------
		# default values
		# -----------------------------------
		self.__radius = 5.0
		self.__actualRadius = 5.0
		self.__yaw = 0.0
		self.__pitch = 135.0 * self.cc_per_angle_in_radian_

		self.__initCamera()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def radius( self ) :
		return self.__radius

	@property
	def yaw( self ) :
		return self.__yaw

	@property
	def pitch( self ) :
		return self.__pitch


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initCamera( self ) :
		"""
		初始化相机的默认值
		"""
		self.camera_.target = Math.Matrix()
		self.__setPreferredPos()
		self.camera_.timeMultiplier = 8.0

	# -------------------------------------------------
	def __setPreferredPos( self ) :
		"""
		获取相机相对目标的坐标
		"""
		y = self.__actualRadius * math.sin( self.__pitch )
		x = self.__actualRadius * math.cos( self.__pitch ) * math.sin( self.__yaw )
		z = self.__actualRadius * math.cos( self.__pitch ) * math.cos( self.__yaw )

		dx = x + self.camera_.viewOffset[0]
		dy = y + self.camera_.viewOffset[1]
		dz = z + self.camera_.viewOffset[2]
		pos = Math.Vector3( dx, dy, dz )
		self.camera_.preferredPos = pos
		return

		# collide detect
#		player = BigWorld.player()
#		if player is None : return pos
#		spaceID = player.spaceID
#		if spaceID is None : return pos
#		direction = Math.Vector3( x, y, z )
#		distance = BigWorld.collide( spaceID, self.camera_.viewOffset, pos )
#		if distance is not None :
#			pos = self.camera_.viewOffset + direction * distance
#		return pos

	def __calcDirection( self ) :
		"""
		计算相机偏角
		"""
		pos = self.camera_.preferredPos
		x = pos.x - self.camera_.viewOffset[0]
		y = pos.y - self.camera_.viewOffset[1]
		z = pos.z - self.camera_.viewOffset[2]
		if self.__actualRadius == 0 : return
		self.__pitch = math.asin( y / self.__actualRadius )
		self.__yaw = math.asin( x / ( self.__actualRadius * math.cos( self.__pitch ) ) )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def handle_( self, dx, dy, dz ) :
		"""
		在三维坐标系中操作相机
		"""
		fov = BigWorld.projection().fov
		changed = False
		deltaYaw = 0.0
		deltaPitch = 0.0
		mouseHVBias = 0.667
		fnSensitivity = 0.003				# far and near sensitivety
		avSensitivity = 0.005				# angle view sensitivety
		if dz != 0 :
			self.addRadius( -dz * fnSensitivity )
			changed = True
		if dx != 0:
			deltaYaw = avSensitivity * fov * math.pi / 2
			deltaYaw = dx * mouseHVBias * deltaYaw
			self.addYaw( deltaYaw )
			changed = True
		if dy != 0:
			deltaPitch = avSensitivity * fov * math.pi / 3
			deltaPitch = dy * ( 1.0 - mouseHVBias ) * deltaPitch
			self.addPitch( -deltaPitch )
			changed = True
		if changed :
			self.__setPreferredPos()
			return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		恢复相机的默认参数
		"""
		self.__radius = 5.0
		self.__actualRadius = 5.0
		self.__yaw = 0.0
		self.__pitch = 135.0 * self.cc_per_angle_in_radian_
		self.__setPreferredPos()

	# -------------------------------------------------
	def getYaw( self ) :
		"""
		get camera yaw value
		@rtype					: float
		@return					: camera yaw value
		"""
		return self.__yaw

	def getPitch( self ) :
		"""
		get camera pitch value
		@rtype					: float
		@return					: camera pitch value
		"""
		return self.__pitch

	def getRadius( self ) :
		"""
		get radius between camera and target
		@rtype					: float
		@return					: radius
		"""
		return self.__radius

	# -------------------------------------------------
	def getTargetPos( self ) :
		"""
		get position of the camera's target
		@rtype					 : Vector3
		@return					 : target position
		"""
		tpos = getattr( self.camera_.target, "translation", None )
		if tpos is None :
			tpos = getattr( self.targetEntity, "position", None )
		if tpos is None :
			ERROR_MSG( "you must set a target to the camera!" )
			return Math.Vector3( 0, 0, 0 )
		return tpos

	def getCameraPos( self ) :
		"""
		get camera's position in world
		@rtype					 : Vector3
		@return					 : the camera's position
		"""
		tpos = self.getTargetPos()
		rcpos = self.camera_.preferredPos
		return tpos + rcpos

	# -------------------------------------------------
	def setRadius( self, value, update = False ) :
		"""
		set radius between camera and target
		@type				value  : float
		@param				value  : radius between camera and target
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		self.addRadius( value - self.__radius, update )

	def addRadius( self, value, update = False ) :
		"""
		add a value to radius
		@type				value  : float
		@param				value  : delta radius between camera and target
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		radius = self.camera_.preferredPos.distTo( self.camera_.viewOffset )
		if ( radius < self.__actualRadius ) :
			self.__radius = radius
			self.__actualRadius = radius
		rate = self.__radius / self.__actualRadius
		self.__radius += value
		self.__radius = min( max ( self.__radius, self.minRadius ), self.maxRadius )
		self.__actualRadius = self.__radius / rate
		if update : self.__setPreferredPos()

	# ---------------------------------------
	def setYaw( self, value, update = False ) :
		"""
		set camera's yaw value
		@type				value  : float
		@param				value  : yaw value of the camera
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		self.__yaw = value
		if value > self.maxYaw :
			self.__yaw = value - self.maxYaw
		elif value < self.minYaw :
			self.__yaw = value + self.maxYaw
		if update : self.__setPreferredPos()

	def addYaw( self, value, update = False ) :
		"""
		add camera's yaw value
		@type				value  : float
		@param				value  : delta yaw value of the camera
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		self.setYaw( self.__yaw + value, update )

	# ---------------------------------------
	def setPitch( self, value, update = False ) :
		"""
		set camera's pitch value
		@type				value  : float
		@param				value  : pitch value of the camera
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		delata = value - self.__pitch
		self.__pitch = min( max( value, self.minPitch ), self.maxPitch )
		actualRadius = self.__actualRadius
		if self.maxPitch - self.__pitch < 10 :
			actualRadius -= abs( delata / 8.0 )
		else :
			actualRadius += abs( delata / 8.0 )
		self.__actualRadius = min( max( actualRadius, self.minRadius ), self.__radius )
		if update : self.__setPreferredPos()

	def addPitch( self, value, update = False ) :
		"""
		add camera's pitch value
		@type				value  : float
		@param				value  : delta pitch value of the camera
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		self.setPitch( self.__pitch + value, update )

	# -------------------------------------------------
	def setMatrixTarget( self,  matrix ) :
		"""
		set camera's target as a matrix
		@type			matrix : Math.Matrix
		@param			matrix : matrix target
		@return				   : None
		"""
		self.camera_.target = matrix

	# ---------------------------------------
	def setCameraPos( self, pos ) :
		"""
		you can call this method to reset camera's position
		if the camera's position is changed, the camera's yaw/pitch/radius/preferredPos attributes will be changed
		@type				pos : Vector3
		@param				pos : camera's position
		@return					: None
		"""
		pos = Math.Vector3( pos )
		tpos = self.getTargetPos()
		self.__radius = self.__actualRadius = pos.distTo( tpos )
		self.camera_.preferredPos = pos - tpos
		self.__calcDirection()

	def stareAt( self, pos ) :
		"""
		set stare pos of the camera
		after this method the camera's yaw/pitch/preferredPos attributes will be changed
		@type				pos : Vector3
		@param				pos : stare position
		@return					: None
		"""
		lpos = Math.Vector3( pos )
		tpos = self.getTargetPos()
		cpos = arithmetic.getSeparatePoint3( tpos, lpos, -self.__radius )
		self.camera_.preferredPos = cpos - tpos
		self.__calcDirection()


# --------------------------------------------------------------------
# implement cursor camera
# --------------------------------------------------------------------
class CUCShell( CAMShell ) :
	def __init__( self ) :
		camera = BigWorld.CursorCamera()
		CAMShell.__init__( self, camera )
		self.lookAt = Math.Vector3( 0.0, 1.8, 0.0 )
		self.minYaw = 0.0
		self.maxYaw = 2 * math.pi

		self.minPitch = 150.0 * self.cc_per_angle_in_radian_
		self.maxPitch = 200.0 * self.cc_per_angle_in_radian_

		self.minDistance = 2.0
		self.maxDistance = 20.0
		self.maxDistHalfLife = 0.1

		# -----------------------------------
		self.__yaw = 0.0
		self.__pitch = math.pi
		# pitch 坐标角度示例
		#     π / 2
		#       │
		# π  ─┼─  0
		#       │
		#    3×π / 2
		# miniPitch / maxPitch 最后需要在 3D 坐标轴中进行取反操作，
		# 即小于 180 的加上 180，大于 180 的减去 180
		# 例如：minPitch = 150.0 时，实际角度是：150.0 + 180.0 = 330.0
		# 而 maxPitch = 230.0 时则实际角度是：230.0 - 180.0 = 50.0
		self.__distance = 7.68
		self.__limit = 155.0 * self.cc_per_angle_in_radian_ - self.minPitch

		self.__initCamera()

	def __initCamera( self ) :
		"""
		初始化相机
		"""
		self.camera_.source = Math.Matrix()
		self.camera_.target = BigWorld.PlayerMatrix()
		self.camera_.pivotPosition = self.lookAt
		self.camera_.pivotMaxDist = 12
		self.camera_.terrainMinDist = 50
		self.camera_.limitVelocity = 0
		self.camera_.maxVelocity = 2
		self.camera_.maxDistHalfLife = self.maxDistHalfLife
		self.camera_.movementHalfLife = 0.1
		self.camera_.turningHalfLife = 0
		self.camera_.enableMinHeightOffsetLimit = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def handle_( self, dx, dy, dz ) :
		"""
		在三维坐标系中控制相机
		"""
		fov = BigWorld.projection().fov
		changed = False
		deltaYaw = 0.0
		deltaPitch = 0.0
		mouseHVBias = 0.667
		fnSensitivity = 0.003				# far and near sensitivety
		avSensitivity = 0.005				# angle view sensitivety
		if dz != 0 :
			self.addDistance( -dz * fnSensitivity )
			changed = True
		if dx != 0:
			deltaYaw = avSensitivity * fov * math.pi / 2
			deltaYaw = dx * mouseHVBias * deltaYaw
			self.addYaw( deltaYaw )
			changed = True
		if dy != 0:
			deltaPitch = avSensitivity * fov * math.pi / 3
			deltaPitch = dy * ( 1.0 - mouseHVBias ) * deltaPitch
			self.addPitch( deltaPitch )
			changed = True
		if changed :
			self.update()
			return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		恢复相机的默认参数
		"""
		self.lookAt = Math.Vector3( 0.0, 1.8, 0.0 )
		self.__yaw = 0.0
		self.__pitch = math.pi
		self.camera_.pivotMaxDist = self.__distance
		self.camera_.movementHalfLife = min( ( self.__distance - self.minDistance ) / ( ( self.maxDistance - self.minDistance ) / 2 ) * 0.1 , 0.1 )

	# -------------------------------------------------
	def getYaw( self ) :
		return self.__yaw

	def getPitch( self ) :
		#pitch = max( self.__pitch, math.pi * 155.0 / 180)
		return self.__pitch

	def getDirection( self ) :
		y = self.__distance * math.sin( self.__pitch )
		x = self.__distance * math.cos( self.__pitch ) * math.sin( self.__yaw )
		z = self.__distance * math.cos( self.__pitch ) * math.cos( self.__yaw )
		vDir = Math.Vector3( x, y, z )
		vDir.normalise()
		return -vDir

	# -------------------------------------------------
	def setYaw( self, value, update = False ) :
		self.addYaw( value - self.__yaw, update )

	def addYaw( self, value, update = False ) :
		self.__yaw += value
		if ( self.__yaw > self.maxYaw ) :
			self.__yaw -= self.maxYaw
		if ( self.__yaw < self.minYaw ) :
			self.__yaw += self.maxYaw
		if update : self.update()

	# ---------------------------------------
	def setPitch( self, value, update = False ) :
		self.__pitch = min( max( value, self.minPitch ), self.maxPitch )
		if update : self.update()

	def addPitch( self, value, update = False ) :
		value += self.__pitch
		self.setPitch( value, update )

	# ---------------------------------------
	def setDistance( self, value, update = False ) :
		self.__distance = min( max( value, self.minDistance ), self.maxDistance )
		if update : self.update()

	def addDistance( self, value, update = False ) :
		value += self.__distance
		self.setDistance( value, update )

	def adjustToTarget( self, enableMinHeightOffset, minHeightOffset, pivotPosition, minDistance, maxDistance ):
		self.camera_.enableMinHeightOffsetLimit = enableMinHeightOffset
		self.camera_.minHeightOffsetLimit = minHeightOffset
		self.camera_.pivotPosition = pivotPosition
		self.minDistance = minDistance
		self.lookAt = pivotPosition
		self.maxDistance = maxDistance
		#如果镜头的距离小于给出的最小距离，那么就将镜头后移
		if self.camera_.pivotMaxDist <= minDistance:
			self.setDistance( self.maxDistance / 4.0, True )

	# -------------------------------------------------
	def update( self ) :
		camera = self.camera_
		camera.pivotMaxDist = self.__distance
		camera.movementHalfLife = min( 0.2 * ( self.__distance - self.minDistance ) / ( self.maxDistance - self.minDistance ), 0.3 )
		camera.source.setRotateYPR( ( self.__yaw, self.__pitch, math.pi ) )


# --------------------------------------------------------------------
# implement rolecreator's controler in world
# --------------------------------------------------------------------
class RCCamHandler( Singleton ) :
	"""
	角色创建的相机控制器
	"""
	def __init__( self ) :
		self.__camShell = CUCShell()					# 在世界中的相机壳
		minDist = 1.0
		maxDist = Const.ROLE_CREATE_MAX_DISTACE #7.68
		self.__camShell.minDistance = minDist
		self.__camShell.maxDistance = maxDist
		self.__deltaDist = ( maxDist - minDist ) / 3	# 每次调整镜头的距离

		self.__isFixup = False							# 指出鼠标指针是否被卡用
		self.__pos = Math.Vector2( 0, 0 )				# 记录鼠标右键按下时的位置
		self.__isEnable = True							# 记录该控制器是否处于开启状态


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def cameraShell( self ) :
		"""
		获取相机壳
		"""
		return self.__camShell


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def use( self, yaw = 0.0 ) :
		"""
		应用相机
		"""
		camera = self.__camShell.camera
		camera.pivotPosition = Math.Vector3( 0.0, 1.8, 0.0 )
		camera.source = Math.Matrix( BigWorld.dcursor().matrix )
		BigWorld.camera( camera )
		self.__camShell.setYaw( yaw )
		dst = self.__camShell.maxDistance
		self.__camShell.setDistance( dst, True )

	def carryUpCamera( self ) :
		"""
		抬高镜头
		"""
		self.__camShell.camera.pivotPosition = Math.Vector3( 0.0, 2.2, 0.0 )

	def carryDownCamera( self ) :
		"""
		抬高镜头
		"""
		self.__camShell.camera.pivotPosition = Math.Vector3( 0.0, 1.8, 0.0 )

	def closeTarget( self ) :
		"""
		拉近镜头
		"""
		self.__camShell.addDistance( -self.__deltaDist, True )

	def extendTarget( self ) :
		"""
		伸展镜头
		"""
		self.__camShell.addDistance( self.__deltaDist, True )

	# ---------------------------------------
	def fixed( self ) :
		"""
		指出鼠标是否被相机控制器卡住
		"""
		return self.__isFixup

	def fix( self ) :
		"""
		卡住鼠标
		"""
		self.__isFixup = True
		self.__pos = GUI.mcursor().position
		GUI.mcursor().visible = False

	def unfix( self ) :
		"""
		恢复鼠标
		"""
		if self.__isFixup :
			self.__isFixup = False
			rds.ccursor.normal()
			GUI.mcursor().position = self.__pos
			GUI.mcursor().visible = True

	# -------------------------------------------------
	def enable( self ) :
		"""
		开启相机控制器
		"""
		self.__isEnable = True

	def disable( self ) :
		"""
		关闭相机控制器
		"""
		self.__isEnable = False

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		截获按键消息
		"""
		if down and not self.__isEnable :
			return False
		if not down and key == KEY_RIGHTMOUSE and self.__isFixup :
			self.unfix()
			return True
		elif down and key == KEY_MIDDLEMOUSE :
			return True
		return False

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		截获鼠标移动消息
		"""
		if not self.__isEnable : return False							# 如果被关闭，则返回
		if BigWorld.isKeyDown( KEY_RIGHTMOUSE ) and csol.isVirtualKeyDown( VK_RBUTTON ): # 鼠标右键处于按下状态
			if not self.__isFixup:										# 如果还没卡住鼠标
				self.fix()												# 则卡住鼠标
			else :														# 否则
				GUI.mcursor().position = self.__pos						# 设置相机位置
				self.__camShell.handle_( dx, dy, dz )
			return True
		if dz != 0.0 and rds.ruisMgr.isMouseHitScreen() :
			self.__camShell.handle_( 0.0, 0.0, dz )
			return True
		return False


# --------------------------------------------------------------------
# implement camera's controler in world
# --------------------------------------------------------------------
class WorldCamHandler :
	"""
	相机控制器
	"""
	def __init__( self ) :
		self.__camShell = CUCShell()				# 在世界中的相机壳
		self.__camShell.minDistance = 1.0			# 镜头最近距离

		self.__isFixup = False						# 指出鼠标指针是否被卡用
		self.__pos = Math.Vector2( 0, 0 )			# 记录鼠标右(左)键按下时的位置，这是成功卡位的位置
		self.__isEnable = True						# 记录该控制器是否处于开启状态

		self.__fixupDistance = 5					# 鼠标按下横向移动多少距离才开始卡位（主要用在鼠标左键移动的处理）
		self.__fixupPos	= Math.Vector2( 0, 0 )		# 判断鼠标是否能够卡位的开始位置
		self.__canfixup = False						# 是否可以进行卡位
		self.isYawLocked = False					# 朝向是否锁定

		shortcutMgr.setHandler( "ACTION_INCREASE_DISTANCE", self.__incDistance )	# 增加视距
		shortcutMgr.setHandler( "ACTION_DECREASE_DISTANCE", self.__decDistance )	# 减小视距

		self._c_control_mod = {
			Const.CAMERA_CONTROL_MOD_1 : self._c_control_1,
			Const.CAMERA_CONTROL_MOD_2 : self._c_control_2,
			}

		self._d_control_mod = {
			Const.CAMERA_CONTROL_MOD_1 : self._d_control_1,
			Const.CAMERA_CONTROL_MOD_2 : self._d_control_2,
			}


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __incDistance( self ) :
		"""
		使用快捷键增加视距
		"""
		player = BigWorld.player()
		if player and player.hasControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA ): return True

		self.__camShell.handle_( 0.0, 0.0, 120 )
		return True

	def __decDistance( self ) :
		"""
		使用快捷键减少视距
		"""
		player = BigWorld.player()
		if player and player.hasControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA ): return True

		self.__camShell.handle_( 0.0, 0.0, -120 )
		return True


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def cameraShell( self ) :
		"""
		获取相机
		"""
		return self.__camShell


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def use( self ) :
		"""
		应用相机
		"""
		self.__camShell.camera.source = Math.Matrix( BigWorld.dcursor().matrix )
		BigWorld.camera( self.__camShell.camera )

	# -------------------------------------------------
	def reset( self, dis = 10.0 ) :
		"""
		恢复相机的各个属性
		"""
		camera = self.__camShell.camera
		camera.target = BigWorld.PlayerMatrix()
		yaw = BigWorld.player().yaw + 3.4
		self.__camShell.setYaw( yaw )							# 默认相机照向角色背部
		self.__camShell.update()								# 更新相机
		self.__camShell.minDistance = 1.0
		self.__camShell.maxDistance = 15.0
		dst = self.__camShell.maxDistance
		self.__camShell.setDistance( dis, True )
		self.__singleKeyPos = Math.Vector2( 0, 0 )


	# ---------------------------------------
	def fixed( self ) :
		"""
		指出鼠标是否被相机控制器卡住
		"""
		return self.__isFixup

	def fix( self ) :
		"""
		卡住鼠标
		"""
		self.__isFixup = True
		self.__pos = GUI.mcursor().position
		GUI.mcursor().visible = False

	def unfix( self ) :
		"""
		恢复鼠标
		"""
		if self.__isFixup :
			self.__isFixup = False
			rds.ccursor.normal()
			GUI.mcursor().position = self.__pos
			GUI.mcursor().visible = True

	# -------------------------------------------------
	def enable( self ) :
		"""
		开启相机控制器
		"""
		self.__isEnable = True

	def disable( self ) :
		"""
		关闭相机控制器
		"""
		self.__isEnable = False

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		截获按键消息
		"""
		if down and not self.__isEnable :
			return False
		player = BigWorld.player()
		if player is None:
			return False
		cm = player.c_control_mod
		return self._d_control_mod[cm]( down, key, mods )

	def _d_control_1( self, down, key, mods ):
		"""
		按键控制模式1
		"""
		if not down and self.__isFixup :
			self.unfix()
			return True
		elif down and key == KEY_MIDDLEMOUSE :
			#self.__camShell.reset()
			return True
		return False

	def _d_control_2( self, down, key, mods ):
		"""
		按键控制模式2
		"""
		self.__fixupPos = Math.Vector2( 0, 0 )
		self.__canfixup = False

		if not down and self.__isFixup :
			self.unfix()
			return True
		elif down :
			if key == KEY_MIDDLEMOUSE :
				#self.__camShell.reset()
				return True
			elif key == KEY_LEFTMOUSE :
				self.__singleKeyPos = self.__pos
				return False
			elif key == KEY_RIGHTMOUSE :
				player = BigWorld.player()
				player.onCameraDirChanged( self.__camShell.camera.direction )
				return True
		return False

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		截获鼠标移动消息
		"""
		if not self.__isEnable : return False							# 如果被关闭，则返回
		player = BigWorld.player()

		# 在游戏刚刚启动的某些时候，player会为None，所以在这里加一个卫句，防止出现异常 by mushuang
		if not player:
			ERROR_MSG( "Can't find player!" )
			return
		return self._c_control_mod[player.c_control_mod]( dx, dy, dz, player )

	def _c_control_1( self, dx, dy, dz, player ):
		"""
		移动控制模式1
		"""
		if BigWorld.isKeyDown( KEY_RIGHTMOUSE ) and csol.isVirtualKeyDown( VK_RBUTTON ): # 鼠标右键处于按下状态
			if player.hasControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA ):
				return True

			if not self.__isFixup :										# 如果还没卡住鼠标
				self.fix()
			else:
				GUI.mcursor().position = self.__pos						# 设置相机位置
				if self.__camShell.handle_( dx, dy, dz ):
					player.onCameraDirChanged( self.__camShell.camera.direction )
			return True
		if dz != 0.0 and rds.ruisMgr.isMouseHitScreen():
			if player.hasControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA ):
				return True
			self.__camShell.handle_( 0.0, 0.0, dz )
			return True
		return False

	def _c_control_2( self, dx, dy, dz, player ):
		"""
		移动控制模式2
		"""
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) and csol.isVirtualKeyDown( VK_LBUTTON ): # 鼠标左键处于按下状态
			if player.hasControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA ):
				return True
			if self.__fixupPos == Math.Vector2( 0, 0 ):
				self.__fixupPos = GUI.mcursor().position

			if self.__fixupPos.x - GUI.mcursor().position.x > 0.01 or self.__fixupPos.x - GUI.mcursor().position.x < -0.01:
				self.__canfixup = True

			if self.__fixupPos.y - GUI.mcursor().position.y > 0.01 or self.__fixupPos.y - GUI.mcursor().position.y < -0.01:
				self.__canfixup = True

			if not self.__canfixup:
				return False

			if not self.__isFixup :										# 如果还没卡住鼠标
				self.fix()												# 则卡住鼠标
			else :														# 否则
				GUI.mcursor().position = self.__pos						# 设置相机位置
				self.__camShell.handle_( dx, dy, dz )
			return True
		elif BigWorld.isKeyDown( KEY_RIGHTMOUSE ) and csol.isVirtualKeyDown( VK_RBUTTON ): # 鼠标右键处于按下状态
			if player.hasControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA ):
				return True
			if self.__fixupPos == Math.Vector2( 0, 0 ):
				self.__fixupPos = GUI.mcursor().position

			if self.__fixupPos.x - GUI.mcursor().position.x > 0.01 or self.__fixupPos.x - GUI.mcursor().position.x < -0.01:
				self.__canfixup = True

			if self.__fixupPos.y - GUI.mcursor().position.y > 0.01 or self.__fixupPos.y - GUI.mcursor().position.y < -0.01:
				self.__canfixup = True

			if not self.__canfixup:
				return False

			if not self.__isFixup :										# 如果还没卡住鼠标
				self.fix()												# 则卡住鼠标
			else :														# 否则
				GUI.mcursor().position = self.__pos						# 设置相机位置
				if self.__camShell.handle_( dx, dy, dz ):
					player.onCameraDirChanged( self.__camShell.camera.direction )
				return True
		if dz != 0.0 and rds.ruisMgr.isMouseHitScreen():
			if player.hasControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA ):
				return True
			self.__camShell.handle_( 0.0, 0.0, dz )
			return True
		return False

	def resetMouseState( self ):
		"""
		重置鼠标相关状态
		"""
		self.unfix()

# --------------------------------------------------------------------
# 账号输入3D场景的摄像机控制器
# --------------------------------------------------------------------
class LNCamHandler( Singleton ) :

	def __init__( self ) :
		self.__camShell = FLCShell()

		self.__cycleCBID = 0
		self.__runCBID = 0
		self.__speedGene = 2.5

		self.__initCamera()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initCamera( self ) :
		"""
		初始化摄像机
		"""
		tMatrix = Math.Matrix()
		tMatrix.setTranslate( ( 238, 8, 110 ) )
		camShell = self.__camShell
		camShell.camera.target = tMatrix
		camShell.camera.viewOffset = ( 0, 0, 0 )
		camShell.camera.positionAcceleration = 0.0
		camShell.camera.trackingAcceleration = 0.0
		camShell.stareAt( ( 238, 8, 105 ) )

	def __circumvolve( self, distance = 1 ) :
		"""
		旋转指定距离
		"""
		deltaX = distance / float( self.__speedGene )
		self.__camShell.handle_( deltaX, 0, 0 )
		self.__cycleCBID = BigWorld.callback( 0.01, self.__circumvolve )

	def __prepareRunning( self ) :
		"""
		准备开始
		"""
		self.__camShell.camera.positionAcceleration = 3				# 设定跟转动速度适合的加速度，让转动更平滑
		self.__circumvolve()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		camShell = self.__camShell
		camShell.camera.positionAcceleration = 0					# 把加速度设置为0，让相机快速定位到指定点
		tMatrix = camShell.camera.target
		tMatrix.setTranslate( ( 238, 8, 110 ) )
		#camShell.stareAt( ( 238, 8, 105 ) )

	def run( self ) :
		"""
		开始转动
		"""
		self.stop()
		self.__runCBID = BigWorld.callback( 1, self.__prepareRunning )

	def stop( self ) :
		"""
		停止转动
		"""
		BigWorld.cancelCallback( self.__runCBID )
		BigWorld.cancelCallback( self.__cycleCBID )
		self.__runCBID = 0
		self.__cycleCBID = 0

	def use( self ) :
		"""
		启用摄像机
		"""
		self.reset()
		BigWorld.camera( self.__camShell.camera )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getSpeedGene( self ) :
		return self.__speedGene

	def _setSpeedGene( self, value ) :
		self.__speedGene = max( 1, value )

	speedGene = property( _getSpeedGene, _setSpeedGene )

# --------------------------------------------------------------------
# implement flexible camera shell
# 自由飞翔摄像机
# --------------------------------------------------------------------
class FlyCameraShell( CAMShell ) :
	def __init__( self ) :
		camera = BigWorld.FlexiCam()
		CAMShell.__init__( self, camera )

		self.minRadius = 0.5									# min radius relative to target
		self.maxRadius = 16.0									# max radius relative to target

		# -----------------------------------
		# default values
		# -----------------------------------
		self.__radius = 5.0
		self.__actualRadius = 5.0
		self.__yaw = 0.0
		self.__pitch = 135.0 * self.cc_per_angle_in_radian_

		self.__initCamera()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def radius( self ) :
		return self.__radius

	@property
	def yaw( self ) :
		return self.__yaw

	@property
	def pitch( self ) :
		return self.__pitch


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initCamera( self ) :
		"""
		初始化相机的默认值
		"""
		self.camera_.target = Math.Matrix()
		self.__setPreferredPos()
		self.camera_.timeMultiplier = 8.0

	# -------------------------------------------------
	def __setPreferredPos( self ) :
		"""
		获取相机相对目标的坐标
		"""
		y = self.__actualRadius * math.sin( self.__pitch )
		x = self.__actualRadius * math.cos( self.__pitch ) * math.sin( self.__yaw )
		z = self.__actualRadius * math.cos( self.__pitch ) * math.cos( self.__yaw )

		dx = x + self.camera_.viewOffset[0]
		dy = y + self.camera_.viewOffset[1]
		dz = z + self.camera_.viewOffset[2]
		pos = Math.Vector3( dx, dy, dz )
		self.camera_.preferredPos = pos
		return

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		恢复相机的默认参数
		"""
		self.__radius = 5.0
		self.__actualRadius = 5.0
		self.__yaw = 0.0
		self.__pitch = 135.0 * self.cc_per_angle_in_radian_
		self.__setPreferredPos()

	def getYaw( self ) :
		"""
		get camera yaw value
		@rtype					: float
		@return					: camera yaw value
		"""
		return self.__yaw

	def getPitch( self ) :
		"""
		get camera pitch value
		@rtype					: float
		@return					: camera pitch value
		"""
		return self.__pitch

	def getRadius( self ) :
		"""
		get radius between camera and target
		@rtype					: float
		@return					: radius
		"""
		return self.__radius

	# -------------------------------------------------
	def getTargetPos( self ) :
		"""
		get position of the camera's target
		@rtype					 : Vector3
		@return					 : target position
		"""
		tpos = getattr( Math.Matrix( self.camera_.target ), "translation", None )
		if tpos is None :
			tpos = getattr( self.targetEntity, "position", None )
		if tpos is None :
			ERROR_MSG( "you must set a target to the camera!" )
			return Math.Vector3( 0, 0, 0 )
		return tpos

	def getCameraPos( self ) :
		"""
		get camera's position in world
		@rtype					 : Vector3
		@return					 : the camera's position
		"""
		tpos = self.getTargetPos()
		rcpos = self.camera_.preferredPos
		return tpos + rcpos

	def setRadius( self, value, update = False ) :
		"""
		set radius between camera and target
		@type				value  : float
		@param				value  : radius between camera and target
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		self.addRadius( value - self.__radius, update )

	def addRadius( self, value, update = False ) :
		"""
		add a value to radius
		@type				value  : float
		@param				value  : delta radius between camera and target
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		radius = self.camera_.preferredPos.distTo( self.camera_.viewOffset )
		if ( radius < self.__actualRadius ) :
			self.__radius = radius
			self.__actualRadius = radius
		rate = self.__radius / self.__actualRadius
		self.__radius += value
		self.__radius = min( max ( self.__radius, self.minRadius ), self.maxRadius )
		self.__actualRadius = self.__radius / rate
		if update : self.__setPreferredPos()

	def setYaw( self, value, update = False ) :
		"""
		set camera's yaw value
		@type				value  : float
		@param				value  : yaw value of the camera
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		self.__yaw = value
		if update : self.__setPreferredPos()

	def setPitch( self, value, update = False ) :
		"""
		set camera's pitch value
		@type				value  : float
		@param				value  : pitch value of the camera
		@type				update : bool
		@param				update : if it is true the camera will be updated immediately
		@return					   : None
		"""
		self.__pitch = value
		if update : self.__setPreferredPos()

	def setMatrixTarget( self,  matrix ) :
		"""
		set camera's target as a matrix
		@type			matrix : Math.Matrix
		@param			matrix : matrix target
		@return				   : None
		"""
		self.camera_.target = matrix

	def setCameraPos( self, pos ) :
		"""
		you can call this method to reset camera's position
		if the camera's position is changed, the camera's yaw/pitch/radius/preferredPos attributes will be changed
		@type				pos : Vector3
		@param				pos : camera's position
		@return					: None
		"""
		pos = Math.Vector3( pos )
		tpos = self.getTargetPos()
		self.__radius = self.__actualRadius = pos.distTo( tpos )
		self.camera_.preferredPos = pos - tpos
		self.__calcDirection()

	def stareAt( self, pos ) :
		"""
		set stare pos of the camera
		after this method the camera's yaw/pitch/preferredPos attributes will be changed
		@type				pos : Vector3
		@param				pos : stare position
		@return					: None
		"""
		lpos = Math.Vector3( pos )
		tpos = self.getTargetPos()
		cpos = arithmetic.getSeparatePoint3( tpos, lpos, -self.__radius )
		self.camera_.preferredPos = cpos - tpos
		self.__calcDirection()

	def __calcDirection( self ) :
		"""
		计算相机偏角
		"""
		pos = self.camera_.preferredPos
		x = pos.x - self.camera_.viewOffset[0]
		y = pos.y - self.camera_.viewOffset[1]
		z = pos.z - self.camera_.viewOffset[2]
		if self.__actualRadius == 0 : return
		self.__pitch = math.asin( y / self.__actualRadius )
		self.__yaw = math.asin( x / ( self.__actualRadius * math.cos( self.__pitch ) ) )

class FixWorldCamHandler( WorldCamHandler ):
	"""
	固定视角相机控制器
	"""
	def __init__( self ) :
		WorldCamHandler.__init__( self )
		self.isYawLocked = True					# 朝向是否锁定


	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		截获按键消息
		"""
		return False


	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		截获鼠标移动消息
		"""
		if dz != 0.0 and rds.ruisMgr.isMouseHitScreen():
			self.cameraShell.handle_( 0.0, 0.0, dz )
			return True
		return False

	def use( self, yaw = -9.4, pitch = 3.766 ):
		WorldCamHandler.use( self )
		self.reset( yaw, pitch )		# 固定视角相机每一次启用都需重置相机参数

	def reset( self, yaw = -9.4, pitch = 3.766, changeMaxPitch = True ) :
		"""
		恢复相机的各个属性
		"""
		camera = self.cameraShell.camera
		camera.target = BigWorld.PlayerMatrix()
		self.cameraShell.setYaw( yaw )
		if changeMaxPitch:
			self.cameraShell.maxPitch = 230 * math.pi / 180     # 调整最大俯视角度
		self.cameraShell.setPitch( pitch )
		self.cameraShell.update()								# 更新相机
		self.cameraShell.minDistance = 1.0
		self.cameraShell.maxDistance = 20.0
		dst = self.cameraShell.maxDistance
		self.cameraShell.setDistance(11.36, True )
		self.cameraShell.camera_.hitModelAlpha = 1.0


class FishingCameraHandler( FixWorldCamHandler ):

	def __init__( self ):
		FixWorldCamHandler.__init__( self )
		camShell = self.cameraShell
		camShell.minPitch = -math.pi
		camShell.maxPitch = math.pi
		camShell.maxDistance = 100

	def use( self ):
		"""
		应用此相机
		"""
		BigWorld.camera( self.cameraShell.camera )

	def reset( self, dis = 10.0 ) :
		"""
		恢复相机的各个属性
		"""
		pass

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		截获鼠标移动消息
		"""
		# 只在测试版本中允许调节摄像机
		if isPublished:
			return False

		if dz != 0.0 and rds.ruisMgr.isMouseHitScreen():
			if BigWorld.isKeyDown(KEY_LCONTROL) or\
				BigWorld.isKeyDown(KEY_RCONTROL):
					sensitivity = 0.03
			else:
				sensitivity = 0.003

			if BigWorld.isKeyDown(KEY_LSHIFT) or\
				BigWorld.isKeyDown(KEY_RSHIFT):
					symbol = dz > 0 and 1 or -1
					self.cameraShell.addPitch( symbol * math.pi/30.001, True )
			elif BigWorld.isKeyDown(KEY_LALT) or\
				BigWorld.isKeyDown(KEY_RALT):
					symbol = dz > 0 and 1 or -1
					self.cameraShell.addYaw( symbol * math.pi/30, True )
			else:
				self.cameraShell.addDistance( -dz * sensitivity, True )
			return True
		return False

	def locate( self, target, ypr, pivotDist ):
		"""
		定位相机
		@param target		: Matrix that this camera looks to
		@param ypr			: tuple as ( yaw, pitch, roll )
		@param pivotDist	: Float
		"""
		camShell = self.cameraShell
		camShell.setYaw( ypr[0] )
		camShell.setPitch( ypr[1] )
		camShell.setDistance( pivotDist )

		cam = camShell.camera
		cam.target = target
		cam.source.setRotateYPR( ypr )
		cam.pivotMaxDist = pivotDist
