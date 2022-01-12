# -*- coding: gb18030 -*-
#
#$Id:$


"""
8:22 2008-9-9,writen by wangshufeng
"""
"""
2010.11
家族擂台移植为帮会擂台 by cxm
"""
import random

import BigWorld
from bwdebug import *

import csdefine
import csconst
import cschannel_msgs
import csstatus
import Love3
import cPickle
import items
import RoleMatchRecorder

g_items = items.instance()
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from MsgLogger import g_logger

ABATTOIR_SIGN_UP_POINT = [ 12, 30, 0 ]		# 擂台赛开始报名时间，12时30分0秒
ABATTOIR_END_SIGN_UP_POINT = [ 12, 40, 0 ]	# 擂台赛报名结束时间，12时40分0秒

# 擂台赛奖励，{ 轮次: 奖励/惩罚参数 }
ABATTOIR_AWARD_WIN_MAP = {  csdefine.ABATTOIR_EIGHTHFINAL:100,
							csdefine.ABATTOIR_QUARTERFINAL:100,
							csdefine.ABATTOIR_SEMIFINAL:100,
							csdefine.ABATTOIR_FINAL:100,
							csdefine.ABATTOIR_GAME_NONE:0
						 }
NOTICE  = 1
SIGNUP  = 2

class TongAbattoirMgr:
	"""
	帮会擂台赛管理模块

	Abattoir：角斗场
	"""
	def __init__( self ):
		"""
		"""
		#self.abattoirCount = 0				# 当前擂台赛进行的轮数
		self.abattoirTongDBIDList = []		# 报名参加擂台赛的帮会dbid列表
		self.abattoirWinerList = []			# 胜利帮会dbid列表
		self.abattoirLoserList = []			# 失败帮会dbid列表
		self.abattoirAntagonistDict = {}	# 参加擂台赛的帮会数据{ 帮会dbid:{ 对手dbid:dbid，在战场中的标记:right或left，帮会在副本的人数:memCount }, ... }
		self.abattoirLastTongDBIDList = []  # 擂台赛上一轮帮会dbid列表(为了提示没有进入比赛的帮会)
		self.joinPlayer = {}

		self.aba_eighthfinalStartTime = 0.0		# 记录八分之一赛开始（倒计时）时间
		self.aba_quarterfinalStartTime = 0.0	# 记录四分之一赛开始（倒计时）时间
		self.aba_semifinalStartTime = 0.0		# 记录二分之一赛开始（倒计时）时间
		self.aba_finalStartTime = 0.0			# 记录决赛开始（倒计时）时间
		self.nextStartTime = 0.0				# 下一轮次开始时间(为了提示)

		self.aba_startTimer2 = 0			# 擂台赛第二轮入场timerID
		self.aba_startTimer3 = 0			# 擂台赛第三轮入场timerID
		self.aba_startTimer4 = 0			# 擂台赛第四轮入场timerID
		self.aba_endTimer = 0				# 擂台赛结束的timerID
		
		self.notice1 = 0			# 第二次公告的timerID
		self.notice2 = 0 			# 第三次公告的timerID
		self.notice3 = 0 			# 第四次公告的timerID
		self.notice4 = 0 			# 第五次公告的timerID
		self.signUpNotice1 = 0			# 开始报名第二次公告的timeID
		self.signUpNotice2 = 0			# 开始报名第三次公告的timeID
		
		self.abaStartNotice1 = 0		# 活动入场第二次公告的timerID
		self.abaStartNotice2 = 0		# 活动入场第三次公告的timerID
		self.abaStartNotice3 = 0		# 活动入场第四次公告的timerID
		self.abaStartNotice4 = 0		# 活动入场第五次公告的timerID
		
		self.abaStart = 0		# 首轮比赛入场结束timerID
		self.endEnterTimer = 0		# 入场结束timerID
		
		self.statu = 0
		self.firstRoundFlag = False
		self.enterTongDBID = []		# 记录进入副本的帮会DBID
		self.lunkongTongDBID = []		# 记录轮空帮会的DBID
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_OVER		#帮会擂台的阶段(未开启)
		
	def onManagerInitOver( self ):
		"""
		virtual method.
		帮会系统启动完毕通知
		"""
		self.tongAbattoirMgr_registerCrond()

	def isAbattoirStart( self ):
		"""
		擂台赛是否开始
		"""
		return BigWorld.globalData[ "tongAbaStep" ] == csconst.TONG_ABATTOIR_START

	def isAbattoirSignUp( self ):
		"""
		擂台赛报名是否开始
		"""
		return BigWorld.globalData[ "tongAbaStep" ] == csconst.TONG_ABATTOIR_SINGUP

	def isAbattoirEnter( self ):
		"""
		擂台赛是否为入场时间
		"""
		return BigWorld.globalData[ "tongAbaStep" ] == csconst.TONG_ABATTOIR_ENTER

	def isAbattoirSignUpFull( self ):
		"""
		报名帮会是否满
		"""
		return len( self.abattoirTongDBIDList ) >= csconst.TONG_ABATTOIR_MAX_NUM

	def openAbattoirSignUp( self ):
		"""
		开启帮会擂台报名
		"""
		self.signUpNotice1 = self.addTimer( 5 * 60 )
		self.signUpNotice2 = self.addTimer( 9 * 60 )
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_SINGUP
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_SIGN_UP % str( 10 ), [] )

	def closeAbattoirSignUp( self ):
		"""
		关闭帮会擂台报名，并入场
		"""
		self.abaStartNotice1 = self.addTimer( 1 * 60 )
		self.abaStartNotice2 = self.addTimer( 2 * 60 )
		self.abaStartNotice3 = self.addTimer( 3 * 60 )
		self.abaStartNotice4 = self.addTimer( 4 * 60 )
		
		self.abaStart = self.addTimer( 5 * 60 )
		
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_ENTER
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_END_SIGN_UP % str( 5 ), [] )
		
		for i in self.abattoirTongDBIDList:
			g_logger.actJoinLog( csdefine.ACTIVITY_BANG_HUI_LEI_TAI, csdefine.ACTIVITY_JOIN_ROLE, i )
		
	def startAbattoir( self ):
		"""
		开启角斗场，擂台赛开始了
		"""
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_START
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_START, [] )
		self.firstRoundFlag = True

	def isTongJoinAba( self, tongDBID ):
		"""
		tongDBID帮会是否参加擂台赛
		"""
		return tongDBID in self.abattoirTongDBIDList

	def sendGiveUpMessage( self ):
		"""
		提示放弃比赛的
		"""
		# 如果上一轮没有参加比赛，给予提示信息。
		for e in self.abattoirLastTongDBIDList:
			if not (self.isAbaWinner( e ) or self.isAbaLoser( e )):
				tongBase = self.findTong( e )		# 清除没进过副本的帮会成员的当前比赛情况信息
				if tongBase:
					tongBase.updateTongAbaRound( csdefine.ABATTOIR_GAME_NONE )
				self.onAbaMessage( e, csstatus.TONG_ABATTOIR_GIVE_UP )

	def initAbattoirWar( self, matchLevel, tongDBIDList ):
		"""
		初始化擂台赛数据

		@param matchLevel : 比赛等级，定义在csdefine中
		@type matchLevel : INT8
		@param tongDBIDList : 参加本轮帮会擂台赛的帮会dbid列表
		@type tongDBIDList : DATABASE_ID
		"""
		DEBUG_MSG( "tongDBIDList", tongDBIDList )
		self.abattoirLastTongDBIDList = tongDBIDList[:]
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_ENTER
		if len( tongDBIDList ) == 1:
			# 如果只有一个帮会报名，也可以进入副本，但是数据要特殊处理
			if BigWorld.globalData.has_key("TongAba_signUp_one"):
				tongDBID1 = tongDBIDList.pop( 0 )
				tongBase = self.findTong( tongDBID1 )
				if tongBase:
					tongBase.tongAbaGather( csdefine.ABATTOIR_EIGHTHFINAL )
					tongBase.updateTongAbaRound( csdefine.ABATTOIR_EIGHTHFINAL )
				self.abattoirAntagonistDict[ tongDBID1 ] = { "opponentDBID":-1, "isRight":True, "memCount":0 }
				self.abattoirAntagonistDict[ 0 ] = { "opponentDBID":tongDBID1, "isRight":False, "memCount":0} 
				self.endEnterTimer = self.addTimer( 5 * 60 + 2 )
			else:
				winTongDBID = tongDBIDList[ 0 ]
				self.addAbaAward( csdefine.ABATTOIR_FINAL, winTongDBID )
				self.abattoirWinerList = []
				self.abattoirWinerList.append( winTongDBID )
				self.endAbattoir()
			return
			
		self.abattoirWinerList = []		# 清空胜利者
		teamCount = len( tongDBIDList ) / 2

		massageID = csstatus.TONG_ABATTOIR_EIGHTHFINAL_READY
		if matchLevel == csdefine.ABATTOIR_QUARTERFINAL:
			massageID = csstatus.TONG_ABATTOIR_QUARTERFINAL_READY
		elif matchLevel == csdefine.ABATTOIR_SEMIFINAL:
			massageID = csstatus.TONG_ABATTOIR_SEMIFINAL_READY
		elif matchLevel == csdefine.ABATTOIR_FINAL:
			massageID = csstatus.TONG_ABATTOIR_FINAL_READY
		for x in xrange( teamCount ):
			tongDBID1 = tongDBIDList.pop( 0 )
			index = random.randint( 0, len( tongDBIDList ) - 1 )
			tongDBID2 = tongDBIDList.pop( index )
			self.abattoirAntagonistDict[ tongDBID1 ] = { "opponentDBID":tongDBID2, "isRight":True, "memCount":0 }
			self.abattoirAntagonistDict[ tongDBID2 ] = { "opponentDBID":tongDBID1, "isRight":False, "memCount":0 }
			
			tongBase1 = self.findTong( tongDBID1 )
			tongBase2 = self.findTong( tongDBID2 )
			
			if tongBase1:
				tongBase1.tongAbaGather( matchLevel )
				tongBase1.updateTongAbaRound( matchLevel )
			if tongBase2:
				tongBase2.tongAbaGather( matchLevel )
				tongBase2.updateTongAbaRound( matchLevel )
			
			self.onAbaMessage( tongDBID1, massageID, self.getTongNameByDBID( tongDBID2 ) )
			self.onAbaMessage( tongDBID2, massageID, self.getTongNameByDBID( tongDBID1 ) )
		self.lunkongTongDBID = []
		if tongDBIDList:				# 很幸运，本轮轮空的帮会，进入下一轮
			self.lunkongTongDBID = tongDBIDList
			winTongDBID = tongDBIDList[ 0 ]
			self.abattoirWinerList.append( winTongDBID )
			self.onAbaMessage( winTongDBID, csstatus.TONG_ABATTOIR_BYE )
		self.endEnterTimer = self.addTimer( 5 * 60 + 2 )

	def onEndEnter( self ):
		"""
		比赛入场结束时通知参赛玩家集合结束
		"""
		foreEnd = True
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_START
		for tongDBID in self.abattoirAntagonistDict.keys():
			tongBase = self.findTong( tongDBID )
			if tongBase:
				tongBase.tongAbaCloseGather()
				
			if BigWorld.globalData.has_key("TongAba_signUp_one"):
				self.addAbaAward( csdefine.ABATTOIR_FINAL, tongDBID )
				if tongDBID not in self.abattoirWinerList:
					self.abattoirWinerList.append( tongDBID )
				return
				
			opponentDBID = self.abattoirAntagonistDict[ tongDBID ]["opponentDBID"]
			if tongDBID not in self.enterTongDBID:
				self.onAbaMessage( tongDBID,csstatus.TONG_ABATTOIR_GIVE_UP )
				
				if opponentDBID not in self.enterTongDBID:				# 如果两个参赛帮会都未进过副本，需要管理器将放弃比赛的帮会加到失败帮会中
					if tongDBID not in self.abattoirLoserList:
						self.abattoirLoserList.append( tongDBID )
					if opponentDBID not in self.abattoirLoserList:
						self.abattoirLoserList.append( opponentDBID )
			else:
				if opponentDBID not in self.enterTongDBID:
					round = self.getAbaRound()
					if round != csdefine.ABATTOIR_FINAL:
						self.onAbaMessage( tongDBID, csstatus.TONG_ABATTOIR_WIN_2,int((self.nextStartTime - BigWorld.time())/60) )
					else:
						self.onAbaMessage( tongDBID,csstatus.TONG_ABATTOIR_WIN_1 )
				else:			# 只要有一对帮会还在副本中就不提前结束活动
					foreEnd = False
		if foreEnd:
			if len( self.abattoirWinerList ) <= 1:
				# 轮空帮会获得冠军时，获得声望奖励
				if len( self.abattoirWinerList ) == 1 and self.abattoirWinerList[0] in self.lunkongTongDBID:
					self.addAbaAward( self.getAbaRound(), self.abattoirWinerList[0] )
				self.aba_endTimer = self.addTimer( 1 )		# 延迟一秒结束
		self.enterTongDBID = []

	def endAbattoir( self ):
		"""
		defined method
		
		帮会擂台赛结束，清除数据，设置下一次帮会擂台赛的开始的timer
		"""
		if not BigWorld.globalData["tongAbaStep"]:		# 如果活动已经结束，全局tongAbaStep为0
			return
			
		if self.abattoirWinerList:
			winTongName = self.getTongNameByDBID( self.abattoirWinerList[ 0 ] )
			self.onAbaMessage( self.abattoirWinerList[0], csstatus.TONG_ABATTOIR_CHAMPION )
			if winTongName:
				tempString = cschannel_msgs.BCT_BHLT_CELEBRATE %( winTongName )
				Love3.g_baseApp.anonymityBroadcast( tempString, [] )

		for e in self.joinPlayer:
			item = g_items.createDynamicItem( 60101260,1 )
			itemDatas = []
			if item:
				item.setLevel( self.joinPlayer[e][1])		# 设置经验丹等级为角色等级
				tempDict = item.addToDict()
				del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
				itemData = cPickle.dumps( tempDict, 2 )
				itemDatas.append( itemData )
			BigWorld.globalData["MailMgr"].send(None, e, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, cschannel_msgs.SHARE_SYSTEM,cschannel_msgs.TONGABATTOIR_MAIL_EXP_TITLE, "", 0, itemDatas)
		
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_ABA_END, [] )
		self.clearData()	# 清空数据

	def clearData( self ):
		"""
		清除数据，不影响新的一次擂台赛
		"""
		#self.onEndEnter()
		# 恢复玩家的集合按钮状态
		for tongDBID in self.abattoirAntagonistDict.keys():
			tongBase = self.findTong( tongDBID )
			if tongBase:
				tongBase.tongAbaCloseGather()
		
		#self.abattoirCount = 0					# 当前擂台赛进行的轮数
		#self.abattoirFamilyDBIDList = []		# 报名参加擂台赛的帮会dbid列表
		self.abattoirWinerList = []				# 胜利帮会dbid列表
		self.abattoirAntagonistDict.clear()		# 参加擂台赛的帮会数据
		self.aba_quarterfinalStartTime = 0.0	# 清零四分之一比赛的开始时间
		self.aba_semifinalStartTime = 0.0		# 清零二分之一赛的开始时间
		self.aba_finalStartTime = 0.0			# 清零决赛开始时间
		self.nextStartTime = 0.0
		self.abattoirLoserList = []
		self.joinPlayer = {}
		self.enterTongDBID = []
		self.lunkongTongDBID = []
		
		self.statu = 0
		self.firstRoundFlag = False
		
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_OVER		#活动结束，全局tongAbaStep为0
		if BigWorld.globalData.has_key( "tongAbaRound" ):
			del BigWorld.globalData["tongAbaRound"]
		if BigWorld.globalData.has_key("TongAba_signUp_one"):
			del BigWorld.globalData["TongAba_signUp_one"]
		
		if self.aba_startTimer2 > 0:
			self.delTimer( self.aba_startTimer2 )
			self.aba_startTimer2 = 0
		elif self.aba_startTimer3 > 0:
			self.delTimer( self.aba_startTimer3 )
			self.aba_startTimer3 = 0
		elif self.aba_startTimer4 > 0:
			self.delTimer( self.aba_startTimer4 )
			self.aba_startTimer4 = 0
		elif self.aba_endTimer > 0:
			self.delTimer( self.aba_endTimer )
			self.aba_endTimer = 0
			
		if self.notice1 > 0:
			self.delTimer( self.notice1 )
			self.notice1 = 0
		if self.notice2 > 0:
			self.delTimer( self.notice2 )
			self.notice2 = 0
		if self.notice3 > 0:
			self.delTimer( self.notice3 )
			self.notice3 = 0
		if self.notice4 > 0:
			self.delTimer( self.notice4 )
			self.notice4 = 0
		if self.signUpNotice1 > 0:
			self.delTimer( self.signUpNotice1 )
			self.signUpNotice1 = 0
		if self.signUpNotice2 > 0:
			self.delTimer( self.signUpNotice2 )
			self.signUpNotice2 = 0
		if self.abaStartNotice1 > 0:
			self.delTimer( self.abaStartNotice1 )
			self.abaStartNotice1 = 0
		if self.abaStartNotice2 > 0:
			self.delTimer( self.abaStartNotice2 )
			self.abaStartNotice2 = 0
		if self.abaStartNotice3 > 0:
			self.delTimer( self.abaStartNotice3 )
			self.abaStartNotice3 = 0
		if self.abaStartNotice4 > 0:
			self.delTimer( self.abaStartNotice4 )
			self.abaStartNotice4 = 0
		if self.abaStart > 0:
			self.delTimer( self.abaStart )
			self.abaStart = 0
		if self.endEnterTimer > 0:
			self.delTimer( self.endEnterTimer )
			self.endEnterTimer = 0
	
	def requestAbattoir( self, playerBaseMailbox, tongDBID ):
		"""
		Define method.
		请求参加帮会擂台赛

		@param playerBaseMailbox : 帮主basemailbox
		@type playerBaseMailbox : MAILBOX
		@param tongDBID : 申请帮会的dbid
		@type tongDBID : DATABASE_ID
		"""
		if not self.isAbattoirSignUp():
			self.abaStatusMessage( playerBaseMailbox, csstatus.TONG_ABATTOIR_NOT_SIGN_UP_TIME )
			return
		if self.isAbattoirSignUpFull():
			self.abaStatusMessage( playerBaseMailbox, csstatus.TONG_ABATTOIR_SIGN_UP_FULL )
			return
		if tongDBID in self.abattoirTongDBIDList:
			self.abaStatusMessage( playerBaseMailbox, csstatus.TONG_ABATTOIR_SIGN_UP_TWICE )
			return
		self.abattoirTongDBIDList.append( tongDBID )
		
		self.onAbaMessage( tongDBID, csstatus.TONG_ABATTOIR_SIGN_UP )
		self.onAbaMessage( tongDBID, csstatus.TONG_ABATTOIR_READY_FOR )
		
		g_logger.actJoinLog( csdefine.ACTIVITY_BANG_HUI_LEI_TAI, csdefine.ACTIVITY_JOIN_TONG, tongDBID, self.getTongNameByDBID( tongDBID ) )
		

	def onAbaMessage( self, tongDBID, statusID, *args ):
		"""
		擂台赛相关统一系统通报 向指定帮会通报
		"""
		if args == ():
			tempArgs = ""
		else:
			tempArgs = str( args )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onStatusMessage( statusID, tempArgs )

	def abaStatusMessage( self, playerBase, statusID, *args ):
		"""
		擂台赛状态信息发送函数
		"""
		if args == ():
			tempArgs = ""
		else:
			tempArgs = str( args )
		playerBase.client.onStatusMessage( statusID, tempArgs )

	#-----------------------------------------------------------------任务计划相关------------------------------------------
	def tongAbattoirMgr_registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"TongAbattoirWar_start_notice" : "onTongAbattoirWarStartNotice",
					  	"TongAbattoirWar_signup_start" : "onTongAbattoirWarSignUpStart",
					  	"TongAbattoirWar_signup_end"   : "onTongAbattoirWarSignUpEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def onTongAbattoirWarStartNotice( self ):
		"""
		defined method.
		活动开始通知
		"""
		self.clearData()		# 清空数据，为了GM指令开启活动
		self.statu = NOTICE
		self.notice1 = self.addTimer( 15 * 60 )
		self.notice2 = self.addTimer( 30 * 60 )
		self.notice3 = self.addTimer( 45 * 60 )
		self.notice4 = self.addTimer( 59 * 60 )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_BEGIN_NOTIFY % str( 60 ), [] )

	def onTongAbattoirWarSignUpStart( self ):
		"""
		defined method.
		报名开始
		"""
		if self.notice1 > 0:
			self.delTimer( self.notice1 )
			self.notice1 = 0
		if self.notice2 > 0:
			self.delTimer( self.notice2 )
			self.notice2 = 0
		if self.notice3 > 0:
			self.delTimer( self.notice3 )
			self.notice3 = 0
		if self.notice4 > 0:
			self.delTimer( self.notice4 )
			self.notice4 = 0
			
		self.statu = SIGNUP
		self.abattoirTongDBIDList = []		# 清空--报名参加擂台赛的帮会dbid列表
		self.openAbattoirSignUp()
		BigWorld.globalData[ "tongAbattoirChampionDBID" ] = []			# 清空上次擂台赛冠军玩家的DBID


	def onTongAbattoirWarSignUpEnd( self ):
		"""
		defined method.
		报名结束
		"""
		
		if self.signUpNotice1 > 0:
			self.delTimer( self.signUpNotice1 )
			self.signUpNotice1 = 0
		if self.signUpNotice2 > 0:
			self.delTimer( self.signUpNotice2 )
			self.signUpNotice2 = 0
			
		self.statu = 0
		self.closeAbattoirSignUp()
		if len( self.abattoirTongDBIDList[:] ) < 1:
			self.aba_endTimer = self.addTimer( 6 * 60 )
		
		elif len( self.abattoirTongDBIDList[:] ) == 1:
			BigWorld.globalData["TongAba_signUp_one"] = True
			BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_EIGHTHFINAL
			self.aba_eighthfinalStartTime = BigWorld.time()
			self.aba_endTimer = self.addTimer( 6 * 60 )
		
		elif len( self.abattoirTongDBIDList[:] ) == 2:
			BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_FINAL
			self.aba_finalStartTime = BigWorld.time()
			self.aba_endTimer = self.addTimer( 21 * 60 )			# 21分钟后结束擂台赛，考虑网络传输的延时，不妨21分钟后处理
		
		elif len( self.abattoirTongDBIDList[:] ) > 2:			# 如果大于2个，需要进入下一轮
			self.aba_startTimer2 = self.addTimer( 20 * 60 )		# 20分钟后第二轮比赛入场
			self.nextStartTime = BigWorld.time() + 20 * 60
			BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_EIGHTHFINAL
			self.aba_eighthfinalStartTime = BigWorld.time()
		
		self.abattoirAntagonistDict.clear()
		self.initAbattoirWar( self.getAbaRound(), self.abattoirTongDBIDList[:] )	# 初始化比赛数据

	def onInputEndGM( self ):
		"""
		defined method
		
		调用GM指令进入不同的活动阶段
		"""
		if self.statu == NOTICE:		# 如果在公告阶段输入指令，结束公告
			self.onTongAbattoirWarSignUpStart()
		
		elif self.statu == SIGNUP:		# 如果在报名阶段输入指令，结束报名
			self.onTongAbattoirWarSignUpEnd()

	#----------------------------------------------------------------------------------------------------------------------
	def onTimer( self, timerID, cbid ):
		"""
		timer触发
		"""
		if timerID == self.abaStart:
			self.startAbattoir()
			self.abaStart = 0
		elif timerID == self.endEnterTimer:
			self.onEndEnter()
			self.endEnterTimer = 0
		elif timerID == self.aba_startTimer2:
			self.aba_startTimer2 = 0
			self.firstRoundFlag = False
			if len( self.abattoirWinerList ) > 4:					#如果参赛帮会大于四个，进行的是四分之一决赛
				self.aba_startTimer3 = self.addTimer( 20 * 60 )		# 20分钟后第三轮比赛入场
				self.nextStartTime = BigWorld.time() + 20 * 60
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_QUARTERFINAL
				self.aba_quarterfinalStartTime = BigWorld.time()	#记录赛开始的时间（为了倒计时）
			elif len( self.abattoirWinerList ) > 2:					#如果参赛帮会大于两个而小于等于4个，进行半决赛
				self.aba_startTimer3 = self.addTimer( 20 * 60 )		# 20分钟后第三轮比赛入场
				self.nextStartTime = BigWorld.time() + 20 * 60
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_SEMIFINAL
				self.aba_semifinalStartTime = BigWorld.time()
			else:
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_FINAL
				self.aba_finalStartTime = BigWorld.time()
				self.aba_endTimer = self.addTimer( 22 * 60 )			# 22分钟后结束擂台赛，考虑网络传输的延时，不妨22分钟后处理
			self.abattoirAntagonistDict.clear()		# 清除，参加擂台赛的帮会数据
			self.initAbattoirWar( self.getAbaRound(), self.abattoirWinerList )
			self.aba_startTimer2 = 0
		elif timerID == self.aba_startTimer3:
			self.aba_startTimer3 = 0
			if len( self.abattoirWinerList ) > 2:
				self.aba_startTimer4 = self.addTimer( 20 * 60 )		# 20分钟后第四轮比赛入场
				self.nextStartTime = BigWorld.time() + 20 * 60
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_SEMIFINAL
				self.aba_semifinalStartTime = BigWorld.time()
			else:
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_FINAL
				self.aba_finalStartTime = BigWorld.time()
				self.aba_endTimer = self.addTimer( 22 * 60 )			# 22分钟后结束擂台赛，考虑网络传输的延时，不妨22分钟后处理
			self.abattoirAntagonistDict.clear()		# 清除，参加擂台赛的帮会数据
			self.initAbattoirWar( self.getAbaRound(), self.abattoirWinerList )
			self.aba_startTimer3 = 0
		elif timerID == self.aba_startTimer4:
			self.aba_startTimer4 = 0
			BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_FINAL
			self.aba_endTimer = self.addTimer( 22 * 60 )			# 22分钟后结束擂台赛，考虑网络传输的延时，不妨22分钟后处理
			self.abattoirAntagonistDict.clear()		# 清除，参加擂台赛的帮会数据
			self.initAbattoirWar( csdefine.ABATTOIR_FINAL, self.abattoirWinerList )
			self.aba_finalStartTime = BigWorld.time()
			self.aba_startTimer4 = 0
		elif timerID == self.aba_endTimer:
			self.aba_endTimer = 0
			self.endAbattoir()
		
		# 一系列通告
		elif timerID == self.notice1:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_BEGIN_NOTIFY % str( 45 ), [] )
			self.notice1 = 0
		elif timerID == self.notice2:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_BEGIN_NOTIFY % str( 30 ), [] )
			self.notice2= 0
		elif timerID == self.notice3:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_BEGIN_NOTIFY % str( 15 ), [] )
			self.notice3= 0
		elif timerID == self.notice4:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_BEGIN_NOTIFY % str( 1 ), [] )
			self.notice4= 0
		elif timerID == self.signUpNotice1:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_SIGN_UP % str( 5 ), [] )
			self.signUpNotice1= 0
		elif timerID == self.signUpNotice2:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_SIGN_UP % str( 1 ), [] )
			self.signUpNotice2= 0
		elif timerID == self.abaStartNotice1:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_END_SIGN_UP % str( 4 ), [] )
			self.abaStartNotice1= 0
		elif timerID == self.abaStartNotice2:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_END_SIGN_UP % str( 3 ), [] )
			self.abaStartNotice2= 0
		elif timerID == self.abaStartNotice3:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_END_SIGN_UP % str( 2 ), [] )
			self.abaStartNotice3= 0
		elif timerID == self.abaStartNotice4:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_END_SIGN_UP % str( 1 ), [] )
			self.abaStartNotice4 = 0

	def addAbaAward( self, awardLevel, tongDBID ):
		"""
		给胜利帮会加上相应奖励 给失败帮会相应惩罚

		@param awardLevel : 奖励级别，定义在csdefine中，例如：csdefine.ABATTOIR_QUARTERFINAL
		@type awardLevel : INT8
		@param tongDBID : 帮会的dbid
		@param tongDBID : DATABASE_ID
		"""
		tongBase = self.findTong( tongDBID )
		if tongBase is None:
			return
		tongBase.addPrestige( ABATTOIR_AWARD_WIN_MAP[ awardLevel ], csdefine.TONG_PRESTIGE_CHANGE_ABA )
		tongBase.onStatusMessage( csstatus.TONG_ABATTOIR_WIN_REWARD, str( ABATTOIR_AWARD_WIN_MAP[ awardLevel ] ) + ',' )
		
	def onMemberLeave( self, tongDBID ):
		"""
		Define method.
		离开擂台赛副本
		
		@param tongDBID 	: 离开擂台赛副本玩家帮会的dbID
		@type tongDBID		: DATABASE_ID
		"""
		self.abattoirAntagonistDict[ tongDBID ][ "memCount" ] -= 1

	def onMemberEnter( self, tongDBID ):
		"""
		Define method.
		进入擂台赛副本
		
		@param tongDBID 	: 进入擂台赛副本玩家帮会的dbID
		@type tongDBID		: DATABASE_ID
		"""
		self.abattoirAntagonistDict[ tongDBID ][ "memCount" ] += 1

	def onEnterAbattoirSpace( self, domainBase, position, direction, playerBase, params ):
		"""
		Define method.
		请求进入擂台赛副本

		@param domainBase : 空间对应的domain的base mailbox
		@type domainBase : MAILBOX
		@param position : 进入空间的初始位置
		@type position : VECTOR3
		@param direction : 进入空间的初始面向
		@type direction : VECTOR3
		@param playerBase : 玩家base mailbox
		@type playerBase : MAILBOX
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT
		"""
		tongDBID = params[ "tongDBID" ]					# 请求进入副本玩家的帮会dbid
		enterKeyDict = self.getEnterAbaDict( tongDBID )	# 获得进入擂台副本的凭证数据
		
		if self.isAbaLoser( tongDBID ):					# 如果已经是失败的帮会
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_ALREADY_LOSE )
		elif self.isAbaWinner( tongDBID ):				# 如果已经是胜利的帮会
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_ALREADY_WIN )
			
		elif self.isAbattoirStart():						#战争开始，不允许进入
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_HAS_OPENED )
		
		elif not self.isAbattoirEnter():					# 不处于入场时间
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_NOT_OPEN )
		
		elif not enterKeyDict:						# 如果没有该帮会的擂台赛存在
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_NOT_JOIN )
			ERROR_MSG( "enter abattoir space error!!can not find tong name!!" )
			
		elif self.abattoirAntagonistDict[ tongDBID ][ "memCount" ] >= csconst.TONG_ABATTOIR_MAX_MEMBER:	#帮会战场人数到达上限
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_NUMBER_LIMIT )
			
		else:
			if params.has_key( "login" ):		# 登录,让他登录进副本
				domainBase.onLoginAbattoirSpace( True, playerBase, enterKeyDict )
			else:								# 一切条件都符合，进入副本
				domainBase.onEnterAbattoirSpace( True, playerBase, enterKeyDict )
			if tongDBID not in self.enterTongDBID:
				self.enterTongDBID.append( tongDBID )
			return
		if params.has_key( "login" ):		# 登录,副本那边有处理,让他回到上一次到达的地图
			domainBase.onLoginAbattoirSpace( False, playerBase, {} )
		

	def isAbaWinner( self, tongDBID ):
		"""
		判断是否胜利帮会
		"""
		return tongDBID in self.abattoirWinerList

	def isAbaLoser( self, tongDBID ):
		"""
		判断是否失败帮会
		"""
		return tongDBID in self.abattoirLoserList

	def getEnterAbaDict( self, tongDBID ):
		"""
		获得帮会进入擂台副本的凭证数据
		"""
		if not self.abattoirAntagonistDict.has_key( tongDBID ):
			return { }
		opponentTongDBID = self.abattoirAntagonistDict[ tongDBID ][ "opponentDBID" ]
		isRight = self.abattoirAntagonistDict[ tongDBID ][ "isRight" ]
		tongName1 = self.getTongNameByDBID( tongDBID )
		tongName2 = self.getTongNameByDBID( opponentTongDBID )
		memCount = self.abattoirAntagonistDict[ tongDBID ][ "memCount" ]
		if tongName1 is None:
			return { }
		return { "tongDBID1":tongDBID, "tongName1":tongName1, "tongDBID2":opponentTongDBID, "tongName2":tongName2, "isRight":isRight,"spaceKey":tongDBID }


	def onTongAbaOverFromSpace( self, winnerTongDBID,foreEnd ):
		"""
		Define method.
		副本通知帮会擂台赛结束了(有胜利者)

		@param winnerTongDBID : 胜利帮会dbid
		@type winnerTongDBID : DATABASE_ID
		"""
		DEBUG_MSG( "winnerTongDBID", winnerTongDBID )
		if winnerTongDBID == 0:	# 约定winnerTongDBID为0则没有胜利者
			return
		if BigWorld.globalData.has_key("TongAba_signUp_one"):
			if winnerTongDBID not in self.abattoirWinerList:
				self.abattoirWinerList.append( winnerTongDBID )
			tongBase = self.findTong( winnerTongDBID )
			if tongBase:
				tongBase.updateTongAbaRound( csdefine.ABATTOIR_GAME_NONE )
			return
		
		opponentDBID = self.abattoirAntagonistDict[ winnerTongDBID ][ "opponentDBID" ]
		opponentTongName = self.getTongNameByDBID( opponentDBID )
		self.abattoirWinerList.append( winnerTongDBID )
		self.abattoirLoserList.append( opponentDBID )
		round = self.getAbaRound()
		self.addAbaAward( round, winnerTongDBID )

		if not foreEnd:
			if round != csdefine.ABATTOIR_FINAL:
				self.onAbaMessage( winnerTongDBID, csstatus.TONG_ABATTOIR_WIN, opponentTongName, int((self.nextStartTime - BigWorld.time())/60) )
			self.onAbaMessage( opponentDBID, csstatus.TONG_ABATTOIR_LOSE )
		tongBase = self.findTong( opponentDBID )
		if tongBase:
			tongBase.updateTongAbaRound( csdefine.ABATTOIR_GAME_NONE )		# 将失败帮会的当前比赛情况信息重置
		
		if round == csdefine.ABATTOIR_FINAL:		# 如果是决赛，将胜利帮会的当前比赛情况信息重置
			tongBase = self.findTong( winnerTongDBID )
			if tongBase:
				tongBase.updateTongAbaRound( csdefine.ABATTOIR_GAME_NONE )
			self.aba_endTimer = self.addTimer( 2 * 60 )
			
		self.firstRoundFlag = False			# 第一轮比赛结束时恢复该标志

	def onTongAbaOverFromSpaceNoWinner( self, tong1DBID, tong2DBID, foreEnd ):
		"""
		Define method.
		副本通知帮会擂台赛结束了(无胜利者)
		"""
		self.abattoirLoserList.append( tong1DBID )
		self.abattoirLoserList.append( tong2DBID )
		if not foreEnd:		# 如果是在入场结束时决出胜负，不提示“放弃比赛”
			self.onAbaMessage( tong1DBID, csstatus.TONG_ABATTOIR_LOSE )
			self.onAbaMessage( tong2DBID, csstatus.TONG_ABATTOIR_LOSE )
		
		tongBase = self.findTong( tong1DBID )
		if tongBase:
			tongBase.updateTongAbaRound( csdefine.ABATTOIR_GAME_NONE )
		tongBase = self.findTong( tong2DBID )
		if tongBase:
			tongBase.updateTongAbaRound( csdefine.ABATTOIR_GAME_NONE )
		
		round = self.getAbaRound()
		if round == csdefine.ABATTOIR_FINAL:
			self.aba_endTimer = self.addTimer( 2 * 60 )
		
		self.firstRoundFlag = False

	def getAbaRound( self ):
		"""
		根据当前时间获得擂台赛的轮次
		"""
		try:
			return BigWorld.globalData["tongAbaRound"]
		except KeyError:
			return csdefine.ABATTOIR_GAME_NONE

	def requestAbaData( self, spaceBaseMB ):
		"""
		Define method.
		擂台赛空间请求擂台赛的时间进度

		@param spaceBaseMB : 擂台赛空间的base mailbox
		"""
		round = self.getAbaRound()
		if round == csdefine.ABATTOIR_EIGHTHFINAL:
			startTime = self.aba_eighthfinalStartTime
		elif round == csdefine.ABATTOIR_QUARTERFINAL:
			startTime = self.aba_quarterfinalStartTime
		elif round == csdefine.ABATTOIR_SEMIFINAL:
			startTime = self.aba_semifinalStartTime
		elif round == csdefine.ABATTOIR_FINAL:
			startTime = self.aba_finalStartTime
		else:
			startTime = 0
		spaceBaseMB.cell.receiveAbaData( round, startTime )
		
	def recordJoinPlayer( self,playerName,playerBase,level ):
		"""
		defined method
		
		记录参加帮会擂台的玩家信息，用于发放参与经验奖
		"""
		self.joinPlayer[ playerName ] = [ playerBase,level ]
	
	def recordRound( self,playerDBID, matchType, scoreOrRound, playerBase = None ):
		"""
		defined method
		
		记录玩家比赛级别
		"""
		RoleMatchRecorder.update( playerDBID, matchType, scoreOrRound, playerBase )
	
	def updateEnterTong( self,tongDBID ):
		"""
		defined method
		在入场帮会列表中删除比赛前就离场的帮会的DBID
		"""
		if tongDBID in self.enterTongDBID:
			self.enterTongDBID.remove( tongDBID )
	
	def addEnterTong( self,tongDBID ):
		"""
		defined method
		进入副本时添加改帮会的入场记录
		"""
		if tongDBID not in self.enterTongDBID:
			self.enterTongDBID.append( tongDBID )
