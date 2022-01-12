# -*- coding: gb18030 -*-

# $Id: SkillTrainerLoader.py,v 1.1 2008-01-31 07:30:27 yangkai Exp $

import Language
from bwdebug import *
import BigWorld
from config.client.labels.ItemsFactory import POSTURE_STR
from LabelGather import labelGather
import config.client.labels.GUIFacade as lbDatas
import config.client.labels.ItemsFactory as lbs_ItemsFactory
from config.skill.SkillTeachData import Datas as skTeachDatas
from ItemsFactory import SkillItem
import csdefine
import math
from Time import Time
import re

class GuardInfosLoader:
	"""
	技能树技能格配置加载
	"""
	__sk_config_path = "config/client/PGNagualUIInfo.xml"
	_instance = None
	
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert GuardInfosLoader._instance is None
		self._datas = {}
		GuardInfosLoader._instance = self
		self.load( self.__sk_config_path )
		
	def load( self, configPath ):
		section = Language.openConfigSection( configPath )
		if section is None:return
		for node in section.values():
			className = node.readString( "className" )
			if className == 0:continue
			name = node.readString( "name" )
			attackType = node.readInt( "attackType" )
			realm = node.readInt( "realm" )
			reqAccum = node.readInt( "reqAccum" )
			HP = node.readInt( "HP" )
			damage = node.readInt( "damage" )
			model = node.readString( "model" )
			mapSkID = node.readInt64( "mapSkID" )
			dsp = node.readString( "discription" )
			guardInfo = GuardInfo( className, realm, name, attackType, reqAccum, HP, damage, model, mapSkID, dsp )
			self._datas[mapSkID] = guardInfo
				
		# 清除缓冲
		Language.purgeConfig( self.__sk_config_path )

	def getGuardInfo( self, mapSkID ):
		"""
		根据npc编号取得对应的技能ID表
		"""
		try:
			return self._datas[mapSkID]
		except KeyError:
			return None
	
	@staticmethod
	def instance():
		"""
		"""
		if GuardInfosLoader._instance is None:
			GuardInfosLoader._instance = GuardInfosLoader()
		return GuardInfosLoader._instance

class GuardInfo:
	def __init__( self, className, realm, name, attackType, reqAccum, HP, damage, model, mapSkID, dsp ):
		"""
		守护数据封装
		"""
		self.className = className
		self.realm = realm
		self.name = name
		self.attackType = attackType
		self.reqAccum = reqAccum
		self.HP = HP
		self.damage = damage
		self.model = model
		self.mapSkID = mapSkID
		self.dsp = dsp
		
guardInfosLoader = GuardInfosLoader.instance()