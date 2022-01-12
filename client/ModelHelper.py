# -*- coding: gb18030 -*-
import Math
import BigWorld
import csdefine
from bwdebug import *

"""
ģ����ص�һЩ���ֺ��� by mushuang
"""




"""
def getModelBoundingBox( model ):
	#��ȡģ����Ӻеİ˸����㣨�ĸ�����Ϊһ�飬˳ʱ�룩
	assert isinstance( model, BigWorld.Model ), "model must be a PyModel instance!"
	
	# ��λ��������xyƽ���ͶӰ( ����ϵ�У�˳ʱ�� )
	xy = ( ( 0, 0, 0 ), ( 1, 0, 0 ), ( 1, 1, 0 ), ( 0, 1, 0 )  )
	
	# ��λ���������ж���
	vertex = list( xy )
	vertex.extend( [ ( v[0], v[1], v[2] + 1 )  for v in vertex ] )
	
	matrix = Math.Matrix( model.bounds )
	
	return [ matrix.applyPoint( p ) for p in vertex ]
"""
	

def equal( f1, f2, delta = 0.01 ):
	"""
	�Ծ���delta�ж�f1��f2�Ƿ����
	"""
	assert delta >= 0, "delta must be positive!"
	
	return abs( f1 - f2 ) <= delta

"""
def collideBoundingBox( model, spaceID, collideCntMax = 6 ):
	#@collideBoundingBox: ����ģ����Ӻ��Ƿ�������������������ײ
	#@model: PyModel ʵ��
	#@spaceID: ģ�����ڵĿռ�
	assert isinstance( model, BigWorld.Model ), "model must be a PyModel instance!"
	
	# ��ӵĵİ˸�����
	v = getModelBoundingBox( model )
	
	DEBUG_MSG( "Vertex: %s"%str(v) )
	
	# ������ײ���ߣ�BBOX���ĸ����������ײ�����������治������ײ��
	diagonals = [ 
				( 0, 2 ), ( 1, 3 ), ( 4, 6 ), ( 5, 7 ), 
				( 3, 4 ), ( 0, 7 ), ( 2, 5 ), ( 1, 6 ),
				( 3, 6 ), ( 2, 7 ),						# �Խ���
				( 0, 1 ), ( 1, 2 ), ( 2, 3 ), ( 3, 0 ),
				( 4, 5 ), ( 5, 6 ), ( 6, 7 ), ( 7, 4 ),
				( 3, 7 ), ( 0, 4 ), ( 2, 6 ), ( 1, 5 ),	# ��
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
# �������������Ϸ����϶�������ײ������״̬
NARROW_SPACE_STATE = ( 7, 11, 13, 14, 15, 19, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31 )

def isLeftCollided( state ):
	"""
	@isLeftCollided: ����state�ж��Ƿ�����������ռ� x���������Ϸ�������ײ��
	"""
	return bool( state & 4 )

def isRightCollided( state ):
	"""
	@isRightCollided: ����state�ж��Ƿ����ҷ�������ռ� x�Ḻ�����Ϸ�������ײ��
	"""
	return bool( state & 8 )

def isForwardCollided( state ):
	"""
	@isForwardCollide: ����state�ж��Ƿ���ǰ��������ռ� z���������Ϸ�������ײ��
	"""
	return bool( state & 1 )
	
def isBackwardCollided( state ):
	"""
	@isBackwardCollide: ����state�ж��Ƿ��ں�������ռ� z�Ḻ�����Ϸ�������ײ��
	"""
	return bool( state & 2 )

def isUpwardCollided( state ):
	"""
	@isUpwardCollided: ����state�ж��Ƿ����Ϸ�������ռ� y���������Ϸ�������ײ��
	"""
	return bool( state & 16 )


def isInNarrowSpace( player, extent = ( 0.4 + 1, 2.5 + 1, 0.3 + 1 ) ):
	"""
	@isInNarrowSpace: �ж�����Ƿ�����խ�ռ�
	@extent: �����extent��Χ��x,y,z �ֱ��ʾ���ҡ��ϡ�ǰ���ƶ����ľ���ֵ ������ǰ�������ϡ���������ƶ�
	��ƣ�
		�����������ǰ������������ƶ��������ײ״̬�����Ҹ�����Щ��ײ״̬������Ƿ��д��������С�Ŀռ䡣
		Ŀǰ������ǣ����������������������������ϣ������϶���������ײ����ô���ж�Ϊ�ռ���С��
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
