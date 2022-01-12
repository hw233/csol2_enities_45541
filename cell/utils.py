# -*- coding: gb18030 -*-

"""This module implements some util function.
$Id: utils.py,v 1.18 2008-01-30 07:55:06 huangyongwei Exp $"""

########################################################################
#
# ģ��: utils
# ����: �ṩһЩ��CellҪʹ�õĹ��ܺ����͹�����
#
########################################################################

import BigWorld
import Math
import Language
import math
import types
import csdefine
import csconst
from bwdebug import *
import re
import random
import copy
from optimize_with_cpp import utils_func as UTILS_CPP_OPTIMIZE

pat = re.compile(r"^\s*-?([1-9]\d*\.{0,1}\d*|0\.\d*[1-9]\d*|0?\.0+|0)(\s*\,|\s+)\s*-?([1-9]\d*\.{0,1}\d*|0\.\d*[1-9]\d*|0?\.0+|0)(\s*\,|\s+)\s*-?([1-9]\d*\.{0,1}\d*|0\.\d*[1-9]\d*|0?\.0+|0)\s*$")


boundingBoxes = {}
def getBoundingBox( modelNumber ):
	global boundingBoxes
	if boundingBoxes.has_key(modelNumber):
		return boundingBoxes[modelNumber]

	# open .visual
	if modelNumber[0] == "g":
		visual = "monster/%s/%s.visual/boundingBox" %( modelNumber, modelNumber )
		DEFAULT_VISUAL =  "monster/gw0001/gw0001.visual/boundingBox"
	elif modelNumber[0] == "n":
		visual = "npc/%s/%s.visual/boundingBox" %( modelNumber, modelNumber )
		DEFAULT_VISUAL = "npc/npcm0001/npcm0001.visual/boundingBox"
	section = Language.openConfigSection( visual )
	if section is None:
		section = Language.openConfigSection( DEFAULT_VISUAL )
		ERROR_MSG("%s  use the DEFAULT_VISUAL's boundingBox" % modelNumber)


	bb = BoundingBox()
	bb.load( section )
	boundingBoxes[modelNumber] = bb
	return bb

#
# ���ܣ��ҵ�����NavPoly Pointλ��Y���򵽵���ĵ�
# ������
#       spaceID			����ID
#       pos				����λ��
# ���أ������
#
def navpolyToGround( spaceID, pos, addY = 0.2, decY = 2.4 ):
	pos1 = Math.Vector3(pos)
	pos1.y -= decY
	pos2 = Math.Vector3(pos)
	pos2.y += addY
	result = BigWorld.collide( spaceID, pos2, pos1 )
	if result is not None:
		return result[0]
	else:
		return pos

# ����: ����position��monster BoundingBox��XYZ�ľ���
# ����:
#       monster			����Entity
#       pos				Vector3
# ����: 2��֮��XYZƽ��ľ���
#
def distanceBB( monster, pos ):
	if monster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		# ���Ǽ�����Ҳ��ܹ������
		return monster.position.flatDistTo( pos ) - 1	# ƫ��1��

	bb = getBoundingBox( monster.modelNumber )
	if bb is None:
		raise AttributeError( monster.modelNumber )
	gpos = navpolyToGround( monster.spaceID, monster.position )
	deltapos = pos - gpos
	return bb.distanceXYZ( deltapos )

#
# ����: ��������֮����XZƽ���yawֵ
#       ����posfrom��posto�۲��yawֵ
# ����:
#       posfrom			�۲�㣬3��������tuple����Vector3
#       posto			Ŀ��㣬3��������tuple����Vector3
# ����: yawֵ�Ļ���(radius)
#
def yawFromPos( posfrom, posto ):
	offX = posto[0] - posfrom[0]
	offZ = posto[2] - posfrom[2]
	return math.atan2(offX, offZ)

#
# ���ܣ��ҵ�����Pointλ��Y������ӽ��ĵ����
# ������
#       spaceID			����ID
#       pos				����λ��
# ���أ���ӽ��ĵ����
#
def toGround( spaceID, pos ):
	pos1 = Math.Vector3(pos)
	pos1.y -= 1.5
	pos2 = Math.Vector3(pos)
	pos2.y += 1.5
	result = BigWorld.collide( spaceID, pos2, pos1 )
	if result is not None:
		return result[0]
	else:
		return pos

class BoundingBox:
	def __init__( self ):
		self.minp = Math.Vector3(0, 0, 0)
		self.maxp = Math.Vector3(0, 0, 0)
		self.boundWidth = 0.0

	def load( self, sect ):
		self.minp.set( sect._min.asVector3 )
		self.maxp.set( sect._max.asVector3 )
		self.boundWidth = self.maxp.z + csconst.ROLE_MODEL_WIDTH

	def distanceXYZ( self, pos ):
		distance = pos.length
		return distance - self.boundWidth

	def __str__( self ):
		return str(self.minp) + " " + str(self.maxp) + " " + str(self.boundWidth)

# �ж�Vector3�������ݸ�ʽ�Ƿ���ȷ
# paramΪstring����
def vector3TypeConvert( param ):
	try:
		m = pat.match( param ).group().replace(",",' ').split()
		if len( m ) != 3:
			return None
	except:
		return None

	result = Math.Vector3( float( m[0] ), float( m[1] ), float( m[2] ) )
	return result


def getSpaceLable( spaceID ):
	"""
	��ȡspaceLabel
	"""
	return BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_KEY )


"""
����ʹ��
"""
def getWitnessMonsterCountInEachSpace():
	"""
	��ȡ������ͼAI����Ĺ�������
	"""
	result = {}
	for i in BigWorld.entities.values():
		if i.thinkControlID > 0:
			spaceLabel = getSpaceLable( i.spaceID )
			if spaceLabel not in result:
				result[spaceLabel] = 0
			result[spaceLabel] += 1

	return result

def cllidePos( spaceID, position, offset ):
	upPos = (position.x, position.y+offset, position.z)
	downPos = (position.x, position.y-offset, position.z)
	result = BigWorld.collide(spaceID, upPos, downPos)
	if result:
		return result[0]
	else:
		return None

#-----------------------------------------------------------
# ����һ��entity֮��������Ĺ�������
#-----------------------------------------------------------
def ent_flatDistance( src, dst ):
	"""xzƽ�������ĵ���룬����entity���ĵ�֮��ľ���
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.ent_flatDistance( src, dst )

def ent_z_distance( src, dst ):
	"""z�᷽��ľ��룬����entity����淽��ľ��룬������boundingBox
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.ent_z_distance( src, dst )

def ent_z_distance_min( src, dst ):
	"""z�᷽������entity����������վ�ľ���
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.ent_z_distance_min( src, dst )

def ent_x_distance( src, dst ):
	"""x�᷽��ľ��룬����entityƽ��վ�ľ��룬������boundingBox
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.ent_x_distance( src, dst )

def ent_x_distance_min( src, dst ):
	"""x�᷽������entityƽ�Ž�����վ�ľ���
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.ent_x_distance_min( src, dst )

def ent_length( entity ):
	"""entity�ĳ���
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.ent_length( entity )

def ent_width( entity ):
	"""entity�Ŀ��
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.ent_width( entity )

def ent_height( entity ):
	"""entity�ĸ߶�
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.ent_height( entity )


def checkForLocation( entity ):
	"""����Ƿ������¶�λ�Լ���λ��
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.checkForLocation( entity )

def locate( entity, maxMove ):
	"""��λentity��λ��
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.locate( entity, maxMove )

def randomPosAround( center, radius, radian, yaw ):
	"""��xzƽ���center��ΪԲ�ģ��뾶��radius��Բ�ϣ����ȡ���ȷ�Χ��radian��
	������yaw�ĵ�
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	@param	center	: POSITION��Բ��λ��
	@param	radius	: float���뾶
	@param	radian	: float��0 - 2*pi����λ�ǻ��ȣ���ʾȡ����Բ����
	@param	yaw		: float��0 - 2*pi����λ�ǻ��ȣ���ʾƫת���ٻ��ȣ���ֵ��ʱ�룬��ֵ˳ʱ��
	"""
	return UTILS_CPP_OPTIMIZE.randomPosAround( center, radius, radian, yaw )

def disperse( entity, centerPos, radius, maxMove ):
	"""
	��ĳ�����ĵ���Χָ����Χ��ɢ����maxMove������������ÿ���ƶ���
	�����룬���ʼ�����������ڷ�ֹ�����ƶ�ʱ����Ŀ�꣬�ƶ���Ŀ��
	���󣬶�ʵ�ʲ��Ա�����maxMove���Ƶ�̫Сʱ�����Ǻ����ҵ�����ȫ
	�������ĵ㣬���Ǽ�ʹ����ȡ�ĵ㲻����maxMove������ֻҪ����
	canNavigateTo������Ȼ���˵���ΪĿ��㡣

	2013/8/14�޸ģ�����ʹ��maxMove��������ƶ����룬��ֹentity��Խ
	Ŀ��ķ�ʽЧ��̫�����Ż��˸÷�ʽ����Ϊ����ȡ�����ʱ������
	��ȡ��Ŀ�����ָ�����ȷ�Χ�ڵĵ㣬�����Ͳ��ᷢ��ɢ��ʱ����Ŀ��
	�ߵ������ȥ���������randomPosAround

	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.disperse( entity, centerPos, radius, maxMove )

# ��AI���Ƶ�����
def checkAndMove( entity ):
	"""���м�⣬������ص�������ɢ��
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.checkAndMove( entity )

def checkAndMoveByDis( entity, maxMove ):
	"""���м�⣬������ص�������ɢ��������ɢ����Ŀ��λ����maxMove����֮��
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.checkAndMoveByDis( entity, maxMove )

def moveOut( srcEntity, dstEntity, distance, moveMax ):
	"""ɢ��
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.moveOut( srcEntity, dstEntity, distance, moveMax )

def followCheckAndMove( srcEntity, dstEntity ):
	"""������ڸ���Ŀ����Χɢ��
	��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
	"""
	return UTILS_CPP_OPTIMIZE.followCheckAndMove( srcEntity, dstEntity )
