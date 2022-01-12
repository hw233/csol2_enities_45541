# -*- coding:gb18030 -*-
#
import math


def cannonballUid(fisherID, number):
	"""����cannonball��uid"""
	return "%s:%s" % (fisherID, number)


def parseCannonballUid(uid):
	"""�ֽ�cannonball��uid"""
	fiserID, number = uid.split(":")
	return int(fiserID), int(number)


def flatToPos(model, dest):
	"""ʹģ�͵�ͷ����y����ָ��dest"""
	model.roll = 0.0
	model.pitch = 0.0
	org_yaw = model.yaw
	d = dest - model.position
	pitch = d.pitch + math.pi/2.0
	# ���´���ʽ�������ܹ���
	# ����ʵ�ʲ��Եı����Ͽ���
	# ����10�θ�ֵ�����б�Ҫ��
	for i in xrange(10):
		model.yaw = d.yaw
		model.pitch = pitch
	model.yaw = org_yaw


def rotateBetween(src, dst, yaw):
	"""
	������3D������������һ��entityվ��srcλ�ã�
	��ʱ����pitch��roll����0������Ҫ�ڱ���yawֵ
	����������ָ��dstλ�ã�Ҫʵ����������ת��
	���ַ�����������yaw���㣩
	1����src������x��ת��dst��Ȼ��������z��ת��dst
	2����src������z��ת��dst��Ȼ��������x��ת��dst
	������õ�һ�ַ���������3D���������srcת��dst
	��pitch��rollֵ
	"""
	dx = dst[0] - src[0]
	dy = dst[1] - src[1]
	dz = dst[2] - src[2]
	dzy = math.sqrt(dz*dz + dy*dy)

	if dx == 0 and dy == 0 and dz == 0:
		return 0, 0

	if dy == 0:
		if dz > 0:
			pitch = -math.pi / 2.0
		else:
			pitch = math.pi / 2.0
	else:
		pitch = math.atan(dz / dy)

	if dzy == 0:
		if dx > 0:
			roll = -math.pi / 2.0
		else:
			roll = math.pi / 2.0
	else:
		roll = math.atan(dx / dzy)

	return pitch, roll


def vVector3(source, xzPoint):
	""""""
	a, b, c = source
	x, z = xzPoint
	y = -(a*x + c*z)/b
	return (x, y, z)
