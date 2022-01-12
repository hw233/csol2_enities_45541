# -*- coding: gb18030 -*-
#
# $Id: utils.py,v 1.40 2008-03-29 09:01:15 phw Exp $

"""
�ṩһЩ��ClientҪʹ�õĹ��ܺ����͹����ࡣ
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
	��������֮����XZƽ���yawֵ������posfrom��posto�۲��yawֵ��
	@param			posfrom : �۲��
	@type			posfrom : tuple3����Vector3
	@param			posto	: Ŀ���
	@type			posto	: tuple3����Vector3
	@return					: posfrom��posto��yaw����ֵ
	@rtype					: float
	"""
	offX = posto[0] - posfrom[0]
	offZ = posto[2] - posfrom[2]
	return math.atan2( offX, offZ )

def world2RScreen( pos, z = 1.0 ):
	"""
	�������굽GUI�����ת����
	@param			pos : ��������
	@type			pos : tuple3 ���� Vector3
	@param			z	: ���ص�Zֵ
	@type			z	: float
	@return				: GUI ����(�������)
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
	�������굽GUI�����ת����
	@param			pos : ��������
	@type			pos : tuple3 ���� Vector3
	@param			z	: ���ص�Zֵ
	@type			z	: float
	@return				: GUI ����(�������)
	@rtype				: Math.Vector3
	"""
	rx, ry, z = world2RScreen( pos, z )
	sw, sh = BigWorld.screenSize()
	left = ( rx + 1 ) * sw * 0.5
	top = ( 1 - ry ) * sh * 0.5
	return Math.Vector3( left, top, z )

def ptIsUnderGround( spaceID, pos ):
	"""
	�ж�ָ�������Ƿ��ڵ��¡�
	@param			spaceID : ����ID
	@type			spaceID : int32
	@param			pos		: λ��
	@type			pos		: tuple3����Vector3
	@return					: �Ƿ��ڵ���
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
	ȡ����Y�����ϵĵر����ꡣ
	@param			spaceID : ����ID
	@type			spaceID : int32
	@param			pos		: λ��
	@type			pos		: tuple3����Vector3
	@return					: �ر�����
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
	"""�����ҵ�pos�ڵر��ͶӰ����"""
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
	"""�������entity֮���Ƿ���ֱ�ӿ����Է���
	�м�û���ϰ����"""
	if entityA.spaceID != entityB.spaceID:
		return False
	else:
		# ȡA�����ĸ߶�λ��
		apos = Math.Vector3(entityA.position)
		apos.y += entityA.getBoundingBox().y/2.0
		# ȡB�����ĸ߶�λ��
		bpos = Math.Vector3(entityB.position)
		bpos.y += entityB.getBoundingBox().y/2.0
		# �������������ײ��⣬���Ƿ������
		return BigWorld.collide(entityA.spaceID, apos, bpos) == None

def getModelSize( pyModel ):
	"""
	��ȡģ�͵ĳ����
	"""
	if pyModel is None:
		return Math.Vector3( 0.0, 0.0, 0.0 )

	x, y, z = getOriginalModelSize( pyModel )
	return Math.Vector3( x * pyModel.scale.x, y * pyModel.scale.y, z * pyModel.scale.z )

def getOriginalModelSize( pyModel ):
	"""
	��ȡģ�͵�ԭʼ�����
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
		ȡ��bounding box��ƽ��뾶

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
	�����ͻ���ֵת��Ϊ��ͼ������ֱ�ʾ���ַ���
	@param		value 	: ����ֵ
	@type		value 	: INT
	@param		iconic	: �Ƿ���ͼ��������
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

