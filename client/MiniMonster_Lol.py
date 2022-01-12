# -*- coding: gb18030 -*-

from Monster import Monster
from YXLMBoss import YXLMBoss
import csdefine
from bwdebug import *
from Attack import Attack

class MiniMonster_Lol( Monster, Attack ):
	def __init__( self ):
		Monster.__init__( self )
		Attack.__init__( self )
		
	def queryRelation( self, entity ):
		"""
		关系判断，考虑到该类型只在特定副本出现，目前只判断两种类型
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if not self.inWorld or not entity.inWorld: 
			return csdefine.RELATION_NEUTRALLY
		
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ): # 判断是否为宠物，
			owner = entity.getOwner()
			if owner is None:
				return csdefine.RELATION_NOFIGHT
			else:
				entity = owner
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			# GM观察者模式
			if entity.effect_state & csdefine.EFFECT_STATE_WATCHER:
				return csdefine.RELATION_NOFIGHT
			
			if entity.teamID == self.belong:
				return csdefine.RELATION_FRIEND
			return csdefine.RELATION_ANTAGONIZE
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM ):
			if entity.belong == self.belong:
				return csdefine.RELATION_FRIEND
			
			return csdefine.RELATION_ANTAGONIZE
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_NEUTRALLY

		return csdefine.RELATION_NEUTRALLY		
	
	def requestNearByEnemy( self, range ):
		"""
		define method
		如果得到的最后结果为玩家，但不是PlayerRole，则不向服务器发送数据，
		主要是解决关系判断中teamID的问题，因为PlayerRole获取不到别的玩家的teamID信息，默认得到的数据为0
		"""
		if not self.inWorld:
			INFO_MSG( "I'm not in world now")
			return
		bossID, bossDis, nearID, nearDis, eid, edis = 0, 100.0, 0, 100.0, 0 , 100.0
		entities = self.entitiesInRange( range )
		entities.sort( key = lambda e : e.position.distTo( self.position ) )
		for e in entities:
			if self.queryRelation( e ) ==  csdefine.RELATION_ANTAGONIZE and e.state != csdefine.ENTITY_STATE_DEAD:
				if e.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or isinstance( e, YXLMBoss ):
					if not bossID: 					# 如果最近的是玩家或者Boss，继续选择
						bossID = e.id
						bossDis = e.position.distTo( self.position )
						continue
				
				if not nearID:						# 先选取最近的目标
					nearID = e.id
					nearDis = e.position.distTo( self.position )
					if e.getDamageLength( ) >= 2:		# 如果最近的目标的攻击者太多，继续选择下一个目标
						continue
					break
				
				edis = e.position.distTo( self.position )
				if edis - nearDis < 3.0:			# 下一个目标距离太远，不再搜索
					break
				if e.getDamageLength() < 2: 			# 如果目标距离最近目标小于3.0，且伤害列表小于2，停止搜索
					eid = e.id
					break
		
		# 只有Boss或玩家、Boss距离小于6米
		if  ( bossID and not nearID and not eid ) \
			or ( bossID and nearID and not eid and bossDis < 6.0 < nearDis and nearDis - bossDis > 3.0 ) \
			or ( bossID and eid and bossDis < 6.0 < edis and edis -  bossDis > 3.0 ):
			eid = bossID
		
		# 只有最近的目标
		if ( not bossID and not eid and nearID ) \
			or ( bossID and nearID and not eid and nearDis - bossDis < 3.0 ):
			eid = nearID
		
		if not eid:
			return
		
		target = BigWorld.entities.get( eid )
		if target and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and target.__class__.__name__ != "PlayerRole": # 如果搜到的是其它玩家，则不通知服务器
			return
		
		self.cell.receiveNearByEnemy( eid )
