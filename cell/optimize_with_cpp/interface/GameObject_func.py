# -*- coding: gb18030 -*-

import Math
import BigWorld
import csdefine
from bwdebug import *

#**
# ��ȡ��Entity.position��Ӧ�ĵ����
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def getDownToGroundPos( self ):
	"""
	��ȡ��Entity.position��Ӧ�ĵ���� by mushuang
	"""

	# ��BigWorld������bug(��ĳ��ʱ�̣�position�ĸ���������ǳ���)���ݴ���
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
# ������Ŀ��entity��boundingbox�߽�֮���3D����ϵ�ľ���
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def distanceBB( self, destEntity ):
	"""
	������Ŀ��entity��boundingbox�߽�֮���3D����ϵ�ľ���

	@return: float
	"""
	if BigWorld.globalData["optimizeWithCPP"]:
		#c++ �滻
		return self.distanceBB_cpp( destEntity )


	# ��ǰֱ����bounding box�Ŀ��һ����Ϊbounding box�����ĵ��߽�ľ���
	s1 = self.getBoundingBox().z / 2
	d1 = destEntity.getBoundingBox().z / 2
		
	selfPos = self.position
	dstPos = destEntity.position

	# if ���ж��Ƿ���ĳ״̬��
	if hasattr( self, "isState" ) and hasattr( destEntity, "isState" ):
		# if ����һ�����ڷ���״̬ then ���������������
		if self.hasFlag( csdefine.ROLE_FLAG_FLY ) or destEntity.hasFlag( csdefine.ROLE_FLAG_FLY ):
			return selfPos.distTo( dstPos ) - s1 - d1

	# ��λ��ͶӰ�����沢�������
	selfPos =self.getGroundPosition()
	dstPos = destEntity.getGroundPosition()

	if not selfPos:
		selfPos = self.position
	if not dstPos:
		dstPos = destEntity.position

	return selfPos.distTo( dstPos ) - s1 - d1


#**
# ���ݹؼ��ֲ�ѯ��ʱmapping����֮��Ӧ��ֵ
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def queryTemp( self, key, default = None ):
		"""
		���ݹؼ��ֲ�ѯ��ʱmapping����֮��Ӧ��ֵ

		@return: ����ؼ��ֲ������򷵻�defaultֵ
		"""
		if BigWorld.globalData.has_key("optimizeWithCPP") and BigWorld.globalData["optimizeWithCPP"]:
			#c++ �滻
			return self.queryTemp_cpp( key, default )

		try:
			return self.tempMapping[key]
		except KeyError:
			return default


#**
# ���ݹؼ��ֲ�ѯ��ʱmapping����֮��Ӧ��ֵ
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def setTemp( self, key, value ):
	"""
	define method.
	��һ��key��дһ��ֵ

	@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
	@param value: �κ�PYTHONԭ����(����ʹ�����ֻ��ַ���)
	"""
	self.tempMapping[key] = value


#**
# �ж�һ��entity�Ƿ���ָ���ı�־
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def hasFlag( self, flag ):
	"""
	�ж�һ��entity�Ƿ���ָ���ı�־

	@param flag: ENTITY_FLAG_*
	@type  flag: INT
	@return: BOOL
	"""
	flag = 1 << flag
	return ( self.flags & flag ) == flag
