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

class TongRobWarInterface:
	"""
	帮会掠夺战的接口
	"""
	def __init__( self ):
		pass
		
	def onRequestRobWar( self, memberDBID ):
		"""
		define mothod.
		玩家代替本帮会申请掠夺战
		"""
		info = self.getMemberInfos( memberDBID )
		mb = info.getBaseMailbox()
		if self.checkRequestRobWarValid( memberDBID ):
			self.getTongManager().onRequestRobWar( mb, self.databaseID )

	def onReceiveRequestRobWar( self, tongEntity, playerDBID, playerBase ):
		"""
		define mothod.
		本帮会收到 某帮会请求与本帮会进行掠夺战。
		"""
		hasShenshou = self.shenshouType
		if self.shenshouReviveTime > 0:
			hasShenshou = 0
		tongEntity.onAnswerRobWar( playerDBID, self.playerName, self.level, hasShenshou )

	def onAnswerRobWar( self, memberDBID, targetTongName, targetTongLevel, targetTongShenshouType ):
		"""
		define mothod.
		客户端确认申请掠夺战目标
		"""
		info = self.getMemberInfos( memberDBID )
		mb = info.getBaseMailbox()

		if not self.checkRequestRobWarValid( memberDBID ):
			return
		elif targetTongLevel < 1:
			self.statusMessage( mb, csstatus.TONG_REQUEST_ROB_WAR_LEVEL_LOW )
			return
		elif self.level - targetTongLevel > 2:
			self.statusMessage( mb, csstatus.TONG_REQUEST_ROB_WAR_LEVEL1_INVALID )
			return
		elif targetTongShenshouType <= 0 or self.shenshouReviveTime > 0:
			self.statusMessage( mb, csstatus.TONG_REQUEST_ROB_WAR_SHENSHOU_TARGET )
			return

		self.payMoney( csconst.TONG_ROBWAR_REQUEST_MONEY, True, csdefine.TONG_CHANGE_MONEY_REQUEST_ROB_WAR  )	# 这里当做已经成功申请，如果以后在管理器那边加了更多判断则需要回调后才扣钱
		self.getTongManager().onRequestRobWarSuccessfully( mb, self.databaseID, targetTongName )

	def onRobWarFailed( self, winTongEntity, winTongDBID, winTongName ):
		"""
		define method.
		本帮会在掠夺战中失败了
		@param winTongEntity:胜利帮会的entity
		@param winTongName	:胜利帮会的名称
		"""
		payMoney = int( self.money * 0.08 )
		prestige = 100
		self.payPrestige( prestige, csdefine.TONG_PRESTIGE_CHANGE_ROB_WAR )
		self.payMoney( payMoney, False, csdefine.TONG_CHANGE_MONEY_ROBWARFAILED )

		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and hasattr( emb, "cell" ):
				emb.cell.tong_onRobWarOver(False)

		if winTongEntity:
			winTongEntity.onRobWarSuccessfully( self.playerName, payMoney )
		else:
			cmd = "update tbl_TongEntity set sm_money=sm_money+%i,sm_prestige=sm_prestige+%i  where id = %i;" % ( payMoney, 50, winTongDBID )
			BigWorld.executeRawDatabaseCommand( cmd )

		self.statusMessageToOnlineMember( csstatus.TONG_ROB_WAR_END_FAIL, winTongName, \
			payMoney / 10000, ( payMoney % 10000 ) / 100, payMoney % 100, \
			prestige )

	def onRobWarSuccessfully( self, failureTongName, money ):
		"""
		define method.
		本帮会在掠夺战中胜利了
		@param money		:失败帮会抢夺过来的金钱
		@param winTongName	:失败帮会的名称
		"""
		prestige = 100
		self.addMoney( money, csdefine.TONG_CHANGE_MONEY_ROBWARSUCCESSFULLY )
		self.addExp( csconst.TONG_EXP_REWARD_ROBWAR, csdefine.TONG_CHANGE_EXP_ROB_WAR )
		self.addPrestige( prestige, csdefine.TONG_PRESTIGE_CHANGE_ROB_WAR )
		self.statusMessageToOnlineMember( csstatus.TONG_ROB_WAR_END_WIN, failureTongName, \
			money / 10000, ( money % 10000 ) / 100, money % 100,\
			prestige )

		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and hasattr( emb, "cell" ):
				emb.cell.tong_onRobWarOver(True)

	def setRobWarTargetTong( self, enemyTongDBID ):
		"""
		define method.
		掠夺战管理器设置帮会当前在线成员的敌对帮会信息
		其他在战争开始后上线的 由管理器重载登陆帮会接口进行设置
		"""
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			member.cell.tong_setRobWarTargetTong( enemyTongDBID )

	def checkRequestRobWarValid( self, memberDBID ):
		"""
		申请掠夺战条件判断
		"""
		info = self.getMemberInfos( memberDBID )
		mb = info.getBaseMailbox()
		userGrade = info.getGrade()

		if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_ACTIVITY ):
			self.statusMessage( mb, csstatus.TONG_REQUEST_ROB_WAR_GRADE_INVALID )
			return False
		elif self.level < 1:
			self.statusMessage( mb, csstatus.TONG_REQUEST_ROB_WAR_LEVEL_INVALID )
			return False
		elif self.shenshouType <= 0 or self.shenshouReviveTime > 0:
			self.statusMessage( mb, csstatus.TONG_REQUEST_ROB_WAR_SHENSHOU_ME )
			return False
		elif self.getValidMoney() < csconst.TONG_ROBWAR_REQUEST_MONEY:
			self.statusMessage( mb, csstatus.TONG_OPEN_ACT_MONEY_LACK )
			
		return True
		