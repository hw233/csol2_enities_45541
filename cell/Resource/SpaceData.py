# -*- coding: gb18030 -*-
#
# $Id: SpaceData.py,v 1.9 2008-04-16 05:55:47 phw Exp $

"""
场景数据
"""

import BigWorld
import Language
from bwdebug import *
import Function
import Language

class SpaceData:
	def __init__( self, configPath = None ):
		"""
		构造函数。
			@param configPath:	技能配置文件路径
			@type  configPath:	string
		"""
		if configPath is not None:
			self.load( configPath )

	def __getitem__( self, key ):
		"""
		取得Space数据部分
		"""
		return self.data[key]

	def load( self, configPath ):
		"""
		加载场景数据。
			@param configPath:	场景配置文件路径
			@type configPath:	string
		"""
		self.data = {}
		files = Language.searchConfigFile( configPath, ".xml" )			# 从取得的配置路径中搜索文件

		# 传送门数据
		doormap = {}
		# 复活地区
		tombmap = {}
		print files
		for path in files:
			sect = Language.openConfigSection( path )
			assert sect is not None, "open %s false." % path
			print path
			name = sect["className"].asString
			sect = sect["Space"]
			if sect.has_key("Transport"):
				doorList = {}
				for objName, objSect in sect["Transport"].items():
					sign = objSect.readInt64("Sign")
					doordict = {"name" : objSect.readString("Name")}
					doordict["pos"] = objSect.readVector3("ReturnPos")
					doordict["direction"] = objSect.readVector3("ReturnDirection")
					doorList[sign] = doordict
				doormap[name] = doorList

			v = sect
			if v.has_key("Tomb"):
				tombs = []
				for objName, sect in v["Tomb"].items():
					s = {}
					s["position"] = sect["Position"].asVector3
					s["name"] = sect["SpaceName"].asString
					s["direction"] = sect["Direction"].asVector3
					tombs.append( s )
				tombmap[name] = tombs
			# 读取完毕则关闭打开的文件
			Language.purgeConfig( path )
		self.data["Transport"] = doormap
		self.data["tomb"] = tombmap

g_spacedata = SpaceData( "config/server/gameObject/space" )

def getSpaceData( key ):
	"""
	获取场景数据。
		@param key:	场景名
		@type key:	string
	"""
	return g_spacedata[key]

#
# $Log: not supported by cvs2svn $
# Revision 1.8  2008/01/25 10:10:47  yangkai
# 配置文件路径修改
#
# Revision 1.7  2007/09/28 02:18:41  yangkai
# 配置文件路径更改:
# res/server/config  -->  res/config
#
# Revision 1.6  2007/09/25 07:26:24  kebiao
# 修改加载路径
#
# Revision 1.5  2007/09/24 02:41:06  kebiao
# 调整路径读取方式
#
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
