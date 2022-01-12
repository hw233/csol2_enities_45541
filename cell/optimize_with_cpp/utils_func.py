# -*- coding: gb18030 -*-

import Math
import BigWorld
import math
import copy
import random
import csdefine
from bwdebug import *

MIN_ATTACK_RADIUS = 1.2			# 定义最小攻击半径
DEFAULT_MAX_MOVE = 4			# 默认散开最大移动距离
FOLLOWING_RADIUS = 4			# 跟随半径


#**
# xz平面上中心点距离，两个entity中心点之间的距离
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def ent_flatDistance( src, dst ):
	"""xz平面上中心点距离，两个entity中心点之间的距离"""
	return src.position.flatDistTo( dst.position )


#**
# z轴方向的距离，两个entity面对面方向的距离，不包含boundingBox
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def ent_z_distance( src, dst ):
	"""z轴方向的距离，两个entity面对面方向的距离，不包含boundingBox"""
	return ent_flatDistance(src, dst) - ent_z_distance_min(src, dst)


#**
# z轴方向，两个entity面对面紧贴着站的距离
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def ent_z_distance_min( src, dst ):
	"""z轴方向，两个entity面对面紧贴着站的距离"""
	return (ent_length(src) + ent_length(dst))/2


#**
# x轴方向的距离，两个entity平排站的距离，不包含boundingBox
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def ent_x_distance( src, dst ):
	"""x轴方向的距离，两个entity平排站的距离，不包含boundingBox"""
	return ent_flatDistance(src, dst) - ent_x_distance_min(src, dst)


#**
# x轴方向，两个entity平排紧贴着站的距离
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def ent_x_distance_min( src, dst ):
	"""x轴方向，两个entity平排紧贴着站的距离"""
	return (ent_width(src) + ent_width(dst))/2


#**
# entity的长度
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def ent_length( entity ):
	"""entity的长度"""
	return entity.getBoundingBox().z


#**
# entity的宽度
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def ent_width( entity ):
	"""entity的宽度"""
	return entity.getBoundingBox().x


#**
# entity的高度
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def ent_height( entity ):
	"""entity的高度"""
	return entity.getBoundingBox().y


#**
# 检测是否能重新定位自己的位置
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def checkForLocation( entity ):
	"""检测是否能重新定位自己的位置"""
	# 是否存在散开标记
	if entity.hasFlag( csdefine.ENTITY_FLAG_NOT_CHECK_AND_MOVE ):
		return False
	# 是否被禁止移动
	if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
		DEBUG_MSG( "Entity(id:%i) cannot  move!" % entity.id )
		return False
	# 检测状态，这个标记最开始的作用是记录是否已经进行过散开检测，
	# 但是如果限制只进行一次检测，则散开效果并不理想，随着不断地修改，
	# 标记的作用已经变得不明确，现在暂时用这个标记进行检测频率的调整
	counter = entity.queryTemp( "disperse_counter", 0 )
	entity.setTemp( "disperse_counter", counter + 1 )
	#DEBUG_MSG( "Entity(id:%i) locate status %i" % ( entity.id, status ) )
	# 沿用旧规则，为零不进行重定位；每4次最多进行一次分散检测
	return counter > 0 and counter % 4 == 0


#**
# 定位entity的位置
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def locate( entity, maxMove ):
	"""定位entity的位置"""
	# 是否正在移动中，可能是因为散开时，entity速度较小，所以移动得比较慢
	if entity.isMoving():
		return True
	# 是否能进行散开
	if not checkForLocation(entity):
		return False
	# 目标检查
	target = BigWorld.entities.get( entity.targetID )
	if target is None:
		return False
	# 如果z轴方向上entity和目标的boudingBox有重叠，则需要移动位置
	# 期望的实际结果是，如果怪物和玩家的模型出现重叠，则移动位置，然而
	# 实际测试的结果并非如此，即计算的结果表明，boudingBox已经是不重叠的，但
	# 是客户端看到模型依然是重叠的
	needDisperse = ent_z_distance(entity, target) < 0
	# 如果entity横向方向周围有其他entity，则需要移动位置
	if not needDisperse:
		for e in entity.entitiesInRangeExt(ent_width(entity)/2.0 + 5):
			if (not e.isEntityType( csdefine.ENTITY_TYPE_SPAWN_POINT )) and ent_x_distance(entity, e) < 0:
				needDisperse = True
				break
	#DEBUG_MSG( "Entity(id:%i) locate, %s disperse, maxMove %f!" % (entity.id, "need" if needDisperse else "not need", maxMove) )
	# todo: 好好考虑究竟移动的半径应该如何获取
	# 如果需要移动位置，则以目标中心点为圆心，以与目标的纵向距离为半径，进行移动
	# 移动半径的选择需要注意：
	#	1、需要考虑到怪物如果离玩家太远，会出现打空的情况，即动作不是打在玩家身上，而是打空气
	#	2、距离不能太远，否则怪物的技能会无法施展，目前以普通攻击的距离为基准
	#	3、要考虑当前施展的技能的施法距离，这个值应该在这里可以获得，并加入到计算里面，但当前没有
	# 目前以一个固定的值（MIN_ATTACK_RADIUS）作为移动半径，同时考虑因boudingBox太大导致玩家站在怪物
	# 模型内部的情况，所以加上这种情况下的距离判定：max(MIN_ATTACK_RADIUS, ent_z_distance_min(entity, target))
	if needDisperse:
		radius = max(MIN_ATTACK_RADIUS, ent_z_distance_min(entity, target), ent_flatDistance(entity, target))
		return disperse( entity, target.position, radius, maxMove )
	else:
		return False


#**
# 在xz平面的center点为圆心，半径是radius的圆上，随机取弧度范围是radian，
# 朝向是yaw的点
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def randomPosAround( center, radius, radian, yaw ):
	"""在xz平面的center点为圆心，半径是radius的圆上，随机取弧度范围是radian，
	朝向是yaw的点
	@param	center	: POSITION，圆心位置
	@param	radius	: float，半径
	@param	radian	: float，0 - 2*pi，单位是弧度，表示取多少圆弧度
	@param	yaw		: float，0 - 2*pi，单位是弧度，表示偏转多少弧度，正值逆时针，负值顺时针
	"""
	minRadian = 2*math.pi - radian*0.5 + yaw
	#maxRadian = 2*math.pi + radian*0.5 * yaw
	#randomRadian = minRadian + (maxRadian - minRadian) * random.random()	# 这条公式简化为下面这条公式
	randomRadian = minRadian + radian * random.random()
	pos = Math.Vector3(center)
	pos.x = center.x + radius * math.cos(randomRadian)
	pos.z = center.z + radius * math.sin(randomRadian)
	return pos


#**
# 在某个中心点周围指定范围内散开
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
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
	"""
	pos = None
	# 引擎yaw的坐标系和世界坐标不一致，它在地图向上的方向上是零，
	# 顺时针转动时变大，逆时针转动时变小，下面的计算把yaw的坐标
	# 系保持和世界坐标一致，在地图向右的方向上是零，逆时针转动时变大。
	yaw = -(centerPos - entity.position).yaw - math.pi/2
	# 根据最大移动距离和散开半径求出散开的弧度范围，避免远程怪物（散开半径比较大）散开时走得比较远
	dispersingRadian = math.asin(min(maxMove, 2*radius)/radius*0.5)*4
	# 以上计算用余弦定理得到下列公式
	#dispersingRadian = math.acos(1 - min(maxMove, 2*radius)**2/radius**2*0.5)
	tryCount = 5
	while tryCount > 0:
		tryCount -= 1
		# 在指定半径的圆上取随机点，为防止穿越目标，取点范围作了限制
		pos = randomPosAround(centerPos, radius, dispersingRadian, yaw)
		# y方向上下偏移10米进行碰撞检测
		hit_point = BigWorld.collide( entity.spaceID, ( pos.x, pos.y+10, pos.z ), ( pos.x, pos.y-10, pos.z ) )
		if hit_point is None:
			continue
		pos = entity.canNavigateTo( hit_point[0], 0.5 )
		if pos:
			break
	# 如果尝试失败了，则不需要移动
	if pos is None:
		DEBUG_MSG( "GSM: cannot find any pos for dispersing!" )
		return False
	# 移动到随机检测得出的位置
	entity.gotoPosition( pos )
	return True


#**
# 散开
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def checkAndMove( entity ):
	# c++调用切换
	if BigWorld.globalData["optimizeWithCPP"]:
		return BigWorld.checkAndMove_csol(entity)

	# 最大移动距离取boudingBox宽度一半加上默认最大移动距离
	return locate( entity, ent_width(entity)/2 + DEFAULT_MAX_MOVE )


#**
# 散开，并接受传入最大移动距离
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def checkAndMoveByDis( entity, maxMove ):
	# c++调用切换
	if BigWorld.globalData["optimizeWithCPP"]:
		return BigWorld.checkAndMoveByDis_csol(entity, maxMove)

	return locate( entity, maxMove )


#**
# 散开
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def moveOut( srcEntity, dstEntity, distance, moveMax ):
	# c++调用切换
	if BigWorld.globalData["optimizeWithCPP"]:
		return BigWorld.moveOut_csol(srcEntity, dstEntity, distance, moveMax)

	# 如果当前正在移动中，则不执行散开
	if srcEntity.isMoving():
		return True

	radius = distance + ent_z_distance_min(srcEntity, dstEntity)	# 散开半径需要加上boudingBox的距离
	return disperse( srcEntity, dstEntity.position, radius, ent_width(srcEntity)/2 + moveMax )


#**
# 跟随怪在跟随目标周围散开
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def followCheckAndMove( srcEntity, dstEntity ):
	"""跟随怪在跟随目标周围散开"""
	if srcEntity.isMoving() or dstEntity.isMoving():
		return False

	# 如果跟随目标的位置未发生改变，则不进行随机走动
	if srcEntity.queryTemp( "previousOwnerPosition" ) == dstEntity.position:
		return False

	# 如果跟随目标的位置发生改变，则进行随机走动并记录下目标当前位置
	radius = FOLLOWING_RADIUS * random.random()
	if moveOut(srcEntity, dstEntity, radius, ent_z_distance(srcEntity, dstEntity)):
		srcEntity.setTemp( "previousOwnerPosition", copy.deepcopy(dstEntity.position) )
		return True
	else:
		return False
