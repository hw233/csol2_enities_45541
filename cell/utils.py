# -*- coding: gb18030 -*-

"""This module implements some util function.
$Id: utils.py,v 1.18 2008-01-30 07:55:06 huangyongwei Exp $"""

########################################################################
#
# 模块: utils
# 功能: 提供一些在Cell要使用的功能函数和功能类
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
# 功能：找到给定NavPoly Point位置Y方向到地面的点
# 参数：
#       spaceID			场景ID
#       pos				给定位置
# 返回：地面点
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

# 功能: 计算position到monster BoundingBox在XYZ的距离
# 参数:
#       monster			怪物Entity
#       pos				Vector3
# 返回: 2点之间XYZ平面的距离
#
def distanceBB( monster, pos ):
	if monster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		# 我们假设玩家不能攻击玩家
		return monster.position.flatDistTo( pos ) - 1	# 偏移1米

	bb = getBoundingBox( monster.modelNumber )
	if bb is None:
		raise AttributeError( monster.modelNumber )
	gpos = navpolyToGround( monster.spaceID, monster.position )
	deltapos = pos - gpos
	return bb.distanceXYZ( deltapos )

#
# 功能: 计算两点之间在XZ平面的yaw值
#       即从posfrom向posto观察的yaw值
# 参数:
#       posfrom			观察点，3个分量的tuple或者Vector3
#       posto			目标点，3个分量的tuple或者Vector3
# 返回: yaw值的弧度(radius)
#
def yawFromPos( posfrom, posto ):
	offX = posto[0] - posfrom[0]
	offZ = posto[2] - posfrom[2]
	return math.atan2(offX, offZ)

#
# 功能：找到给定Point位置Y方向最接近的地面点
# 参数：
#       spaceID			场景ID
#       pos				给定位置
# 返回：最接近的地面点
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

# 判断Vector3类型数据格式是否正确
# param为string类型
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
	获取spaceLabel
	"""
	return BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_KEY )


"""
调试使用
"""
def getWitnessMonsterCountInEachSpace():
	"""
	获取各个地图AI激活的怪物数量
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
# 定义一组entity之间距离计算的公共方法
#-----------------------------------------------------------
def ent_flatDistance( src, dst ):
	"""xz平面上中心点距离，两个entity中心点之间的距离
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.ent_flatDistance( src, dst )

def ent_z_distance( src, dst ):
	"""z轴方向的距离，两个entity面对面方向的距离，不包含boundingBox
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.ent_z_distance( src, dst )

def ent_z_distance_min( src, dst ):
	"""z轴方向，两个entity面对面紧贴着站的距离
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.ent_z_distance_min( src, dst )

def ent_x_distance( src, dst ):
	"""x轴方向的距离，两个entity平排站的距离，不包含boundingBox
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.ent_x_distance( src, dst )

def ent_x_distance_min( src, dst ):
	"""x轴方向，两个entity平排紧贴着站的距离
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.ent_x_distance_min( src, dst )

def ent_length( entity ):
	"""entity的长度
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.ent_length( entity )

def ent_width( entity ):
	"""entity的宽度
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.ent_width( entity )

def ent_height( entity ):
	"""entity的高度
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.ent_height( entity )


def checkForLocation( entity ):
	"""检测是否能重新定位自己的位置
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.checkForLocation( entity )

def locate( entity, maxMove ):
	"""定位entity的位置
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.locate( entity, maxMove )

def randomPosAround( center, radius, radian, yaw ):
	"""在xz平面的center点为圆心，半径是radius的圆上，随机取弧度范围是radian，
	朝向是yaw的点
	禁止直接编辑该方法，请到下层模块中修改。
	@param	center	: POSITION，圆心位置
	@param	radius	: float，半径
	@param	radian	: float，0 - 2*pi，单位是弧度，表示取多少圆弧度
	@param	yaw		: float，0 - 2*pi，单位是弧度，表示偏转多少弧度，正值逆时针，负值顺时针
	"""
	return UTILS_CPP_OPTIMIZE.randomPosAround( center, radius, radian, yaw )

def disperse( entity, centerPos, radius, maxMove ):
	"""
	在某个中心点周围指定范围内散开。maxMove的作用是限制每次移动的
	最大距离，最初始的期望是用于防止怪物移动时穿过目标，移动到目标
	背后，而实际测试表明，maxMove限制得太小时，总是很难找到符合全
	部条件的点，于是即使最后获取的点不符合maxMove条件，只要符合
	canNavigateTo条件依然将此点作为目标点。

	2013/8/14修改：由于使用maxMove限制最大移动距离，防止entity穿越
	目标的方式效果太差，因此优化了该方式，改为：获取随机点时，避免
	获取到目标后面指定弧度范围内的点，这样就不会发生散开时穿过目标
	走到其后面去的情况。见randomPosAround

	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.disperse( entity, centerPos, radius, maxMove )

# 从AI中移到外面
def checkAndMove( entity ):
	"""进行检测，如果有重叠就主动散开
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.checkAndMove( entity )

def checkAndMoveByDis( entity, maxMove ):
	"""进行检测，如果有重叠就主动散开，但是散开的目标位置在maxMove距离之内
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.checkAndMoveByDis( entity, maxMove )

def moveOut( srcEntity, dstEntity, distance, moveMax ):
	"""散开
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.moveOut( srcEntity, dstEntity, distance, moveMax )

def followCheckAndMove( srcEntity, dstEntity ):
	"""跟随怪在跟随目标周围散开
	禁止直接编辑该方法，请到下层模块中修改。
	"""
	return UTILS_CPP_OPTIMIZE.followCheckAndMove( srcEntity, dstEntity )
