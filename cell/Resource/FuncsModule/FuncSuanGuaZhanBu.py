# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
算卦占卜
"""
import time
import cschannel_msgs
import ShareTexts as ST
import random
from Function import Function
import csstatus
import csdefine
from csarithmetic import getRandomElement
from Resource.SuanGuaZhanBuLoader import SuanGuaZhanBuLoader
g_SuanGuaZhanBuLoader = SuanGuaZhanBuLoader.instance()

class FuncSuanGuaZhanBu( Function ):
	"""
	算卦占卜
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )		# 占卜算卦的最低等级
		self._param2 = section.readInt( "param2" )		# 一天占卜次数
		
		"""
		self._param3 = section.readString( "param3" )	# 占卜金钱消耗，配置："30-59,60-89,90-119,120-150;1,2,5,15"
		self._param4 = section.readString( "param4" )	# 占卜技能和机率，配置："ID1:机率1;ID2:机率2"

		self._expendKey = []	# [[30, 59], [60, 89], [90, 119], [120, 150]]
		self._expendValue = []	# [1,2,5,15]
		keyStr = self._param3.split( ";" )[0]
		valStr = self._param3.split( ";" )[1]
		for e in keyStr.split(","):
			self._expendKey.append( [ int(e.split( "-" )[0]), int(e.split( "-" )[1]) ] )
		for e in valStr.split(","):
			self._expendValue.append( int(e) )

		self._skillIDList = []				# 存放技能的ID
		self._skillOddsList = []			# 存放技能ID对应的机率数组
		for e in self._param4.split( ";" ):
			self._skillIDList.append( str( e.split( ":" )[0] ) )
			self._skillOddsList.append( float( e.split( ":" )[1] ) )
		"""

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if player.level < self._param2:		# 是否满足最低等级要求
			player.statusMessage( csstatus.SUAN_GUA_ZHAN_BU_NEED_LEVEL, self._param1 )
			return

		# 将这里的判断增加至Role.selectSuanGuaZhanBu()，用来避免在服务器卡的情况下出现多次祈福的问题
		# 参见CSOL-9799 updated by mushuang
		if not player.suanGuaZhanBuDailyRecord.checklastTime():				# 判断是否同一天
			player.suanGuaZhanBuDailyRecord.reset()
		if player.suanGuaZhanBuDailyRecord.getDegree() >= self._param2:		# 判断次数
			player.statusMessage( csstatus.SUAN_GUA_ZHAN_BU_LIMIT_NUM )
			return

		cost = g_SuanGuaZhanBuLoader.getNeedMoney( player.level )
		if player.money < cost:
			gold = cost / 10000
			silver = cost / 100 - gold * 100
			coin = cost - gold * 10000 - silver * 100
			costText = ""
			if gold : costText += cschannel_msgs.SHI_TU_GIFT_INFO_1%gold
			if silver : costText += cschannel_msgs.SHI_TU_GIFT_INFO_2%silver
			if coin : costText += cschannel_msgs.SHI_TU_GIFT_INFO_3%coin
			player.statusMessage( csstatus.SUAN_GUA_ZHAN_BU_LIMIT_MONEY, costText )
			return

		player.client.askSuanGuaZhanBu( cost )	# 询问是否进行
		
#		player.suanGuaZhanBuDailyRecord.incrDegree()	# 算卦占卜次数加1
#		player.payMoney( self._expendValue[index], csdefine.CHANGE_MONEY_SUANGUAZHANBU )		# 玩家扣除金钱

#		skillID = int( getRandomElement( self._skillIDList, self._skillOddsList ) )		# 根据概率，选取技能ID
#		player.spellTarget( skillID, player.id )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True