# -*- coding: gb18030 -*-
#
# BovineDevil类 2009-05-27 SongPeifang
#

from WXMonster import WXMonster
import cschannel_msgs
import ShareTexts as ST


class BovineDevil( WXMonster ):
	"""
	牛魔王脚本文件
	"""
	def __init__( self ):
		"""
		"""
		WXMonster.__init__( self )
		self.bornNPC = False
		#self.callMonsterID	= "20712014"
		#self.fightingText	= cschannel_msgs.NIU_MO_WANG_VOICE_5
		#self.freeText		= cschannel_msgs.NIU_MO_WANG_VOICE_6
		#self.fightOption	= cschannel_msgs.NIU_MO_WANG_VOICE_1
		#self.leaveOption	= cschannel_msgs.NIU_MO_WANG_VOICE_2
		#self.fightSay		= cschannel_msgs.NIU_MO_WANG_VOICE_3
		#self.dieSay			= cschannel_msgs.NIU_MO_WANG_VOICE_4
		
	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		NPCObject.gossipWith( self, selfEntity, playerEntity, dlgKey )
		
	def getSpawnPos( self, selfEntity ):
		return selfEntity.position
	