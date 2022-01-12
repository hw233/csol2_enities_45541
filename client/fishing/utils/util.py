# -*- coding:gb18030 -*-
#
import math


def cannonballUid(fisherID, number):
	"""生成cannonball的uid"""
	return "%s:%s" % (fisherID, number)


def parseCannonballUid(uid):
	"""分解cannonball的uid"""
	fiserID, number = uid.split(":")
	return int(fiserID), int(number)


def flatToPos(model, dest):
	"""使模型的头顶（y方向）指向dest"""
	model.roll = 0.0
	model.pitch = 0.0
	org_yaw = model.yaw
	d = dest - model.position
	pitch = d.pitch + math.pi/2.0
	# 以下处理方式看起来很怪异
	# 但从实际测试的表现上看，
	# 加上10次赋值还是有必要的
	for i in xrange(10):
		model.yaw = d.yaw
		model.pitch = pitch
	model.yaw = org_yaw


def rotateBetween(src, dst, yaw):
	"""
	假设在3D世界坐标中有一个entity站在src位置，
	此时它的pitch和roll都是0，它需要在保持yaw值
	不变的情况下指向dst位置，要实现这样的旋转有
	两种方案：（假设yaw是零）
	1、从src先绕着x轴转向dst，然后再绕着z轴转向dst
	2、从src先绕着z轴转向dst，然后再绕着x轴转向dst
	这里采用第一种方案计算在3D世界坐标从src转向dst
	的pitch和roll值
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
