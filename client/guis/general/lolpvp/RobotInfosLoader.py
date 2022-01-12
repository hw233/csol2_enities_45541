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
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()
import csdefine
import math
from Time import Time
import re

class RobotInfosLoader:
	"""
	技能树技能格配置加载
	"""
	__sk_config_path = "config/client/RobotClientInfo.xml"
	_instance = None
	
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert RobotInfosLoader._instance is None
		self._datas = {}
		RobotInfosLoader._instance = self
		self.load( self.__sk_config_path )
		
	def load( self, configPath ):
		section = Language.openConfigSection( configPath )
		if section is None:return
		for node in section.values():
			className = node.readString( "className" )
			if className == "":continue
			name = node.readString( "name" )
			soulCoin = node.readInt( "soulCoin" )
			HP = node.readInt( "HP" )
			force = node.readInt( "force" )
			modelNum = node.readString( "modelNum" )
			dsp = node.readString( "discription" )
			robotInfo = RobotInfo( className, name, soulCoin, HP, force, modelNum, dsp )
			self._datas[className] = robotInfo
				
		# 清除缓冲
		Language.purgeConfig( self.__sk_config_path )

	def getRobotInfo( self, className ):
		"""
		根据npc编号取得对应的技能ID表
		"""
		try:
			return self._datas[className]
		except KeyError:
			return None
	
	def setRbtExtraInfo( self, className, level, raceclass, soulCoin, life, mp, force ):
		"""
		设置机器人扩展属性
		"""
		rbtInfo = self._datas.get( className )
		if rbtInfo is None:return
		rbtInfo.setRbtExtraInfo( level, raceclass, soulCoin, life, mp, force )
	
	@staticmethod
	def instance():
		"""
		"""
		if RobotInfosLoader._instance is None:
			RobotInfosLoader._instance = RobotInfosLoader()
		return RobotInfosLoader._instance

class RobotInfo:
	def __init__( self, className, name, soulCoin, hp, force, modelNum, dsp ):
		"""
		守护数据封装
		"""
		self.className = className
		self.name = name
		self.soulCoin = soulCoin
		self.hp = hp
		self.force = force
		self.modelNum = modelNum
		self.dsp = dsp
		self.raceclass = 0
		self.level = 0
		self.mp = 0
		self.hpMax = 0
		self.mpMax = 0
		self.header = g_npcmodel.getHeadTexture( modelNum )
		self.isRobot = True
	
	def setRbtExtraInfo( self, level, raceclass, soulCoin, life, MP, force ):
		self.level = level
		self.raceclass = raceclass
		self.soulCoin = soulCoin
		self.hp = life
		self.mp = MP
		self.force = force
		self.hpMax = MP
		self.mpMax = life
		
robotInfosLoader = RobotInfosLoader.instance()