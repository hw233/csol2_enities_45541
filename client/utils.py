# -*- coding: gb18030 -*-
#
# $Id: utils.py,v 1.40 2008-03-29 09:01:15 phw Exp $

"""
提供一些在Client要使用的功能函数和功能类。
"""

import math
import BigWorld
import Math
import csconst
import Language
import ShareTexts
from bwdebug import *

def yawFromPos( posfrom, posto ):
	"""
	计算两点之间在XZ平面的yaw值，即从posfrom向posto观察的yaw值。
	@param			posfrom : 观察点
	@type			posfrom : tuple3或者Vector3
	@param			posto	: 目标点
	@type			posto	: tuple3或者Vector3
	@return					: posfrom到posto的yaw弧度值
	@rtype					: float
	"""
	offX = posto[0] - posfrom[0]
	offZ = posto[2] - posfrom[2]
	return math.atan2( offX, offZ )

def world2RScreen( pos, z = 1.0 ):
	"""
	世界坐标到GUI坐标的转换。
	@param			pos : 世界坐标
	@type			pos : tuple3 或者 Vector3
	@param			z	: 返回的Z值
	@type			z	: float
	@return				: GUI 坐标(相对坐标)
	@rtype				: Math.Vector3
	"""
	projac = BigWorld.projection()
	leny = math.tan( projac.fov * 0.5 )
	lenx = leny * BigWorld.screenWidth() / BigWorld.screenHeight()
	mc = Math.Matrix( BigWorld.camera().matrix )
	campos = mc.applyPoint( pos )
	spos = Math.Vector3()
	spos.x = campos.x / lenx / campos.z
	spos.y = campos.y / leny / campos.z
	spos.z = z
	return spos

def world2PScreen( pos, z = 1.0 ) :
	"""
	世界坐标到GUI坐标的转换。
	@param			pos : 世界坐标
	@type			pos : tuple3 或者 Vector3
	@param			z	: 返回的Z值
	@type			z	: float
	@return				: GUI 坐标(相对坐标)
	@rtype				: Math.Vector3
	"""
	rx, ry, z = world2RScreen( pos, z )
	sw, sh = BigWorld.screenSize()
	left = ( rx + 1 ) * sw * 0.5
	top = ( 1 - ry ) * sh * 0.5
	return Math.Vector3( left, top, z )

def ptIsUnderGround( spaceID, pos ):
	"""
	判断指定坐标是否在地下。
	@param			spaceID : 场景ID
	@type			spaceID : int32
	@param			pos		: 位置
	@type			pos		: tuple3或者Vector3
	@return					: 是否在地下
	@rtype					: bool
	"""
	ugpos = Math.Vector3( pos )
	ugpos.y -= 500.0
	try:
		cr = BigWorld.collide( spaceID, pos, ugpos )
		return ( cr is None )
	except ValueError, ve :
		WARNING_MSG( "ptIsUnderGround: ", ve )
	return False

def ptUpToGround( spaceID, pos ):
	"""
	取得沿Y轴向上的地表坐标。
	@param			spaceID : 场景ID
	@type			spaceID : int32
	@param			pos		: 位置
	@type			pos		: tuple3或者Vector3
	@return					: 地表坐标
	@rtype					: Math.Vector3
	"""
	if not ptIsUnderGround( spaceID, pos ):
		return pos
	uppos = Math.Vector3( pos )
	uppos.y += 500.0
	try:
		cr = BigWorld.collide( spaceID, pos, uppos )
		if cr is None:
			return pos
		else:
			cr[0].y += 0.3
			return cr[0]
	except ValueError, ve:
		WARNING_MSG( "ptUpToGround: ", ve )
	return pos

def posOnGround( spaceID, pos, default = None, addY = 3.0, decY = 100.0 ):
	"""尝试找到pos在地表的投影坐标"""
	pos1 = Math.Vector3(pos)
	pos1.y -= decY
	pos2 = Math.Vector3(pos)
	pos2.y += addY
	result = BigWorld.collide( spaceID, pos2, pos1 )
	if result is not None:
		return result[0]
	else:
		return default

def sightDirectly( entityA, entityB ):
	"""检测两个entity之间是否能直接看到对方，
	中间没有障碍阻隔"""
	if entityA.spaceID != entityB.spaceID:
		return False
	else:
		# 取A的中心高度位置
		apos = Math.Vector3(entityA.position)
		apos.y += entityA.getBoundingBox().y/2.0
		# 取B的中心高度位置
		bpos = Math.Vector3(entityB.position)
		bpos.y += entityB.getBoundingBox().y/2.0
		# 用两个点进行碰撞检测，看是否有阻隔
		return BigWorld.collide(entityA.spaceID, apos, bpos) == None

def getModelSize( pyModel ):
	"""
	获取模型的长宽高
	"""
	if pyModel is None:
		return Math.Vector3( 0.0, 0.0, 0.0 )

	x, y, z = getOriginalModelSize( pyModel )
	return Math.Vector3( x * pyModel.scale.x, y * pyModel.scale.y, z * pyModel.scale.z )

def getOriginalModelSize( pyModel ):
	"""
	获取模型的原始长宽高
	"""
	if pyModel is None:
		return Math.Vector3( 0.0, 0.0, 0.0 )
	m = Math.Matrix( pyModel.bounds )
	m2 = Math.Matrix( pyModel.matrix )
	try:
		x = m.get( 0, 0 )/m2.get( 0, 0 )
		y = m.get( 1, 1 )/m2.get( 1, 1 )
		z = m.get( 2, 2 )/m2.get( 2, 2 )
		return Math.Vector3( x, y, z )
	except ZeroDivisionError:
		return Math.Vector3( 0.0, 0.0, 0.0 )

# --------------------------------------------------------------------
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

	def getFlatRadius( self ):
		"""
		取得bounding box的平面半径

		@return: float
		"""
		x = ( self.minp.x + self.maxp.x ) / 2
		z = ( self.minp.z + self.maxp.z ) / 2
		radius = ( abs( x - self.minp.x ) + abs( z - self.minp.z ) ) / 2
		return radius

	def __str__( self ):
		return str(self.minp) + " " + str(self.maxp)

_defaultBB = BoundingBox()


# --------------------------------------------------------------------
# convert integer currency to string express
# --------------------------------------------------------------------
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
goldGUI		=PL_Image.getSource( "guis_v2/controls/goldicon.gui" )
silverGUI	=PL_Image.getSource( "guis_v2/controls/silvericon.gui" )
coinGUI		=PL_Image.getSource( "guis_v2/controls/coinicon.gui" )
def currencyToViewText( value, iconic = True ) :
	"""
	把整型货币值转换为用图标或文字表示的字符串
	@param		value 	: 货币值
	@type		value 	: INT
	@param		iconic	: 是否用图标来表现
	@type		iconic	: BOOL
	@return		STRING
	"""
	global goldGUI
	global silverGUI
	global coinGUI
	gold = value / 10000
	silver = value % 10000 / 100
	coin = value % 100
	valueStr = ""
	if value == 0:
		valueStr += "0" + \
		( iconic and coinGUI or ShareTexts.MONEY_COPPER )
	if gold :
		valueStr += str( gold ) + \
		( iconic and goldGUI or ShareTexts.MONEY_GOLD )
	if silver :
		valueStr += str( silver ) + \
		( iconic and silverGUI or ShareTexts.MONEY_SILVER )
	if coin :
		valueStr += str( coin ) + \
		( iconic and coinGUI or ShareTexts.MONEY_COPPER )


	return valueStr

