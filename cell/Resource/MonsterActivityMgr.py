# -*- coding: gb18030 -*-
#
# $Id:  Exp $



from bwdebug import *
import Language
import Function

class MonsterActivityMgr:
	"""
	巡逻数据管理
	"""
	_instance = None
	def __init__( self ):
		assert MonsterActivityMgr._instance is None
		MonsterActivityMgr._instance = self
		self.activityMonsterBossIDs = [ '20614002', '20624003','20634002', '20644001', '20654002', '20614004', '20624005','20624008']
		self.activityMonsterIDs = ['20651008', '20641002', '20631007', '20621006', '20611007',]
		self.activityCowMonsterIDs = ['20611157', '20621157', '20631157', '20641157', '20651157',]
		self.activityGhostMonsterIDs = ['20611158', '20621158', '20631158', '20641158', '20651158',]


	@staticmethod
	def instance():
		"""
		"""
		if MonsterActivityMgr._instance is None:
			MonsterActivityMgr._instance = MonsterActivityMgr()
		return MonsterActivityMgr._instance
