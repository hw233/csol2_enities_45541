# -*- coding: gb18030 -*-

# $Id: NPCBaseAttrLoader.py,v 1.8 2008-09-04 07:45:21 kebiao Exp $

import Language
from bwdebug import *
import csconst
from config.server import NPCBaseAttr

class NPCBaseAttrLoader:
	"""
	怪物四项基本属性配置加载器
	体质、智力、力量、敏捷
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert NPCBaseAttrLoader._instance is None
		# key == 对应的怪物职业
		# value == 在该职业下的数据字典
		#		key == 对应的怪物等级
		# 		value == 在该等级下的四项属性字典
		# like as { 法师 : { 等级 : { 智力 : xxx, 体质 : xxx, 力量 : xxx, 敏捷 : xxx }, ... }, ...}
		self._datas = NPCBaseAttr.Datas
		NPCBaseAttrLoader._instance = self

	def get( self, raceclass, level ):
		"""
		根据等取得对应的经验值
		@param type: 怪物基础类别
		@param raceclass: 怪物职业编号，如战士(0x00)等
		@return: { 智力 : xxx, 体质 : xxx, 力量 : xxx, 敏捷 : xxx }
		"""
		try:
			# 需要执行(raceclass >> 4) & 0xf的原因是因为当前entity.getClass()返回的是一个左移了4位的值，详看csdefine.CLASS_*
			return self._datas[(raceclass >> 4) & 0xf][level]
		except KeyError:
			if level != 0:
				ERROR_MSG( "level %i or class %i has not in table." % ( level, raceclass ) )
			return {	"strength_base" : 10000.0,
						"dexterity_base" : 10000.0,
						"intellect_base" : 10000.0,
						"corporeity_base" : 10000.0, }
			

	@staticmethod
	def instance():
		"""
		"""
		if NPCBaseAttrLoader._instance is None:
			NPCBaseAttrLoader._instance = NPCBaseAttrLoader()
		return NPCBaseAttrLoader._instance
