# -*- coding: gb18030 -*-
#
#$Id:$


"""
8:22 2008-9-9,writen by wangshufeng
"""
"""
2010.11
������̨��ֲΪ�����̨ by cxm
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

ABATTOIR_SIGN_UP_POINT = [ 12, 30, 0 ]		# ��̨����ʼ����ʱ�䣬12ʱ30��0��
ABATTOIR_END_SIGN_UP_POINT = [ 12, 40, 0 ]	# ��̨����������ʱ�䣬12ʱ40��0��

# ��̨��������{ �ִ�: ����/�ͷ����� }
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
	�����̨������ģ��

	Abattoir���Ƕ���
	"""
	def __init__( self ):
		"""
		"""
		#self.abattoirCount = 0				# ��ǰ��̨�����е�����
		self.abattoirTongDBIDList = []		# �����μ���̨���İ��dbid�б�
		self.abattoirWinerList = []			# ʤ�����dbid�б�
		self.abattoirLoserList = []			# ʧ�ܰ��dbid�б�
		self.abattoirAntagonistDict = {}	# �μ���̨���İ������{ ���dbid:{ ����dbid:dbid����ս���еı��:right��left������ڸ���������:memCount }, ... }
		self.abattoirLastTongDBIDList = []  # ��̨����һ�ְ��dbid�б�(Ϊ����ʾû�н�������İ��)
		self.joinPlayer = {}

		self.aba_eighthfinalStartTime = 0.0		# ��¼�˷�֮һ����ʼ������ʱ��ʱ��
		self.aba_quarterfinalStartTime = 0.0	# ��¼�ķ�֮һ����ʼ������ʱ��ʱ��
		self.aba_semifinalStartTime = 0.0		# ��¼����֮һ����ʼ������ʱ��ʱ��
		self.aba_finalStartTime = 0.0			# ��¼������ʼ������ʱ��ʱ��
		self.nextStartTime = 0.0				# ��һ�ִο�ʼʱ��(Ϊ����ʾ)

		self.aba_startTimer2 = 0			# ��̨���ڶ����볡timerID
		self.aba_startTimer3 = 0			# ��̨���������볡timerID
		self.aba_startTimer4 = 0			# ��̨���������볡timerID
		self.aba_endTimer = 0				# ��̨��������timerID
		
		self.notice1 = 0			# �ڶ��ι����timerID
		self.notice2 = 0 			# �����ι����timerID
		self.notice3 = 0 			# ���Ĵι����timerID
		self.notice4 = 0 			# ����ι����timerID
		self.signUpNotice1 = 0			# ��ʼ�����ڶ��ι����timeID
		self.signUpNotice2 = 0			# ��ʼ���������ι����timeID
		
		self.abaStartNotice1 = 0		# ��볡�ڶ��ι����timerID
		self.abaStartNotice2 = 0		# ��볡�����ι����timerID
		self.abaStartNotice3 = 0		# ��볡���Ĵι����timerID
		self.abaStartNotice4 = 0		# ��볡����ι����timerID
		
		self.abaStart = 0		# ���ֱ����볡����timerID
		self.endEnterTimer = 0		# �볡����timerID
		
		self.statu = 0
		self.firstRoundFlag = False
		self.enterTongDBID = []		# ��¼���븱���İ��DBID
		self.lunkongTongDBID = []		# ��¼�ֿհ���DBID
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_OVER		#�����̨�Ľ׶�(δ����)
		
	def onManagerInitOver( self ):
		"""
		virtual method.
		���ϵͳ�������֪ͨ
		"""
		self.tongAbattoirMgr_registerCrond()

	def isAbattoirStart( self ):
		"""
		��̨���Ƿ�ʼ
		"""
		return BigWorld.globalData[ "tongAbaStep" ] == csconst.TONG_ABATTOIR_START

	def isAbattoirSignUp( self ):
		"""
		��̨�������Ƿ�ʼ
		"""
		return BigWorld.globalData[ "tongAbaStep" ] == csconst.TONG_ABATTOIR_SINGUP

	def isAbattoirEnter( self ):
		"""
		��̨���Ƿ�Ϊ�볡ʱ��
		"""
		return BigWorld.globalData[ "tongAbaStep" ] == csconst.TONG_ABATTOIR_ENTER

	def isAbattoirSignUpFull( self ):
		"""
		��������Ƿ���
		"""
		return len( self.abattoirTongDBIDList ) >= csconst.TONG_ABATTOIR_MAX_NUM

	def openAbattoirSignUp( self ):
		"""
		���������̨����
		"""
		self.signUpNotice1 = self.addTimer( 5 * 60 )
		self.signUpNotice2 = self.addTimer( 9 * 60 )
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_SINGUP
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_SIGN_UP % str( 10 ), [] )

	def closeAbattoirSignUp( self ):
		"""
		�رհ����̨���������볡
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
		�����Ƕ�������̨����ʼ��
		"""
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_START
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_START, [] )
		self.firstRoundFlag = True

	def isTongJoinAba( self, tongDBID ):
		"""
		tongDBID����Ƿ�μ���̨��
		"""
		return tongDBID in self.abattoirTongDBIDList

	def sendGiveUpMessage( self ):
		"""
		��ʾ����������
		"""
		# �����һ��û�вμӱ�����������ʾ��Ϣ��
		for e in self.abattoirLastTongDBIDList:
			if not (self.isAbaWinner( e ) or self.isAbaLoser( e )):
				tongBase = self.findTong( e )		# ���û���������İ���Ա�ĵ�ǰ���������Ϣ
				if tongBase:
					tongBase.updateTongAbaRound( csdefine.ABATTOIR_GAME_NONE )
				self.onAbaMessage( e, csstatus.TONG_ABATTOIR_GIVE_UP )

	def initAbattoirWar( self, matchLevel, tongDBIDList ):
		"""
		��ʼ����̨������

		@param matchLevel : �����ȼ���������csdefine��
		@type matchLevel : INT8
		@param tongDBIDList : �μӱ��ְ����̨���İ��dbid�б�
		@type tongDBIDList : DATABASE_ID
		"""
		DEBUG_MSG( "tongDBIDList", tongDBIDList )
		self.abattoirLastTongDBIDList = tongDBIDList[:]
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_ENTER
		if len( tongDBIDList ) == 1:
			# ���ֻ��һ����ᱨ����Ҳ���Խ��븱������������Ҫ���⴦��
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
			
		self.abattoirWinerList = []		# ���ʤ����
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
		if tongDBIDList:				# �����ˣ������ֿյİ�ᣬ������һ��
			self.lunkongTongDBID = tongDBIDList
			winTongDBID = tongDBIDList[ 0 ]
			self.abattoirWinerList.append( winTongDBID )
			self.onAbaMessage( winTongDBID, csstatus.TONG_ABATTOIR_BYE )
		self.endEnterTimer = self.addTimer( 5 * 60 + 2 )

	def onEndEnter( self ):
		"""
		�����볡����ʱ֪ͨ������Ҽ��Ͻ���
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
				
				if opponentDBID not in self.enterTongDBID:				# �������������ᶼδ������������Ҫ�����������������İ��ӵ�ʧ�ܰ����
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
				else:			# ֻҪ��һ�԰�ỹ�ڸ����оͲ���ǰ�����
					foreEnd = False
		if foreEnd:
			if len( self.abattoirWinerList ) <= 1:
				# �ֿհ���ùھ�ʱ�������������
				if len( self.abattoirWinerList ) == 1 and self.abattoirWinerList[0] in self.lunkongTongDBID:
					self.addAbaAward( self.getAbaRound(), self.abattoirWinerList[0] )
				self.aba_endTimer = self.addTimer( 1 )		# �ӳ�һ�����
		self.enterTongDBID = []

	def endAbattoir( self ):
		"""
		defined method
		
		�����̨��������������ݣ�������һ�ΰ����̨���Ŀ�ʼ��timer
		"""
		if not BigWorld.globalData["tongAbaStep"]:		# �����Ѿ�������ȫ��tongAbaStepΪ0
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
				item.setLevel( self.joinPlayer[e][1])		# ���þ��鵤�ȼ�Ϊ��ɫ�ȼ�
				tempDict = item.addToDict()
				del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
				itemData = cPickle.dumps( tempDict, 2 )
				itemDatas.append( itemData )
			BigWorld.globalData["MailMgr"].send(None, e, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, cschannel_msgs.SHARE_SYSTEM,cschannel_msgs.TONGABATTOIR_MAIL_EXP_TITLE, "", 0, itemDatas)
		
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_ABA_END, [] )
		self.clearData()	# �������

	def clearData( self ):
		"""
		������ݣ���Ӱ���µ�һ����̨��
		"""
		#self.onEndEnter()
		# �ָ���ҵļ��ϰ�ť״̬
		for tongDBID in self.abattoirAntagonistDict.keys():
			tongBase = self.findTong( tongDBID )
			if tongBase:
				tongBase.tongAbaCloseGather()
		
		#self.abattoirCount = 0					# ��ǰ��̨�����е�����
		#self.abattoirFamilyDBIDList = []		# �����μ���̨���İ��dbid�б�
		self.abattoirWinerList = []				# ʤ�����dbid�б�
		self.abattoirAntagonistDict.clear()		# �μ���̨���İ������
		self.aba_quarterfinalStartTime = 0.0	# �����ķ�֮һ�����Ŀ�ʼʱ��
		self.aba_semifinalStartTime = 0.0		# �������֮һ���Ŀ�ʼʱ��
		self.aba_finalStartTime = 0.0			# ���������ʼʱ��
		self.nextStartTime = 0.0
		self.abattoirLoserList = []
		self.joinPlayer = {}
		self.enterTongDBID = []
		self.lunkongTongDBID = []
		
		self.statu = 0
		self.firstRoundFlag = False
		
		BigWorld.globalData[ "tongAbaStep" ] = csconst.TONG_ABATTOIR_OVER		#�������ȫ��tongAbaStepΪ0
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
		����μӰ����̨��

		@param playerBaseMailbox : ����basemailbox
		@type playerBaseMailbox : MAILBOX
		@param tongDBID : �������dbid
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
		��̨�����ͳһϵͳͨ�� ��ָ�����ͨ��
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
		��̨��״̬��Ϣ���ͺ���
		"""
		if args == ():
			tempArgs = ""
		else:
			tempArgs = str( args )
		playerBase.client.onStatusMessage( statusID, tempArgs )

	#-----------------------------------------------------------------����ƻ����------------------------------------------
	def tongAbattoirMgr_registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
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
		���ʼ֪ͨ
		"""
		self.clearData()		# ������ݣ�Ϊ��GMָ����
		self.statu = NOTICE
		self.notice1 = self.addTimer( 15 * 60 )
		self.notice2 = self.addTimer( 30 * 60 )
		self.notice3 = self.addTimer( 45 * 60 )
		self.notice4 = self.addTimer( 59 * 60 )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHLT_BEGIN_NOTIFY % str( 60 ), [] )

	def onTongAbattoirWarSignUpStart( self ):
		"""
		defined method.
		������ʼ
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
		self.abattoirTongDBIDList = []		# ���--�����μ���̨���İ��dbid�б�
		self.openAbattoirSignUp()
		BigWorld.globalData[ "tongAbattoirChampionDBID" ] = []			# ����ϴ���̨���ھ���ҵ�DBID


	def onTongAbattoirWarSignUpEnd( self ):
		"""
		defined method.
		��������
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
			self.aba_endTimer = self.addTimer( 21 * 60 )			# 21���Ӻ������̨�����������紫�����ʱ������21���Ӻ���
		
		elif len( self.abattoirTongDBIDList[:] ) > 2:			# �������2������Ҫ������һ��
			self.aba_startTimer2 = self.addTimer( 20 * 60 )		# 20���Ӻ�ڶ��ֱ����볡
			self.nextStartTime = BigWorld.time() + 20 * 60
			BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_EIGHTHFINAL
			self.aba_eighthfinalStartTime = BigWorld.time()
		
		self.abattoirAntagonistDict.clear()
		self.initAbattoirWar( self.getAbaRound(), self.abattoirTongDBIDList[:] )	# ��ʼ����������

	def onInputEndGM( self ):
		"""
		defined method
		
		����GMָ����벻ͬ�Ļ�׶�
		"""
		if self.statu == NOTICE:		# ����ڹ���׶�����ָ���������
			self.onTongAbattoirWarSignUpStart()
		
		elif self.statu == SIGNUP:		# ����ڱ����׶�����ָ���������
			self.onTongAbattoirWarSignUpEnd()

	#----------------------------------------------------------------------------------------------------------------------
	def onTimer( self, timerID, cbid ):
		"""
		timer����
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
			if len( self.abattoirWinerList ) > 4:					#��������������ĸ������е����ķ�֮һ����
				self.aba_startTimer3 = self.addTimer( 20 * 60 )		# 20���Ӻ�����ֱ����볡
				self.nextStartTime = BigWorld.time() + 20 * 60
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_QUARTERFINAL
				self.aba_quarterfinalStartTime = BigWorld.time()	#��¼����ʼ��ʱ�䣨Ϊ�˵���ʱ��
			elif len( self.abattoirWinerList ) > 2:					#�������������������С�ڵ���4�������а����
				self.aba_startTimer3 = self.addTimer( 20 * 60 )		# 20���Ӻ�����ֱ����볡
				self.nextStartTime = BigWorld.time() + 20 * 60
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_SEMIFINAL
				self.aba_semifinalStartTime = BigWorld.time()
			else:
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_FINAL
				self.aba_finalStartTime = BigWorld.time()
				self.aba_endTimer = self.addTimer( 22 * 60 )			# 22���Ӻ������̨�����������紫�����ʱ������22���Ӻ���
			self.abattoirAntagonistDict.clear()		# ������μ���̨���İ������
			self.initAbattoirWar( self.getAbaRound(), self.abattoirWinerList )
			self.aba_startTimer2 = 0
		elif timerID == self.aba_startTimer3:
			self.aba_startTimer3 = 0
			if len( self.abattoirWinerList ) > 2:
				self.aba_startTimer4 = self.addTimer( 20 * 60 )		# 20���Ӻ�����ֱ����볡
				self.nextStartTime = BigWorld.time() + 20 * 60
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_SEMIFINAL
				self.aba_semifinalStartTime = BigWorld.time()
			else:
				BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_FINAL
				self.aba_finalStartTime = BigWorld.time()
				self.aba_endTimer = self.addTimer( 22 * 60 )			# 22���Ӻ������̨�����������紫�����ʱ������22���Ӻ���
			self.abattoirAntagonistDict.clear()		# ������μ���̨���İ������
			self.initAbattoirWar( self.getAbaRound(), self.abattoirWinerList )
			self.aba_startTimer3 = 0
		elif timerID == self.aba_startTimer4:
			self.aba_startTimer4 = 0
			BigWorld.globalData["tongAbaRound"] = csdefine.ABATTOIR_FINAL
			self.aba_endTimer = self.addTimer( 22 * 60 )			# 22���Ӻ������̨�����������紫�����ʱ������22���Ӻ���
			self.abattoirAntagonistDict.clear()		# ������μ���̨���İ������
			self.initAbattoirWar( csdefine.ABATTOIR_FINAL, self.abattoirWinerList )
			self.aba_finalStartTime = BigWorld.time()
			self.aba_startTimer4 = 0
		elif timerID == self.aba_endTimer:
			self.aba_endTimer = 0
			self.endAbattoir()
		
		# һϵ��ͨ��
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
		��ʤ����������Ӧ���� ��ʧ�ܰ����Ӧ�ͷ�

		@param awardLevel : �������𣬶�����csdefine�У����磺csdefine.ABATTOIR_QUARTERFINAL
		@type awardLevel : INT8
		@param tongDBID : ����dbid
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
		�뿪��̨������
		
		@param tongDBID 	: �뿪��̨��������Ұ���dbID
		@type tongDBID		: DATABASE_ID
		"""
		self.abattoirAntagonistDict[ tongDBID ][ "memCount" ] -= 1

	def onMemberEnter( self, tongDBID ):
		"""
		Define method.
		������̨������
		
		@param tongDBID 	: ������̨��������Ұ���dbID
		@type tongDBID		: DATABASE_ID
		"""
		self.abattoirAntagonistDict[ tongDBID ][ "memCount" ] += 1

	def onEnterAbattoirSpace( self, domainBase, position, direction, playerBase, params ):
		"""
		Define method.
		���������̨������

		@param domainBase : �ռ��Ӧ��domain��base mailbox
		@type domainBase : MAILBOX
		@param position : ����ռ�ĳ�ʼλ��
		@type position : VECTOR3
		@param direction : ����ռ�ĳ�ʼ����
		@type direction : VECTOR3
		@param playerBase : ���base mailbox
		@type playerBase : MAILBOX
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT
		"""
		tongDBID = params[ "tongDBID" ]					# ������븱����ҵİ��dbid
		enterKeyDict = self.getEnterAbaDict( tongDBID )	# ��ý�����̨������ƾ֤����
		
		if self.isAbaLoser( tongDBID ):					# ����Ѿ���ʧ�ܵİ��
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_ALREADY_LOSE )
		elif self.isAbaWinner( tongDBID ):				# ����Ѿ���ʤ���İ��
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_ALREADY_WIN )
			
		elif self.isAbattoirStart():						#ս����ʼ�����������
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_HAS_OPENED )
		
		elif not self.isAbattoirEnter():					# �������볡ʱ��
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_NOT_OPEN )
		
		elif not enterKeyDict:						# ���û�иð�����̨������
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_NOT_JOIN )
			ERROR_MSG( "enter abattoir space error!!can not find tong name!!" )
			
		elif self.abattoirAntagonistDict[ tongDBID ][ "memCount" ] >= csconst.TONG_ABATTOIR_MAX_MEMBER:	#���ս��������������
			self.abaStatusMessage( playerBase, csstatus.TONG_ABATTOIR_NUMBER_LIMIT )
			
		else:
			if params.has_key( "login" ):		# ��¼,������¼������
				domainBase.onLoginAbattoirSpace( True, playerBase, enterKeyDict )
			else:								# һ�����������ϣ����븱��
				domainBase.onEnterAbattoirSpace( True, playerBase, enterKeyDict )
			if tongDBID not in self.enterTongDBID:
				self.enterTongDBID.append( tongDBID )
			return
		if params.has_key( "login" ):		# ��¼,�����Ǳ��д���,�����ص���һ�ε���ĵ�ͼ
			domainBase.onLoginAbattoirSpace( False, playerBase, {} )
		

	def isAbaWinner( self, tongDBID ):
		"""
		�ж��Ƿ�ʤ�����
		"""
		return tongDBID in self.abattoirWinerList

	def isAbaLoser( self, tongDBID ):
		"""
		�ж��Ƿ�ʧ�ܰ��
		"""
		return tongDBID in self.abattoirLoserList

	def getEnterAbaDict( self, tongDBID ):
		"""
		��ð�������̨������ƾ֤����
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
		����֪ͨ�����̨��������(��ʤ����)

		@param winnerTongDBID : ʤ�����dbid
		@type winnerTongDBID : DATABASE_ID
		"""
		DEBUG_MSG( "winnerTongDBID", winnerTongDBID )
		if winnerTongDBID == 0:	# Լ��winnerTongDBIDΪ0��û��ʤ����
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
			tongBase.updateTongAbaRound( csdefine.ABATTOIR_GAME_NONE )		# ��ʧ�ܰ��ĵ�ǰ���������Ϣ����
		
		if round == csdefine.ABATTOIR_FINAL:		# ����Ǿ�������ʤ�����ĵ�ǰ���������Ϣ����
			tongBase = self.findTong( winnerTongDBID )
			if tongBase:
				tongBase.updateTongAbaRound( csdefine.ABATTOIR_GAME_NONE )
			self.aba_endTimer = self.addTimer( 2 * 60 )
			
		self.firstRoundFlag = False			# ��һ�ֱ�������ʱ�ָ��ñ�־

	def onTongAbaOverFromSpaceNoWinner( self, tong1DBID, tong2DBID, foreEnd ):
		"""
		Define method.
		����֪ͨ�����̨��������(��ʤ����)
		"""
		self.abattoirLoserList.append( tong1DBID )
		self.abattoirLoserList.append( tong2DBID )
		if not foreEnd:		# ��������볡����ʱ����ʤ��������ʾ������������
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
		���ݵ�ǰʱ������̨�����ִ�
		"""
		try:
			return BigWorld.globalData["tongAbaRound"]
		except KeyError:
			return csdefine.ABATTOIR_GAME_NONE

	def requestAbaData( self, spaceBaseMB ):
		"""
		Define method.
		��̨���ռ�������̨����ʱ�����

		@param spaceBaseMB : ��̨���ռ��base mailbox
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
		
		��¼�μӰ����̨�������Ϣ�����ڷ��Ų��뾭�齱
		"""
		self.joinPlayer[ playerName ] = [ playerBase,level ]
	
	def recordRound( self,playerDBID, matchType, scoreOrRound, playerBase = None ):
		"""
		defined method
		
		��¼��ұ�������
		"""
		RoleMatchRecorder.update( playerDBID, matchType, scoreOrRound, playerBase )
	
	def updateEnterTong( self,tongDBID ):
		"""
		defined method
		���볡����б���ɾ������ǰ���볡�İ���DBID
		"""
		if tongDBID in self.enterTongDBID:
			self.enterTongDBID.remove( tongDBID )
	
	def addEnterTong( self,tongDBID ):
		"""
		defined method
		���븱��ʱ��Ӹİ����볡��¼
		"""
		if tongDBID not in self.enterTongDBID:
			self.enterTongDBID.append( tongDBID )
