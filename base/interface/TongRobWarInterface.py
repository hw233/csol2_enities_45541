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
	����Ӷ�ս�Ľӿ�
	"""
	def __init__( self ):
		pass
		
	def onRequestRobWar( self, memberDBID ):
		"""
		define mothod.
		��Ҵ��汾��������Ӷ�ս
		"""
		info = self.getMemberInfos( memberDBID )
		mb = info.getBaseMailbox()
		if self.checkRequestRobWarValid( memberDBID ):
			self.getTongManager().onRequestRobWar( mb, self.databaseID )

	def onReceiveRequestRobWar( self, tongEntity, playerDBID, playerBase ):
		"""
		define mothod.
		������յ� ĳ��������뱾�������Ӷ�ս��
		"""
		hasShenshou = self.shenshouType
		if self.shenshouReviveTime > 0:
			hasShenshou = 0
		tongEntity.onAnswerRobWar( playerDBID, self.playerName, self.level, hasShenshou )

	def onAnswerRobWar( self, memberDBID, targetTongName, targetTongLevel, targetTongShenshouType ):
		"""
		define mothod.
		�ͻ���ȷ�������Ӷ�սĿ��
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

		self.payMoney( csconst.TONG_ROBWAR_REQUEST_MONEY, True, csdefine.TONG_CHANGE_MONEY_REQUEST_ROB_WAR  )	# ���ﵱ���Ѿ��ɹ����룬����Ժ��ڹ������Ǳ߼��˸����ж�����Ҫ�ص���ſ�Ǯ
		self.getTongManager().onRequestRobWarSuccessfully( mb, self.databaseID, targetTongName )

	def onRobWarFailed( self, winTongEntity, winTongDBID, winTongName ):
		"""
		define method.
		��������Ӷ�ս��ʧ����
		@param winTongEntity:ʤ������entity
		@param winTongName	:ʤ����������
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
		��������Ӷ�ս��ʤ����
		@param money		:ʧ�ܰ����������Ľ�Ǯ
		@param winTongName	:ʧ�ܰ�������
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
		�Ӷ�ս���������ð�ᵱǰ���߳�Ա�ĵж԰����Ϣ
		������ս����ʼ�����ߵ� �ɹ��������ص�½���ӿڽ�������
		"""
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			member.cell.tong_setRobWarTargetTong( enemyTongDBID )

	def checkRequestRobWarValid( self, memberDBID ):
		"""
		�����Ӷ�ս�����ж�
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
		