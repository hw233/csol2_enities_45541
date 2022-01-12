# -*- coding: gb18030 -*-
#
# $Id: AreaDefine.py,v 1.13 2008-07-15 04:05:54 kebiao Exp $

"""
区域选择
"""

import BigWorld
import Language
from bwdebug import *
import Math
import math
import csdefine
import SkillTargetObjImpl

class Area:
	def __init__( self, parent ):
		"""
		构造函数。
		"""
		self.parent = parent
		pass

	def load( self, dictDat ):
		pass

	def getObjectList( self, caster, target ):
		"""
		获取区域中的对象列表。
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		#object.entitiesInRangeExt
		return []


class Single( Area ):
	def __init__( self, parent ):
		"""
		构造函数。
		"""
		Area.__init__( self, parent )

	def getObjectList( self, caster, target ):
		entity = target.getObject()
		if isinstance( entity, BigWorld.Entity ):
			return [ entity ] 
		else:
			#如果配置上CastObjectType == 2 或者必须在<CastObjectType>中配置出条件为entity与相关的条件
			#如果<ReceiverCondition>条件为RECEIVER_CONDITION_ENTITY_SELF 那么CastObjectType必须为2且条件必须为RECEIVER_CONDITION_ENTITY_SELF
			#因为<ReceiverCondition>条件为RECEIVER_CONDITION_ENTITY_SELF其实隐含说明了这个技能影响的是单个entity
			printStackTrace()
			if not isinstance( target, SkillTargetObjImpl.SkillTargetObjEntity ):
				ERROR_MSG( "config in xml is Error! skill ID is %s"%self.parent.getID() )
		return []


class Circle( Area ):
	def __init__( self, parent ):
		"""
		构造函数。
		"""
		Area.__init__( self, parent )
		self.radius = 10	# 默认值10米

	def load( self, dictDat ):
		if dictDat.has_key( "value1" ):
			self.radius = dictDat["value1"]

	def getObjectList( self, caster, target ):
		es = caster.entitiesInRangeExt( self.radius, None, target.getObjectPosition() )
		es.append( caster )
		return es


class Radial( Area ):
	def __init__( self, parent ):
		"""
		构造函数。
		"""
		Area.__init__( self, parent )

	def load( self, dictDat ):
		self.width = dictDat["value1"] / 2
		self.length = dictDat["value2"]

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

	def getObjectList( self, caster, target ):
		dis = caster.queryTemp( "MOVE_EFFECT_DIS", 0 )
		length = max( self.length, dis )
		return [ e for e in caster.entitiesInRangeExt( math.sqrt( pow( length, 2 ) + pow( self.width, 2 ) ) , None, target.getObjectPosition() ) if self.inArea( target.getObjectPosition(),target.convertReference( caster ).yaw, e.position ) ]


class Sector( Area ):
	def __init__( self, parent ):
		"""
		构造函数。
		"""
		Area.__init__( self, parent )
		self.radius = 2.0
		self.angle = 120 / 2

	def load( self, dictDat ):
		self.radius = dictDat["value1"]
		self.angle = dictDat["value2"] / 2

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

		if an == 0:	 # 刚好与施法者在同一个位置
			an = 1

		if an > 1:
			an = 1

		angle = int( math.acos( an ) / 3.1415926 * 180 )
		if angle <= self.angle:	# 小于或等于夹角
			return True
		return False

	def getObjectList( self, caster, target ):
		"""
		获取区域中的对象列表。
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 发射方向
		transmitDir = Math.Vector3()
		# 对于自身扇形等自身性的东西 此时target.getObjectPosition()是自身位置，那么自身位置-自身位置会导致方向为(0,0,0)的一个错误 因此加上了这句判断
		# 本来可以使用target的参考者判断是否是施法者，但对于一个向某个位置施法来说，参考者也是施法者，而且某种情况下怪物可能和施法者是相同的位置
		# 所以使用位置距离来做判断
		position = target.getObjectPosition()
		if caster.position.flatDistTo( position ) > 0.0:
			transmitDir = target.convertReference( caster ).position - caster.position
			transmitDir.y = 0
		else:
			transmitDir.x = math.sin( caster.direction.z )
			transmitDir.z = math.cos( caster.direction.z )
		transmitDir.normalise()

		return [ ob for ob in caster.entitiesInRangeExt( self.radius, None, position ) if self.inArea( caster, ob, transmitDir ) ]

g_areas = {
	csdefine.SKILL_SPELL_AREA_SINGLE	:	Single,
	csdefine.SKILL_SPELL_AREA_CIRCLE	:	Circle,
	csdefine.SKILL_SPELL_AREA_RADIAL	:	Radial,
	csdefine.SKILL_SPELL_AREA_SECTOR	:	Sector,
}

def newInstance( objectType, parent ):
	"""
	获取对象选择实例。
		@param areaName:	名称
		@type areaName:		string
	"""
	return g_areas[objectType]( parent )

