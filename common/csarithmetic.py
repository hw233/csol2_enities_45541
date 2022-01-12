# -*- coding: gb18030 -*-
#
# $Id: csarithmetic.py,v 1.15 2008-08-27 09:08:43 huangyongwei Exp $

"""
This module implements common arithmetic
2007/07/17: writen by huangyongwei
"""

import math
import Math
import random
from bwdebug import *
import BigWorld

import BigWorld


# --------------------------------------------------------------------
# value convertor
# --------------------------------------------------------------------
def toUSValue( n ) :
	"""
	��ʽ��ΪӢ����ֵ��ʾ��
	@type			n : int
	@param			n : ����ֵ
	@rtype			  : str
	@return			  : �ö��ŷָ���Ӣ����ֵ��ʾ��
	"""
	absn = abs( n )
	if absn < 1000 : return str( n )
	strn = ""
	while( absn > 0 ) :
		resn = absn % 1000
		absn = absn / 1000
		strn = ( ",%03d" % resn ) + strn
		if absn < 1000 :
			strn = str( absn ) + strn
			break
	if n < 0 : strn = "-" + strn
	return strn

def toHexValue( value, hCount ) :
	"""
	ת��Ϊʮ��������
	@type			hCount : int
	@param			hCount : ��ʾ��λ����λ����������ǰ��� 0 ��ʾ��
	@rtype				   : str
	@return				   : ����ʮ��������
	"""
	exec_str = "%%#.%dx" % hCount
	h_value = exec_str % value
	return h_value.upper()

def sum( elems, key = lambda x : x ) :
	"""
	���� elems ��Ԫ�ص�ĳ����Ա�ܺ�
	@type			elems : list
	@param			elems : Ԫ�ؼ���
	@key			key	  : functor
	@param			key	  : ����Ԫ�س�Ա�Ļص�
	"""
	total = 0
	for elem in elems :
		total += key( elem )
	return total

# --------------------------------------------------------------------
# common methods about math
# --------------------------------------------------------------------
def half_orderInsert( elms, elm, key = lambda v : v, ascending = True ) :
	"""
	���۰���ҷ�����һ��Ԫ����ӵ�˳�������У�ʹ����Ӻ��������Ȼ���򡣵�������Ԫ�غܶ�ʱ��Ч�ʺܸ�
	�����Ƿ���˳����жϣ��������Ժϲ�����д�ġ���������ϲ�����д����ÿ��ѭ����Ҫ���жϣ���˷ֿ���д�����������˵㣩
	@type				elms	  : list
	@param				elms	  : ����
	@type				elm		  : all types
	@param				elm		  : Ҫ��ӵ�Ԫ��
	@type				key		  : functor
	@param				key		  : ����ͨ���� key ��ָ������Ĺؼ���
	@type				ascending : bool
	@param				ascending : ����� true �������������ģ������ǽ����
	"""
	count = len( elms )
	start = 0
	end = count
	mid = count / 2
	if ascending :
		while start < end :
			if key( elm ) <= key( elms[mid] ) :
				if mid == 0 or key( elm ) >= key( elms[mid - 1] ) :
					break
				else :
					end = mid
			else :
				if mid == count - 1 or key( elm ) <= key( elms[mid + 1] ) :
					mid += 1
					break
				else :
					start = mid
			mid = ( start + end ) / 2
	else :
		while start < end :
			if key( elm ) >= key( elms[mid] ) :
				if mid == 0 or key( elm ) <= key( elms[mid - 1] ) :
					break
				else :
					end = mid
			else :
				if mid == count - 1 or key( elm ) >= key( elms[mid + 1] ) :
					mid += 1
					break
				else :
					start = mid
			mid = ( start + end ) / 2
	elms.insert( mid, elm )


# -----------------------------------------------------
def getRandomElement( elements, rndOdds = None ) :
	"""
	������ elements �е�һ��Ԫ�أ����߸��� rndOdds �е���Ӧ���������һ��Ԫ��
	@type			elements : list
	@param			elements : һ��Ԫ��
	@type			rndOdds	 : list
	@param			rndOdds	 : �� elements ��ÿ��Ԫ����Ӧ�����ֵ, Ԫ�ص�ֵ�����Ǵ��� 0 ��������һ��������ܺ�Ӧ�õ��� 100����ʾÿ��Ԫ��Ϊ�ٷ�ֵ��
	@rtype					 : all types
	@return					 : element �е�һ��Ԫ��
	"""
	if rndOdds is None :
		return random.choice( elements )
	if len( elements ) != len( rndOdds ) :
		raise "random values and elements are not match!"
	total = sum( rndOdds )
	rndValue = random.randrange( 0, total )
	segment = 0
	for index, value in enumerate( rndOdds ) :
		segment += value
		if rndValue < segment :
			return elements[index]
	return None


# --------------------------------------------------------------------
# about 2D
# --------------------------------------------------------------------
# -----------------------------------------------------
# ��
# -----------------------------------------------------
def distancePP2( pos1, pos2 ) :
	"""
	���������ľ���
	@type			pos1 : Vector2 or tuple of float
	@param			pos1 : ��ʼ��
	@type			pos2 : Vector2 or tuple of float
	@param			pos2 : ������
	@rtype				 : float
	@return				 : �����ľ���
	"""
	pow0 = math.pow( pos1[0] - pos2[0], 2 )
	pow1 = math.pow( pos1[1] - pos2[1], 2 )
	return math.pow( pow0 + pow1, 0.5 )

def getPointToVector2( pos, bevel, distance ) :
	"""
	֪�������ϵ�ĳ�㣬���ڸ������Ͼ���õ�һ���������һ�����꣨��ά����
	@type			pos		 : tuple or Vector2
	@param			pos		 : �ο������
	@type			bevel	 : float
	@param			bevel	 : ����б��
	@type			distance : float
	@param			distance : ��㵽�ο������ľ���
	@rtype					 : Vector2
	@return					 : ���
	"""
	rx, ry = pos
	x = rx + distance * math.sin( bevel )
	y = ry + distance * math.cos( bevel )
	return Math.Vector2( x, y )

def inSameLine( points ) :
	"""
	�ж϶�����Ƿ���ͬһ��ֱ����
	@type				points : list
	@param				points : [( x, y ), ( x, y ), ����]
	@rtype					   : bool
	@return					   : �����ͬһ��ֱ�����򷵻� True
	"""
	if len( points ) < 3 : return True
	pos0 = points[0]
	pos1 = points[1]
	for index in xrange( 2, len( points ) ) :
		pos = points[index]
		a = ( pos1[1] - pos0[1] ) * ( pos[0] - pos0[0] )
		b = ( pos1[0] - pos0[0] ) * ( pos[1] - pos0[1] )
		if a != b : return False
	return True

# -----------------------------------------------------
# ֱ��
# -----------------------------------------------------
def isIntersectant( line1, line2 ) :
	"""
	�ж�����ֱ���Ƿ��ཻ
	@type			line1 : tuple
	@param			line1 : ֱ�� 1 ( ��1, ��2 )
	@type			line2 : tuple
	@param			line2 : ֱ�� 2 ( ��1, ��2 )
	"""
	( x1, y1 ), ( x2, y2 ) = line1
	( xx1, yy1 ), ( xx2, yy2 ) = line2
	a = ( x2 - x1 ) * ( yy2 - yy1 )
	b = ( y2 - y1 ) * ( xx2 - xx1 )
	return a != b

def getIntersectantPoint( ( pos11, pos12 ), ( pos21, pos22 ) ) :
	"""
	����ֱ�ߵĽ��㣨��ά��
	@type			pos11 : Vector2
	@param			pos11 : ֱ�� 1 �ϵĵ�1
	@type			pos12 : Vector2
	@param			pos12 : ֱ�� 1 �ϵĵ�2
	@type			pos21 : Vector2
	@param			pos21 : ֱ�� 2 �ϵĵ�1
	@type			pos22 : Vector2
	@param			pos22 : ֱ�� 2 �ϵĵ�2
	@rtype				  : Vector2
	@return				  : �����ֱ�߲�ƽ���򷵻���ֱ���ཻ�ĵ㣬���򷵻� None
	"""
	pos11 = Math.Vector2( pos11 )
	pos12 = Math.Vector2( pos12 )
	pos21 = Math.Vector2( pos21 )
	pos22 = Math.Vector2( pos22 )
	plainP1 = ( pos12 - pos11 )
	plainP2 = ( pos22 - pos21 )
	tanAngle1 = plainP1.y / plainP1.x
	tanAngle2 = plainP2.y / plainP2.x
	if abs( tanAngle1 - tanAngle2 ) < math.tan( 0.1 ) :
		return None											# ƽ��

	x11, y11 = pos11
	x12, y12 = pos12
	x21, y21 = pos21
	x22, y22 = pos22
	y = ( ( x12 * y11 - x11 * y11 ) * ( y22 - y21 ) - \
		x11 * y22 + y21 * x11 - \
		( x22 * y21 - x21 * y21 ) * ( y12 - y11 ) + ( x21 * y12 - x21 * y11 ) ) / \
		( ( x12 - x11 ) * ( y22 - y21 ) - ( x22 - x21 ) * ( y12 - y11 ) )
	x = ( y - y11 ) * ( x12 - x11 ) / ( y12 - y11 )  + x11
	return Math.Vector( x, y )

# -----------------------------------------------------
def getYawOfV2( v2 ) :
	"""
	��ȡһ����ά������ƫ�ǣ���Χ��[0��2�У�
	@type			v2 : Vector2
	@param			v2 : ��ά����
	@rtype			   : float
	@return			   : ƫ�ǵĻ���ֵ( ���裺�� Y ��������ָʱΪ 0���� X ��������ڶ�ʱ�Ƕ����� )
	"""
	x, y = v2
	if x == 0 :								# �������� Y ����
		if y >= 0 : return 0.0				# ���������� Y ����������ͬ
		else : return math.pi				# ���������� Y ���������෴
	elif y == 0 :							# �������� X ����
		if x >= 0 : return math.pi / 2		# ���������� X ����������ͬ
		else : return 3 * math.pi / 2		# ���������� X ���������෴
	yaw = math.atan( x / y )
	if x > 0 :
		if y > 0 : return yaw				# �ڵ�һ����
		return math.pi + yaw				# �ڵڶ�����
	else :
		if y < 0 : return math.pi + yaw		# �ڵ�������
		return 2 * math.pi + yaw			# �ڵ�������


# --------------------------------------------------------------------
# about 3D
# --------------------------------------------------------------------
def distancePP3( pos1, pos2 ) :
	"""
	���������ľ��루��ά��
	@type			pos1 : tuple or Vector3
	@param			pos1 : ��ʼ�������
	@type			pos2 : tuple or Vector3
	@param			pos2 : �����������
	@rtype				 : float
	@param				 : pos1 �� pos2 ֮��ľ���
	"""
	dx = pow( pos1[0] - pos2[0], 2 )
	dy = pow( pos1[1] - pos2[1], 2 )
	dz = pow( pos1[2] - pos2[2], 2 )
	return pow( dx + dy + dz, 0.5 )

def getSeparatePoint3( pos1, pos2, dst ) :
	"""
	���������Ķ��ȷֵ����꣨��ά����
	֪������(pos1,pos2)�������������γɵ�ֱ���Ͼ���pos1һ������(dst)�ĵ㡣
	���dstΪ��������ֵ��pos1Ϊ������pos1��pos2�ķ���ǰ����
	���dstΪ��������ֵ��pos1Ϊ������pos2��pos1�ķ���ǰ����
	@type			pos1 : Vector3
	@param			pos1 : ��ʼ�������
	@type			pos2 : Vector3
	@param			pos2 : �����������
	@type			dst  : float
	@param			dst  : Ҫ����Ķ��ȷֵ㵽 pos2 �ľ���
	@rtype				 : Vector3
	@return				 : ���ȷֵ�����
	"""
	dist = pos1.distTo( pos2 )
	if dist == 0 : return pos1
	scale = dst / dist
	x = pos1.x + ( pos2.x - pos1.x ) * scale
	y = pos1.y + ( pos2.y - pos1.y ) * scale
	z = pos1.z + ( pos2.z - pos1.z ) * scale
	return Math.Vector3( x, y, z )

# -----------------------------------------------------
def getYawOfV3( v3 ) :
	"""
	��ȡһ����ά������ yaw ֵ [0��2�У�
	@type			v3 : Vector3
	@param			v3 : ��ά����
	@rtype			   : float
	@return			   : ����ֵ( ���裺�������⣨Z ��������ָʱΪ 0�����ң�X �������򣩰ڶ�ʱ�Ƕ����� )
	"""
	x, y, z = v3
	if x == 0 and z == 0 : return 0.0					# �� X ��� Z ���϶�û�з���
	if x == 0 :
		if z > 0 : return 0.0							# ƽ���� Z �ᣬ���� Z ��������һ��
		return math.pi									# ƽ���� Z �ᣬ���� Z ���������෴
	if z == 0 :
		if x > 0 : return math.pi / 2					# ƽ���� X �ᣬ���� X ��������һ��
		return 3 * math.pi / 2							# ƽ���� X �ᣬ���� X ���������෴
	if x > 0 : return v3.yaw							# �ڵ�һ�ڶ�����
	return 2 * math.pi + v3.yaw							# �ڵ�����������

def getPitchOfV3( v3 ) :
	"""
	��ȡһ����ά������ pitch ֵ [0��2�У�
	@type			v3 : Vector3
	@param			v3 : ��ά����
	@rtype			   : float
	@return			   : ����ֵ( ���裺�������ϣ�Y ��������ָʱΪ 0����ǰ��Z �������򣩰ڶ�ʱ�Ƕ����� )
	"""
	x, y, z = v3
	if y == 0 and z == 0 : return 0.0					# �� Y �� Z ���϶�û�з���
	if z == 0 :
		if y > 0 : return 0.0							# ƽ���� Y �Ტ�� Y ��������һ��
		return math.pi									# ƽ���� Y �Ტ�� Y ���������෴
	if y == 0 :
		if z > 0 : return math.pi / 2					# ƽ���� Z �Ტ�� Z ��������һ��
		return 3 * math.pi / 2							# ƽ���� Z �Ტ�� Z ���������෴
	if z > 0 :
		if y > 0 : return math.atan( z / y )			# �ڵ�һ����
		return math.pi + math.atan( z / y )				# �ڵڶ�����
	else :
		if y < 0 : return math.pi + math.atan( z / y )	# �ڵ�������
		return math.pi * 2 + math.atan( z / y )			# �ڵ�������

def getRollOfV3( v3 ) :
	"""
	��ȡһ����ά������ roll ֵ [0��2�У�
	@type			v3 : Vector3
	@param			v3 : ��ά����
	@rtype			   : float
	@return			   : ����ֵ�����裺�������ң�Z ��������ʱΪ 0����ʱ��ڶ����� Y ��������ڶ���ʱ�Ƕ����ӣ�
	"""
	x, y, z = v3
	if x == 0 and y == 0 : return 0.0					# �� X �� Y ���϶�û�з���
	if y == 0 :
		if x > 0 : return 0.0							# �� Y ��ƽ�У����ҷ����� Y ��������һ��
		return math.pi									# �� Y ��ƽ�У����ҷ����� Y ���������෴
	if x == 0 :
		if y > 0 : return math.pi / 2					# �� X ��ƽ�У����ҷ����� X ��������һ��
		return 3 * math.pi / 2							# �� X ��ƽ�У����ҷ����� X ���������෴
	if y > 0 :
		if x > 0 : return math.atan( y / x )			# �ڵ�һ����
		return math.pi + math.atan( y / x )				# �ڵڶ�����
	else :
		if x < 0 : return math.pi + math.atan( y / x )	# �ڵ�������
		return 2 * math.pi + math.atan( y / x )			# �ڵ�������

def getCollidePoint( spaceID, srcPos, dstPos ):
	"""
	virtual method.
	����Ŀ��㣬������ײ�������Ŀ���
	@param dstPos			: �˶�Ŀ���
	@type dstPos			: Vector3
	"""
	# ǰ����ײ�������0.5��
	srcPos = Math.Vector3( srcPos )
	srcCollidePos = srcPos + ( 0, 0.5, 0 )
	dstCollidePos = dstPos + ( 0, 0.5, 0 )

	collideYaw = BigWorld.collide( spaceID, srcCollidePos, dstCollidePos )
	# ƽ�е�����ײ������֮������ǰ0.5���Ա�֤�����ݽ���ײ���ڲ�
	if collideYaw != None:
		position = collideYaw[0]
		direction = Math.Vector3( srcPos - ( position.x, position.y - 0.5, position.z ) )
		direction.normalise()
		dstPos = position + direction * 0.5

	# ��ֱ������ײ
	collide = BigWorld.collide( spaceID, ( dstPos.x, dstPos.y + 1.0, dstPos.z ), ( dstPos.x, dstPos.y - 1.0, dstPos.z ) )
	if collide != None: dstPos.y = collide[0].y
	return dstPos

def checkSkillCollide( spaceID, srcPos, dstPos ):
	"""
	��鼼���Ƿ��ܵ���
	ǰ����ײ�������0.5��
	"""
	srcCollidePos = srcPos + ( 0, 0.5, 0 )
	dstCollidePos = dstPos + ( 0, 0.5, 0 )
	return BigWorld.collide( spaceID, srcCollidePos, dstCollidePos )
