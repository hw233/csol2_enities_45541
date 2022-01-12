# -*- coding: gb18030 -*-

import Math
import BigWorld
import math
import copy
import random
import csdefine
from bwdebug import *

MIN_ATTACK_RADIUS = 1.2			# ������С�����뾶
DEFAULT_MAX_MOVE = 4			# Ĭ��ɢ������ƶ�����
FOLLOWING_RADIUS = 4			# ����뾶


#**
# xzƽ�������ĵ���룬����entity���ĵ�֮��ľ���
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def ent_flatDistance( src, dst ):
	"""xzƽ�������ĵ���룬����entity���ĵ�֮��ľ���"""
	return src.position.flatDistTo( dst.position )


#**
# z�᷽��ľ��룬����entity����淽��ľ��룬������boundingBox
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def ent_z_distance( src, dst ):
	"""z�᷽��ľ��룬����entity����淽��ľ��룬������boundingBox"""
	return ent_flatDistance(src, dst) - ent_z_distance_min(src, dst)


#**
# z�᷽������entity����������վ�ľ���
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def ent_z_distance_min( src, dst ):
	"""z�᷽������entity����������վ�ľ���"""
	return (ent_length(src) + ent_length(dst))/2


#**
# x�᷽��ľ��룬����entityƽ��վ�ľ��룬������boundingBox
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def ent_x_distance( src, dst ):
	"""x�᷽��ľ��룬����entityƽ��վ�ľ��룬������boundingBox"""
	return ent_flatDistance(src, dst) - ent_x_distance_min(src, dst)


#**
# x�᷽������entityƽ�Ž�����վ�ľ���
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def ent_x_distance_min( src, dst ):
	"""x�᷽������entityƽ�Ž�����վ�ľ���"""
	return (ent_width(src) + ent_width(dst))/2


#**
# entity�ĳ���
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def ent_length( entity ):
	"""entity�ĳ���"""
	return entity.getBoundingBox().z


#**
# entity�Ŀ��
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def ent_width( entity ):
	"""entity�Ŀ��"""
	return entity.getBoundingBox().x


#**
# entity�ĸ߶�
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def ent_height( entity ):
	"""entity�ĸ߶�"""
	return entity.getBoundingBox().y


#**
# ����Ƿ������¶�λ�Լ���λ��
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def checkForLocation( entity ):
	"""����Ƿ������¶�λ�Լ���λ��"""
	# �Ƿ����ɢ�����
	if entity.hasFlag( csdefine.ENTITY_FLAG_NOT_CHECK_AND_MOVE ):
		return False
	# �Ƿ񱻽�ֹ�ƶ�
	if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
		DEBUG_MSG( "Entity(id:%i) cannot  move!" % entity.id )
		return False
	# ���״̬���������ʼ�������Ǽ�¼�Ƿ��Ѿ����й�ɢ����⣬
	# �����������ֻ����һ�μ�⣬��ɢ��Ч���������룬���Ų��ϵ��޸ģ�
	# ��ǵ������Ѿ���ò���ȷ��������ʱ�������ǽ��м��Ƶ�ʵĵ���
	counter = entity.queryTemp( "disperse_counter", 0 )
	entity.setTemp( "disperse_counter", counter + 1 )
	#DEBUG_MSG( "Entity(id:%i) locate status %i" % ( entity.id, status ) )
	# ���þɹ���Ϊ�㲻�����ض�λ��ÿ4��������һ�η�ɢ���
	return counter > 0 and counter % 4 == 0


#**
# ��λentity��λ��
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def locate( entity, maxMove ):
	"""��λentity��λ��"""
	# �Ƿ������ƶ��У���������Ϊɢ��ʱ��entity�ٶȽ�С�������ƶ��ñȽ���
	if entity.isMoving():
		return True
	# �Ƿ��ܽ���ɢ��
	if not checkForLocation(entity):
		return False
	# Ŀ����
	target = BigWorld.entities.get( entity.targetID )
	if target is None:
		return False
	# ���z�᷽����entity��Ŀ���boudingBox���ص�������Ҫ�ƶ�λ��
	# ������ʵ�ʽ���ǣ�����������ҵ�ģ�ͳ����ص������ƶ�λ�ã�Ȼ��
	# ʵ�ʲ��ԵĽ��������ˣ�������Ľ��������boudingBox�Ѿ��ǲ��ص��ģ���
	# �ǿͻ��˿���ģ����Ȼ���ص���
	needDisperse = ent_z_distance(entity, target) < 0
	# ���entity��������Χ������entity������Ҫ�ƶ�λ��
	if not needDisperse:
		for e in entity.entitiesInRangeExt(ent_width(entity)/2.0 + 5):
			if (not e.isEntityType( csdefine.ENTITY_TYPE_SPAWN_POINT )) and ent_x_distance(entity, e) < 0:
				needDisperse = True
				break
	#DEBUG_MSG( "Entity(id:%i) locate, %s disperse, maxMove %f!" % (entity.id, "need" if needDisperse else "not need", maxMove) )
	# todo: �úÿ��Ǿ����ƶ��İ뾶Ӧ����λ�ȡ
	# �����Ҫ�ƶ�λ�ã�����Ŀ�����ĵ�ΪԲ�ģ�����Ŀ����������Ϊ�뾶�������ƶ�
	# �ƶ��뾶��ѡ����Ҫע�⣺
	#	1����Ҫ���ǵ�������������̫Զ������ִ�յ���������������Ǵ���������ϣ����Ǵ����
	#	2�����벻��̫Զ���������ļ��ܻ��޷�ʩչ��Ŀǰ����ͨ�����ľ���Ϊ��׼
	#	3��Ҫ���ǵ�ǰʩչ�ļ��ܵ�ʩ�����룬���ֵӦ����������Ի�ã������뵽�������棬����ǰû��
	# Ŀǰ��һ���̶���ֵ��MIN_ATTACK_RADIUS����Ϊ�ƶ��뾶��ͬʱ������boudingBox̫�������վ�ڹ���
	# ģ���ڲ�����������Լ�����������µľ����ж���max(MIN_ATTACK_RADIUS, ent_z_distance_min(entity, target))
	if needDisperse:
		radius = max(MIN_ATTACK_RADIUS, ent_z_distance_min(entity, target), ent_flatDistance(entity, target))
		return disperse( entity, target.position, radius, maxMove )
	else:
		return False


#**
# ��xzƽ���center��ΪԲ�ģ��뾶��radius��Բ�ϣ����ȡ���ȷ�Χ��radian��
# ������yaw�ĵ�
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def randomPosAround( center, radius, radian, yaw ):
	"""��xzƽ���center��ΪԲ�ģ��뾶��radius��Բ�ϣ����ȡ���ȷ�Χ��radian��
	������yaw�ĵ�
	@param	center	: POSITION��Բ��λ��
	@param	radius	: float���뾶
	@param	radian	: float��0 - 2*pi����λ�ǻ��ȣ���ʾȡ����Բ����
	@param	yaw		: float��0 - 2*pi����λ�ǻ��ȣ���ʾƫת���ٻ��ȣ���ֵ��ʱ�룬��ֵ˳ʱ��
	"""
	minRadian = 2*math.pi - radian*0.5 + yaw
	#maxRadian = 2*math.pi + radian*0.5 * yaw
	#randomRadian = minRadian + (maxRadian - minRadian) * random.random()	# ������ʽ��Ϊ����������ʽ
	randomRadian = minRadian + radian * random.random()
	pos = Math.Vector3(center)
	pos.x = center.x + radius * math.cos(randomRadian)
	pos.z = center.z + radius * math.sin(randomRadian)
	return pos


#**
# ��ĳ�����ĵ���Χָ����Χ��ɢ��
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def disperse( entity, centerPos, radius, maxMove ):
	"""
	��ĳ�����ĵ���Χָ����Χ��ɢ����maxMove������������ÿ���ƶ���
	�����룬���ʼ�����������ڷ�ֹ�����ƶ�ʱ����Ŀ�꣬�ƶ���Ŀ��
	���󣬶�ʵ�ʲ��Ա�����maxMove���Ƶ�̫Сʱ�����Ǻ����ҵ�����ȫ
	�������ĵ㣬���Ǽ�ʹ����ȡ�ĵ㲻����maxMove������ֻҪ����
	canNavigateTo������Ȼ���˵���ΪĿ��㡣

	2013/8/14�޸ģ�����ʹ��maxMove��������ƶ����룬��ֹentity��Խ
	Ŀ��ķ�ʽЧ��̫�����Ż��˸÷�ʽ����Ϊ����ȡ�����ʱ������
	��ȡ��Ŀ�����ָ�����ȷ�Χ�ڵĵ㣬�����Ͳ��ᷢ��ɢ��ʱ����Ŀ��
	�ߵ������ȥ���������randomPosAround
	"""
	pos = None
	# ����yaw������ϵ���������겻һ�£����ڵ�ͼ���ϵķ��������㣬
	# ˳ʱ��ת��ʱ�����ʱ��ת��ʱ��С������ļ����yaw������
	# ϵ���ֺ���������һ�£��ڵ�ͼ���ҵķ��������㣬��ʱ��ת��ʱ���
	yaw = -(centerPos - entity.position).yaw - math.pi/2
	# ��������ƶ������ɢ���뾶���ɢ���Ļ��ȷ�Χ������Զ�̹��ɢ���뾶�Ƚϴ�ɢ��ʱ�ߵñȽ�Զ
	dispersingRadian = math.asin(min(maxMove, 2*radius)/radius*0.5)*4
	# ���ϼ��������Ҷ���õ����й�ʽ
	#dispersingRadian = math.acos(1 - min(maxMove, 2*radius)**2/radius**2*0.5)
	tryCount = 5
	while tryCount > 0:
		tryCount -= 1
		# ��ָ���뾶��Բ��ȡ����㣬Ϊ��ֹ��ԽĿ�꣬ȡ�㷶Χ��������
		pos = randomPosAround(centerPos, radius, dispersingRadian, yaw)
		# y��������ƫ��10�׽�����ײ���
		hit_point = BigWorld.collide( entity.spaceID, ( pos.x, pos.y+10, pos.z ), ( pos.x, pos.y-10, pos.z ) )
		if hit_point is None:
			continue
		pos = entity.canNavigateTo( hit_point[0], 0.5 )
		if pos:
			break
	# �������ʧ���ˣ�����Ҫ�ƶ�
	if pos is None:
		DEBUG_MSG( "GSM: cannot find any pos for dispersing!" )
		return False
	# �ƶ���������ó���λ��
	entity.gotoPosition( pos )
	return True


#**
# ɢ��
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def checkAndMove( entity ):
	# c++�����л�
	if BigWorld.globalData["optimizeWithCPP"]:
		return BigWorld.checkAndMove_csol(entity)

	# ����ƶ�����ȡboudingBox���һ�����Ĭ������ƶ�����
	return locate( entity, ent_width(entity)/2 + DEFAULT_MAX_MOVE )


#**
# ɢ���������ܴ�������ƶ�����
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def checkAndMoveByDis( entity, maxMove ):
	# c++�����л�
	if BigWorld.globalData["optimizeWithCPP"]:
		return BigWorld.checkAndMoveByDis_csol(entity, maxMove)

	return locate( entity, maxMove )


#**
# ɢ��
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def moveOut( srcEntity, dstEntity, distance, moveMax ):
	# c++�����л�
	if BigWorld.globalData["optimizeWithCPP"]:
		return BigWorld.moveOut_csol(srcEntity, dstEntity, distance, moveMax)

	# �����ǰ�����ƶ��У���ִ��ɢ��
	if srcEntity.isMoving():
		return True

	radius = distance + ent_z_distance_min(srcEntity, dstEntity)	# ɢ���뾶��Ҫ����boudingBox�ľ���
	return disperse( srcEntity, dstEntity.position, radius, ent_width(srcEntity)/2 + moveMax )


#**
# ������ڸ���Ŀ����Χɢ��
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def followCheckAndMove( srcEntity, dstEntity ):
	"""������ڸ���Ŀ����Χɢ��"""
	if srcEntity.isMoving() or dstEntity.isMoving():
		return False

	# �������Ŀ���λ��δ�����ı䣬�򲻽�������߶�
	if srcEntity.queryTemp( "previousOwnerPosition" ) == dstEntity.position:
		return False

	# �������Ŀ���λ�÷����ı䣬���������߶�����¼��Ŀ�굱ǰλ��
	radius = FOLLOWING_RADIUS * random.random()
	if moveOut(srcEntity, dstEntity, radius, ent_z_distance(srcEntity, dstEntity)):
		srcEntity.setTemp( "previousOwnerPosition", copy.deepcopy(dstEntity.position) )
		return True
	else:
		return False
