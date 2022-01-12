# -*- coding: gb18030 -*-
#
# $Id: preload.py,v 1.3 2007-02-09 02:58:07 phw Exp $

"""
数据预加载模块
"""

import BigWorld
import ResMgr
from bwdebug import *
import time

g_models = []

def preloadAvatar():
	"""
	预加载所有角色
	"""
	"""
	paths = [
				"avatar/nanfashi/000/all.model",
				"avatar/nanjianke/000/all.model",
				#"avatar/nanjishi/000/all.model",
				#"avatar/nansheshou/000/all.model",
				#"avatar/nanwushi/000/all.model",
				"avatar/nanzhanshi/000/all.model",
				#"avatar/nvfashi/000/all.model",
				#"avatar/nvjianke/000/all.model",
				"avatar/nvjishi/000/all.model",
				"avatar/nvsheshou/000/all.model",
				"avatar/nvwushi/000/all.model",
				#"avatar/nvzhanshi/000/all.model",
			]
	"""
	avatars = [
				"avatar/nanfashi",
				"avatar/nanjianke",
				#"avatar/nanjishi",
				#"avatar/nansheshou",
				#"avatar/nanwushi",
				"avatar/nanzhanshi",
				#"avatar/nvfashi",
				#"avatar/nvjianke",
				"avatar/nvjishi",
				"avatar/nvsheshou",
				"avatar/nvwushi",
				#"avatar/nvzhanshi",
			]

	#leves = [ "000", "010", "020", "030", "040", "050", "060", "070", "080", "090", "100"  ]
	leves = [ "000", "010", ]

	components = ['lian.model', 'qunzi.model', 'shangshen.model', 'shoutao.model', 'xiashen.model', 'xiezi.model']

	total = time.time()
	for avatar in avatars:
		for level in leves:
			# 检查是否有指定的等级
			prefix = "%s/%s" % (avatar, level)
			section = ResMgr.openSection( prefix )
			if section is None: continue
			for component in components:
				# 检查是否有指定的模型
				path = "%s/%s/%s" % ( avatar, level, component )
				section = ResMgr.openSection( path )
				if section is None: continue

				# 开始加载模型
				#INFO_MSG( "preloading ...", path )
				#t = time.time()
				try:
					g_models.append( BigWorld.Model( path ) )
				except ValueError, errstr:
					ERROR_MSG( "model %s load fail." % path )
					ERROR_MSG( errstr )
				#print "-->", time.time() - t
	INFO_MSG( "all model preload finish.", time.time() - total )

# preload.py
