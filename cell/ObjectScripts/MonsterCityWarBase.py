# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from Monster import Monster

class MonsterCityWarBase(  Monster ):
	"""
	资源据点
	"""
	def __init__( self ):
		Monster.__init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_NONE		# 据点类型
	
	def onCreated( self, selfEntity ):
		"""	
		资源点创建
		"""
		selfEntity.baseType == self.baseType
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onCityWarBaseCreated( selfEntity.base, self.baseType, selfEntity.belong, selfEntity.className )

	def onActivated( self, selfEntity ):
		"""
		被激活
		"""
		pass

	def onOccupied( self, selfEntity, belong ):
		"""
		被占领
		"""
		if self.baseType in [ csdefine.CITY_WAR_FINAL_BASE_BATTLE, csdefine.CITY_WAR_FINAL_BASE_FLAG,\
		 csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD, csdefine.CITY_WAR_FINAL_BASE_HEROMONU ]:
			spaceBase = selfEntity.getCurrentSpaceBase()
			if spaceBase:
				spaceBase.cell.baseOccupiedNotice( self.baseType, selfEntity.getName(), belong )

	def reset( self, selfEntity ):
		"""
		重置
		"""
		selfEntity.belong = csdefine.CITY_WAR_FINAL_FACTION_NONE

	def receiveDamage( self, selfEntity, casterID, damage ):
		"""
		接收到伤害
		"""
		pass

 	def onReceiveSpell( self, selfEntity, caster, spell ):
 		"""
 		法术到达的回调，由某些特殊技能调用
 		"""
 		pass
 
 	def taskStatus( self, selfEntity, playerEntity ):
		"""
		任务箱子进入到某玩家的视野，任务箱子向服务器乞求它于这个玩家的关系
		"""
		pass

