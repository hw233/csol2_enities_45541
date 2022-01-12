# -*- coding: gb18030 -*-
#
# $Id: SpaceFace.py,v 1.10 2007-09-24 07:38:39 kebiao Exp $

import time
import BigWorld
import Function
from bwdebug import *
from Function import Functor
import csstatus
import csdefine
import csconst

from MsgLogger import g_logger

TASK_KEY_HOLD_CITY_DATA		= 11		# 处理帮会所控制的城市数据

TONG_CITY_WAR_PRESTIGE_HAS = 200 # 帮会城市战报名所需的帮会声望

class TongCityWarInterface:
	"""
	帮会夺城战的接口
	"""
	def __init__( self ):
		self.isJoinTongCityWar = False
	
	def setHoldCity( self, city, isInit ):
		"""
		define mothod.
		设置帮会控制的城市
		@param city: spaceName
		"""
		self.holdCity = city
		# 通知客户端进行更新
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_HOLD_CITY_DATA ):
				if hasattr( emb, "cell" ):
					emb.cell.tong_onSetHoldCity( self.holdCity, isInit )

		# 将数据更新到管理器
		self.getTongManager().updateTongHoldCity( self.databaseID, self.holdCity )

	def onContestCityWar( self, memberDBID, replevel, repMoney, spaceName ):
		"""
		define mothod.
		某帮主申请城市战争.
		@param replevel: 帮会级别需求
		@param spaceName	: 申请争夺的城市地图名称
		@param repMoney:	在无竞争价下需求最底资金
		"""
		info = self.getMemberInfos( memberDBID )
		mb = info.getBaseMailbox()
		succeeded = True
		if self.level < replevel:
			self.statusMessage( mb, csstatus.TONG_CITY_WAR_LEVEL_INVALID, replevel )
			succeeded = False
		elif self.prestige < TONG_CITY_WAR_PRESTIGE_HAS:
			self.statusMessage( mb, csstatus.TONG_CITY_WAR_PRESTIGE_LESS )
			succeeded = False
		elif self.money - self.getKeepMoney() < repMoney:
			self.statusMessage( mb, csstatus.TONG_CITY_WAR_MONEY_LOW, Function.switchMoney( repMoney ) )
			succeeded = False
		else:
			self.payMoney( repMoney, True, csdefine.TONG_CHANGE_MONEY_SUBMITCONTESTMONEY )
			for dbid in self._onlineMemberDBID:
				member = self.getMemberInfos( dbid ).getBaseMailbox()
				cityName = csconst.TONG_CITYWAR_CITY_MAPS.get( spaceName, spaceName )
				self.statusMessage( member, csstatus.TONG_CITY_WAR_CONTEST_SUCCESS, cityName )
				
		if succeeded:
			self.isJoinTongCityWar = True
			
		self.getTongManager().onSignUpCityWarResult( self.databaseID, succeeded )
	
	def onNotifyTongCityWarEnd( self ):
		# define method.
		# 通知城战结束
		self.isJoinTongCityWar = False

	def onCityWarBuyMachine( self, memberDBID, type, space, createPos ):
		"""
		define method.
		夺城战购买机械
		"""
		info = self.getMemberInfos( memberDBID )
		mb = info.getBaseMailbox()
		userGrade = info.getGrade()

		if userGrade < csdefine.TONG_DUTY_TONG:
			self.statusMessage( mb, csstatus.TONG_CITY_BUY_GRADE_INVALID )
			return

		needMoney = 150000
		if type == csdefine.TONG_CW_FLAG_XJ: # 玄坚
			needMoney = 100000

		if self.money - needMoney < self.getKeepMoney():
			self.statusMessage( mb, csstatus.TONG_CITY_BUY_MONEY_INVALID, needMoney )
			return

		self.payMoney( needMoney, True, csdefine.TONG_CHANGE_MONEY_CITYWARBUYMACHINE )
		space.cell.onCastCityMachine( type, createPos, mb.id )

	def buildCityWarTower( self, memberDBID, type, space ):
		"""
		define method.
		建造城战塔楼
		@param type: 0，1，2，3 代表 东西南北塔楼
		"""
		info = self.getMemberInfos( memberDBID )
		mb = info.getBaseMailbox()
		userGrade = info.getGrade()

		if userGrade < csdefine.TONG_DUTY_TONG:
			self.statusMessage( mb, csstatus.TONG_CITY_BUY_GRADE_INVALID )
			return

		#塔楼
		needMoney = 2000000
		if self.money - needMoney < self.getKeepMoney():
			self.statusMessage( mb, csstatus.TONG_CITY_BUY_MONEY_INVALID, needMoney )
			return

		self.payMoney( needMoney, True, csdefine.TONG_CHANGE_MONEY_BUILDCITYWARTOWER )
		space.cell.onbuildTowerSuccessfully( type )	
	
	def onCityWarIntegralRewar( self, integral ):
		# define method
		# 帮会城市战决赛积分竞换资金
		"""
		帮会等级	积分最大值	每点积分兑换资金	帮会资金奖励最大额
		1			81600		1.5				1500
		2			81600		2				2000
		3			81600		2.5				2500
		4			81600		3				3000
		5			81600		3.5				3500
		"""
		if integral <= 0:
			return
			
		maxReardDict = {
			1:1500,
			2:2000,
			3:2500,
			4:3000,
			5:3500
			}
			
		integralMax = 81600
		proportion = maxReardDict.get( self.level ) / float( integralMax )
		rewardMoney = int( integral * proportion * 10000 )
		self.addMoney( rewardMoney, csdefine.TONG_CHANGE_MONEY_CITY_WAR_INTEGAL )
		self.statusMessageToOnlineMember( csstatus.TONG_CITY_WAR_INTERGAL_REWARD, integral, rewardMoney / 10000, ( rewardMoney % 10000 ) / 100, rewardMoney % 100 )

	def requestCityTongRevenue( self, spaceName, playerDBID ):
		"""
		Define method.
		申请领取帮会税收。

		验证符合领取条件才能向管理器申请领取，申请后设置今天已经领取的标志

		@param spaceName : 占领的空间名字
		@type spaceName : STRING
		@param playerDBID : 申请玩家的dbid
		@type playerDBID : DATABASE_ID
		"""
		try:
			playerBase = self.getMemberInfos( playerDBID ).getBaseMailbox()
		except:
			ERROR_MSG( "cant find player(%i)'s base mailbox in tong(%s)." % ( playerDBID, self.playerName ) )
			return
			
		if self.holdCity != spaceName:
			self.statusMessage( playerBase, csstatus.TONG_GET_CITY_REVENUE_GRADE_VALID )
			return
			
		
		if self.getHoldCityRevenueData == time.strftime('%Y-%W'):	# 这周已经领取过了。
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_GET_MONEY_EXIST )
			return
		
		playerBase.client.tong_onRequestCityTongRevenue( self.__getRevenue() )

	def onGetCityTongRevenue( self, memberDBID ):
		"""
		define method.
		帮主领取了城市的税收
		"""
		playerBase = self.getMemberInfos( memberDBID ).getBaseMailbox()
		if self.getHoldCityRevenueData == time.strftime('%Y-%W'):	# 这周已经领取过了。
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_GET_MONEY_EXIST )
			return
			
		val = self.__getRevenue()
		self.addMoney( val, csdefine.TONG_CHANGE_MONEY_CITY_REVENUE )
		
		self.getHoldCityRevenueData = time.strftime('%Y-%W')
		try:
			g_logger.tongGetRevenueLog( self.databaseID, self.getName(), memberDBID, val )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
	
	def __getRevenue( self ):
		# 获取可领取多少
		MONEY_TABLE = {
			1 : 20570000,
			2 : 26740000,
			3 : 32910000,
			4 : 39090000,
			5 : 45260000,
		}

		return MONEY_TABLE.get(self.level, 0)