# -*- coding: gb18030 -*-
#

#

import BigWorld
from Monster import Monster
from ObjectScripts.GameObjectFactory import g_objFactory
from bwdebug import *
import Pet
import csconst
import cschannel_msgs 
LIU_WANG_MU_ACTIVITY_END  = 1

class LiuWangMuBoss( Monster ):
	def __init__( self ):
		Monster.__init__( self )
		self.playerDamageList = {} #记录所有对boss产生伤害的玩家
		self.playerNameTotongName = {} #{playerName:tongName}

	
	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		接受伤害。
		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skillID: 技能ID
		@type     skillID: INT
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: 伤害数值
		@type      damage: INT
		"""		
		DEBUG_MSG("liuwangmu boss is damaged by %d ,damge count is %d"%(casterID, damage))
		entityID = casterID
		entity = BigWorld.entities.get( entityID, None )
		if not entity: #通过ID不能获取entity
			return
		if entity.__class__.__name__ == "Role":
			player = entity
		elif entity.__class__.__name__ == "Pet":
			entityID = entity.ownerID
			player = BigWorld.entities.get( entityID, None )
			if not player:#通过ID不能获取playerentity
				return
		else:
			return	
		playerName = player.playerName
		tongName = player.tongName  #如果没有则为空
		if tongName:#有帮会的才记录
			self.playerNameTotongName[ playerName ] = tongName
		if self.playerDamageList.has_key( playerName ):			
			self.playerDamageList[ playerName ] += damage
		else:
			self.playerDamageList[ playerName ] = damage
		#下面的处理只能放在后面，主要是为了避免最后一击时，boss死了，获得的数据不完整，出现新问题。	
		Monster.receiveDamage( self, casterID, skillID, damageType, damage )
		
						
	def getTongDamageList(self):
		"""
		在用到的地方统计帮会对boss伤害
		"""
		tongDamageList = {}
		for key,value in self.playerDamageList.items():
			if self.playerNameTotongName.has_key(key): #有帮会
				tongName = self.playerNameTotongName[key]
				if tongDamageList.has_key(tongName):
					tongDamageList[ tongName ] += value
				else :
					tongDamageList[ tongName ] = value
		return tongDamageList
				
	def getMaxDamagePlayerName(self):
		"""
		return maxDamagePlayer's name
		"""
		if self.getAllDamagePlayersName():
			DEBUG_MSG("liuwangmu boss getMaxDamagePlayerName is %s"%self.getMaxDamagePlayers(1)[0][0])
			return self.getMaxDamagePlayers(1)[0][0]
		else:
			return None

	def getAllDamagePlayersName(self):
		"""
		return allDamagePlayers' name
		"""
		DEBUG_MSG("all players hit liuwangmu boss are %s "%([ name for [name,damage] in self.getMaxDamagePlayers(0)]))
		return [ name for [name,damage] in self.getMaxDamagePlayers(0)]
	
	def getMaxDamageTongName(self):
		"""
		return maxDamageTong's name
		"""	
		if self.getMaxDamageTongs(1):	
			DEBUG_MSG("liuwangmu getMaxDamageTongName is %s"%self.getMaxDamageTongs(1)[0][0])
			return self.getMaxDamageTongs(1)[0][0]
		else:
			return None
	
	def getAllDamageTongsName(self):
		"""
		return allDamageTongss' name
		"""
		DEBUG_MSG("all tongs hit liuwangmu boss are %s "%([ name for [name,damage] in self.getMaxDamageTongs(0)]))
		return [ name for [name,damage] in self.getMaxDamageTongs(0)]

	def getMaxDamageInfos(self, topNumber, damageList):
		"""
		param : topNumber 伤害最高的的topNumber人
		return 伤害最高的的topNumber人的信息[[palyerName, damages],]
		"""
		infos = sorted( damageList.items(), key=lambda d: d[1], reverse = True )
		if topNumber == 0 : #返回所有人的伤害列表
			return infos
					
		if len(infos) >= topNumber:	
			return infos[:topNumber]
		
		return infos		
		
	def getMaxDamagePlayers(self, topNumber):
		"""
		param : topNumber 伤害最高的的topNumber人
		return 伤害最高的的topNumber人的信息[[palyerName, damages],]
		"""
		return self.getMaxDamageInfos(topNumber, self.playerDamageList)
			
	def getMaxDamageTongs(self, topNumber):
		"""
		param : topNumber 伤害最高的的topNumber人
		return 伤害最高的的topNumber人的信息[[tongName, damages],]
		"""	
		return self.getMaxDamageInfos(topNumber, self.getTongDamageList())

	def sendReward(self, type):
		"""
		param type:区分boss杀死与未杀死的奖励 1为杀死，0 为未杀死
		"""
		msg = [self.getMaxDamagePlayers(10), self.getMaxDamageTongs(3), self.playerNameTotongName]
		BigWorld.globalData["LiuWangMuMgr"].sendReward(type, self.getAllDamagePlayersName(), self.getAllDamageTongsName(), msg)
		INFO_MSG("BigWorld.globalData[LiuWangMuMgr].sendReward reward is %s"%msg)
	
	def onActivityClosed(self):
		INFO_MSG("LIU_WANG_MU_ACTIVITY_END boss'className is %s"%self.className)
		if self.playerDamageList:#有人对boss造成伤害才显示排行榜
			#self.RankList()在LiuWangMuMgr中处理中处理显示排行榜
			self.sendReward(0) #发放boss未被击杀奖励
			BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.LIUWANGMU_BOSS_GOAWAY %self.uname,[])
			BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.BCT_LIUWANGMU_MAX_DAMAGE_PLAYER %self.getMaxDamagePlayerName(),[])
			if self.getMaxDamageTongName():#如果有帮会才显示
				BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.BCT_LIUWANGMU_MAX_DAMAGE_TONG %self.getMaxDamageTongName(),[])		
			self.playerDamageList = {}
		self.destroy()