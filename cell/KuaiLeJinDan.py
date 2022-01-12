# -*- coding: gb18030 -*-
#
# 快乐金蛋活动

from bwdebug import *
import csdefine
import csconst
import Language
import csstatus
import time
import sys

SKILL_ID = 780004001				# 砸蛋完毕，给角色一个buff
SUPER_KLJD_ITEM = 10101002			# 快乐金蛋超级大奖，必须有这个物品

class KuaiLeJinDan():
	"""
	快乐金蛋活动
	"""
	_instance = None

	def __init__( self ):
		assert KuaiLeJinDan._instance is None, "KuaiLeJinDan instance already exist in"
		KuaiLeJinDan._instance = self
		self.restrictLevel = 0
		self.g_rewards = None		# 因为服务器初始化时不能直接import Love3的g_rewards，所以改为使用时import

	@staticmethod
	def instance():
		if KuaiLeJinDan._instance is None:
			KuaiLeJinDan._instance = KuaiLeJinDan()
		return KuaiLeJinDan._instance

	def load( self, xmlPath = "" ):
		"""
		加载xml文件配置
		"""
		section = Language.openConfigSection( xmlPath )
		assert section is not None,"open file( path:%s ) error:not exist!" % xmlPath

		self.restrictLevel = section.readInt( "restrictLevel" )
		self.restrictTime = section.readInt( "restrictTime" )

	def startKLJDActivity( self, player ):
		"""
		活动开始--打开砸蛋界面
		"""
		if player.level < self.restrictLevel:
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_LEVEL, self.restrictLevel )
			return
		if not player.kuaiLeJinDanDailyRecord.checklastTime():				# 判断是否同一天
			player.kuaiLeJinDanFlag = False									# 重置标记是否已经砸蛋为false
		if player.kuaiLeJinDanFlag:
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_FLAG )
			return
		if player.wallow_isEffected() and player.antiIndulgenceRec.onlineCount < 60:	# 必须在线一小时以上(必须开启防沉迷，才会开始计时)
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_ONLINE )
			return

		player.client.startKLJDActivity()	# 通知客户端打开砸蛋界面

	def doKLJDActivity( self, player ):
		"""
		砸蛋中
		"""
		if player.level < self.restrictLevel:
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_LEVEL )
			return

		if not player.kuaiLeJinDanDailyRecord.checklastTime():				# 判断是否同一天
			player.kuaiLeJinDanFlag = False									# 重置标记是否已经砸蛋为false
			player.kuaiLeJinDanDailyRecord.reset()							# 重置记录数据
		if player.kuaiLeJinDanFlag:
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_FLAG )
			return
		if player.kuaiLeJinDanDailyRecord.getDegree() >= self.restrictTime:		# 判断砸蛋次数
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_TIME )
			return

		if player.wallow_isEffected() and player.antiIndulgenceRec.onlineCount < 60:	# 必须在线一小时以上(必须开启防沉迷，才会开始计时)
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_ONLINE )
			return

		self.doKLJDReward( player )		# 砸蛋奖励

	def doKLJDReward( self, player ):
		"""
		砸蛋奖励
		"""
		if self.g_rewards is None:
			from Love3 import g_rewards
			self.g_rewards = g_rewards
		awarder = self.g_rewards.fetch( csdefine.RCG_HAPPY_GODEN_EGG, player )
		if len( awarder.items ) <= 0:
			player.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		item = awarder.items[0]		# 该活动只会奖励一个东西一次，理论上长度是1，再来就是配置问题了 by 姜毅
		item.set( "level", player.level )

		if item.id == SUPER_KLJD_ITEM:		# 如果奖励是超级大奖的抽奖机会
			today = self.getToday()
			item.set( "createTime", today )
		elif item.id == 10101001:			# 如果奖励是经验物品
			item.set( "rewardExp", pow( player.level, 1.6 )*60 )

		if not player.checkItemsPlaceIntoNK_( awarder.items ) == csdefine.KITBAG_CAN_HOLD:
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return
		awarder.award( player, csdefine.ADD_ITEM_DOKLJDREWARD )
		
		player.kuaiLeJinDanFlag = True					# 标记已经砸过蛋了
		player.client.endKLJDReward()					# 可能客户端需要奖励的数据
		player.kuaiLeJinDanDailyRecord.incrDegree()		# 砸蛋次数加1
		if player.kuaiLeJinDanDailyRecord.getDegree() == 3:		# 如果角色已经砸蛋三次(可能不用这种方式处理)
			player.spellTarget( SKILL_ID, player.id )


	def startSuperKLJDActivity( self, player ):
		"""
		超级大奖--心态要好
		"""
		player.client.startSuperKLJDActivity()	# 通知客户端打开砸蛋界面

	def validStartSuperKLJDActivity( self, player ):
		"""
		超级大奖，是否满足条件
		"""
		item = player.findItemFromNKCK_( SUPER_KLJD_ITEM )		# 取得角色身上超级大奖参加，必须携带的物品
		if not item:return False
		return self.checkTodayTime( item.query( "createTime" ) )

	def doSuperKLJDActivity( self, player ):
		"""
		超级砸蛋奖励
		"""
		items = player.findItemsFromNKCK_( SUPER_KLJD_ITEM )		# 取得角色身上超级大奖参加，必须携带的物品
		if len( items ) <= 0:
			HACK_MSG( "找不到参加超级大奖的物品" )
			return
		sorce_item = None
		for item in items:
			if self.checkTodayTime( item.query( "createTime" ) ):
				sorce_item = item
				break
		if sorce_item is None:
			HACK_MSG( "参加超级大奖的物品不是当天产生的，没有用了" )
			return
		if self.g_rewards is None:
			from Love3 import g_rewards
			self.g_rewards = g_rewards
		awarder = self.g_rewards.fetch( csdefine.RCG_SUPER_HAPPY_GODEN_EGG, player )
		if len( awarder.items ) <= 0:
			player.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		rewardItem = awarder.items[0]		# 该活动只会奖励一个东西一次，理论上长度是1，再来就是配置问题了 by 姜毅
		rewardItem.set( "level", player.level )
		if not player.checkItemsPlaceIntoNK_( awarder.items ) == csdefine.KITBAG_CAN_HOLD:
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return
		player.removeItem_( sorce_item.order, 1, csdefine.DELETE_ITEM_SUPERKLJDACTIVITY )
		awarder.award( player, csdefine.ADD_ITEM_DOSUPERKLJDACTIVITY )

	def getToday( self ):
		"""
		开始时间为今天
		"""
		year, month, day = time.localtime()[:3]
		lastTime = year * 10000 + month * 100 + day
		return lastTime

	def checkTodayTime( self, today ):
		"""
		检查接任务时间与当前时间是否是同一天
		@return: bool
		"""
		year, month, day = time.localtime()[:3]
		curr = year * 10000 + month * 100 + day
		return curr == today

	def doKLJDExpReward( self, player ):
		"""
		快乐金蛋，获取经验奖励
		"""
		item = player.findItemFromNKCK_( 10101001 )		# 快乐金蛋，获取经验奖励，必须有奖励的物品
		if not item:
			HACK_MSG( "找不到快乐金蛋经验奖励物品" )
			return
		player.addExp( int( item.query( "rewardExp" ) ), csdefine.CHANGE_EXP_KLJDEXPREWARD )
		player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_KLJDEXPREWARD )

	def validDoKLJDExpReward( self, player ):
		"""
		快乐金蛋，获取经验奖励的valid
		"""
		item = player.findItemFromNKCK_( 10101001 )		# 快乐金蛋，获取经验奖励，必须有奖励的物品
		if not item:
			return False
		return True

	def doKLJDZuoQiReward( self, player ):
		"""
		快乐金蛋，获取坐骑奖励
		"""
		id_list = [ 10101001, 10101002, 10101003, 10101004 ]
		items = player.findItemsByIDsFromNKCK( id_list )
		for item in items:
			if item.id in id_list:
				id_list.remove( item.id )
		if len( id_list ) > 0:
			HACK_MSG( "找不到快乐金蛋坐骑奖励物品" )		# 快乐金蛋，获取经验奖励，必须有奖励的物品
			return
		if self.g_rewards is None:
			from Love3 import g_rewards
			self.g_rewards = g_rewards
		awarder = self.g_rewards.fetch( csdefine.RCG_HAPPY_GODEN_EGG_V, player )
		if len( awarder.items ) <= 0:		# 该活动只会奖励一个东西一次，理论上长度是1，再来就是配置问题了 by 姜毅
			player.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		if not player.checkItemsPlaceIntoNK_( awarder.items ) == csdefine.KITBAG_CAN_HOLD:
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return
		for item in items:
			if item.id in id_list:
				continue
			id_list.append( item.id )
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_KLJDZUOQIREWARD )
			
		awarder.award( player, csdefine.ADD_ITEM_DOKLJDZUOQIREWARD )


	def validDoKLJDZuoQiReward( self, player ):
		"""
		快乐金蛋，获取坐骑奖励的valid
		"""
		id_list = [ 10101001, 10101002, 10101003, 10101004 ]
		items = player.findItemsByIDsFromNKCK( id_list )
		for item in items:
			if item.id in id_list:
				id_list.remove( item.id )
		return len( id_list ) <= 0
