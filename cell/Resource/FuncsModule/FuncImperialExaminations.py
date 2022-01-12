# -*- coding: gb18030 -*-
#
# $Id: FuncWarehouse.py,v 1.12 2008-01-15 06:06:34 phw Exp $

"""
"""
from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from Function import Function
from Resource.QuestLoader import QuestsFlyweight
import csdefine
import csstatus
import ECBExtend
import BigWorld
import time
import items

g_items = items.instance()
g_taskData = QuestsFlyweight.instance()

TITLE_ID_XIUCAI		= 30	# 秀才称号id
TITLE_ID_JUREN		= 31	# 举人称号id


class FuncImperialExaminations( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.exaCount = section.readInt( 'param1' )

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
		talkEntity.remoteScriptCall( "startExamination", ( player, self.exaCount ) )


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
		return self.exaCount == player.getCurrentExaID() + 1


class FuncImperialExamCheck( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.exaCount = section.readInt( "param1" )	# 第几题
		self.key1 = section.readString( "param2" )	# 考官正确
		self.key2 = section.readString( "param3" )	# 没有接科举任务
		self.key3 = section.readString( "param4" )	# 考官不正确
		self.key4 = section.readString( "param5" )	# 没有在考试时间内

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		pass


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
		if talkEntity is None:
			return False

		questStateXiangshi = g_taskData[30701001].query( player )
		questStateHuishi = g_taskData[30701002].query( player )

		if ( questStateHuishi == csdefine.QUEST_STATE_NOT_ALLOW or questStateHuishi == csdefine.QUEST_STATE_NOT_HAVE ) and \
			( questStateXiangshi == csdefine.QUEST_STATE_NOT_ALLOW or questStateXiangshi == csdefine.QUEST_STATE_NOT_HAVE ):
			# 既没接会试任务也没接乡试任务
			dlgKey = self.key2
		elif ( questStateXiangshi == csdefine.QUEST_STATE_NOT_ALLOW or questStateXiangshi == csdefine.QUEST_STATE_NOT_HAVE ):
			# 没有接乡试任务，但是身上有会试任务
			if not BigWorld.globalData.has_key( "AS_HuishiActivityStart" ):
				dlgKey = self.key4
			elif player.getCurrentExaID()+1 != self.exaCount:
				dlgKey = self.key3
			elif questStateHuishi == csdefine.QUEST_STATE_NOT_FINISH:
				dlgKey = self.key1
			else:
				dlgKey = self.key3
		else:
			# 有乡试任务
			if not BigWorld.globalData.has_key( "AS_XiangshiActivityStart" ):
				dlgKey = self.key4
			elif player.getCurrentExaID()+1 != self.exaCount:
				dlgKey = self.key3
			elif questStateXiangshi == csdefine.QUEST_STATE_NOT_FINISH:
				dlgKey = self.key1
			else:
				dlgKey = self.key3

		player.endGossip( talkEntity )
		player.setTemp( "talkNPCID", talkEntity.id )
		player.setTemp( "talkID", dlgKey )
		player.addTimer( 0.3, 0, ECBExtend.AUTO_TALK_CBID )
		return False


class FuncImperialXHSignUpCheck( Function ):
	"""
	乡试、会试报名对话检查
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.key1 = section.readInt( "param1" )	# 乡试任务id
		self.key2 = section.readInt( "param2" )	# 会试任务id

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		pass


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
		if talkEntity is None:
			return False

		player.endGossip( talkEntity )
		questStateXiangshi = g_taskData[self.key1].query( player )	# 乡试状态
		questStateHuishi = g_taskData[self.key2].query( player )	# 会试状态
		if BigWorld.globalData.has_key( "AS_XiangshiActivityStart" ):
			# 乡试处理
			if questStateXiangshi == csdefine.QUEST_STATE_NOT_ALLOW:
				# 不能参加乡试考试
				lpLog = player.getLoopQuestLog( self.key1, True )
				if lpLog.getDegree() >= player.getQuest( self.key1 )._finish_count:
					# 今天已经完成了乡试了
					dataQuestID = str(time.localtime()[2])+':' + str( self.key1 )
					if dataQuestID in player.failedGroupQuestList:
						player.setGossipText( cschannel_msgs.KE_JU_VOICE_1 )
					else:
						player.setGossipText( cschannel_msgs.KE_JU_VOICE_2 )
				else:
					# 不满足参加乡试的条件
					player.setGossipText( cschannel_msgs.KE_JU_VOICE_3 )
				return False
			if questStateXiangshi == csdefine.QUEST_STATE_NOT_FINISH:
				# 正在参加乡试考试
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_4 )
				return False
			if questStateXiangshi != csdefine.QUEST_STATE_NOT_HAVE_LEVEL_SUIT:
				# 可以参加乡试考试，可以接任务，那么没有对话
				return False
			else:
				# 其他情况
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_1 )
				return False
		elif BigWorld.globalData.has_key( "AS_HuishiActivityStart" ):
			# 会试处理
			if not player.hasTitle( TITLE_ID_XIUCAI ):
				# 如果玩家不是秀才，不允许参加会试
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_5 )
				return False
			if questStateHuishi == csdefine.QUEST_STATE_NOT_ALLOW:
				# 不能参加会试考试
				lpLog = player.getLoopQuestLog( self.key2, True )
				if lpLog.getDegree() >= player.getQuest( self.key2 )._finish_count:
					dataQuestID = str(time.localtime()[2])+':' + str( self.key2 )
					# 今天已经完成了会试了
					if dataQuestID in player.failedGroupQuestList:
						player.setGossipText( cschannel_msgs.KE_JU_VOICE_6 )
					else:
						msg = cschannel_msgs.KE_JU_VOICE_7
						player.setGossipText( msg )
				else:
					# 不满足参加会试的条件
					player.setGossipText( cschannel_msgs.KE_JU_VOICE_5 )
				return False
			if questStateHuishi == csdefine.QUEST_STATE_NOT_FINISH:
				# 正在参加会试考试
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_4 )
				return False
			if questStateHuishi != csdefine.QUEST_STATE_NOT_HAVE_LEVEL_SUIT:
				# 可以参加会试考试，可以接任务，那么没有对话
				return False
			else:
				# 其他情况
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_6 )
				return False
		else:
			# 乡试没开始，会试也没开始
			player.setGossipText( cschannel_msgs.KE_JU_VOICE_8 )
			return False

class FuncImperialDSignUpCheck( Function ):
	"""
	殿试报名对话检查
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.key1 = section.readString( "param1" )
		self.key2 = section.readString( "param2" )
		self.key3 = section.readString( "param3" )
		self.key4 = section.readString( "param4" )
		self.key5 = section.readInt( "param5" )	# 任务id

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		pass


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
		if talkEntity is None:
			return False

		keydlg = ""
		questState = g_taskData[self.key5].query( player )
		questDegree = player.getLoopQuestLog( self.key5, True ).getDegree()
		if not BigWorld.globalData.has_key( "AS_DianshiActivityStart" ) and questDegree <= 0:
			# 殿试报名还没开始
			keydlg = self.key1
		elif questState == csdefine.QUEST_STATE_NOT_ALLOW and questDegree <= 0:
			# 不满足殿试报名条件
			keydlg = self.key2
		elif questState == csdefine.QUEST_STATE_COMPLETE and questDegree > 0:
			# 殿试考试已经完成了
			keydlg = self.key3
		elif questState != csdefine.QUEST_STATE_NOT_HAVE and questState != csdefine.QUEST_STATE_FINISH and \
			BigWorld.globalData.has_key( "AS_DianshiActivityStart" ) and player.queryTemp( "imperial_exam_start_time", 0 ) != 0:
			# 正在进行科举考试
			keydlg = self.key4
		elif questDegree >= 1 and not BigWorld.globalData.has_key( "AS_DianshiActivityStart" ) and \
			BigWorld.globalData.has_key( "IE_DianShi_Reward_DBID_List" ) \
			and player.databaseID in BigWorld.globalData[ "IE_DianShi_Reward_DBID_List" ]:
			# 考试已经结束了，并且可以领取奖励,而且显示领取奖励选项
			player.setGossipText( cschannel_msgs.KE_JU_VOICE_9 )
			return False
		elif BigWorld.globalData.has_key( "AS_DianshiActivityStart" ):
			# 玩家已经完成了考试，但是殿试并没有结束，不显示领取奖励选项
			player.setGossipText( cschannel_msgs.KE_JU_VOICE_10 )
			return False
		else:
			# 其他情况
			player.setGossipText( cschannel_msgs.KE_JU_VOICE_9 )
			return False
		player.endGossip( talkEntity )
		player.setTemp( "talkNPCID", talkEntity.id )
		player.setTemp( "talkID", self.key4 )
		if keydlg != "":
			player.setTemp( "talkID", keydlg )
			player.addTimer( 0.5, 0, ECBExtend.AUTO_TALK_CBID )
		return False


class FuncImperialHuiShiBuKao( Function ):
	"""
	科举会试补考
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.key1 = section.readString( "param1" )
		self.questID = section.readInt( "param2" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			return
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.endGossip( talkEntity )
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return

		payMoney = int( player.level ** 2 * 10 )	# 注意：这个公式，QuestImperialExamination里也用到，如果做改动，两个必须要一致。
		moneyStr = self.convertPrice( payMoney )	# 这里只检查玩家钱够不够，但是不会扣除玩家的钱，在任务的accept里做的扣除。
		lpLog = player.getLoopQuestLog( self.questID, True )

		if lpLog.getDegree() >= 4:
			player.setGossipText( cschannel_msgs.KE_JU_VOICE_11 )
			player.sendGossipComplete( talkEntity.id )
			return

		if player.money < payMoney:
			player.setGossipText( cschannel_msgs.KE_JU_VOICE_12 % moneyStr )
			player.sendGossipComplete( talkEntity.id )
			return

		#player.getQuest( self.questID ).accept( player )
		msgStr = cschannel_msgs.KE_JU_VOICE_13 % moneyStr
		player.client.acceptQuestConfirm( self.questID, msgStr )
		player.endGossip( talkEntity )
		return

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
		if talkEntity is None:
			return False
		questStateHuishi = g_taskData[self.questID].query( player )	# 会试状态
		valid1 = BigWorld.globalData.has_key( "AS_HuishiActivityStart" )
		valid2 = ( questStateHuishi != csdefine.QUEST_STATE_NOT_FINISH and questStateHuishi != csdefine.QUEST_STATE_FINISH )
		valid3 = pLog = player.getLoopQuestLog( self.questID, True ).getDegree() > 0
		return valid1 and valid2 and valid3

	def convertPrice( self, price ):
		"""
		转换价格，把诸如“10102”形式的价格转换成“1金1银2铜”
		"""
		gold = price / 10000
		silver = price / 100 - gold * 100
		coin = price - gold * 10000 - silver * 100
		goldStr = ""
		silverStr = ""
		coinStr	= ""
		if gold != 0:
			goldStr = str( gold ) + cschannel_msgs.LOOP_QUEST_INFO_1
		if silver != 0:
			silverStr = str( silver ) + cschannel_msgs.LOOP_QUEST_INFO_2
		if coin != 0:
			coinStr = str( coin ) + cschannel_msgs.LOOP_QUEST_INFO_3

		return goldStr + silverStr + coinStr


class FuncFetchIEReward( Function ):
	"""
	领取科举奖励(会试、殿试)
	目前为称号奖励，如有扩展以后再加
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.ieType = section.readInt( "param1" )			# 科举类型 4为会试、5为殿试
		self.zhuangyuanItemID = section.readInt( "param2" )	# 状元的额外奖励(物品)

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			return
		isItemsBagFull = False
		if player.getNormalKitbagFreeOrderCount() < 1:
			isItemsBagFull = True
		BigWorld.globalData["ImperialExaminationsMgr"].requestIETitleReward( player.base, player.databaseID, player.getName(), self.ieType, self.zhuangyuanItemID, isItemsBagFull )
		player.endGossip( talkEntity )
		return

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
		if talkEntity is None:
			return False

		if self.ieType == 4:
			# 科举会试
			return ( BigWorld.globalData.has_key( "IE_HuiShi_Reward_DBID_List" ) \
			and player.databaseID in BigWorld.globalData[ "IE_HuiShi_Reward_DBID_List" ] \
			and not BigWorld.globalData.has_key( "AS_HuishiActivityStart" ) )
		elif self.ieType == 5:
			# 科举殿试
			return ( BigWorld.globalData.has_key( "IE_DianShi_Reward_DBID_List" ) \
			and player.databaseID in BigWorld.globalData[ "IE_DianShi_Reward_DBID_List" ] \
			and not BigWorld.globalData.has_key( "AS_DianshiActivityStart" ) )
		return False