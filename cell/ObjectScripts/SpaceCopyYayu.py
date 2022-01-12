# -*- coding: gb18030 -*-


from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate
import cschannel_msgs
import ShareTexts as ST
from CopyContent import CopyContent
from CopyContent import CCWait
from CopyContent import CCKickPlayersProcess
from CopyContent import NEXT_CONTENT
from CopyContent import CCEndWait
import BigWorld
import csconst
import time
import csdefine
import ECBExtend
import csstatus
from config.item.yayuConfigScript import Datas as yayuMonster


NUMBER_OF_YAYU_BOSS = 1
YAYU_DIED = 12456				#猰貐死亡

# STEP_1_TIME = yayuMonster["step_time"] 				#每波怪物时间

YA_YU_MONSTER_NUM = {
	csconst.SPACE_COPY_YE_WAI_EASY:180,
	csconst.SPACE_COPY_YE_WAI_DIFFICULTY:150,
	csconst.SPACE_COPY_YE_WAI_NIGHTMARE:200,
}
def getMonsterCount( difficulty ):
	count = 0
	monsterLens = len( yayuMonster[ difficulty ] )
	for i in yayuMonster[ difficulty ].keys():
		if i <= monsterLens - 2 :
			count = count + yayuMonster[ difficulty ][ i ]["spawn_count"]
	return count


class CCSpawnYayu( CopyContent ):
	"""
	#刷新猰貐
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanYayu"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnYayu( spaceEntity.params["copyLevel"] )


	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		CopyContent.onConditionChange( self, spaceEntity, params )
		spaceEntity.base.setYayuID( params["yayuID"] )
		spaceEntity.setTemp("yayuID", params["yayuID"] )



class CCTalkToYayu( CopyContent ):
	"""
	#和猰貐对话，暂时不使用，而是在对话里进行onConditionChange
	"""
	def __init__( self ):
		"""
		"""
		self.key = "talkToYayu"
		self.val = 1


class CCSpawnMonster1( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster1"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 1 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][1]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "1_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(1), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False



class CCSpawnMonster2( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster2"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 2 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][2]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "2_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(2), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False


class CCSpawnMonster3( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster3"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 3 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][3]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "3_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(3), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster4( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster4"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 4 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][4]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "4_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(4), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster5( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster5"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 5 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][5]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "5_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(5), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster6( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster6"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 6 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][6]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "6_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(6), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster7( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster7"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 7 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][7]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "7_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(7), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster8( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster8"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 8 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][8]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "8_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(8), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster9( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster9"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 9 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][9]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME - 10, 0, NEXT_CONTENT )		# boss刷新前10秒时，刷出一个传送光效
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "9_%i_%i"%(STEP_1_TIME,int(time.time())))
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			for e in spaceEntity._players:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(9), [] )
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE14, [] )
		else:
			for e in spaceEntity._players:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(9), [] )
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster10( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster10"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 10 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][10]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "10_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(10), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False
		
class CCSpawnMonster11( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster11"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 11 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][11]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "11_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(11), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster12( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster12"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 12 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][12]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "12_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(12), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster13( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster13"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 13 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][13]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "13_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(13), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster14( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster14"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 14 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][14]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME - 10, 0, NEXT_CONTENT )		# boss刷新前10秒时，刷出一个传送光效
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "14_%i_%i"%(STEP_1_TIME,int(time.time())))
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			for e in spaceEntity._players:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(9), [] )
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE14, [] )
		else:
			for e in spaceEntity._players:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(9), [] )
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster15( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster15"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 15 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][15]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "15_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(15), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster16( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster16"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 16 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][16]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "16_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(16), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster17( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster17"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 17 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][17]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "17_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(17), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster18( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster18"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 18 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][18]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "18_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(18), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnMonster19( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster19"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			spaceEntity.addTimer( 0, 0, NEXT_CONTENT )
			return
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "step" : 19 } )
		difficulty = spaceEntity.params[ "difficulty" ]
		STEP_1_TIME = yayuMonster[difficulty][19]["step_time"]
		spaceEntity.addTimer( STEP_1_TIME - 10, 0, NEXT_CONTENT )		# boss刷新前10秒时，刷出一个传送光效
		spaceEntity.addTimer( STEP_1_TIME, 0, NEXT_CONTENT )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "19_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE7%int(19), [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE14, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY or spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			return True
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class CCSpawnGuangXiao( CopyContent ):
	"""
	#刷新一个传送光效（制造假象，以为boss从这里刷出来）
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spawnGuangXiao"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			spaceEntity.base.spawnGuangXiao( {"level" : spaceEntity.params["copyLevel"], "step" : 10 } )
			spaceEntity.addTimer( 10, 0, NEXT_CONTENT )
			#BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "10_%i_%i"%(0,int(time.time())))
		elif spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			spaceEntity.base.spawnGuangXiao( {"level" : spaceEntity.params["copyLevel"], "step" : 15 } )
			spaceEntity.addTimer( 10, 0, NEXT_CONTENT )
			#BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "15_%i_%i"%(0,int(time.time())))
		elif spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_NIGHTMARE:
			spaceEntity.base.spawnGuangXiao( {"level" : spaceEntity.params["copyLevel"], "step" : 20 } )
			spaceEntity.addTimer( 10, 0, NEXT_CONTENT )
			#BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "20_%i_%i"%(0,int(time.time())))

		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE16, [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE17, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )
		return True

class CCSpawnBoss( CopyContent ):
	"""
	#刷新BOSS
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanBoss"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_EASY:
			spaceEntity.base.spawnBoss( {"level" : spaceEntity.params["copyLevel"], "step" : 11 } )
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "11_%i_%i_%i"%(0,int(time.time()),0))
		elif spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
			spaceEntity.base.spawnBoss( {"level" : spaceEntity.params["copyLevel"], "step" : 16 } )
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "16_%i_%i_%i"%(0,int(time.time()),1))
		elif spaceEntity.params[ "difficulty" ] == csconst.SPACE_COPY_YE_WAI_NIGHTMARE:
			spaceEntity.base.spawnBoss( {"level" : spaceEntity.params["copyLevel"], "step" : 21 } )
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "21_%i_%i_%i"%(0,int(time.time()),2))

		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE16, [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE17, [] )



	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] in [0,1]:
			count = spaceEntity.queryTemp("littleMonsterDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( spaceEntity.params[ "difficulty" ] ) - count )
			spaceEntity.setTemp("littleMonsterDiedCount", count )

		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] == 2:
			count = spaceEntity.queryTemp("bossDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, NUMBER_OF_YAYU_BOSS - count )
			spaceEntity.setTemp("bossDiedCount", count )


		if spaceEntity.queryTemp("littleMonsterDiedCount", 0 ) == getMonsterCount( spaceEntity.params[ "difficulty" ] ) and spaceEntity.queryTemp("bossDiedCount", 0 ) == 1:
			return True

		return False





class CCSuccess( CopyContent ):
	"""
	#成功拯救
	"""
	def __init__( self ):
		"""
		"""
		self.key = "success"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		#猰貐跳舞
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE4, [] )
		spaceEntity.addTimer( 60.0, 0, NEXT_CONTENT )
		self.createDoor( spaceEntity )
		yayu = BigWorld.entities.get( spaceEntity.queryTemp("yayuID", 0), None )
		if yayu is not None:
			yayu.onKillAllMonster()

	def createDoor( self, spaceEntity ):
		"""
		创建Door
		"""
		doordict = {"name" : cschannel_msgs.YA_YU_VOICE5}
		doordict["radius"] = 2.0
		doordict["destSpace"] = spaceEntity.params["spaceLabel"]
		doordict["destPosition"] = spaceEntity.params["position"]
		doordict["destDirection"] = ( 0, 0, 0 )
		doordict["modelNumber"] = "gw7504"
		doordict["modelScale"] = 25
		BigWorld.createEntity( "SpaceDoor", spaceEntity.spaceID, (13.308, 48.693, 120.754), (0, 0, 0), doordict )


	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class SpaceCopyYayu( SpaceCopyTeamTemplate ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeamTemplate.__init__( self )
		self.recordKey = "yayu_record"


	def initContent( self ):
		"""
		"""
		self.contents.append( CCWait() )
		self.contents.append( CCSpawnYayu() )
		self.contents.append( CCTalkToYayu() )
		self.contents.append( CCSpawnMonster1() )
		self.contents.append( CCSpawnMonster2() )
		self.contents.append( CCSpawnMonster3() )
		self.contents.append( CCSpawnMonster4() )
		self.contents.append( CCSpawnMonster5() )
		self.contents.append( CCSpawnMonster6() )
		self.contents.append( CCSpawnMonster7() )
		self.contents.append( CCSpawnMonster8() )
		self.contents.append( CCSpawnMonster9() )
		self.contents.append( CCSpawnMonster10() )
		self.contents.append( CCSpawnMonster11() )
		self.contents.append( CCSpawnMonster12() )
		self.contents.append( CCSpawnMonster13() )
		self.contents.append( CCSpawnMonster14() )
		self.contents.append( CCSpawnMonster15() )
		self.contents.append( CCSpawnMonster16() )
		self.contents.append( CCSpawnMonster17() )
		self.contents.append( CCSpawnMonster18() )
		self.contents.append( CCSpawnMonster19() )
		self.contents.append( CCSpawnGuangXiao() )
		self.contents.append( CCSpawnBoss() )
		self.contents.append( CCSuccess() )
		#self.contents.append( CCOutDoor() )
		self.contents.append( CCEndWait() )
		self.contents.append( CCKickPlayersProcess() )


	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		pass


	def packedDomainData( self, player ):
		"""
		"""
		captain = player.getTeamCaptain()
		data = {"copyLevel"			: 	captain.level if captain else 0,
				"dbID" 				: 	player.databaseID,
				"teamID" 			: 	player.teamMailbox.id,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceLabel"		:	BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ),
				"position"			:	player.position,
				"difficulty"		:	player.popTemp( "EnterSpaceCopyYayuType" ),
				"spaceKey"			:	player.teamMailbox.id,
				}
		return data

	def onStartContent( self, selfEntity, baseMailbox, params ):
		"""
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, "" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, getMonsterCount( selfEntity.params[ "difficulty" ] ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_YAYU_HP_PRECENT, 100 )

		selfEntity.setTemp("littleMonsterDiedCount", 0 )
		selfEntity.setTemp("bossDiedCount", 0 )

		SpaceCopyTeamTemplate.onStartContent( self, selfEntity, baseMailbox, params )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_ZHENG_JIU_YA_YU, self.recordKey )

		SpaceCopyTeamTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )

	def onYayuDie( self, selfEntity ):
		"""
		"""
		selfEntity.addTimer( 10.0, 0, YAYU_DIED )
		for e in selfEntity._players:						#通知玩家猰貐死亡了
			if BigWorld.entities.has_key( e.id ):
				e.client.onStatusMessage( csstatus.TASK_FAIL_FOR_YAYU_DIE, "" )

	def onYayuHPChange( self, selfEntity, hp, hp_Max ):
		"""
		"""
		percent = int(hp*1.0/ hp_Max*100)
		if  int( BigWorld.getSpaceDataFirstForKey( selfEntity.spaceID, csconst.SPACE_SPACEDATA_YAYU_HP_PRECENT ) ) == percent:
			return
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_YAYU_HP_PRECENT, int(hp*1.0/ hp_Max*100) )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == YAYU_DIED:
			for e in selfEntity._players:
				if BigWorld.entities.has_key( e.id ):
					BigWorld.entities[ e.id ].gotoForetime()
				else:
					e.cell.gotoForetime()
			return
		SpaceCopyTeamTemplate.onTimer( self, selfEntity, id, userArg )