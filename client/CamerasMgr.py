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
	cc_per_angle_in_radian_ = math.pi / 180			# 1��Ļ���ֵ

	def __init__( self, camera ) :
		assert self.__class__ != CAMShell, "CAMShell is an abstract class!"
		self.camera_ = camera						# ���
		self.targetEntity_ = None					# ����󶨵� entity


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def camera( self ) :
		"""
		��ȡ���
		"""
		return self.camera_

	@property
	def targetEntity( self ) :
		"""
		����󶨵�Ŀ��
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
		�˴�ʹ�� EntityPosProvider ���ṩ�����ԭ���Ƿ�ֹ camera �ܵ� direction ��Ӱ��
		EntityPosProvider ������ direction����ʹ�� target matrix �� translation ����
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

	preferredPos �Ǽ���Ŀ���ڣ�0��0����������λ�ã�Ҳ����������Ŀ���λ�ã�
	viewOffset ������۲�㵽Ŀ���ƫ�ƣ�ͬ���Ǽ���Ŀ���ڣ�0��0����
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
		��ʼ�������Ĭ��ֵ
		"""
		self.camera_.target = Math.Matrix()
		self.__setPreferredPos()
		self.camera_.timeMultiplier = 8.0

	# -------------------------------------------------
	def __setPreferredPos( self ) :
		"""
		��ȡ������Ŀ�������
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
		�������ƫ��
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
		����ά����ϵ�в������
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
		�ָ������Ĭ�ϲ���
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
		# pitch ����Ƕ�ʾ��
		#     �� / 2
		#       ��
		# ��  ���੤  0
		#       ��
		#    3���� / 2
		# miniPitch / maxPitch �����Ҫ�� 3D �������н���ȡ��������
		# ��С�� 180 �ļ��� 180������ 180 �ļ�ȥ 180
		# ���磺minPitch = 150.0 ʱ��ʵ�ʽǶ��ǣ�150.0 + 180.0 = 330.0
		# �� maxPitch = 230.0 ʱ��ʵ�ʽǶ��ǣ�230.0 - 180.0 = 50.0
		self.__distance = 7.68
		self.__limit = 155.0 * self.cc_per_angle_in_radian_ - self.minPitch

		self.__initCamera()

	def __initCamera( self ) :
		"""
		��ʼ�����
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
		����ά����ϵ�п������
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
		�ָ������Ĭ�ϲ���
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
		#�����ͷ�ľ���С�ڸ�������С���룬��ô�ͽ���ͷ����
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
	��ɫ���������������
	"""
	def __init__( self ) :
		self.__camShell = CUCShell()					# �������е������
		minDist = 1.0
		maxDist = Const.ROLE_CREATE_MAX_DISTACE #7.68
		self.__camShell.minDistance = minDist
		self.__camShell.maxDistance = maxDist
		self.__deltaDist = ( maxDist - minDist ) / 3	# ÿ�ε�����ͷ�ľ���

		self.__isFixup = False							# ָ�����ָ���Ƿ񱻿���
		self.__pos = Math.Vector2( 0, 0 )				# ��¼����Ҽ�����ʱ��λ��
		self.__isEnable = True							# ��¼�ÿ������Ƿ��ڿ���״̬


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def cameraShell( self ) :
		"""
		��ȡ�����
		"""
		return self.__camShell


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def use( self, yaw = 0.0 ) :
		"""
		Ӧ�����
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
		̧�߾�ͷ
		"""
		self.__camShell.camera.pivotPosition = Math.Vector3( 0.0, 2.2, 0.0 )

	def carryDownCamera( self ) :
		"""
		̧�߾�ͷ
		"""
		self.__camShell.camera.pivotPosition = Math.Vector3( 0.0, 1.8, 0.0 )

	def closeTarget( self ) :
		"""
		������ͷ
		"""
		self.__camShell.addDistance( -self.__deltaDist, True )

	def extendTarget( self ) :
		"""
		��չ��ͷ
		"""
		self.__camShell.addDistance( self.__deltaDist, True )

	# ---------------------------------------
	def fixed( self ) :
		"""
		ָ������Ƿ������������ס
		"""
		return self.__isFixup

	def fix( self ) :
		"""
		��ס���
		"""
		self.__isFixup = True
		self.__pos = GUI.mcursor().position
		GUI.mcursor().visible = False

	def unfix( self ) :
		"""
		�ָ����
		"""
		if self.__isFixup :
			self.__isFixup = False
			rds.ccursor.normal()
			GUI.mcursor().position = self.__pos
			GUI.mcursor().visible = True

	# -------------------------------------------------
	def enable( self ) :
		"""
		�������������
		"""
		self.__isEnable = True

	def disable( self ) :
		"""
		�ر����������
		"""
		self.__isEnable = False

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		�ػ񰴼���Ϣ
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
		�ػ�����ƶ���Ϣ
		"""
		if not self.__isEnable : return False							# ������رգ��򷵻�
		if BigWorld.isKeyDown( KEY_RIGHTMOUSE ) and csol.isVirtualKeyDown( VK_RBUTTON ): # ����Ҽ����ڰ���״̬
			if not self.__isFixup:										# �����û��ס���
				self.fix()												# ��ס���
			else :														# ����
				GUI.mcursor().position = self.__pos						# �������λ��
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
	���������
	"""
	def __init__( self ) :
		self.__camShell = CUCShell()				# �������е������
		self.__camShell.minDistance = 1.0			# ��ͷ�������

		self.__isFixup = False						# ָ�����ָ���Ƿ񱻿���
		self.__pos = Math.Vector2( 0, 0 )			# ��¼�����(��)������ʱ��λ�ã����ǳɹ���λ��λ��
		self.__isEnable = True						# ��¼�ÿ������Ƿ��ڿ���״̬

		self.__fixupDistance = 5					# ��갴�º����ƶ����پ���ſ�ʼ��λ����Ҫ�����������ƶ��Ĵ���
		self.__fixupPos	= Math.Vector2( 0, 0 )		# �ж�����Ƿ��ܹ���λ�Ŀ�ʼλ��
		self.__canfixup = False						# �Ƿ���Խ��п�λ
		self.isYawLocked = False					# �����Ƿ�����

		shortcutMgr.setHandler( "ACTION_INCREASE_DISTANCE", self.__incDistance )	# �����Ӿ�
		shortcutMgr.setHandler( "ACTION_DECREASE_DISTANCE", self.__decDistance )	# ��С�Ӿ�

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
		ʹ�ÿ�ݼ������Ӿ�
		"""
		player = BigWorld.player()
		if player and player.hasControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA ): return True

		self.__camShell.handle_( 0.0, 0.0, 120 )
		return True

	def __decDistance( self ) :
		"""
		ʹ�ÿ�ݼ������Ӿ�
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
		��ȡ���
		"""
		return self.__camShell


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def use( self ) :
		"""
		Ӧ�����
		"""
		self.__camShell.camera.source = Math.Matrix( BigWorld.dcursor().matrix )
		BigWorld.camera( self.__camShell.camera )

	# -------------------------------------------------
	def reset( self, dis = 10.0 ) :
		"""
		�ָ�����ĸ�������
		"""
		camera = self.__camShell.camera
		camera.target = BigWorld.PlayerMatrix()
		yaw = BigWorld.player().yaw + 3.4
		self.__camShell.setYaw( yaw )							# Ĭ����������ɫ����
		self.__camShell.update()								# �������
		self.__camShell.minDistance = 1.0
		self.__camShell.maxDistance = 15.0
		dst = self.__camShell.maxDistance
		self.__camShell.setDistance( dis, True )
		self.__singleKeyPos = Math.Vector2( 0, 0 )


	# ---------------------------------------
	def fixed( self ) :
		"""
		ָ������Ƿ������������ס
		"""
		return self.__isFixup

	def fix( self ) :
		"""
		��ס���
		"""
		self.__isFixup = True
		self.__pos = GUI.mcursor().position
		GUI.mcursor().visible = False

	def unfix( self ) :
		"""
		�ָ����
		"""
		if self.__isFixup :
			self.__isFixup = False
			rds.ccursor.normal()
			GUI.mcursor().position = self.__pos
			GUI.mcursor().visible = True

	# -------------------------------------------------
	def enable( self ) :
		"""
		�������������
		"""
		self.__isEnable = True

	def disable( self ) :
		"""
		�ر����������
		"""
		self.__isEnable = False

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		�ػ񰴼���Ϣ
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
		��������ģʽ1
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
		��������ģʽ2
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
		�ػ�����ƶ���Ϣ
		"""
		if not self.__isEnable : return False							# ������رգ��򷵻�
		player = BigWorld.player()

		# ����Ϸ�ո�������ĳЩʱ��player��ΪNone�������������һ�����䣬��ֹ�����쳣 by mushuang
		if not player:
			ERROR_MSG( "Can't find player!" )
			return
		return self._c_control_mod[player.c_control_mod]( dx, dy, dz, player )

	def _c_control_1( self, dx, dy, dz, player ):
		"""
		�ƶ�����ģʽ1
		"""
		if BigWorld.isKeyDown( KEY_RIGHTMOUSE ) and csol.isVirtualKeyDown( VK_RBUTTON ): # ����Ҽ����ڰ���״̬
			if player.hasControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA ):
				return True

			if not self.__isFixup :										# �����û��ס���
				self.fix()
			else:
				GUI.mcursor().position = self.__pos						# �������λ��
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
		�ƶ�����ģʽ2
		"""
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) and csol.isVirtualKeyDown( VK_LBUTTON ): # ���������ڰ���״̬
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

			if not self.__isFixup :										# �����û��ס���
				self.fix()												# ��ס���
			else :														# ����
				GUI.mcursor().position = self.__pos						# �������λ��
				self.__camShell.handle_( dx, dy, dz )
			return True
		elif BigWorld.isKeyDown( KEY_RIGHTMOUSE ) and csol.isVirtualKeyDown( VK_RBUTTON ): # ����Ҽ����ڰ���״̬
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

			if not self.__isFixup :										# �����û��ס���
				self.fix()												# ��ס���
			else :														# ����
				GUI.mcursor().position = self.__pos						# �������λ��
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
		����������״̬
		"""
		self.unfix()

# --------------------------------------------------------------------
# �˺�����3D�����������������
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
		��ʼ�������
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
		��תָ������
		"""
		deltaX = distance / float( self.__speedGene )
		self.__camShell.handle_( deltaX, 0, 0 )
		self.__cycleCBID = BigWorld.callback( 0.01, self.__circumvolve )

	def __prepareRunning( self ) :
		"""
		׼����ʼ
		"""
		self.__camShell.camera.positionAcceleration = 3				# �趨��ת���ٶ��ʺϵļ��ٶȣ���ת����ƽ��
		self.__circumvolve()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		camShell = self.__camShell
		camShell.camera.positionAcceleration = 0					# �Ѽ��ٶ�����Ϊ0����������ٶ�λ��ָ����
		tMatrix = camShell.camera.target
		tMatrix.setTranslate( ( 238, 8, 110 ) )
		#camShell.stareAt( ( 238, 8, 105 ) )

	def run( self ) :
		"""
		��ʼת��
		"""
		self.stop()
		self.__runCBID = BigWorld.callback( 1, self.__prepareRunning )

	def stop( self ) :
		"""
		ֹͣת��
		"""
		BigWorld.cancelCallback( self.__runCBID )
		BigWorld.cancelCallback( self.__cycleCBID )
		self.__runCBID = 0
		self.__cycleCBID = 0

	def use( self ) :
		"""
		���������
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
# ���ɷ��������
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
		��ʼ�������Ĭ��ֵ
		"""
		self.camera_.target = Math.Matrix()
		self.__setPreferredPos()
		self.camera_.timeMultiplier = 8.0

	# -------------------------------------------------
	def __setPreferredPos( self ) :
		"""
		��ȡ������Ŀ�������
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
		�ָ������Ĭ�ϲ���
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
		�������ƫ��
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
	�̶��ӽ����������
	"""
	def __init__( self ) :
		WorldCamHandler.__init__( self )
		self.isYawLocked = True					# �����Ƿ�����


	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		"""
		�ػ񰴼���Ϣ
		"""
		return False


	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		�ػ�����ƶ���Ϣ
		"""
		if dz != 0.0 and rds.ruisMgr.isMouseHitScreen():
			self.cameraShell.handle_( 0.0, 0.0, dz )
			return True
		return False

	def use( self, yaw = -9.4, pitch = 3.766 ):
		WorldCamHandler.use( self )
		self.reset( yaw, pitch )		# �̶��ӽ����ÿһ�����ö��������������

	def reset( self, yaw = -9.4, pitch = 3.766, changeMaxPitch = True ) :
		"""
		�ָ�����ĸ�������
		"""
		camera = self.cameraShell.camera
		camera.target = BigWorld.PlayerMatrix()
		self.cameraShell.setYaw( yaw )
		if changeMaxPitch:
			self.cameraShell.maxPitch = 230 * math.pi / 180     # ��������ӽǶ�
		self.cameraShell.setPitch( pitch )
		self.cameraShell.update()								# �������
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
		Ӧ�ô����
		"""
		BigWorld.camera( self.cameraShell.camera )

	def reset( self, dis = 10.0 ) :
		"""
		�ָ�����ĸ�������
		"""
		pass

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		�ػ�����ƶ���Ϣ
		"""
		# ֻ�ڲ��԰汾��������������
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
		��λ���
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
