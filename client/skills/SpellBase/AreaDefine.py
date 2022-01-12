# -*- coding: gb18030 -*-
#
# $Id: AreaDefine.py,v 1.2 2008-07-15 04:08:01 kebiao Exp $

"""
区域选择
"""

import BigWorld
import Language
from bwdebug import *
import Math
import math
import csdefine

class Area:
	def __init__( self ):
		"""
		构造函数。
		"""
		pass

	def load( self, dict ):
		pass

	def getObjectList( self, caster, object, position ):
		"""
		获取区域中的对象列表。
			@param object:		参考对象
			@type object:		BigWorld.entity
			@param position:	参考坐标
			@type position:		vector3
		"""
		#object.entitiesInRange
		return []


class Single( Area ):
	def __init__( self ):
		"""
		构造函数。
		"""
		Area.__init__( self )

	def getObjectList( self, caster, object, position ):
		return [object]


class Circle( Area ):
	def __init__( self ):
		"""
		构造函数。
		"""
		Area.__init__( self )
		self.radius = 10	# 默认值10米

	def load( self, dict ):
		if dict.has_key( "value1" ):
			self.radius = dict["value1"]

	def getObjectList( self, caster, object, position ):
		return object.entitiesInRange( self.radius, None, position )


class Radial( Area ):
	def __init__( self ):
		"""
		构造函数。
		"""
		Area.__init__( self )

	def load( self, dict ):
		self.width = dict["value1"] / 2
		self.length = dict["value2"]

	def inArea( self, spos, yaw, tpos ):
		"""
		判断是否在区域内。
		"""
		m = Math.Matrix()
		m.setRotateY( - yaw )
		v = tpos - spos
		v = m.applyPoint(v)

		if abs( v[0] ) > self.width or v[2] < 0 or v[2] > self.length:
			return False

		return True

	def getObjectList( self, caster, object, position ):
		return [ e for e in object.entitiesInRange( self.length, None, position ) if self.inArea( position, object.direction, e.position ) ]


class Sector( Area ):
	def __init__( self ):
		"""
		构造函数。
		"""
		Area.__init__( self )
		self.radius = 2.0
		self.angle = 120 / 2

	def load( self, dict ):
		self.radius = dict["value1"]
		self.angle = dict["value2"] / 2

	def inArea( self, caster, entity, transmitDir ):
		"""
		实体是否在扇形范围内
		"""
		srcPos = Math.Vector3( caster.position )
		srcPos.y = 0
		desPos = Math.Vector3( entity.position )
		desPos.y = 0

		desDir = desPos - srcPos
		desDir.y = 0
		desDir.normalise()

		an = transmitDir.dot( desDir )

		if an < -1:
			an = -1

		if an == 0:		# 刚好与施法者在同一个位置
			an = 1

		if an > 1:
			an = 1

		angle = int(math.acos( an ) / 3.1415926 * 180)
		if angle <= self.angle:	# 小于或等于夹角
			return True
		return False

	def getObjectList( self, caster, object, position ):
		"""
		获取区域中的对象列表。
			@param object:		参考对象
			@type object:		BigWorld.entity
			@param position:	参考坐标
			@type position:		vector3
		"""
		# 发射方向
		transmitDir = Math.Vector3()
		transmitDir = object.position - caster.position
		transmitDir.y = 0
		transmitDir.normalise()

		return [ ob for ob in caster.entitiesInRange( self.radius, None, position ) if self.inArea( caster, ob, transmitDir ) ]


g_areas = {
	csdefine.SKILL_SPELL_AREA_SINGLE	:	Single,
	csdefine.SKILL_SPELL_AREA_CIRCLE	:	Circle,
	csdefine.SKILL_SPELL_AREA_RADIAL	:	Radial,
	csdefine.SKILL_SPELL_AREA_SECTOR	:	Sector,
}

def newInstance( objectType ):
	"""
	获取对象选择实例。
		@param areaName:	名称
		@type areaName:		string
	"""
	return g_areas[objectType]()


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/01/05 03:47:16  kebiao
# 调整技能结构，目录结构
#
#
