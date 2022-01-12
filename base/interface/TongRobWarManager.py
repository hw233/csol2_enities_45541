# -*- coding: gb18030 -*-
# ����Ӷ�ս
# $Id: TongCityWarManager.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

import time
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import csdefine
import csstatus
import csconst
import random
import Love3
import Const
from bwdebug import *
from Function import Functor
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from MsgLogger import g_logger

CONST_ROB_WAR_TIME 			 		= 19 					# ս������ʱ��
REQUEST_OVERDUE_TIME				= 2						# �Ӷ�ս�������ʱ�䣬���ⶨ��ģ���Ŵ����������������ݴ���ʱ�伴��
ROBWAR_FAILURE_PAY_PERCENTAGE		= 0.10					# ����Ӷ�սʧ�ܰ����Ҫ֧�ֽ�Ǯ�ı���


class TongRobWarManager:
	def __init__( self ):
		self.robWarTmpData = {}								# ��ʱ���ݻ���
		self.robwar_dataClear_timerID = 0
		self.requestRobTongInfos = {}						# �����Ӷ�ս�İ����ʱ����{(������dbid,Ŀ����dbid):��¼ʱ��, ...}
		self.requestRobTongTimer = 0						# ���������Ӷ�ս��ʱ����timer
		self.robWarReset()

	def isInRobWarRequest( self, tongDBID ):
		"""
		�Ƿ��ڰ���Ӷ�������
		"""
		for tongDBIDs in self.requestRobTongInfos:
			if tongDBID in tongDBIDs:
				return True
		return False
		
	def checkRobWarRequest( self ):
		"""
		�����ʱ�Ӷ���������
		"""
		for tongDBIDs, requestTime in self.requestRobTongInfos.items():
			if time.time() - requestTime > REQUEST_OVERDUE_TIME:
				self.removeRobTongRequest( tongDBIDs[0], tongDBIDs[1] )
				
	def addRequestRobTongInfo( self, srcTongDBID, dstTongDBID ):
		"""
		���µ��Ӷ�ս����
		
		@param srcTongDBID : �������dbid
		@param dstTongDBID : Ŀ�����dbid
		"""
		self.requestRobTongInfos[( srcTongDBID, dstTongDBID )] = time.time()
		if not self.requestRobTongTimer:
			self.requestRobTongTimer = self.addTimer( REQUEST_OVERDUE_TIME, REQUEST_OVERDUE_TIME, 0 )
			
	def removeRobTongRequest( self, srcTongDBID, dstTongDBID ):
		"""
		���һ���Ӷ�ս����
		"""
		try:
			self.requestRobTongInfos.pop( (srcTongDBID, dstTongDBID) )
		except KeyError:
			ERROR_MSG( "there's no request tong: %i and %i" % ( srcTongDBID, dstTongDBID ) )
		if len( self.requestRobTongInfos ) == 0:
			self.delTimer( self.requestRobTongTimer )
			self.requestRobTongTimer = 0
			
	def onManagerInitOver( self ):
		"""
		virtual method.
		��������ʼ�����
		"""
		# 8Сʱ ��ѯһ��ʱ��
		self.robwar_dataClear_timerID = self.addTimer(  0, 60 * 60 * 8, 0 )
		self.tongRobWarManager_registerCrond()

	def robWarReset( self ):
		"""
		"""
		self.robwar_start_remain30_timerID = 0
		self.robwar_start_timerID = 0
		self.robwar_end30_timerID = 0
		self.robwar_end_timerID = 0
		self.robWarTmpData[ "overTongs" ] = []

	def isRobWarFailure( self, tongDBID ):
		"""
		�Ƿ���һ��������ʧ�ܹ�, ��ΪrobWarFailureList��ĩ����գ���˲����ж�ʱ��
		"""
		return tongDBID in self.robWarFailureList

	def hasRobWarLog( self, tongDBID ):
		"""
		�Ƿ���ڸð���ս����ϵ��¼
		"""
		for item in self.robWarInfos:
			if tongDBID == item[ "rightTongDBID" ] or tongDBID == item[ "leftTongDBID" ]:
				return True
		return False

	def getRobWarTongEnemyTongDBID( self, tongDBID ):
		"""
		���ĳ�����ĵж԰��
		"""
		for item in self.robWarInfos:
			if tongDBID == item[ "rightTongDBID" ]:
				return item[ "leftTongDBID" ]
			elif tongDBID == item[ "leftTongDBID" ]:
				return item[ "rightTongDBID" ]

		return 0

	def isRobWarRight( self, tongDBID ):
		"""
		�Ƿ��Ǳ�����ս����
		"""
		for item in self.robWarInfos:
			if tongDBID in item.itervalues():
				if item[ "rightTongDBID" ] == tongDBID:
					return True
				else:
					return False
		return False

	def onRegisterPreMonthRobWarPoint( self ):
		"""
		define method.
		�Ǽ������Ӷ�ս����
		"""
		tm = time.localtime()

		if self.isRegisterRobWarRecord != tm[1]:
			self.preMonthRobWarTopRecords = self.robWarTopRecords
			self.isRegisterRobWarRecord = tm[1]
			self.robWarTopRecords = {}
			self.robWarGetRewardRecords = []
			self.writeToDB()
			INFO_MSG("Rob war point table update.PreMonth point datas is: ", self.preMonthRobWarTopRecords )

	def queryTongRobWarPoint( self, playerBase, tongDBID, npcID ):
		"""
		define method.
		��ѯ�����Ӷ�ս����
		"""
		DEBUG_MSG( "view:", playerBase, tongDBID, npcID )
		msg = ""
		datas = sorted(self.preMonthRobWarTopRecords.items(), key=lambda d:d[1])[0:10]
		datas.reverse()
		for item in datas:
			tongName = self.getTongNameByDBID(item[0])
			if tongName == "":
				self.preMonthRobWarTopRecords.pop(item[0])
				continue

			msg += "%s:%i@B" % (tongName, item[1])

		msg += cschannel_msgs.TONG_INFO_19 % self.preMonthRobWarTopRecords.get(tongDBID, 0)
		playerBase.client.onSetGossipText(msg)
		playerBase.client.onGossipComplete( npcID )

	def getTongRobWarPoint( self, playerBase, tongDBID ):
		"""
		define method.
		ĳ��������ȡ�Ӷ�ս����
		"""
		if tongDBID in self.robWarGetRewardRecords:
			self.statusMessage( playerBase, csstatus.TONG_ROB_WAR_REWARD_EXIST )
			return

		datas = sorted(self.preMonthRobWarTopRecords.items(), key=lambda d:d[1])[-3:]
		datas.reverse()
		for idx, item in enumerate(datas):
			if item[0] == tongDBID:
				playerBase.cell.tong_rewardRobWar(idx + 1)
				return

		self.statusMessage( playerBase, csstatus.TONG_ROB_WAR_REWARD_TOP )

	def onRewardRobWarPlayerCB( self, tongDBID, isSuccess ):
		"""
		define method.
		�Ӷ�ս���������֮���Ƿ�ɹ��Ļص�
		"""
		if isSuccess:
			self.robWarGetRewardRecords.append( tongDBID )

	def onRequestRobWar( self, playerBase, playerTongDBID ):
		"""
		define method.
		ĳ�����������Ӷ�ս
		"""
		if self.isInRobWarRequest( playerTongDBID ):	# ����Ѿ��ڰ���Ӷ�ս�����У���ô���Ա�������
			return
			
		if self.hasRobWarLog( playerTongDBID ):
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_LOG_EXIST )
			return
		elif self.isRobWarFailure( playerTongDBID ):
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_ISFAILURE )
			return
		elif playerTongDBID in self.tongRequestRecord:
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_HAS_JOIN )
			return
			
		playerBase.client.tong_onRequestRobWar()

	def onAnswerRobWar( self, playerBase, playerDBID, playerTongDBID, targetTongName ):
		"""
		define method.
		�ͻ���ȷ�������Ӷ�սĿ��
		"""
		targetTongDBID = self.getTongDBIDByName( targetTongName )
		if targetTongDBID == 0:
			self.statusMessage( playerBase, csstatus.TONG_TARGET_NOT_EXIST )
			return
		elif targetTongDBID == playerTongDBID:
			self.statusMessage( playerBase, csstatus.TONG_TARGET_INVALID )
			return
		if self.isInRobWarRequest( targetTongDBID ):	# ����Ѿ��ڰ���Ӷ�ս�����У���ô���Ա�������
			return
		elif self.hasRobWarLog( targetTongDBID ):
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_LOG_TARGET_EXIST, targetTongName )
			return
		elif self.isRobWarFailure( targetTongDBID ):
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_TARGET_ISFAILURE )
			return
		elif targetTongDBID not in self.topActivityPointTongDBIDs[0 : Const.TONG_ACTIVITY_POINT_TOP_COUNT]:
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_ISFAILURE1 )
			return
		self.addRequestRobTongInfo( playerTongDBID, targetTongDBID )
		
		tongEntity = self.findTong( targetTongDBID )

		if tongEntity:
			tongEntity.onReceiveRequestRobWar( self.findTong( playerTongDBID ), playerDBID, playerBase )
		else:
			cmd = "select sm_level, sm_shenshouType, sm_shenshouReviveTime from tbl_TongEntity where %i = id;" % targetTongDBID
			BigWorld.executeRawDatabaseCommand( cmd, Functor( self.robWarQueryTongLevel_Callback, targetTongName, playerTongDBID, playerDBID ) )

	def robWarQueryTongLevel_Callback( self, targetTongName, playerTongDBID, playerDBID, result, dummy, error ):
		"""
		��ѯ�Է���ἶ�� ���ݿ�ص�
		"""
		if (error):
			ERROR_MSG( error )
			return

		tongEntity = self.findTong( playerTongDBID )
		hasShenshou = int( result[0][1] )
		if int( result[0][2] ) > 0:
			hasShenshou = 0
		tongEntity.onAnswerRobWar( playerDBID, targetTongName, int( result[0][0] ), hasShenshou )

	def findRequestRobWar( self, playerBase, targetTongName ):
		"""
		define method.
		��Ҳ������Ҫ�Ӷ�İ��
		"""
		cmd = "select sm_level,sm_shenshouType,id,sm_ssd_level from tbl_TongEntity where sm_playerName = \'%s\';" % BigWorld.escape_string( targetTongName )
		BigWorld.executeRawDatabaseCommand( cmd, Functor( self.findRequestRobWar_Callback, playerBase ) )

	def findRequestRobWar_Callback( self, playerBase, result, dummy, error ):
		"""
		��Ҳ������Ҫ�Ӷ�İ�� ���ݿ�ص�
		"""
		if (error):
			ERROR_MSG( error )
			return

		if len( result ) <= 0:
			playerBase.client.onfindRequestRobWarCallBack( 0, 0, 0, 0 )

		level = int( result[0][0] )
		shenshouType = int( result[0][1] )
		isRobWarFailure = self.isRobWarFailure( int( result[0][2] ) )
		ssd_level = int( result[0][3] )
		playerBase.client.onfindRequestRobWarCallBack( level, shenshouType, ssd_level, isRobWarFailure )

	def onRequestRobWarSuccessfully( self, playerBase, playerTongDBID, targetTongName ):
		"""
		define method.
		�����Ӷ�ս�ɹ�
		"""
		targetTongDBID = self.getTongDBIDByName( targetTongName )
		self.removeRobTongRequest( playerTongDBID, targetTongDBID )
		if targetTongDBID == 0:
			self.statusMessage( playerBase, csstatus.TONG_TARGET_NOT_EXIST )
			return

		tongEntity = self.findTong( playerTongDBID )
		if tongEntity:
			self.statusTongMessage( tongEntity, csstatus.TONG_REQUEST_ROB_WAR_SUCCESS1, targetTongName )

		playerTongName = self.getTongNameByDBID( playerTongDBID )
		tongEntity = self.findTong( targetTongDBID )
		if tongEntity:
			self.statusTongMessage( tongEntity, csstatus.TONG_REQUEST_ROB_WAR_SUCCESS2, playerTongName )

		self.tongRequestRecord.append( playerTongDBID )
		d = { "rightTongDBID" : targetTongDBID, "leftTongDBID" : playerTongDBID, "rightTongName" : targetTongName, "leftTongName" : playerTongName }
		self.robWarInfos.append( d )

		
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_TONG_LUE_DUO, csdefine.ACTIVITY_JOIN_TONG, playerTongDBID )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def onRegisterTerritory( self, tongDBID, territory ):
		"""
		define method.
		@param tongDBID: ���DBID
		@param territory:��ظ�����basemailbox
		"""
		if not BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
			return
		# �������������ˣ� ����������ս����¼����֪ͨ�ø��� ս���Ѿ���ʼ��
		if self.hasRobWarLog( tongDBID ):
			territory.onRobWarStart( self.getRobWarTongEnemyTongDBID( tongDBID ) )

	def onRobWarOver( self, failureTongDBID ):
		"""
		define method.
		�Ӷ�ս��ǰ����
		@param failureTongDBID:ʧ�ܷ����DBID
		"""
		warInfos = None
		for item in self.robWarInfos:
			if failureTongDBID == item[ "rightTongDBID" ] or failureTongDBID == item[ "leftTongDBID" ]:
				warInfos = item
				break

		if warInfos is None:
			ERROR_MSG( " not found warInfos, failureTongDBID %i." )
			return

		# ��¼�ð����ǰ����ս����
		self.robWarTmpData[ "overTongs" ].append( warInfos[ "rightTongDBID" ] )
		self.robWarTmpData[ "overTongs" ].append( warInfos[ "leftTongDBID" ] )
		# ��������˵ĵж԰����Ϣ
		self.clearAllRobWarTargetTong( item[ "rightTongDBID" ] )
		self.clearAllRobWarTargetTong( item[ "leftTongDBID" ] )

		# ֪ͨ���ս�������� ��ؿ��ܻ���ս������һЩ������ �磺��ص�����ֹͣ�
		territory = self.findTerritoryByTongDBID( warInfos[ "rightTongDBID" ] )
		if territory:
			territory.onRobWarStop()
		territory = self.findTerritoryByTongDBID( warInfos[ "leftTongDBID" ] )
		if territory:
			territory.onRobWarStop()

		# ��ʼ֧��ս������
		if failureTongDBID == warInfos[ "rightTongDBID" ]:
			self.payRobWar( warInfos[ "leftTongDBID" ], warInfos[ "leftTongName" ], warInfos[ "rightTongDBID" ], warInfos[ "rightTongName" ] )
		else:
			self.payRobWar( warInfos[ "rightTongDBID" ], warInfos[ "rightTongName" ], warInfos[ "leftTongDBID" ], warInfos[ "leftTongName" ] )

		self.writeToDB()

	def clearAllRobWarTargetTong( self, tongDBID ):
		"""
		��������˵ĵж԰����Ϣ
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.setRobWarTargetTong( 0 )

	def onAllRobWarOver( self ):
		"""
		����ս��������  ��Ϊϵͳս������ʱ�䵽��
		"""
		overTongs = self.robWarTmpData[ "overTongs" ]
		for item in self.robWarInfos:
			if item[ "rightTongDBID" ] in overTongs:
				continue
			else:
				# ��������˵ĵж԰����Ϣ
				self.clearAllRobWarTargetTong( item[ "rightTongDBID" ] )
				self.clearAllRobWarTargetTong( item[ "leftTongDBID" ] )
				self.payRobWar( item[ "rightTongDBID" ], item[ "rightTongName" ], \
				item[ "leftTongDBID" ], item[ "leftTongName" ] )
				# ��ʧ���߼���ʧ������
				self.robWarFailureList.append( item[ "leftTongDBID" ] )
				# ֪ͨ���ս�������� ��ؿ��ܻ���ս������һЩ������ �磺��ص�����ֹͣ�
				territory = self.findTerritoryByTongDBID( item[ "rightTongDBID" ] )
				if territory:
					territory.onRobWarStop()
				territory = self.findTerritoryByTongDBID( item[ "leftTongDBID" ] )
				if territory:
					territory.onRobWarStop()

		self.robWarInfos = []
		self.writeToDB()

	def payRobWar( self, winTongDBID, winTongName, failureTongDBID, failureTongName ):
		"""
		֧���Ӷ�ս������
		"""
		failureTongEntity = self.findTong( failureTongDBID )
		winTongEntity = self.findTong( winTongDBID )

		if winTongDBID in self.robWarTopRecords:
			self.robWarTopRecords[ winTongDBID ] += 3
		else:
			self.robWarTopRecords[ winTongDBID ] = 3

		if failureTongDBID in self.robWarTopRecords:
			self.robWarTopRecords[ failureTongDBID ] -= 1
		else:
			self.robWarTopRecords[ failureTongDBID ] = -1

		if failureTongEntity:
			failureTongEntity.onRobWarFailed( winTongEntity, winTongDBID, winTongName )
		else:
			cmd = "select sm_money, sm_prestige from tbl_TongEntity where id = %i;" % failureTongDBID
			BigWorld.executeRawDatabaseCommand( cmd, Functor( self.robWarQueryTongMoney_Callback, failureTongDBID, failureTongName, winTongDBID, winTongName ) )

	def robWarQueryTongMoney_Callback( self, failureTongDBID, failureTongName, winTongDBID, winTongName, result, dummy, error ):
		"""
		��ѯ�Է�����Ǯ����Ϣ  ���ݿ�ص�
		"""
		if (error):
			ERROR_MSG( error )
			return
		if result is None or len( result ) == 0:
			DEBUG_MSG( "the failure tong( dbid:%i, name:%s ) had been dissmiss.winer dbid:%i,name:%s." % ( failureTongDBID, failureTongName, winTongDBID, winTongName ) )
			return
		money = int( result[0][0] )
		prestige = int( result[0][1] ) - 100
		payMoney = int( money * ROBWAR_FAILURE_PAY_PERCENTAGE )

		money -= payMoney
		if prestige < 0:
			prestige = 0

		cmd = "update tbl_TongEntity set sm_money=%i,sm_prestige=%i  where id = %i;" % ( money, prestige, failureTongDBID )
		BigWorld.executeRawDatabaseCommand( cmd )

		tongEntity = self.findTong( winTongDBID )
		if tongEntity:
			tongEntity.onRobWarSuccessfully( failureTongName, payMoney )
		else:
			cmd = "update tbl_TongEntity set sm_money=sm_money+%i  where id = %i;" % ( payMoney, failureTongDBID )
			BigWorld.executeRawDatabaseCommand( cmd )

	def onWarMessage( self, tongDBID, statusID, *args ):
		"""
		ս�����ͳһϵͳͨ�� ��ָ�����ͨ��
		"""
		args = "" if args == () else str( args )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onStatusMessage( statusID, args )

	def robWarTimeAlert( self, statusID ):
		"""
		�Ӷ�սʱ����ʾ
		"""
		for item in self.robWarInfos:
			if item[ "rightTongDBID" ] in self.robWarTmpData[ "overTongs" ] or item[ "leftTongDBID" ] in self.robWarTmpData[ "overTongs" ]:
				continue
			self.onWarMessage( item[ "rightTongDBID" ], statusID, item[ "leftTongName" ] )
			self.onWarMessage( item[ "leftTongDBID" ], statusID, item[ "rightTongName" ] )

	def initRobWar( self ):
		"""
		��ʼ���Ӷ�ս����
		"""
		tongList = []
		for item in self.robWarInfos:
			# ֪ͨ���ս����ʼ�� ��ؿ��ܻ���ս������һЩ������ �磺��ص����޿�ʼ�
			territory = self.findTerritoryByTongDBID( item[ "rightTongDBID" ] )
			if territory:
				territory.onRobWarStart( item[ "leftTongDBID" ] )
			territory = self.findTerritoryByTongDBID( item[ "leftTongDBID" ] )
			if territory:
				territory.onRobWarStart( item[ "rightTongDBID" ] )
			# ���ð�������˵ĵж԰����Ϣ�� ���ڿͻ�����ʾ��ս���ͷ��жϵ�
			tongEntity = self.findTong( item[ "rightTongDBID" ] )
			if tongEntity:
				tongEntity.setRobWarTargetTong( item[ "leftTongDBID" ] )
			tongEntity = self.findTong( item[ "leftTongDBID" ] )
			if tongEntity:
				tongEntity.setRobWarTargetTong( item[ "rightTongDBID" ] )

			tongList.append( item[ "leftTongDBID" ] )
			tongList.append( item[ "rightTongDBID" ] )
			
		BigWorld.globalData[ "TONG_ROB_WAR_START" ] = tongList
		
	def onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID ):
		"""
		define method.
		��Ա��½֪ͨ
		"""
		if not BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
			return
		if tongDBID in self.robWarTmpData[ "overTongs" ]:
			return
		for item in self.robWarInfos:
			if tongDBID == item[ "rightTongDBID" ]:
				baseEntity.cell.tong_setRobWarTargetTong( item[ "leftTongDBID" ] )
				return
			elif tongDBID == item[ "leftTongDBID" ]:
				baseEntity.cell.tong_setRobWarTargetTong( item[ "rightTongDBID" ] )
				return

	#-----------------------------------------------------------------����ƻ����------------------------------------------

	def tongRobWarManager_registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"TongRobWarManager_start_notice" : "onTongRobWarManagerStartNotice",
					  	"TongRobWarManager_start" : "onTongRobWarManagerStart",
					  	"TongRobWarManager_end" : "onTongRobWarManagerEnd",
					  	"TongRobWarManagerSignUp_start" : "onTongRobWarManagerSignUpStart",
					  	"TongRobWarManagerSignUp_end" : "onTongRobWarManagerSignUpEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
		BigWorld.globalData["Crond"].addAutoStartScheme( "TongRobWarManagerSignUp_start", self, "onTongRobWarManagerSignUpStart" )

	def onTongRobWarManagerStartNotice( self ):
		"""
		defined method.
		ս��������ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONG_ROB_WAR_BEGIN_NOTIFY, [] )

	def onTongRobWarManagerSignUpStart( self ):
		"""
		defined method.
		ս��������ʼͨ��
		"""
		if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
			return
		BigWorld.globalData[ "TONG_ROB_WAR_SIGNUP_START" ] = True

	def onTongRobWarManagerSignUpEnd( self ):
		"""
		defined method.
		ս����������ͨ��
		"""
		if BigWorld.globalData.has_key( "TONG_ROB_WAR_SIGNUP_START" ):
			del BigWorld.globalData[ "TONG_ROB_WAR_SIGNUP_START" ]

		for item in self.robWarInfos:
			#(csol-7884) ����Ӷ�վ(���A��dbid ���A������ ���B��dbid ���B������)
			try:
				g_logger.actDistributionLog( item[ "rightTongDBID" ], item["rightTongName"], item[ "leftTongDBID" ], item["leftTongName"] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )


	def onTongRobWarManagerStart( self ):
		"""
		defined method.
		ս����ʼͨ��
		"""
		# ս������һ���ӿ�ʼ
		self.robWarTimeAlert( csstatus.TONG_ROB_WAR_START1 )
		self.robwar_start_remain30_timerID = self.addTimer( 30, 0, 0 )


	def onTongRobWarManagerEnd( self ):
		"""
		defined method.
		����ս��
		"""
		# ս�������1����
		self.robWarTimeAlert( csstatus.TONG_ROB_WAR_END1 )
		self.robwar_end30_timerID = self.addTimer( 30, 0, 0 )

	#----------------------------------------------------------------------------------------------------------------------

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if timerID == self.robwar_dataClear_timerID:
			t = time.localtime()
			# �������ĩ����ձ����ڵ�ʤ����Ϣ
			if t[6] > 4:
				self.robWarFailureList = []
				self.tongRequestRecord = []
		elif timerID == self.robwar_start_remain30_timerID:	# ս������30�뿪ʼ
			self.robwar_start_remain30_timerID = 0
			self.robwar_start_timerID = self.addTimer( 30, 0, 0 )
			self.robWarTimeAlert( csstatus.TONG_ROB_WAR_START30 )
		elif timerID == self.robwar_start_timerID:			# ս����ʼ
			DEBUG_MSG( ">>tong of rob war is start!" )
			self.initRobWar()
			self.robwar_start_timerID = 0
			self.robWarTimeAlert( csstatus.TONG_ROB_WAR_START )
		elif timerID == self.robwar_end30_timerID:			# ս�������30��
			self.robwar_end30_timerID = 0
			self.robwar_end_timerID = self.addTimer( 30, 0, 0 )
			self.robWarTimeAlert( csstatus.TONG_ROB_WAR_END30 )
		elif timerID == self.robwar_end_timerID:			# ս������
			DEBUG_MSG( ">>tong of rob war is end!" )
			if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
				del BigWorld.globalData[ "TONG_ROB_WAR_START" ]

			self.onAllRobWarOver()
			self.robwar_end_timerID = 0
			self.robWarReset()								# ��������
		elif timerID == self.requestRobTongTimer:
			self.checkRobWarRequest()
			
#
# $Log: not supported by cvs2svn $
#