# -*- coding: gb18030 -*-

# $Id: NPCQuestDroppedItemLoader.py,v 1.3 2008-08-09 01:50:15 wangshufeng Exp $

import Language
from bwdebug import *

class NPCQuestDroppedItemLoader:
	"""
	怪物掉落物品加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert NPCQuestDroppedItemLoader._instance is None
		# key == 对应的npc className
		# value == dict
		# 	key == questID
		#	value == array of tuple like as [(rate, itemID, amount), ...]
		# like as { npcID : { questID : [ (rate, itemID, amount), ... ], ... }, ...}
		self._datas = {}
		self._questToItemDatas = {}
		NPCQuestDroppedItemLoader._instance = self

	def load( self, configPath ):
		"""
		加载经验配置表
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			classID = node.readString( "npcID" )
			questID = node.readInt( "questID" )
			itemID = node.readInt( "itemID" )
			amount = node.readInt( "amount" )
			rate = node.readFloat( "rate" )
			if amount <= 0: amount = 1


			if classID not in self._datas:
				self._datas[classID] = {}
			if questID not in self._datas[classID]:
				self._datas[classID][questID] = []
			self._datas[classID][questID].append( (rate, itemID, amount) )
			
			if self._questToItemDatas.has_key( questID ):
				self._questToItemDatas[ questID ].append( itemID )
			else:
				self._questToItemDatas[ questID ] = [ itemID ]

		# 清除缓冲
		Language.purgeConfig( configPath )

	def get( self, classID ):
		"""
		根据npc编号和等级取得对应的编号表

		@param classID: NPC编号
		@return: { questID : [ (rate, itemID, amount), ... ], ... }
		"""
		try:
			return self._datas[classID]
		except KeyError:
			DEBUG_MSG( "npc %s has no quest dropped item." % ( classID ) )
			return {}

	
	def getQuestNeedItems( self, questID ):
		if self._questToItemDatas.has_key( questID ):
			return self._questToItemDatas[ questID ]
		else:
			return []

	@staticmethod
	def instance():
		"""
		"""
		if NPCQuestDroppedItemLoader._instance is None:
			NPCQuestDroppedItemLoader._instance = NPCQuestDroppedItemLoader()
		return NPCQuestDroppedItemLoader._instance


#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/12/22 02:29:38  phw
# method modified: get(), fix: NameError: global name 'level' is not defined
#
# Revision 1.1  2007/12/22 01:59:15  phw
# no message
#
#