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

TITLE_ID_XIUCAI		= 30	# ��ųƺ�id
TITLE_ID_JUREN		= 31	# ���˳ƺ�id


class FuncImperialExaminations( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.exaCount = section.readInt( 'param1' )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		talkEntity.remoteScriptCall( "startExamination", ( player, self.exaCount ) )


	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
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
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.exaCount = section.readInt( "param1" )	# �ڼ���
		self.key1 = section.readString( "param2" )	# ������ȷ
		self.key2 = section.readString( "param3" )	# û�нӿƾ�����
		self.key3 = section.readString( "param4" )	# ���ٲ���ȷ
		self.key4 = section.readString( "param5" )	# û���ڿ���ʱ����

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		pass


	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
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
			# ��û�ӻ�������Ҳû����������
			dlgKey = self.key2
		elif ( questStateXiangshi == csdefine.QUEST_STATE_NOT_ALLOW or questStateXiangshi == csdefine.QUEST_STATE_NOT_HAVE ):
			# û�н��������񣬵��������л�������
			if not BigWorld.globalData.has_key( "AS_HuishiActivityStart" ):
				dlgKey = self.key4
			elif player.getCurrentExaID()+1 != self.exaCount:
				dlgKey = self.key3
			elif questStateHuishi == csdefine.QUEST_STATE_NOT_FINISH:
				dlgKey = self.key1
			else:
				dlgKey = self.key3
		else:
			# ����������
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
	���ԡ����Ա����Ի����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.key1 = section.readInt( "param1" )	# ��������id
		self.key2 = section.readInt( "param2" )	# ��������id

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		pass


	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if talkEntity is None:
			return False

		player.endGossip( talkEntity )
		questStateXiangshi = g_taskData[self.key1].query( player )	# ����״̬
		questStateHuishi = g_taskData[self.key2].query( player )	# ����״̬
		if BigWorld.globalData.has_key( "AS_XiangshiActivityStart" ):
			# ���Դ���
			if questStateXiangshi == csdefine.QUEST_STATE_NOT_ALLOW:
				# ���ܲμ����Կ���
				lpLog = player.getLoopQuestLog( self.key1, True )
				if lpLog.getDegree() >= player.getQuest( self.key1 )._finish_count:
					# �����Ѿ������������
					dataQuestID = str(time.localtime()[2])+':' + str( self.key1 )
					if dataQuestID in player.failedGroupQuestList:
						player.setGossipText( cschannel_msgs.KE_JU_VOICE_1 )
					else:
						player.setGossipText( cschannel_msgs.KE_JU_VOICE_2 )
				else:
					# ������μ����Ե�����
					player.setGossipText( cschannel_msgs.KE_JU_VOICE_3 )
				return False
			if questStateXiangshi == csdefine.QUEST_STATE_NOT_FINISH:
				# ���ڲμ����Կ���
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_4 )
				return False
			if questStateXiangshi != csdefine.QUEST_STATE_NOT_HAVE_LEVEL_SUIT:
				# ���Բμ����Կ��ԣ����Խ�������ôû�жԻ�
				return False
			else:
				# �������
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_1 )
				return False
		elif BigWorld.globalData.has_key( "AS_HuishiActivityStart" ):
			# ���Դ���
			if not player.hasTitle( TITLE_ID_XIUCAI ):
				# �����Ҳ�����ţ�������μӻ���
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_5 )
				return False
			if questStateHuishi == csdefine.QUEST_STATE_NOT_ALLOW:
				# ���ܲμӻ��Կ���
				lpLog = player.getLoopQuestLog( self.key2, True )
				if lpLog.getDegree() >= player.getQuest( self.key2 )._finish_count:
					dataQuestID = str(time.localtime()[2])+':' + str( self.key2 )
					# �����Ѿ�����˻�����
					if dataQuestID in player.failedGroupQuestList:
						player.setGossipText( cschannel_msgs.KE_JU_VOICE_6 )
					else:
						msg = cschannel_msgs.KE_JU_VOICE_7
						player.setGossipText( msg )
				else:
					# ������μӻ��Ե�����
					player.setGossipText( cschannel_msgs.KE_JU_VOICE_5 )
				return False
			if questStateHuishi == csdefine.QUEST_STATE_NOT_FINISH:
				# ���ڲμӻ��Կ���
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_4 )
				return False
			if questStateHuishi != csdefine.QUEST_STATE_NOT_HAVE_LEVEL_SUIT:
				# ���Բμӻ��Կ��ԣ����Խ�������ôû�жԻ�
				return False
			else:
				# �������
				player.setGossipText( cschannel_msgs.KE_JU_VOICE_6 )
				return False
		else:
			# ����û��ʼ������Ҳû��ʼ
			player.setGossipText( cschannel_msgs.KE_JU_VOICE_8 )
			return False

class FuncImperialDSignUpCheck( Function ):
	"""
	���Ա����Ի����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.key1 = section.readString( "param1" )
		self.key2 = section.readString( "param2" )
		self.key3 = section.readString( "param3" )
		self.key4 = section.readString( "param4" )
		self.key5 = section.readInt( "param5" )	# ����id

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		pass


	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
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
			# ���Ա�����û��ʼ
			keydlg = self.key1
		elif questState == csdefine.QUEST_STATE_NOT_ALLOW and questDegree <= 0:
			# ��������Ա�������
			keydlg = self.key2
		elif questState == csdefine.QUEST_STATE_COMPLETE and questDegree > 0:
			# ���Կ����Ѿ������
			keydlg = self.key3
		elif questState != csdefine.QUEST_STATE_NOT_HAVE and questState != csdefine.QUEST_STATE_FINISH and \
			BigWorld.globalData.has_key( "AS_DianshiActivityStart" ) and player.queryTemp( "imperial_exam_start_time", 0 ) != 0:
			# ���ڽ��пƾٿ���
			keydlg = self.key4
		elif questDegree >= 1 and not BigWorld.globalData.has_key( "AS_DianshiActivityStart" ) and \
			BigWorld.globalData.has_key( "IE_DianShi_Reward_DBID_List" ) \
			and player.databaseID in BigWorld.globalData[ "IE_DianShi_Reward_DBID_List" ]:
			# �����Ѿ������ˣ����ҿ�����ȡ����,������ʾ��ȡ����ѡ��
			player.setGossipText( cschannel_msgs.KE_JU_VOICE_9 )
			return False
		elif BigWorld.globalData.has_key( "AS_DianshiActivityStart" ):
			# ����Ѿ�����˿��ԣ����ǵ��Բ�û�н���������ʾ��ȡ����ѡ��
			player.setGossipText( cschannel_msgs.KE_JU_VOICE_10 )
			return False
		else:
			# �������
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
	�ƾٻ��Բ���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.key1 = section.readString( "param1" )
		self.questID = section.readInt( "param2" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			return
		if player.iskitbagsLocked():	# ����������by����
			player.endGossip( talkEntity )
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return

		payMoney = int( player.level ** 2 * 10 )	# ע�⣺�����ʽ��QuestImperialExamination��Ҳ�õ���������Ķ�����������Ҫһ�¡�
		moneyStr = self.convertPrice( payMoney )	# ����ֻ������Ǯ�����������ǲ���۳���ҵ�Ǯ���������accept�����Ŀ۳���
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
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if talkEntity is None:
			return False
		questStateHuishi = g_taskData[self.questID].query( player )	# ����״̬
		valid1 = BigWorld.globalData.has_key( "AS_HuishiActivityStart" )
		valid2 = ( questStateHuishi != csdefine.QUEST_STATE_NOT_FINISH and questStateHuishi != csdefine.QUEST_STATE_FINISH )
		valid3 = pLog = player.getLoopQuestLog( self.questID, True ).getDegree() > 0
		return valid1 and valid2 and valid3

	def convertPrice( self, price ):
		"""
		ת���۸񣬰����硰10102����ʽ�ļ۸�ת���ɡ�1��1��2ͭ��
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
	��ȡ�ƾٽ���(���ԡ�����)
	ĿǰΪ�ƺŽ�����������չ�Ժ��ټ�
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.ieType = section.readInt( "param1" )			# �ƾ����� 4Ϊ���ԡ�5Ϊ����
		self.zhuangyuanItemID = section.readInt( "param2" )	# ״Ԫ�Ķ��⽱��(��Ʒ)

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
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
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if talkEntity is None:
			return False

		if self.ieType == 4:
			# �ƾٻ���
			return ( BigWorld.globalData.has_key( "IE_HuiShi_Reward_DBID_List" ) \
			and player.databaseID in BigWorld.globalData[ "IE_HuiShi_Reward_DBID_List" ] \
			and not BigWorld.globalData.has_key( "AS_HuishiActivityStart" ) )
		elif self.ieType == 5:
			# �ƾٵ���
			return ( BigWorld.globalData.has_key( "IE_DianShi_Reward_DBID_List" ) \
			and player.databaseID in BigWorld.globalData[ "IE_DianShi_Reward_DBID_List" ] \
			and not BigWorld.globalData.has_key( "AS_DianshiActivityStart" ) )
		return False