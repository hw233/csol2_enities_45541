# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from MonsterCityWarBase import MonsterCityWarBase

SPELL_INTONE_TIME = 3.0
RESOURCE_SPELLID = 313100002

class MonsterCityWarBase_Resource(  MonsterCityWarBase ):
	"""
	资源据点
	可以使用技能Spell_313100002 进行拾取操作
	"""
	def __init__( self ):
		MonsterCityWarBase. __init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_RESOURCE		# 据点类型

	def onCreated( self, selfEntity ):
		"""	
		资源点创建( 资源点没有base )
		"""
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onCityWarBaseCreated( selfEntity, self.baseType, selfEntity.belong, selfEntity.className )

	def onOccupied( self, selfEntity, belong ):
		"""
		被占领
		"""
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.onResourceBaseOccupied( self.baseType, selfEntity.id, selfEntity.ownerID, belong )

	def gossipWith(self, selfEntity, playerEntity, dlgKey):
		"""
		@param playerEntity: 玩家实体
		@type  playerEntity: entity
		"""
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return

		playerEntity.setTemp( "quest_box_intone_time", SPELL_INTONE_TIME )	# 设置临时变量以让玩家能正确吟唱技能
		print "quest_box_intone_time:",SPELL_INTONE_TIME
		playerEntity.spellTarget( RESOURCE_SPELLID, selfEntity.id )

 	def onReceiveSpell( self, selfEntity, caster, spell ):
 		"""
 		法术到达的回调，由某些特殊技能调用
 		"""
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		if not selfEntity.isReal():
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return
		
		# 去掉临时标志
		caster.removeTemp( "quest_box_intone_time" )
		# 指示客户端播放光效动画
		#selfEntity.playEffect = self.effectName
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.onRoleOccupyResource( caster.id, selfEntity )

 	def taskStatus( self, selfEntity, playerEntity ):
		"""
		资源点进入到某玩家的视野，资源点向服务器乞求它于这个玩家的关系( 默认玩家和资源点在一个cell中)
		"""
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return

		if selfEntity.belong == playerEntity.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ):
			playerEntity.statusMessage( csstatus.TONG_CITY_WAR_BASE_OCCUPIED )
			return

		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 1 )