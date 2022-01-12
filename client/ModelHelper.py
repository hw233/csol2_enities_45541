# -*- coding: gb18030 -*-
import Math
import BigWorld
import csdefine
from bwdebug import *

"""
模型相关的一些助手函数 by mushuang
"""




"""
def getModelBoundingBox( model ):
	#获取模型外接盒的八个顶点（四个顶点为一组，顺时针）
	assert isinstance( model, BigWorld.Model ), "model must be a PyModel instance!"
	
	# 单位立方体在xy平面的投影( 右手系中，顺时针 )
	xy = ( ( 0, 0, 0 ), ( 1, 0, 0 ), ( 1, 1, 0 ), ( 0, 1, 0 )  )
	
	# 单位立方体所有顶点
	vertex = list( xy )
	vertex.extend( [ ( v[0], v[1], v[2] + 1 )  for v in vertex ] )
	
	matrix = Math.Matrix( model.bounds )
	
	return [ matrix.applyPoint( p ) for p in vertex ]
"""
	

def equal( f1, f2, delta = 0.01 ):
	"""
	以精度delta判断f1，f2是否相等
	"""
	assert delta >= 0, "delta must be positive!"
	
	return abs( f1 - f2 ) <= delta

"""
def collideBoundingBox( model, spaceID, collideCntMax = 6 ):
	#@collideBoundingBox: 测试模型外接盒是否在与其他东西发生碰撞
	#@model: PyModel 实例
	#@spaceID: 模型所在的空间
	assert isinstance( model, BigWorld.Model ), "model must be a PyModel instance!"
	
	# 外接的的八个顶点
	v = getModelBoundingBox( model )
	
	DEBUG_MSG( "Vertex: %s"%str(v) )
	
	# 构造碰撞射线（BBOX的四个侧面参与碰撞，上下两个面不参与碰撞）
	diagonals = [ 
				( 0, 2 ), ( 1, 3 ), ( 4, 6 ), ( 5, 7 ), 
				( 3, 4 ), ( 0, 7 ), ( 2, 5 ), ( 1, 6 ),
				( 3, 6 ), ( 2, 7 ),						# 对角线
				( 0, 1 ), ( 1, 2 ), ( 2, 3 ), ( 3, 0 ),
				( 4, 5 ), ( 5, 6 ), ( 6, 7 ), ( 7, 4 ),
				( 3, 7 ), ( 0, 4 ), ( 2, 6 ), ( 1, 5 ),	# 边
				]
	
	collideCnt = 0
	
	for line in diagonals:
		state = BigWorld.collide( spaceID, v[ line[0] ], v[ line[1] ] )
		if state:
			DEBUG_MSG( "Collide line: %s, %s"%( line[0], line[1] ) )
			DEBUG_MSG( "%s\n"%str(state) )
			collideCnt += 1
			
	DEBUG_MSG( "Collide cnt: %s"%collideCnt )
	
	return collideCnt > collideCntMax
"""
# 三个或三个以上方向上都发生碰撞的所有状态
NARROW_SPACE_STATE = ( 7, 11, 13, 14, 15, 19, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31 )

def isLeftCollided( state ):
	"""
	@isLeftCollided: 根据state判断是否在左方向（世界空间 x轴正方向）上发生了碰撞。
	"""
	return bool( state & 4 )

def isRightCollided( state ):
	"""
	@isRightCollided: 根据state判断是否在右方向（世界空间 x轴负方向）上发生了碰撞。
	"""
	return bool( state & 8 )

def isForwardCollided( state ):
	"""
	@isForwardCollide: 根据state判断是否在前方向（世界空间 z轴正方向）上发生了碰撞。
	"""
	return bool( state & 1 )
	
def isBackwardCollided( state ):
	"""
	@isBackwardCollide: 根据state判断是否在后方向（世界空间 z轴负方向）上发生了碰撞。
	"""
	return bool( state & 2 )

def isUpwardCollided( state ):
	"""
	@isUpwardCollided: 根据state判断是否在上方向（世界空间 y轴正方向）上发生了碰撞。
	"""
	return bool( state & 16 )


def isInNarrowSpace( player, extent = ( 0.4 + 1, 2.5 + 1, 0.3 + 1 ) ):
	"""
	@isInNarrowSpace: 判断玩家是否处于狭窄空间
	@extent: 玩家在extent范围（x,y,z 分别表示左右、上、前后移动量的绝对值 ）内向“前后左右上”五个方向移动
	设计：
		玩家在左右上前后五个方向上移动并检测碰撞状态，并且根据这些碰撞状态来检测是否有处于相对狭小的空间。
		目前的设计是，如果玩家在任意三个（或三个以上）方向上都发生了碰撞，那么则判定为空间狭小。
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"
	
	if player != BigWorld.player():
		return False
	physics = player.physics
	
	if not hasattr( physics, "collideAround" ):
		ERROR_MSG( "Deprecated client found, please update to latest version!" )
		return False
	
	state = physics.collideAround( extent )
	DEBUG_MSG( "state = %s"%state )
	return state in NARROW_SPACE_STATE
