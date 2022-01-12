# -*- coding: gb18030 -*-

import Math
import BigWorld
import csdefine
from bwdebug import *

#**
# 获取此Entity.position对应的地面点
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def getDownToGroundPos( self ):
	"""
	获取此Entity.position对应的地面点 by mushuang
	"""

	# 对BigWorld著名的bug(在某个时刻，position的各个分量会非常大)做容错处理
	x, y, z = self.position.x, self.position.y, self.position.z
	xOK = -10000 < x and x < 10000
	yOK = -10000 < y and y < 10000
	zOK = -10000 < z and z < 10000
	if not ( xOK and yOK and zOK ):
		ERROR_MSG( "Unexpected huge coordinate, Entity: %s, position = %s"%( self.id, self.position ) )
		return None

	pos = self.position
	pos1 = self.position + ( 0, 0.1, 0 )
	pos2 = self.position + ( 0, -10, 0 )
	collideResult = BigWorld.collide( self.spaceID, pos1, pos2 )
	if not collideResult:
		return self.position

	return collideResult[0]


#**
# 计算与目标entity的boundingbox边界之间的3D坐标系的距离
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def distanceBB( self, destEntity ):
	"""
	计算与目标entity的boundingbox边界之间的3D坐标系的距离

	@return: float
	"""
	if BigWorld.globalData["optimizeWithCPP"]:
		#c++ 替换
		return self.distanceBB_cpp( destEntity )


	# 当前直接以bounding box的宽的一半作为bounding box的中心到边界的距离
	s1 = self.getBoundingBox().z / 2
	d1 = destEntity.getBoundingBox().z / 2
		
	selfPos = self.position
	dstPos = destEntity.position

	# if 可判定是否在某状态：
	if hasattr( self, "isState" ) and hasattr( destEntity, "isState" ):
		# if 任意一方处于飞行状态 then 返回两点坐标距离
		if self.hasFlag( csdefine.ROLE_FLAG_FLY ) or destEntity.hasFlag( csdefine.ROLE_FLAG_FLY ):
			return selfPos.distTo( dstPos ) - s1 - d1

	# 将位置投影到地面并计算距离
	selfPos =self.getGroundPosition()
	dstPos = destEntity.getGroundPosition()

	if not selfPos:
		selfPos = self.position
	if not dstPos:
		dstPos = destEntity.position

	return selfPos.distTo( dstPos ) - s1 - d1


#**
# 根据关键字查询临时mapping中与之对应的值
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def queryTemp( self, key, default = None ):
		"""
		根据关键字查询临时mapping中与之对应的值

		@return: 如果关键字不存在则返回default值
		"""
		if BigWorld.globalData.has_key("optimizeWithCPP") and BigWorld.globalData["optimizeWithCPP"]:
			#c++ 替换
			return self.queryTemp_cpp( key, default )

		try:
			return self.tempMapping[key]
		except KeyError:
			return default


#**
# 根据关键字查询临时mapping中与之对应的值
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def setTemp( self, key, value ):
	"""
	define method.
	往一个key里写一个值

	@param   key: 任何PYTHON原类型(建议使用字符串)
	@param value: 任何PYTHON原类型(建议使用数字或字符串)
	"""
	self.tempMapping[key] = value


#**
# 判断一个entity是否有指定的标志
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def hasFlag( self, flag ):
	"""
	判断一个entity是否有指定的标志

	@param flag: ENTITY_FLAG_*
	@type  flag: INT
	@return: BOOL
	"""
	flag = 1 << flag
	return ( self.flags & flag ) == flag
