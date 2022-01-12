# -*- coding:gb18030 -*-

import Math
import math
import BigWorld
import random
import csconst

def zero():
	"""
	��̨��Χ�ĵ㲻��ȡ�������յ㣬��˽�ȥһ����̨�뾶
	"""
	return ( 0, random.randint( csconst.FISH_FORT_RADIUS, csconst.FISHING_GROUND_WIDE / 2 ) )

def one():
	return ( random.randint( csconst.FISH_FORT_RADIUS, csconst.FISHING_GROUND_LENGTH / 2 ), 0 )

def two():
	return ( random.randint( csconst.FISHING_GROUND_LENGTH / 2, csconst.FISHING_GROUND_LENGTH - csconst.FISH_FORT_RADIUS ), 0 )

def three():
	return ( csconst.FISHING_GROUND_LENGTH, random.randint( csconst.FISH_FORT_RADIUS, csconst.FISHING_GROUND_WIDE / 2 ) )
	
def four():
	return ( csconst.FISHING_GROUND_LENGTH, random.randint( csconst.FISHING_GROUND_WIDE / 2, csconst.FISHING_GROUND_WIDE - csconst.FISH_FORT_RADIUS ) )

def five():
	return ( random.randint(  csconst.FISHING_GROUND_LENGTH / 2, csconst.FISHING_GROUND_LENGTH - csconst.FISH_FORT_RADIUS ), csconst.FISHING_GROUND_WIDE )
	
def six():
	return ( random.randint( csconst.FISH_FORT_RADIUS, csconst.FISHING_GROUND_LENGTH / 2 ), csconst.FISHING_GROUND_WIDE )
	
def seven():
	return ( 0, random.randint( csconst.FISHING_GROUND_WIDE / 2, csconst.FISHING_GROUND_WIDE - csconst.FISH_FORT_RADIUS ) )

MAP_DICT = { 0:(4,), 1:(5,), 2:(6,), 3:(7,), 4:(0,), 5:(1,), 6:(2,), 7:(3,) }		# ˢ�µ���յ������߶εĶ�Ӧ��ϵ
FUNC_MAP_DICT = { 0:zero, 1:one, 2:two, 3:three, 4:four, 5:five, 6:six, 7:seven }			# �߶������꣨ͨ��������ȡ���Ķ�Ӧ��ϵ


def createFishPath():
	"""
	@return [ spawnPoint, endPoint ]
	"""
	startLineKey = random.choice( MAP_DICT.keys() )
	endLineKey = random.choice( MAP_DICT[ startLineKey ] )
	spawnPoint = Math.Vector2 ( FUNC_MAP_DICT[ startLineKey ]() )
	endPoint = Math.Vector2 ( FUNC_MAP_DICT[ endLineKey ]() )
	return ( spawnPoint, endPoint )
