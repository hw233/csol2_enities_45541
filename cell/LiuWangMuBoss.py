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
		self.playerDamageList = {} #��¼���ж�boss�����˺������
		self.playerNameTotongName = {} #{playerName:tongName}

	
	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		�����˺���
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skillID: ����ID
		@type     skillID: INT
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""		
		DEBUG_MSG("liuwangmu boss is damaged by %d ,damge count is %d"%(casterID, damage))
		entityID = casterID
		entity = BigWorld.entities.get( entityID, None )
		if not entity: #ͨ��ID���ܻ�ȡentity
			return
		if entity.__class__.__name__ == "Role":
			player = entity
		elif entity.__class__.__name__ == "Pet":
			entityID = entity.ownerID
			player = BigWorld.entities.get( entityID, None )
			if not player:#ͨ��ID���ܻ�ȡplayerentity
				return
		else:
			return	
		playerName = player.playerName
		tongName = player.tongName  #���û����Ϊ��
		if tongName:#�а��Ĳż�¼
			self.playerNameTotongName[ playerName ] = tongName
		if self.playerDamageList.has_key( playerName ):			
			self.playerDamageList[ playerName ] += damage
		else:
			self.playerDamageList[ playerName ] = damage
		#����Ĵ���ֻ�ܷ��ں��棬��Ҫ��Ϊ�˱������һ��ʱ��boss���ˣ���õ����ݲ����������������⡣	
		Monster.receiveDamage( self, casterID, skillID, damageType, damage )
		
						
	def getTongDamageList(self):
		"""
		���õ��ĵط�ͳ�ư���boss�˺�
		"""
		tongDamageList = {}
		for key,value in self.playerDamageList.items():
			if self.playerNameTotongName.has_key(key): #�а��
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
		param : topNumber �˺���ߵĵ�topNumber��
		return �˺���ߵĵ�topNumber�˵���Ϣ[[palyerName, damages],]
		"""
		infos = sorted( damageList.items(), key=lambda d: d[1], reverse = True )
		if topNumber == 0 : #���������˵��˺��б�
			return infos
					
		if len(infos) >= topNumber:	
			return infos[:topNumber]
		
		return infos		
		
	def getMaxDamagePlayers(self, topNumber):
		"""
		param : topNumber �˺���ߵĵ�topNumber��
		return �˺���ߵĵ�topNumber�˵���Ϣ[[palyerName, damages],]
		"""
		return self.getMaxDamageInfos(topNumber, self.playerDamageList)
			
	def getMaxDamageTongs(self, topNumber):
		"""
		param : topNumber �˺���ߵĵ�topNumber��
		return �˺���ߵĵ�topNumber�˵���Ϣ[[tongName, damages],]
		"""	
		return self.getMaxDamageInfos(topNumber, self.getTongDamageList())

	def sendReward(self, type):
		"""
		param type:����bossɱ����δɱ���Ľ��� 1Ϊɱ����0 Ϊδɱ��
		"""
		msg = [self.getMaxDamagePlayers(10), self.getMaxDamageTongs(3), self.playerNameTotongName]
		BigWorld.globalData["LiuWangMuMgr"].sendReward(type, self.getAllDamagePlayersName(), self.getAllDamageTongsName(), msg)
		INFO_MSG("BigWorld.globalData[LiuWangMuMgr].sendReward reward is %s"%msg)
	
	def onActivityClosed(self):
		INFO_MSG("LIU_WANG_MU_ACTIVITY_END boss'className is %s"%self.className)
		if self.playerDamageList:#���˶�boss����˺�����ʾ���а�
			#self.RankList()��LiuWangMuMgr�д����д�����ʾ���а�
			self.sendReward(0) #����bossδ����ɱ����
			BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.LIUWANGMU_BOSS_GOAWAY %self.uname,[])
			BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.BCT_LIUWANGMU_MAX_DAMAGE_PLAYER %self.getMaxDamagePlayerName(),[])
			if self.getMaxDamageTongName():#����а�����ʾ
				BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.BCT_LIUWANGMU_MAX_DAMAGE_TONG %self.getMaxDamageTongName(),[])		
			self.playerDamageList = {}
		self.destroy()