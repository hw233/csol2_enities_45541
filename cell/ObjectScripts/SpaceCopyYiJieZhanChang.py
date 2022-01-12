# -*- coding: gb18030 -*-
#python
import random
#bigworld
import BigWorld
#common
import csdefine
import csstatus
from bwdebug import INFO_MSG,ERROR_MSG

from SpaceCopy import SpaceCopy


# 战场内阵营：天、地、人
FACTION_TIAN					= csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN
FACTION_DI						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI
FACTION_REN						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN

# entity className
YI_JIE_TOWER			= 20254095		# 箭塔
YI_JIE_STONE			= 20254098		# 洪荒灵石
YI_JIE_FACTION_FLAG		= 10121771		# 阵营柱

class SpaceCopyYiJieZhanChang( SpaceCopy ):
	# 异界战场
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.enterInfos = []
		

# ----------------------------------------------------------------
# 新方法
# ----------------------------------------------------------------

	def getRandomEnterPos( self ):
		"""
		随机取得一个进入的位置
		"""
		return random.choice( self.enterInfos )
	
	def getFactionEnterPos( self, faction ) :
		"""
		取得阵营进入点
		"""
		if faction == FACTION_TIAN :
			return self.enterInfos[0][0]
		elif faction == FACTION_DI :
			return self.enterInfos[1][0]
		else :
			return self.enterInfos[2][0]
	
	def __isInCircle( self, pos, center, radius ) :
		"""
		点 pos 是否在圆（圆心为center,半径为radius）内
		"""
		dx = pos[0] - center[0]
		dy = pos[1] - center[1]
		if dx * dx + dy * dy < radius * radius :
			return True
		else :
			return False
	
	def onYiJieStoneCreate( self, selfEntity ) :
		"""
		洪荒灵石生成时处理
		"""
		selfEntity.battlegroundMgr.onYiJieStoneCreate()
	
	def onYiJieStoneDie( self, selfEntity, killerDBID ):
		"""
		洪荒灵石死亡时处理
		"""
		selfEntity.battlegroundMgr.finalBlowStone( killerDBID )
	

# ----------------------------------------------------------------
# 重载方法
# ----------------------------------------------------------------

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopy.load( self, section )
		
		for idx, item in enumerate( section[ "Space" ][ "enterInfos" ].values() ):
			pos = tuple( [ float(x) for x in item["position"].asString.split() ] )
			direction = tuple( [ float(x) for x in item["direction"].asString.split() ] )
			self.enterInfos.append( ( pos, direction ) )
			
		self.canAllianceTime = section[ "Space" ][ "canAllianceTime" ].asInt
		self.enrageTime = section[ "Space" ][ "enrageTime" ].asInt
		self.closeTime = section[ "Space" ][ "closeTime" ].asInt
		self.reviveTime = section[ "Space" ][ "reviveTime" ].asInt
		self.reviveRadius = section[ "Space" ][ "reviveRadius" ].asInt
		self.maxRage = section[ "Space" ][ "maxRage" ].asInt
		self.minLevel = section[ "Space" ][ "minLevel" ].asInt
	
	def initEntity( self, selfEntity ):
		"""
		初始化自己的entity的数据
		"""
		SpaceCopy.initEntity( self, selfEntity )
		
	
	def _createDoor( self, selfEntity ):
		"""
		创建Door
		"""
		print "Create createDoor..."
		configInfo = self.getSpaceConfig()
		for name, otherDict in configInfo[ "Doormap" ].iteritems():
			print "create Door ", name
			BigWorld.createEntity( "SpaceDoorYiJieZhanChang", selfEntity.spaceID, otherDict["position"], (0, 0, 0), otherDict )
	
	def checkDomainLeaveEnable( self, entity ):
		"""
		在cell上检查该空间离开的条件
		"""
		# 只有使用副本内传送门时才会设置这个标记,其他任何途径都无法离开。
		if not entity.popTemp( "leaveYiJieZhanChang", False ) :
			return csstatus.SPACE_MISS_LEAVE_CANNOT_TELEPORT_SPACE
		return csstatus.SPACE_OK
	
	def packedDomainData( self, entity ):
		"""
		创建SpaceDomainYiJieZhanChang时，传递参数
		"""
		d = {}
		d[ "dbID" ] = entity.databaseID
		d[ "level" ] = entity.level
		if entity.teamMailbox :
			d[ "teamID" ] = entity.teamMailbox.id
		return d
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		pickDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		enterPos = entity.position
		if self.__isInCircle( enterPos, self.enterInfos[0][0], self.reviveRadius ) :
			entity.yiJieFaction = FACTION_TIAN
			pickDict[ "faction" ] = FACTION_TIAN
		elif self.__isInCircle( enterPos, self.enterInfos[1][0], self.reviveRadius ) :
			entity.yiJieFaction = FACTION_DI
			pickDict[ "faction" ] = FACTION_DI
		elif self.__isInCircle( enterPos, self.enterInfos[2][0], self.reviveRadius ) :
			entity.yiJieFaction = FACTION_REN
			pickDict[ "faction" ] = FACTION_REN
		else :
			#ERROR_MSG( "Role[databaseID : %s] enter error position. " % entity.databaseID )
			pickDict[ "faction" ] = FACTION_REN
		
		return pickDict
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		进入
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEMPORARY_FACTION )
		
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		离开
		"""
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def onRoleDie( self, role, killer ):
		"""
		某role在该副本中死亡
		"""
		if not killer :
			return
		killerType = killer.getEntityType()
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ) :
			killer = killer.getOwner().entity
		
		killerDBID = 0
		killerName = ""
		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			killerDBID = killer.databaseID
			killerName = killer.playerName
		elif killer.isEntityType( csdefine.ENTITY_TYPE_YI_JIE_ZHAN_CHANG_TOWER ) :
			killerName = killer.uname
		role.client.yiJieSetReviveInfo( self.reviveTime, killerName )
		role.getCurrentSpaceBase().cell.onRoleBeKill( tuple( role.position ), role.databaseID, killerDBID, killerType )

	def kickAllPlayer( self, selfEntity ):
		"""
		将副本所有玩家踢出
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].yiJieLeaveSpace()
			else:
				e.cell.yiJieLeaveSpace()

