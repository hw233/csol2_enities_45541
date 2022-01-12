# -*- coding: gb18030 -*-

# $Id: SkillTrainerLoader.py,v 1.1 2008-01-31 07:30:27 yangkai Exp $

import Language
from bwdebug import *

class SkillTrainerLoader:
	"""
	技能训练师教授的技能加载
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert SkillTrainerLoader._instance is None
		self._datas = {}
		self._skillIDs = set([])
		SkillTrainerLoader._instance = self

	def load( self, configPath ):
		"""
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			npcID = node.readString( "npcID" )
			skillID = node.readInt64( "skillID" )
			self._skillIDs.add( skillID )
			if self._datas.has_key( npcID ):
				self._datas[ npcID ].add( skillID )
			else:
				self._datas[ npcID ] = set( [skillID] )
		# 清除缓冲
		Language.purgeConfig( configPath )

	def get( self, npcID ):
		"""
		根据npc编号取得对应的技能ID表
		"""
		try:
			return list( self._datas[npcID] )
		except KeyError:
			DEBUG_MSG( "npc %s has not config" % npcID)
			return  []
	
	def has( self, skillID ):
		"""
		是否在学习技能列表
		"""
		return skillID in self._skillIDs

	@staticmethod
	def instance():
		"""
		"""
		if SkillTrainerLoader._instance is None:
			SkillTrainerLoader._instance = SkillTrainerLoader()
		return SkillTrainerLoader._instance


#
# $Log: not supported by cvs2svn $