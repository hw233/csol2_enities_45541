# -*- coding: gb18030 -*-

# bigworld
import BigWorld
# common
import csdefine
import csconst
import ItemTypeEnum
from bwdebug import *
# cell
import Const
import items
from Love3 import g_skills
# config 
import csstatus

g_items = items.instance()

# 阵型位置数据
PG_FORMATION_TYPE_POSITION = {
	csdefine.PG_FORMATION_TYPE_CIRCLE:[(2.0000,0.00),(2.2361,26.57),(2.2361,333.43),(2.2361,296.57),(2.2361,63.43),(2.0000,270.00),(2.0000,90.00),(2.0000,180.00),(2.2361,153.43),(2.2361,206.57),(2.2361,243.43),(2.2361,116.57)],
	csdefine.PG_FORMATION_TYPE_SNAKE:[(2.0000,0.00),(1.4142,45.00),(1.4142,315.00),(2.2361,206.57),(2.2361,153.43),(3.1623,198.43),(3.1623,161.57),(1.0000,180.00),(4.1231,194.04),(4.1231,165.96),(2.2361,206.57),(2.2361,153.43)],
	csdefine.PG_FORMATION_TYPE_FISH:[(3.0000,0.00),(2.2361,333.43),(2.2361,26.57),(3.1623,288.43),(3.1623,71.57),(4.0000,270.00),(4.0000,90.00),(2.0000,180.00),(2.0000,270.00),(2.0000,90.00),(3.1623,198.43),(3.1623,161.57)],
	csdefine.PG_FORMATION_TYPE_ARROW:[(3.0000,0.00),(2.2361,333.43),(2.2361,26.57),(2.2361,296.57),(2.2361,63.43),(2.2361,206.57),(2.2361,153.43),(4.0000,180.00),(1.4142,225.00),(1.4142,135.00),(3.1623,198.43),(3.1623,161.57)],
	csdefine.PG_FORMATION_TYPE_GOOSE:[(3.0000,0.00),(2.2361,26.57),(2.2361,333.43),(2.0000,270.00),(2.0000,90.00),(4.4721,243.43),(4.4721,116.57),(1.0000,180.00),(2.2361,116.57),(2.2361,243.43),(3.1623,108.43),(3.1623,251.57)],
	csdefine.PG_FORMATION_TYPE_CRANE:[(2.0000,0.00),(2.0000,270.00),(2.0000,90.00),(5.0000,270.00),(5.0000,90.00),(6.0000,90.00),(6.0000,270.00),(2.0000,180.00),(3.0000,90.00),(3.0000,270.00),(4.0000,90.00),(4.0000,270.00)],
	csdefine.PG_FORMATION_TYPE_MOON:[(2.8284,45.00),(1.4142,45.00),(4.2426,45.00),(3.6056,56.31),(2.2361,63.43),(5.6569,225.00),(5.0000,216.87),(1.4142,225.00),(2.8284,225.00),(2.2361,206.57),(4.2426,225.00),(3.6056,213.69)],
	csdefine.PG_FORMATION_TYPE_EIGHT:[(2.0000,0.00),(2.0000,270.00),(2.0000,90.00),(3.6056,326.31),(3.6056,33.69),(4.0000,270.00),(4.0000,90.00),(2.0000,180.00),(3.6056,213.69),(3.6056,146.31),(1.0000,270.00),(1.0000,90.00)],
	csdefine.PG_FORMATION_TYPE_TAIL:[(2.0000,180.00),(2.8284,225.00),(2.8284,135.00),(4.4721,116.57),(4.4721,206.57),(4.0000,180.00),(4.4721,153.43),(5.6569,135.00),(6.3246,198.43),(6.0000,180.00),(6.3246,161.57),(7.2111,146.31)],
	csdefine.PG_FORMATION_TYPE_SCATTERED:[(3.5355,225.00),(5.5902,153.43),(7.0711,225.00),(7.5000,180.00),(9.0139,146.31),(10.3078,194.04),(10.6066,225.00),(11.1803,206.57),(12.5000,180.00),(5.0000,180.00),(14.5774,210.96),(10.3078,165.96)],
}

# 召唤守护技能列表
PG_CALL_SKILL_LIST = [ 730901]

# PG == 盘古
class RoleStarMapInterface:
	"""
	星际任务相关
	"""
	def __init__( self ):
		pass

	def getAccum( self ):
		"""
		define method
		"""
		return self.accumPoint
	
	def registerPGNagual( self, type, id ):
		"""
		define method
		怪物创建后，把自己注册到主人上
		"""
		callPGDict = self.queryTemp( "callPGDict", {} )
		recorder = callPGDict.get( type )
		if recorder is None:
			recorder = []
			callPGDict[type] = recorder
		callPGDict[type].append( id )
		self.setTemp( "callPGDict", callPGDict )
		# 设置阵型，保证刚召唤出来的盘古守护能找到自己的位置
		pg_fomation = self.queryTemp("pg_formation", csdefine.PG_FORMATION_TYPE_SCATTERED )
		self.setStarMapFormation( self.id, pg_fomation )
		
	def removePGNagual( self, type, id ):
		"""
		define method
		从字典中删除无效的entity
		"""
		callPGDict = self.queryTemp( "callPGDict", {} )
		if id in callPGDict.get( type ):
			callPGDict[type].remove( id )
			self.setTemp( "callPGDict", callPGDict )
		# 重新布阵
		pg_fomation = self.queryTemp("pg_formation", csdefine.PG_FORMATION_TYPE_SCATTERED )
		self.setStarMapFormation( self.id, pg_fomation )

	# -------------------------------------------------------------- #
	# 界面操作相关
	# -------------------------------------------------------------- #
	def setPGActionMode( self, srcEntityID, mode):
		"""
		Exposed method
		设置盘古守护的行为模式 一共有六种模式
		"""
		if not self.hackVerify_( srcEntityID ) : 
			return
			
		if mode not in[ \
			csdefine.PGNAGUAL_ACTION_MODE_FOLLOW,\
			csdefine.PGNAGUAL_ACTION_MODE_ATTACK,\
			csdefine.PGNAGUAL_ACTION_MODE_NEAR_GROUP,\
			csdefine.PGNAGUAL_ACTION_MODE_NEAR_SINGLE,\
			csdefine.PGNAGUAL_ACTION_MODE_FAR_PHYSIC,\
			csdefine.PGNAGUAL_ACTION_MODE_FAR_MAGIC,
			]:
			HACK_MSG( "Pangu nagual error motion from %i " % srcEntityID )
			return
		
		# 获得玩家身上的守护列表
		callPGDict = self.queryTemp( "callPGDict", {} )
		
		# 跟随
		if mode == csdefine.PGNAGUAL_ACTION_MODE_FOLLOW:
			for pg_ids in callPGDict.itervalues():
				for id in pg_ids:
					nagual = BigWorld.entities.get( id )
					if nagual:
						self.spellTarget( Const.PGNAGUAL_ACTION_FOLLOW_SKILLID, nagual.id )
		
		# 攻击
		elif mode == csdefine.PGNAGUAL_ACTION_MODE_ATTACK:
			for pg_ids in callPGDict.itervalues():
				for id in pg_ids:
					nagual = BigWorld.entities.get( id )
					if nagual:
						self.spellTarget( Const.PGNAGUAL_ACTION_ATTACK_SKILLID, nagual.id )
		
		# 近战群体类盘古守护使用技能
		elif mode == csdefine.PGNAGUAL_ACTION_MODE_NEAR_GROUP:		
			for id in callPGDict[ csdefine.PGNAGUAL_TYPE_NEAR_GROUP ]:
				nagual = BigWorld.entities.get( id )
				if nagual:
					self.spellTarget( Const.PGNAGUAL_NEAR_GROUP_SKILLID, nagual.id )
		
		# 近战单体类盘古守护使用技能
		elif mode == csdefine.PGNAGUAL_ACTION_MODE_NEAR_SINGLE:
			for id in callPGDict[ csdefine.PGNAGUAL_TYPE_NEAR_SINGLE ]:
				nagual = BigWorld.entities.get( id )
				if nagual:
					self.spellTarget( Const.PGNAGUAL_NEAR_SINGLE_SKILLID, nagual.id )
		
		# 远程物理类盘古守护使用技能
		elif mode == csdefine.PGNAGUAL_ACTION_MODE_FAR_PHYSIC:
			for id in callPGDict[ csdefine.PGNAGUAL_TYPE_FAR_PHYSIC ]:
				nagual = BigWorld.entities.get( id )
				if nagual:
					self.spellTarget( Const.PGNAGUAL_FAR_PHYSIC_SKILLID, nagual.id )
			
		# 远程法术类盘古守护使用技能
		else:
			for id in callPGDict[ csdefine.PGNAGUAL_TYPE_FAR_MAGIC ]:
				nagual = BigWorld.entities.get( id )
				if nagual:
					self.spellTarget( Const.PGNAGUAL_FAR_MAGIC_SKILLID, nagual.id )
	
	def setStarMapFormation( self, srcEntityID, formation ):
		"""
		Exposed method
		设置召唤NPC布阵
		"""
		self.setTemp("pg_formation", formation )
		callPGDict = self.queryTemp( "callPGDict", {} )
		npcIDs = []
		npcIDs.extend( callPGDict.get( csdefine.PGNAGUAL_TYPE_NEAR_GROUP, [] ) )
		npcIDs.extend( callPGDict.get( csdefine.PGNAGUAL_TYPE_NEAR_SINGLE, [] ) )
		npcIDs.extend( callPGDict.get( csdefine.PGNAGUAL_TYPE_FAR_PHYSIC, [] ) )
		npcIDs.extend( callPGDict.get( csdefine.PGNAGUAL_TYPE_FAR_MAGIC, [] ) )
		posInfos = PG_FORMATION_TYPE_POSITION.get( formation, [] )
		for index,nid in enumerate( npcIDs ):
			npcEntity = BigWorld.entities.get( nid )
			if npcEntity and index < self.queryTemp( "ROLE_CALL_PGNAGUAL_LIMIT", csconst.ROLE_CALL_PGNAGUAL_LIMIT ) :
				posInofs = posInfos[ index ]
				npcEntity.setToOwnerPos( posInofs[0], posInofs[1] )
	
	def autoSetStarMapFormation( self, srcEntityID, formation ):
		"""
		Exposed method
		自动排兵布阵
		"""
		pass
	
	def addMapSkill( self, srcEntityID, index, skillID ):
		"""
		Exposed method
		设置地图守护技能
		"""
		if not self.hackVerify_( srcEntityID ) : 
			return
		spaceName = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if self.mapSkills.has_key( spaceName ):
			mapSkills = self.mapSkills[spaceName]
			mapSkills[index] = skillID
		else:
			self.mapSkills[spaceName] = { index:skillID}
		self.client.onAddMapSkill( index, skillID )
	
	def removeMapSkill( self, srcEntityID, index ):
		"""
		Exposed method
		移除地图守护技能
		"""
		if not self.hackVerify_( srcEntityID ) : 
			return
		spaceName = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if not spaceName in self.mapSkills:
			return
		mapSkills = self.mapSkills[spaceName]
		if index in mapSkills:
			mapSkills.pop( index )
			self.client.onRemoveMapSkill( index )
		if len( mapSkills ) <= 0:
			self.mapSkills.pop( spaceName )
	
	# -------------------------------------------------------------- #
	# 气运值相关
	# -------------------------------------------------------------- #
	def initAccumPoint( self ):
		"""
		define method
		初始化气运值
		"""
		self.accumPoint = Const.ROLE_INIT_ACCUM_POINT
		
	def addAccumPoint( self, point ):
		"""
		define method
		增加气运点数
		"""
		self.accumPoint += point
		
	def resetAccumPoint( self ):
		"""
		define method
		将玩家的气运点数清零
		"""
		self.accumPoint = 0

	def queryItemFromBagAndAddItem( self, itemID1, amount, itemID2 ):
		"""
		define method
		查询玩家是否有一定数量的某个物品，如果有将玩家该物品删除，同时给玩家加一个新的物品
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType != csdefine.SPACE_TYPE_MERCURY_CORE_MAP:
			return
			
		if self.checkItemFromNKCK_( itemID1, amount ) and not self.queryTemp( "hasMercuryCoreItem", False ):
			self.setTemp( "hasMercuryCoreItem", True )
			if not self.removeItemTotal( itemID1, amount, csdefine.DELETE_ITEM_BUYFROMITEMCHAPMAN ):
				self.removeTemp( "hasMercuryCoreItem" )
			else:
				item = g_items.createDynamicItem( itemID2 )
				if item == None:
					return
				self.addItem( item, csdefine.ADD_ITEM_USE )
