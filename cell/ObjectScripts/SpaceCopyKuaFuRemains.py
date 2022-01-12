# -*- coding: gb18030 -*-


from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate
import cschannel_msgs
from CopyContent import CopyContent
from CopyContent import CCWait
from CopyContent import CCKickPlayersProcess
from CopyContent import NEXT_CONTENT
from CopyContent import CCEndWait
from CopyEvent import CopyEvent
import BigWorld
import csconst
import csdefine
import ECBExtend
import csstatus

GW_HP_CHANGE_RATE = 85

"""
8个石像代表 1～ 8 组的怪。
特殊事件：
KUA_FU_EVENT_JUBI_FLY_TO_SKY		= 1										#据比飞向天空
KUA_FU_EVENT_SPAWN_TO_DEADBODY		= 2										#刷出两个死尸
KUA_FU_EVENT_CENTER_FIRE_FLY_TO_SKY	= 3										#触发中心火球飞向天空
KUA_FU_EVENT_FEILIAN_KUI_DI			= 4										#飞廉跪地
KUA_FU_EVENT_STONE_DESTROY			= 5										#石像被摧毁
"""

class CCSpawnStep1( CopyContent ):
	"""
	#刷新第一关Entity
	"""
	def __init__( self ):
		"""
		"""
		self.key = "step1BossDiedCount"
		self.val = 1


	def onContent( self, spaceEntity ):
		"""
		"""
		#print "开始第一关"
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 0 } )
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 1 } )


	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if not "step" in params or params["step"] != 1:
			return False
		
		if "entityType" in params and params["entityType"] == csconst.KUA_FU_ENTITY_TYPE_BOSS:
			#print "夸父神殿:通过第一关"
			
			return True
		return False
		
	def endContent( self, spaceEntity ):
		"""
		内容结束
		"""
		spaceEntity.base.openDoor( 1 )
		CopyContent.endContent( self, spaceEntity )


class CCSpawnStep2( CopyContent ):
	"""
	#刷新第二关Entity
	"""
	def __init__( self ):
		"""
		"""
		self.key = "step2BossDiedCount"
		self.val = 2

	def onContent( self, spaceEntity ):
		"""
		"""
		#print "开始第二关"
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 2 } )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if not "step" in params or params["step"] != 2:
			return False
		
		if "entityType" in params :
			entityType = params["entityType"]
			if  entityType == csconst.KUA_FU_ENTITY_TYPE_SHITI:
				count = spaceEntity.queryTemp( self.key, 0 ) + 1
				if count == self.val:
					#print "夸父神殿:通过第二关"
					spaceEntity.base.eventHandle( csconst.KUA_FU_EVENT_HOU_QING, {"aiLevel" : 1} )
					spaceEntity.base.eventHandle( csconst.KUA_FU_EVENT_CENTER_FIRE_FLY_TO_SKY, {"aiLevel" : 1} )
					return True
				spaceEntity.setTemp( self.key, count )
			if entityType == csconst.KUA_FU_ENTITY_TYPE_STONE:
				spaceEntity.base.eventHandle( csconst.KUA_FU_EVENT_STONE_DESTROY, {"group": params["group"] } )
		return False

	def endContent( self, spaceEntity ):
		"""
		内容结束
		"""
		spaceEntity.base.openDoor( 2 )
		CopyContent.endContent( self, spaceEntity )
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.KUA_FU_SHEN_DIAN_HOU_QING, cschannel_msgs.KUA_FU_SHEN_DIAN_KUA_FU_MAKE, [] )
			e.client.onMakeASound( "monsterbossyuyin01/hou_qing_attack02", 0 )

class CCSpawnStep3( CopyContent ):
	"""
	#刷新第三关Entity
	"""
	def __init__( self ):
		"""
		"""
		self.key = "step3BossDiedCount"
		self.val = 1


	def onContent( self, spaceEntity ):
		"""
		"""
		#print "开始第三关"
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 3 } )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_TREE_HP_PRECENT, 100 )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if not "step" in params or params["step"] != 3:
			return False
		
		if "entityType" in params and params["entityType"] == csconst.KUA_FU_ENTITY_TYPE_BOSS:
			#print "夸父神殿:通过第三关"
			return True
		return False


class CCSuccess( CopyContent ):
	"""
	# 完成副本
	"""
	def __init__( self ):
		"""
		"""
		self.key = "success"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		self.createDoor( self, spaceEntity )

	def createDoor( self, spaceEntity ):
		"""
		创建Door
		"""
		doordict = {"name" : cschannel_msgs.KUAFU_REMAINS_DOOR}
		doordict["radius"] = 2.0
		doordict["destSpace"] = spaceEntity.params["spaceLabel"]
		doordict["destPosition"] = spaceEntity.params["position"]
		doordict["destDirection"] = ( 0, 0, 0 )
		doordict["modelNumber"] = "gw7504"
		doordict["modelScale"] = 25
		# 还没准确的位置，用暂代的
		BigWorld.createEntity( "SpaceDoor", spaceEntity.spaceID, (13.308, 48.693, 120.754), (0, 0, 0), doordict )


	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "timeOver":
			return True
		return False


class SpaceCopyKuaFuRemains( SpaceCopyTeamTemplate ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.BOSS_CLASSNAMES = []
		self.STONE_CLASSNAME = ""
		SpaceCopyTeamTemplate.__init__( self )
		self.recordKey = "kuafu_record"

	def initContent( self ):
		"""
		"""
		self.contents.append( CCWait() )
		self.contents.append( CCSpawnStep1() )
		self.contents.append( CCWait() )
		self.contents.append( CCSpawnStep2() )
		self.contents.append( CCWait() )
		self.contents.append( CCSpawnStep3() )
		self.contents.append( CCEndWait() )
		self.contents.append( CCKickPlayersProcess() )


	def packedDomainData( self, player ):
		"""
		"""
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = 0
		data = {"copyLevel"			: 	level,
				"dbID" 				: 	player.databaseID,
				"teamID" 			: 	player.teamMailbox.id,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceLabel"		:	BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ),
				"position"			:	player.position,
				}
		return data

	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		packDict = SpaceCopyTeamTemplate.packedSpaceDataOnEnter( self, player )
		if player.teamMailbox:
			packDict[ "teamID" ] = player.teamMailbox.id
		
		packDict[ "dbID" ] = player.databaseID
		return packDict
		
	def onMonsterDie( self, selfEntity, params ):
		"""
		当一般怪物死亡
		"""
		self.onConditionChange( selfEntity, params )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if selfEntity.queryTemp("firstPlayer", 0 ) == 0:
			BigWorld.globalData['KuafuRemain_%i'%params['teamID'] ] = True
			selfEntity.setTemp('globalkey','KuafuRemain_%i'%params['teamID'])
		if baseMailbox is not None:
			baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_KUA_FU, self.recordKey )
		SpaceCopyTeamTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )

	def doStoneDestroy( self, id, group ):
		"""
		"""
		selfEntity = BigWorld.entities[id]
		#print "石像摧毁"
		total = selfEntity.queryTemp( "destroyStoneTotal", 0 ) + 1
		selfEntity.setTemp( "destroyStoneTotal", total )
		
		if total == 1:
			#print "一个石像被摧毁"
			for e in selfEntity._players:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.KUA_FU_SHEN_DIAN_HOU_QING, cschannel_msgs.KUA_FU_SHEN_DIAN_ONE_STONE_DESTROY, [] )
				e.client.onMakeASound( "monsterbossyuyin01/hou_qing_attack01", 0 )
		elif total == 3:
			#print "三个石像被摧毁"
			for e in selfEntity._players:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.KUA_FU_SHEN_DIAN_JU_BI, cschannel_msgs.KUA_FU_SHEN_DIAN_THREE_STONE_DESTROY, [] )
				e.client.onMakeASound( "monsterbossyuyin01/ju_bi_attack01", 0 )
		elif total == 5:
			#print "五个石像被摧毁"
			for e in selfEntity._players:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.KUA_FU_SHEN_DIAN_JU_BI, cschannel_msgs.KUA_FU_SHEN_DIAN_FIVE_STONE_DESTROY, [] )
				e.client.onMakeASound( "monsterbossyuyin01/ju_bi_attack02", 0 )
		elif total == 6:
			#print "六个石像被摧毁"
			selfEntity.base.eventHandle( csconst.KUA_FU_EVENT_JUBI_FLY_TO_SKY, {"aiLevel" : 1} )
			selfEntity.base.eventHandle( csconst.KUA_FU_EVENT_SPAWN_TO_DEADBODY, {"level" : selfEntity.params["copyLevel"]} )
			for e in selfEntity._players:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.KUA_FU_SHEN_DIAN_JU_BI, cschannel_msgs.KUA_FU_SHEN_DIAN_SIX_STONE_DESTROY, [] )
				e.client.onMakeASound( "monsterbossyuyin01/ju_bi_die01", 0 )
		elif total == 7:
			#print "七个石像被摧毁"
			for e in selfEntity._players:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.KUA_FU_SHEN_DIAN_FEI_LIAN, cschannel_msgs.KUA_FU_SHEN_DIAN_SEVEN_STONE_DESTROY, [] )
				e.client.onMakeASound( "monsterbossyuyin01/fei_lian_attack01", 0 )
		elif total == 8:
			#print "八个石像被摧毁"
			selfEntity.base.eventHandle( csconst.KUA_FU_EVENT_FEILIAN_KUI_DI, {"aiLevel" : 1} )


	def onRoleDie( self, role, killer ):
		"""
		某role在该副本中死亡
		"""
		selfEntity = BigWorld.entities.get( role.getCurrentSpaceBase().id )
		if selfEntity is None or not selfEntity.isReal():
			return
		selfEntity.setTemp( "roleDieNum", (selfEntity.queryTemp( "roleDieNum", 0 ) + 1) )
		
	def onTreeHPChange( self, selfEntity, precent ):
		"""
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_TREE_HP_PRECENT, precent )
		if precent < GW_HP_CHANGE_RATE:
			selfEntity.setTemp( "godWoodHPTooLow", True )