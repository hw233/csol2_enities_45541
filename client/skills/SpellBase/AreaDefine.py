# -*- coding: gb18030 -*-
#
# $Id: AreaDefine.py,v 1.2 2008-07-15 04:08:01 kebiao Exp $

"""
����ѡ��
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
		���캯����
		"""
		pass

	def load( self, dict ):
		pass

	def getObjectList( self, caster, object, position ):
		"""
		��ȡ�����еĶ����б�
			@param object:		�ο�����
			@type object:		BigWorld.entity
			@param position:	�ο�����
			@type position:		vector3
		"""
		#object.entitiesInRange
		return []


class Single( Area ):
	def __init__( self ):
		"""
		���캯����
		"""
		Area.__init__( self )

	def getObjectList( self, caster, object, position ):
		return [object]


class Circle( Area ):
	def __init__( self ):
		"""
		���캯����
		"""
		Area.__init__( self )
		self.radius = 10	# Ĭ��ֵ10��

	def load( self, dict ):
		if dict.has_key( "value1" ):
			self.radius = dict["value1"]

	def getObjectList( self, caster, object, position ):
		return object.entitiesInRange( self.radius, None, position )


class Radial( Area ):
	def __init__( self ):
		"""
		���캯����
		"""
		Area.__init__( self )

	def load( self, dict ):
		self.width = dict["value1"] / 2
		self.length = dict["value2"]

	def inArea( self, spos, yaw, tpos ):
		"""
		�ж��Ƿ��������ڡ�
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
		���캯����
		"""
		Area.__init__( self )
		self.radius = 2.0
		self.angle = 120 / 2

	def load( self, dict ):
		self.radius = dict["value1"]
		self.angle = dict["value2"] / 2

	def inArea( self, caster, entity, transmitDir ):
		"""
		ʵ���Ƿ������η�Χ��
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

		if an == 0:		# �պ���ʩ������ͬһ��λ��
			an = 1

		if an > 1:
			an = 1

		angle = int(math.acos( an ) / 3.1415926 * 180)
		if angle <= self.angle:	# С�ڻ���ڼн�
			return True
		return False

	def getObjectList( self, caster, object, position ):
		"""
		��ȡ�����еĶ����б�
			@param object:		�ο�����
			@type object:		BigWorld.entity
			@param position:	�ο�����
			@type position:		vector3
		"""
		# ���䷽��
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
	��ȡ����ѡ��ʵ����
		@param areaName:	����
		@type areaName:		string
	"""
	return g_areas[objectType]()


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/01/05 03:47:16  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
#
