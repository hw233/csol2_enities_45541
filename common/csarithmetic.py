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
	格式化为英文数值表示法
	@type			n : int
	@param			n : 整数值
	@rtype			  : str
	@return			  : 用逗号分隔的英文数值表示法
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
	转化为十六进制数
	@type			hCount : int
	@param			hCount : 显示的位数（位数不够则以前面加 0 表示）
	@rtype				   : str
	@return				   : 返回十六进制数
	"""
	exec_str = "%%#.%dx" % hCount
	h_value = exec_str % value
	return h_value.upper()

def sum( elems, key = lambda x : x ) :
	"""
	计算 elems 中元素的某个成员总和
	@type			elems : list
	@param			elems : 元素集合
	@key			key	  : functor
	@param			key	  : 返回元素成员的回调
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
	用折半查找法，将一个元素添加到顺序链表中，使得添加后的链表仍然有序。当链表中元素很多时，效率很高
	对于是否是顺序的判断，本来可以合并起来写的。但是如果合并起来写，则每个循环都要作判断，因此分开来写（代码量多了点）
	@type				elms	  : list
	@param				elms	  : 链表
	@type				elm		  : all types
	@param				elm		  : 要添加的元素
	@type				key		  : functor
	@param				key		  : 可以通过该 key 来指定排序的关键字
	@type				ascending : bool
	@param				ascending : 如果是 true 则该链表是升序的，否则是降序的
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
	随机获得 elements 中的一个元素，或者根据 rndOdds 中的相应比率来获得一个元素
	@type			elements : list
	@param			elements : 一组元素
	@type			rndOdds	 : list
	@param			rndOdds	 : 与 elements 中每个元素相应的随机值, 元素的值必须是大于 0 的整数（一般情况下总和应该等于 100，表示每个元素为百分值）
	@rtype					 : all types
	@return					 : element 中的一个元素
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
# 点
# -----------------------------------------------------
def distancePP2( pos1, pos2 ) :
	"""
	计算两点间的距离
	@type			pos1 : Vector2 or tuple of float
	@param			pos1 : 起始点
	@type			pos2 : Vector2 or tuple of float
	@param			pos2 : 结束点
	@rtype				 : float
	@return				 : 两点间的距离
	"""
	pow0 = math.pow( pos1[0] - pos2[0], 2 )
	pow1 = math.pow( pos1[1] - pos2[1], 2 )
	return math.pow( pow0 + pow1, 0.5 )

def getPointToVector2( pos, bevel, distance ) :
	"""
	知道向量上的某点，求在该向量上距离该点一定距离的另一点坐标（二维）。
	@type			pos		 : tuple or Vector2
	@param			pos		 : 参考坐标点
	@type			bevel	 : float
	@param			bevel	 : 向量斜角
	@type			distance : float
	@param			distance : 求点到参考坐标点的距离
	@rtype					 : Vector2
	@return					 : 求点
	"""
	rx, ry = pos
	x = rx + distance * math.sin( bevel )
	y = ry + distance * math.cos( bevel )
	return Math.Vector2( x, y )

def inSameLine( points ) :
	"""
	判断多个点是否在同一条直线上
	@type				points : list
	@param				points : [( x, y ), ( x, y ), ……]
	@rtype					   : bool
	@return					   : 如果在同一条直线上则返回 True
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
# 直线
# -----------------------------------------------------
def isIntersectant( line1, line2 ) :
	"""
	判断两条直线是否相交
	@type			line1 : tuple
	@param			line1 : 直线 1 ( 点1, 点2 )
	@type			line2 : tuple
	@param			line2 : 直线 2 ( 点1, 点2 )
	"""
	( x1, y1 ), ( x2, y2 ) = line1
	( xx1, yy1 ), ( xx2, yy2 ) = line2
	a = ( x2 - x1 ) * ( yy2 - yy1 )
	b = ( y2 - y1 ) * ( xx2 - xx1 )
	return a != b

def getIntersectantPoint( ( pos11, pos12 ), ( pos21, pos22 ) ) :
	"""
	求两直线的交点（二维）
	@type			pos11 : Vector2
	@param			pos11 : 直线 1 上的点1
	@type			pos12 : Vector2
	@param			pos12 : 直线 1 上的点2
	@type			pos21 : Vector2
	@param			pos21 : 直线 2 上的点1
	@type			pos22 : Vector2
	@param			pos22 : 直线 2 上的点2
	@rtype				  : Vector2
	@return				  : 如果两直线不平行则返回两直线相交的点，否则返回 None
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
		return None											# 平行

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
	获取一个二维向量的偏角，范围：[0－2π）
	@type			v2 : Vector2
	@param			v2 : 二维向量
	@rtype			   : float
	@return			   : 偏角的弧度值( 假设：往 Y 轴正方向指时为 0，往 X 轴正方向摆动时角度增加 )
	"""
	x, y = v2
	if x == 0 :								# 向量落在 Y 轴上
		if y >= 0 : return 0.0				# 向量方向于 Y 轴正方向相同
		else : return math.pi				# 向量方向于 Y 轴正方向相反
	elif y == 0 :							# 向量落在 X 轴上
		if x >= 0 : return math.pi / 2		# 向量方向于 X 轴正方向相同
		else : return 3 * math.pi / 2		# 向量方向于 X 轴正方向相反
	yaw = math.atan( x / y )
	if x > 0 :
		if y > 0 : return yaw				# 在第一象限
		return math.pi + yaw				# 在第二象限
	else :
		if y < 0 : return math.pi + yaw		# 在第三象限
		return 2 * math.pi + yaw			# 在第四象限


# --------------------------------------------------------------------
# about 3D
# --------------------------------------------------------------------
def distancePP3( pos1, pos2 ) :
	"""
	计算两点间的距离（三维）
	@type			pos1 : tuple or Vector3
	@param			pos1 : 起始点的坐标
	@type			pos2 : tuple or Vector3
	@param			pos2 : 结束点的坐标
	@rtype				 : float
	@param				 : pos1 与 pos2 之间的距离
	"""
	dx = pow( pos1[0] - pos2[0], 2 )
	dy = pow( pos1[1] - pos2[1], 2 )
	dz = pow( pos1[2] - pos2[2], 2 )
	return pow( dx + dy + dz, 0.5 )

def getSeparatePoint3( pos1, pos2, dst ) :
	"""
	计算两点间的定比分点坐标（三维）。
	知道两点(pos1,pos2)，求这两点所形成的直线上距离pos1一定距离(dst)的点。
	如果dst为正，则点的值以pos1为基础从pos1往pos2的方向前进，
	如果dst为负，则点的值从pos1为基础从pos2往pos1的方向前进。
	@type			pos1 : Vector3
	@param			pos1 : 起始点的坐标
	@type			pos2 : Vector3
	@param			pos2 : 结束点的坐标
	@type			dst  : float
	@param			dst  : 要计算的定比分点到 pos2 的距离
	@rtype				 : Vector3
	@return				 : 定比分点坐标
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
	获取一个三维向量的 yaw 值 [0－2π）
	@type			v3 : Vector3
	@param			v3 : 三维向量
	@rtype			   : float
	@return			   : 弧度值( 假设：向量往外（Z 轴正方向）指时为 0，向右（X 轴正方向）摆动时角度增加 )
	"""
	x, y, z = v3
	if x == 0 and z == 0 : return 0.0					# 在 X 轴和 Z 轴上都没有分量
	if x == 0 :
		if z > 0 : return 0.0							# 平行于 Z 轴，并与 Z 轴正方向一至
		return math.pi									# 平行于 Z 轴，并与 Z 轴正方向相反
	if z == 0 :
		if x > 0 : return math.pi / 2					# 平行于 X 轴，并与 X 轴正方向一至
		return 3 * math.pi / 2							# 平行于 X 轴，并与 X 轴正方向相反
	if x > 0 : return v3.yaw							# 在第一第二象限
	return 2 * math.pi + v3.yaw							# 在第三第四象限

def getPitchOfV3( v3 ) :
	"""
	获取一个三维向量的 pitch 值 [0－2π）
	@type			v3 : Vector3
	@param			v3 : 三维向量
	@rtype			   : float
	@return			   : 弧度值( 假设：向量往上（Y 轴正方向）指时为 0，向前（Z 轴正方向）摆动时角度增加 )
	"""
	x, y, z = v3
	if y == 0 and z == 0 : return 0.0					# 在 Y 和 Z 轴上都没有分量
	if z == 0 :
		if y > 0 : return 0.0							# 平行于 Y 轴并与 Y 轴正方向一至
		return math.pi									# 平行于 Y 轴并与 Y 轴正方向相反
	if y == 0 :
		if z > 0 : return math.pi / 2					# 平行于 Z 轴并与 Z 轴正方向一至
		return 3 * math.pi / 2							# 平行于 Z 轴并与 Z 轴正方向相反
	if z > 0 :
		if y > 0 : return math.atan( z / y )			# 在第一象限
		return math.pi + math.atan( z / y )				# 在第二象限
	else :
		if y < 0 : return math.pi + math.atan( z / y )	# 在第三象限
		return math.pi * 2 + math.atan( z / y )			# 在第四象限

def getRollOfV3( v3 ) :
	"""
	获取一个三维向量的 roll 值 [0－2π）
	@type			v3 : Vector3
	@param			v3 : 三维向量
	@rtype			   : float
	@return			   : 弧度值（假设：向量向右（Z 轴正方向）时为 0，逆时针摆动（向 Y 轴正方向摆动）时角度增加）
	"""
	x, y, z = v3
	if x == 0 and y == 0 : return 0.0					# 在 X 和 Y 轴上都没有分量
	if y == 0 :
		if x > 0 : return 0.0							# 与 Y 轴平行，并且方向与 Y 轴正方向一至
		return math.pi									# 与 Y 轴平行，并且方向与 Y 轴正方向相反
	if x == 0 :
		if y > 0 : return math.pi / 2					# 与 X 轴平行，并且方向与 X 轴正方向一至
		return 3 * math.pi / 2							# 与 X 轴平行，并且方向与 X 轴正方向相反
	if y > 0 :
		if x > 0 : return math.atan( y / x )			# 在第一象限
		return math.pi + math.atan( y / x )				# 在第二象限
	else :
		if x < 0 : return math.pi + math.atan( y / x )	# 在第三象限
		return 2 * math.pi + math.atan( y / x )			# 在第四象限

def getCollidePoint( spaceID, srcPos, dstPos ):
	"""
	virtual method.
	给定目标点，返回碰撞后的最终目标点
	@param dstPos			: 运动目标点
	@type dstPos			: Vector3
	"""
	# 前后碰撞，需提高0.5米
	srcPos = Math.Vector3( srcPos )
	srcCollidePos = srcPos + ( 0, 0.5, 0 )
	dstCollidePos = dstPos + ( 0, 0.5, 0 )

	collideYaw = BigWorld.collide( spaceID, srcCollidePos, dstCollidePos )
	# 平行地面碰撞，碰到之后还需拉前0.5米以保证不会陷进碰撞体内部
	if collideYaw != None:
		position = collideYaw[0]
		direction = Math.Vector3( srcPos - ( position.x, position.y - 0.5, position.z ) )
		direction.normalise()
		dstPos = position + direction * 0.5

	# 垂直地面碰撞
	collide = BigWorld.collide( spaceID, ( dstPos.x, dstPos.y + 1.0, dstPos.z ), ( dstPos.x, dstPos.y - 1.0, dstPos.z ) )
	if collide != None: dstPos.y = collide[0].y
	return dstPos

def checkSkillCollide( spaceID, srcPos, dstPos ):
	"""
	检查技能是否能到达
	前后碰撞，需提高0.5米
	"""
	srcCollidePos = srcPos + ( 0, 0.5, 0 )
	dstCollidePos = dstPos + ( 0, 0.5, 0 )
	return BigWorld.collide( spaceID, srcCollidePos, dstCollidePos )
