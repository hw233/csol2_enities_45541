# -*- coding: gb18030 -*-
#
# $Id: AreaDefine.py,v 1.13 2008-07-15 04:05:54 kebiao Exp $

"""
����ѡ��
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
		���캯����
		"""
		self.parent = parent
		pass

	def load( self, dictDat ):
		pass

	def getObjectList( self, caster, target ):
		"""
		��ȡ�����еĶ����б�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		#object.entitiesInRangeExt
		return []


class Single( Area ):
	def __init__( self, parent ):
		"""
		���캯����
		"""
		Area.__init__( self, parent )

	def getObjectList( self, caster, target ):
		entity = target.getObject()
		if isinstance( entity, BigWorld.Entity ):
			return [ entity ] 
		else:
			#���������CastObjectType == 2 ���߱�����<CastObjectType>�����ó�����Ϊentity����ص�����
			#���<ReceiverCondition>����ΪRECEIVER_CONDITION_ENTITY_SELF ��ôCastObjectType����Ϊ2����������ΪRECEIVER_CONDITION_ENTITY_SELF
			#��Ϊ<ReceiverCondition>����ΪRECEIVER_CONDITION_ENTITY_SELF��ʵ����˵�����������Ӱ����ǵ���entity
			printStackTrace()
			if not isinstance( target, SkillTargetObjImpl.SkillTargetObjEntity ):
				ERROR_MSG( "config in xml is Error! skill ID is %s"%self.parent.getID() )
		return []


class Circle( Area ):
	def __init__( self, parent ):
		"""
		���캯����
		"""
		Area.__init__( self, parent )
		self.radius = 10	# Ĭ��ֵ10��

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
		���캯����
		"""
		Area.__init__( self, parent )

	def load( self, dictDat ):
		self.width = dictDat["value1"] / 2
		self.length = dictDat["value2"]

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

	def getObjectList( self, caster, target ):
		dis = caster.queryTemp( "MOVE_EFFECT_DIS", 0 )
		length = max( self.length, dis )
		return [ e for e in caster.entitiesInRangeExt( math.sqrt( pow( length, 2 ) + pow( self.width, 2 ) ) , None, target.getObjectPosition() ) if self.inArea( target.getObjectPosition(),target.convertReference( caster ).yaw, e.position ) ]


class Sector( Area ):
	def __init__( self, parent ):
		"""
		���캯����
		"""
		Area.__init__( self, parent )
		self.radius = 2.0
		self.angle = 120 / 2

	def load( self, dictDat ):
		self.radius = dictDat["value1"]
		self.angle = dictDat["value2"] / 2

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

		if an == 0:	 # �պ���ʩ������ͬһ��λ��
			an = 1

		if an > 1:
			an = 1

		angle = int( math.acos( an ) / 3.1415926 * 180 )
		if angle <= self.angle:	# С�ڻ���ڼн�
			return True
		return False

	def getObjectList( self, caster, target ):
		"""
		��ȡ�����еĶ����б�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# ���䷽��
		transmitDir = Math.Vector3()
		# �����������ε������ԵĶ��� ��ʱtarget.getObjectPosition()������λ�ã���ô����λ��-����λ�ûᵼ�·���Ϊ(0,0,0)��һ������ ��˼���������ж�
		# ��������ʹ��target�Ĳο����ж��Ƿ���ʩ���ߣ�������һ����ĳ��λ��ʩ����˵���ο���Ҳ��ʩ���ߣ�����ĳ������¹�����ܺ�ʩ��������ͬ��λ��
		# ����ʹ��λ�þ��������ж�
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
	��ȡ����ѡ��ʵ����
		@param areaName:	����
		@type areaName:		string
	"""
	return g_areas[objectType]( parent )

