# -*- coding: gb18030 -*-
#
# $Id: TransporterData.py,v 1.1 2007-05-14 00:36:37 panguankong Exp $

"""
场景数据
"""

import BigWorld
import Language
from bwdebug import *

class TransporterData:
	def __init__( self ):
		"""
		构造函数。
		"""
		self.data = {}
		
	def getData( self ):
		"""
		取传送器数据
		"""
		if BigWorld.cellAppData.has_key("Transporters"):
			return BigWorld.cellAppData["Transporters"]
		return None
			
	def __getitem__( self, key ):
		"""
		取得Space数据部分
		"""
		objects = getData()
		if objects:
			return objects[key]
		return None

	def register( self, name, sign, pos, direction, spaceName ):
		"""
		注册传送器
		@param spaceName: 场景名称
		@type  spaceName: string
		@param name: 传送器名称
		@type  name: string
		@param sign: 传送器ID
		@type  sign: INT64
		@param pos: 传送器回传位置
		@type  pos: Vector3
		@param pos: 传送器回传方向
		@type  pos: Vector3
		"""
		objects = {}
		
		door = { "name":name, "pos":pos, "direction":direction }
		
		if BigWorld.cellAppData.has_key("Transporters"):
			objects = BigWorld.cellAppData["Transporters"]
			if objects.has_key( spaceName ):
				objects[spaceName][sign] = door
			else:
				objects[spaceName] = {sign:door}
		else:			
			objects[spaceName] = {sign:door}
		
		BigWorld.cellAppData["Transporters"] = objects


g_transporterData = TransporterData()

def getSpaceData( key ):
	"""
	获取场景数据。
		@param key:	场景名
		@type key:	string
	"""
	return g_transporterData[key]

def register( name, sign, pos, direction, spaceName ):
	"""
	注册传送器
	@param spaceName: 场景名称
	@type  spaceName: string
	@param name: 传送器名称
	@type  name: string
	@param sign: 传送器ID
	@type  sign: INT64
	@param pos: 传送器回传位置
	@type  pos: Vector3
	@param pos: 传送器回传方向
	@type  pos: Vector3
	"""
	g_transporterData.register( name, sign, pos, direction, spaceName )

def getData():
	"""
	返回传送器数据	
	"""
	return 	g_transporterData.getData()
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2006/12/21 08:01:06  panguankong
# 按策划要求修改了传送点和复活点信息
#
# Revision 1.3  2006/12/09 03:18:19  panguankong
# 添加了墓地方向
#
# Revision 1.2  2006/11/03 01:22:37  panguankong
# 添加空间管理器
#
# Revision 1.1  2005/12/01 06:38:22  xuning
# 工会
#
#
