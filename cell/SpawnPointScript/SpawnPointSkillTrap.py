# -*- coding: gb18030 -*-
import random

import BigWorld
from bwdebug import *
import csdefine
import csconst
import random
from SpawnPoint import SpawnPoint

class SpawnPointSkillTrap( SpawnPoint ):
	"""
	陷阱专用刷新点
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		pass

	def onBaseGotCell( self, selfEntity ):
		"""
		由base回调回来，通知spawn point，base已经获得了cell的通知
		"""
		# 当base获得了onGetCell()回调后再开始怪物的增产生，以求能解决怪物出生时出生点不正确的问题
		# 当前该问题很可能是底层的bug
		pass	# 副本怪物出生点，不需要创建出生点的怪物
	
	def converSkillID( self, strSkill ):
		if strSkill:
			skills = [ int( sid ) for sid in strSkill.split( ";" ) ]
			return random.choice( skills )
			
		return 0
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPoint.getEntityArgs( self, selfEntity, params )
		args[ "enterSpell" ] = self.converSkillID( args[ "enterSpell" ] )
		args[ "leaveSpell" ] = self.converSkillID( args[ "leaveSpell" ] )
		args[ "destroySpell" ] = self.converSkillID( args[ "destroySpell" ] )
		return args

	def createEntity( self, selfEntity, params = {} ):
		"""
		define method
		初始化怪物
		"""
		args = self.getEntityArgs( selfEntity, params )
		selfEntity.createEntityNear( "SkillTrap", selfEntity.position, selfEntity.direction, args )