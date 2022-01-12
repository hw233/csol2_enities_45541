# -*- coding: gb18030 -*-
#

import time
import random
import BigWorld

import csconst
import csstatus
import csdefine
from bwdebug import *
from MsgLogger import g_logger
from Function import Functor
from TitleMgr import TitleMgr

import cschannel_msgs
import ShareTexts as ST

import Const
from Love3 import g_teachCreditLoader
from Love3 import g_chatProfanity
from Love3 import g_rewards
from VehicleHelper import isFlying

g_titleLoader = TitleMgr.instance()

INVITE_PERIOD_OF_VALIDITY = 20		# ������Ч��

class RoleRelation:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass

	def onCellReady( self ):
		"""
		"""
		if self.query( "teach_register_teachInfo", False ):	# ȥ��������ѯ�Լ��Ƿ�ע����ͽ
			self._getTeachMgr().onPlayerGetCell( self.databaseID, self.base )

	def onDestroy( self ):
		"""
		"""
		if self.query( "teach_register_teachInfo", False ):
			self._getTeachMgr().onPlayerLoseCell( self.databaseID )

	def rlt_sendPlayerInfo( self, playerBase, relationUID, friendlyValue, relationStatus ):
		"""
		Define method.
		��mailboxΪplayerBase����ҷ���ָ����������Ϣ
		���ڵ�һ�ΰ��������Ϣ���µ��Է��Ŀͻ���
		"""
		playerBase.client.rlt_receivePlayerInfo( relationUID, self.getName(), self.level, self.raceclass, self.tongName, friendlyValue, self.headTextureID, relationStatus )

	def rlt_requestPlayerInfo( self, playerBase, relationUID ):
		"""
		Define method.
		����������ߣ�������¼�����Ϣ���Է��ͻ���
		"""
		playerBase.client.rlt_playerLogon( relationUID, self.level, self.raceclass, self.tongName, self.headTextureID )

	def beAskedToFriend( self, playerBase, playerName ):
		"""
		Define method.
		�Է����뼺����Ϊ����
		"""
		if self.qieCuoState != csdefine.QIECUO_NONE:
			playerBase.client.onStatusMessage( csstatus.TARGET_IS_QIECUO, "" )
			return

		self.base.beInvitedToFriend( playerBase, playerName )

	def addSweetie( self, srcEntityID, relationUID ):
		"""
		Exposed method.
		��������
		"""
		if self.id != srcEntityID:
			ERROR_MSG( "�Ƿ�ʹ����, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return
		if self.level < csconst.SWEETIE_LEVEL_LIMIT:
			self.statusMessage( csstatus.SWEETIE_PLAYER_LEVEL_LACK )
			return
		item = self.findItemFromNKCK_( 50101001 )
		if self.iskitbagsLocked() or item is None or item.isFrozen():
			self.statusMessage( csstatus.SWEETIE_NEED_TOGETHER_ITEM )
			return
		self.base.addSweetie( relationUID )

	def beInvitedToSweetie( self, playerBase, relationUID ):
		"""
		Define method.
		�������Ϊ����
		"""
		if self.qieCuoState != csdefine.QIECUO_NONE:
			playerBase.client.onStatusMessage( csstatus.TARGET_IS_QIECUO, "" )
			return

		self.base.beInvitedToSweetie( relationUID )

	def addSweetieSuceeded( self, relationUID ):
		"""
		Define method.
		�Է�ͬ���Ϊ���ˣ��ٴμ��ͬ�Ľ���Ʒ�������������ɾ��ͬ�ĽᲢ֪ͨbase������������
		"""
		item = self.findItemFromNKCK_( 50101001 )
		if self.iskitbagsLocked() or item is None or item.isFrozen():
			self.statusMessage( csstatus.SWEETIE_NEED_TOGETHER_ITEM )
			return
		self.removeItem_( item.order, reason = csdefine.DELETE_ITEM_COMMAND_SWEAR )
		self.base.addSweetieSuceeded( relationUID )

	def hasCouple( self ):
		"""
		�Ƿ���ڷ��޹�ϵ
		"""
		return self.coupleItem["playerDBID"]

	def isCouple( self, entityID ):
		"""
		entityID������Ƿ���Լ��Ƿ���
		"""
		playerBase = self.coupleItem["playerBase"]
		if playerBase:
			return playerBase.id == entityID
		else:
			return False

	def isCoupleOnline( self ):
		"""
		��ż�Ƿ�����
		"""
		return self.coupleItem["playerBase"] is not None

	def getCoupleMB( self ):
		"""
		"""
		return self.coupleItem["playerBase"]

	def requestMarriage( self, talkEntity ):
		"""
		�����npc�Ի���ѡ��������Ĺ���ѡ�����������Ľӿ�
		�ж�˫���Ƿ���Ͻ����������˫���ͻ��˷�������ȷ�ϡ�
		�ȼ�鷢���ߵ�������Ȼ����Ŀ��entity�����������base����Ƿ����ˡ�

		���������
		��ɫ֮�以Ϊ���ˣ�
		˫����ɫ�ȼ�������20����
		˫������δ��״̬��
		���֧��30��Ľ����ã�
		˫���������״̬������10�׷�Χ�ڡ�
		������ֻ�����ˡ�
		"""
		if self.level < csconst.COUPLE_LEVEL_LIMIT:
			self.statusMessage( csstatus.COUPLE_LEVEL_LIMIT )
			return
		if self.hasCouple():
			self.statusMessage( csstatus.COUPLE_NOT_MARRY_TWICE )
			return
		if self.money < csconst.COUPLE_WEDDING_CHARGE:
			self.statusMessage( csstatus.COUPLE_WEDDING_MONEY_LACK )
			return
		if not self.isInTeam():
			self.statusMessage( csstatus.COUPLE_PLAYER_NOT_TEAM )
			return

		teammateList = talkEntity.searchTeamMember( self.teamMailbox.id, csconst.COUPLE_SWARE_DISTANCE )
		if len(teammateList) == 1:
			self.statusMessage( csstatus.COUPLE_ONE_PLAYER_TEAM )
			return
		elif len( teammateList ) > 2:
			self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
			return
		lover = teammateList[0].id == self.id and teammateList[1] or teammateList[0]
		if self.getGender() == lover.getGender():
			self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
			return
		if lover.level < csconst.COUPLE_LEVEL_LIMIT:
			self.statusMessage( csstatus.COUPLE_LEVEL_LIMIT )
			return
		self.base.requestMarriage( lover.databaseID )

	def couple_canMarry( self, loverID ):
		"""
		Define method.
		��base�ϼ��Է��Ǽ������ˣ����Խ�飬���ô˽ӿ����ý��ǰ�����ݣ��Ա���ʱ�ж�2���Ƿ��ܹ���顣
		"""
		self.setTemp( "couple_targetID", loverID )

	def isInMarriageAffair( self ):
		"""
		�Ƿ��ڴ����������
		"""
		return self.queryTemp( "couple_targetID" )

	def couple_replyForMarriage( self, srcEntityID, reply ):
		"""
		Exposed mehtod.
		�ظ��������

		@param reply : �Ƿ�ͬ�⣬BOOL
		"""
		if self.id != srcEntityID:
			ERROR_MSG( "�Ƿ�ʹ����, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return
		if not self.isInTeam():
			self.statusMessage( csstatus.COUPLE_PLAYER_NOT_TEAM )
			return
		if self.getTeamCount() != 2:
			self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
			return
		if self.level < csconst.COUPLE_LEVEL_LIMIT:
			self.statusMessage( csstatus.COUPLE_LEVEL_LIMIT )
			return
		if self.hasCouple():
			self.statusMessage( csstatus.COUPLE_NOT_MARRY_TWICE )
			return
		lover = [ e for e in self.entitiesInRangeExt( csconst.COUPLE_SWARE_DISTANCE, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == self.teamMailbox.id ]
		if len(lover) == 0:
			self.statusMessage( csstatus.COUPLE_TARGET_NOT_TOGETHER )
			return
		lover = lover[0]
		if not lover.isInMarriageAffair():
			return
		if not reply:
			self.removeTemp( "couple_targetID" )
			lover.couple_dstMarryFalse( self.id )
			return
		if self.getNormalKitbagFreeOrder() == -1:
			self.statusMessage( csstatus.COUPLE_CANT_KITBAG_FULL )
			return
		if self.money < csconst.COUPLE_WEDDING_CHARGE:
			self.statusMessage( csstatus.COUPLE_WEDDING_MONEY_LACK )
			lover.client.onStatusMessage( csstatus.COUPLE_WEDDING_MONEY_LACK, "" )
			return
		if lover.hasFlag( csdefine.ROLE_FLAG_COUPLE_AGREE ):
			if lover.level < csconst.COUPLE_LEVEL_LIMIT:
				self.statusMessage( csstatus.COUPLE_LEVEL_LIMIT )
				return
			if lover.hasCouple():
				self.statusMessage( csstatus.COUPLE_NOT_MARRY_TWICE )
				return
			if self.position.flatDistTo( lover.position ) > csconst.TEACH_COMMUNICATE_DISTANCE:		# 10������
				self.statusMessage( csstatus.COUPLE_TARGET_NOT_TOGETHER )
				return
			if lover.money < csconst.COUPLE_WEDDING_CHARGE:
				self.statusMessage( csstatus.COUPLE_WEDDING_MONEY_LACK )
				return
			# ���Խ����
			playerName = lover.getName()
			playerDBID = lover.databaseID
			self.coupleItem = { "playerDBID":playerDBID,"playerBase":lover.base}
			self.base.couple_swear( playerDBID )
			lover.couple_marrySuccess( self.base, self.getName(), self.databaseID )
			self.removeTemp( "couple_targetID" )
			self.payMoney( csconst.COUPLE_WEDDING_CHARGE, csdefine.CHANGE_MONEY_REPLYFORMARRIAGE )
			titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
											or csdefine.TITLE_COUPLE_MALE_ID
			self.addTitle( titleID )
			self.statusMessage( csstatus.TITLE_ADDED, g_titleLoader.getName( titleID ) % playerName )
			awarder = g_rewards.fetch( csdefine.RCG_MARRY_RING, self )
			if awarder is None or len( awarder.items ) <= 0:
				self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
				return
			item = awarder.items[0]		# ������ֻ��һ����Ʒ
			item.set( "creator", playerName )
			awarder.award( self, csdefine.ADD_ITEM_REPLYFORMARRIAGE )
			try:
				g_logger.coupleBuildLog( self.databaseID, self.getName(), playerDBID, playerName )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG()  )
		else:
			self.addFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )

	def couple_marrySuccess( self, loverBase, loverName, loverDBID ):
		"""
		Define method.
		���˽��,ͨ���˽ӿ����ý������

		@param loverBase:	�������base mailbox
		@type loverBase:	MAILBOX
		@param loverName:	�����������
		@type loverName:	STRING
		@param loverDBID:	�������dbid
		@type loverDBID:	DATABASE_ID
		"""
		self.coupleItem = { "playerDBID":loverDBID, "playerBase":loverBase }
		self.base.couple_marrySuccess( loverDBID )
		self.removeTemp( "couple_targetID" )
		self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )
		self.payMoney( csconst.COUPLE_WEDDING_CHARGE, csdefine.CHANGE_MONEY_REPLYFORMARRIAGE )
		titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
										or csdefine.TITLE_COUPLE_MALE_ID
		self.addTitle( titleID )
		self.statusMessage( csstatus.TITLE_ADDED, g_titleLoader.getName( titleID ) % loverName )
		awarder = g_rewards.fetch( csdefine.RCG_MARRY_RING, self )
		if awarder is None or len( awarder.items ) <= 0:
			self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		item = awarder.items[0]		# ������ֻ��һ����Ʒ
		item.set( "creator", loverName )
		awarder.award( self, csdefine.ADD_ITEM_MARRYSUCCESS )

	def couple_dstMarryFalse( self, entityID ):
		"""
		Define method.
		�Է���ͬ����
		
		@param entityID:�������entity id
		@type entityID:	OBJECT_ID
		"""
		if self.queryTemp( "couple_targetID", 0 ) != entityID:
			ERROR_MSG( "%i ���� %s �Ľ�����" % ( entityID, self.getName() ) )
			return
		self.statusMessage( csstatus.COUPLE_NOT_AGREE_WEDDING )
		self.removeTemp( "couple_targetID" )
		if self.hasFlag( csdefine.ROLE_FLAG_COUPLE_AGREE ):
			self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )

	def couple_requestDivorce( self, talkEntity ):
		"""
		��飬��npc��cell���ã�for real
		"""
		if not self.hasCouple():
			self.statusMessage( csstatus.COUPLE_BE_MARRY_FIRST )
			return

		if not self.isCoupleOnline() or not self.isInTeam():
			if self.money < csconst.COUPLE_FORCE_DIVORCE_CHARGE:
				self.statusMessage( csstatus.COUPLE_DIVORCE_MONEY_LACK )
			else:				# ѯ���Ƿ�Ҫǿ�����.
				self.client.couple_requestForceDivorce()
		else:
			teammateList = talkEntity.searchTeamMember( self.teamMailbox.id, 10 )
			if len(teammateList) == 1:
				self.statusMessage( csstatus.COUPLE_ONE_PLAYER_TEAM )
				return
			elif len( teammateList ) > 2:
				self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
				return
			lover = teammateList[0].id == self.id and teammateList[1] or teammateList[0]
			if not self.isCouple( lover.id ):
				self.statusMessage( csstatus.COUPLE_BE_COUPLE_FIRST )
				return
			if self.position.flatDistTo( lover.position ) > csconst.TEACH_COMMUNICATE_DISTANCE:		# 10������
				self.statusMessage( csstatus.COUPLE_TARGET_NOT_TOGETHER )
				return
			self.setTemp( "couple_divorce_manage", True )
			lover.setTemp( "couple_divorce_manage", True )
			self.client.couple_requestDivorce()
			lover.client.couple_requestDivorce()

	def couple_replyForDivorce( self, srcEntityID, reply ):
		"""
		Exposed method.
		��Ҷ��������Ļظ�

		@param reply:	True��ʾͬ���飬False��ʾ��ͬ��
		@type reply:	BOOL
		"""
		if self.id != srcEntityID:
			ERROR_MSG( "�Ƿ�ʹ����, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return
		if not self.hasCouple():
			self.statusMessage( csstatus.COUPLE_BE_MARRY_FIRST )
			return
		if not self.queryTemp( "couple_divorce_manage", False ):	# �Ѿ�������鴦����
			DEBUG_MSG( "�Ѿ�������鴦����." )
			return
		if reply:
			if not self.isInTeam():
				self.statusMessage( csstatus.COUPLE_PLAYER_NOT_TEAM )
				return
			teammateList = [ e for e in self.entitiesInRangeExt( 10, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == self.teamMailbox.id ]
			if len( teammateList ) != 1:
				self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
				return
			lover = teammateList[0]
			if not self.isCouple( lover.id ):
				self.statusMessage( csstatus.COUPLE_BE_COUPLE_FIRST )
				return
			if not lover.hasFlag( csdefine.ROLE_FLAG_COUPLE_AGREE ):	# �Է���ûͬ�����
				self.addFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )		# ����ͬ�������
			else:	# ��鴦��
				self.coupleItem = { "playerDBID":0, "playerBase":None }
				titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
												or csdefine.TITLE_COUPLE_MALE_ID
				self.removeTitle( titleID )
				try:
					g_logger.coupleRemoveLog( self.databaseID, self.getName(), lover.databaseID )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG()  )
				self.base.couple_divorceSuccess()
				lover.couple_divorceSuccess()
				msg = cschannel_msgs.BCT_JSGX_DIVROCE % ( self.getName(), lover.getName() )
				BigWorld.globalData[csconst.C_PREFIX_GBAE].anonymityBroadcast( msg, [] )
				self.removeTemp( "couple_divorce_manage" )
				lover.removeTemp( "couple_divorce_manage" )
		else:
			self.statusMessage( csstatus.COUPLE_AGREE_DIVORCE_FAIL )
			self.removeTemp( "couple_divorce_manage" )
			self.coupleItem["playerBase"].cell.couple_dstDivorceFalse()

	def couple_dstDivorceFalse( self ):
		"""
		Define method.
		�Է���ͬ�����
		"""
		self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )
		self.removeTemp( "couple_divorce_manage" )

	def couple_divorceSuccess( self ):
		"""
		Define method.
		���ɹ�
		"""
		self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )
		#self.removeTemp( "couple_divorceReply" )
		self.coupleItem = { "playerDBID":0, "playerBase":None }
		titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
										or csdefine.TITLE_COUPLE_MALE_ID
		self.removeTitle( titleID )
		self.base.couple_divorceSuccess()

	def couple_dstForceDivorce( self ):
		"""
		Define method.
		�Է�������ǿ�����

		�����������ݣ���base��cell��һ�����ã��п���cell���������ò��ɹ������´���������Ȼ�ɴ�������Ϊ
		"""
		titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
										or csdefine.TITLE_COUPLE_MALE_ID
		self.removeTitle( titleID )
		self.base.couple_divorceSuccess()
		self.coupleItem = { "playerDBID":0, "playerBase":None }

	def couple_forceDivorce( self, srcEntityID, dstPlayerName ):
		"""
		Exposed method.
		���ͬ�ⵥ������飬�����Ҳ�ͬ�⣬��ô����Ҫ֪ͨ������
		"""
		if self.id != srcEntityID:
			return
		if not self.hasCouple():
			self.statusMessage( csstatus.COUPLE_BE_MARRY_FIRST )
			return
		if self.money < csconst.COUPLE_FORCE_DIVORCE_CHARGE:
			self.statusMessage( csstatus.COUPLE_DIVORCE_MONEY_LACK )
			return

		self.payMoney( csconst.COUPLE_FORCE_DIVORCE_CHARGE, csdefine.CHANGE_MONEY_FORCEDIVORCE )
		titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
										or csdefine.TITLE_COUPLE_MALE_ID
		self.removeTitle( titleID )
		self.base.couple_forceDivorce()
		title = cschannel_msgs.ROLERELATION_INFO_1
		content = self.getName() + cschannel_msgs.ROLERELATION_INFO_2
		self.mail_send_on_air( dstPlayerName, csdefine.MAIL_TYPE_QUICK, title, content )
		self.coupleItem = { "playerDBID":0, "playerBase":None }

	def cancelAgreeCouple( self, srcEntityID ):
		"""
		Exposed method.
		���ȡ���������ͬ����
		"""
		self.removeTemp( "couple_divorce_manage" )
		self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )

	def rlt_sendAreaInfo( self, relationUID, playerBase ):
		"""
		Define method.
		�����Լ����ڵĵ������ݸ��������
		"""
		playerBase.client.rlt_receiveAreaInfo( relationUID, self.spaceType, self.position, self.getCurrentSpaceLineNumber() )

	def couple_requestPosition( self ):
		"""
		Define method.
		����ʹ���� ��Ӱ���� ���ܣ�ͨ���˽ӿ����󼺷���λ����Ϣ
		�жϼ����Ƿ��ڸ����У�������Է������ʾ��Ϣ���Է�ʹ�ü��ܲ��ɹ���������Ѽ�����λ����Ϣ���͸��Է���
		"""
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			#self.coupleItem["playerBase"].client.onStatusMessage( csstatus.COUPLE_CANT_TELEPORT_SPECIAL_SPACE, "" )
			return
		
		# ����Լ����ڷ��У�������Է����͵��Լ���� by mushuang
		if isFlying( self ):
			self.coupleItem["playerBase"].cell.interruptSpell( csstatus.CANT_TELEPORT_WHEN_TARGET_FLYING ) # �����������ʾ�Է�
			return
		
		spaceName = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		lineNumber = self.getCurrentSpaceLineNumber()
		self.coupleItem["playerBase"].cell.couple_teleport( spaceName, lineNumber, self.position, self.direction, self.getName() )

	def couple_teleport( self, spaceName, lineNumber, position, direction, playerName ):
		"""
		Define method.
		����ͨ���˽ӿڰ�λ����Ϣ���͸����������ô������ݣ���������ʱ��ʹ�ô����ݴ���
		"""
		self.setTemp( "couple_ringTeleport", ( spaceName, lineNumber, position, direction, playerName ) )

	def receiveCoupleInfo( self, relationItem ):
		"""
		Define method.
		���հ�����Ϣ

		@param helpmateBase : ���mailbox���п���ΪNone
		@type helpmateBase : MAILBOX
		"""
		self.coupleItem = relationItem

	def onHelpmateLogin( self, helpmateBase ):
		"""
		Define method.
		��������
		"""
		self.coupleItem["playerBase"] = helpmateBase

	def onHelpmateLogout( self ):
		"""
		Define method.
		��������
		"""
		self.coupleItem["playerBase"] = None

	def couple_findWeddingRing( self, loverName ):
		"""
		Define method.
		��������һؽ���ָ��
		"""
		if self.payMoney( csconst.COUPLE_WEDDING_RING_PRICE, csdefine.CHANGE_MONEY_FINDWEDDINGRING ):
			awarder = g_rewards.fetch( csdefine.RCG_MARRY_RING, self )
			if awarder is None or len( awarder.items ) <= 0:
				self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
				return
			item = awarder.items[0]		# ������ֻ��һ����Ʒ
			item.set( "creator", loverName )
			awarder.award( self, csdefine.ADD_ITEM_FINDWEDDINGRING )
		else:
			self.statusMessage( csstatus.COUPLE_LACK_MONEY_FOR_RING )

	def rlt_checkAddFriendyResult( self, canAdd ):
		"""
		Define method.
		�Ƿ��ܹ������Ѻöȼ��ص�
		"""
		if not self.queryTemp( "addFriendlyRequesting", False ):	# �������ʹ�ü�����
			return
		if not canAdd: # ���߻�Ҫ������������ʾ��Ϣ (MB):���� %s û���Ѻù�ϵ������ʹ�ø���Ʒ��
			name = self.queryTemp( "addFriendlyName", "δ֪���" )
			self.statusMessage( csstatus.FRIEND_ITEM_ADD_NOT_FRIEND, name )
			
			self.interruptSpell( csstatus.FRIEND_ADD_VALUE_NOT_FRIEND )

	# ------------------------------------------------------------------------
	# ʦͽ��ϵ
	# ------------------------------------------------------------------------
	def iAmMaster( self ):
		"""
		�Լ��Ƿ���ʦ��
		"""
		return len( self.prenticeList ) > 0

	def isPrentice( self, playerDBID ):
		"""
		for real
		�Է��Ƿ�ͽ��
		"""
		for prentice in self.prenticeList:
			if prentice["playerDBID"] == playerDBID:
				return True
		return False

	def getPrenticeMbByDBID( self, playerDBID ):
		for prentice in self.prenticeList:
			if prentice["playerDBID"] == playerDBID:
				return prentice["playerBase"]
		return None

	def hasShiTuRelation( self ):
		"""
		����Ƿ�ӵ��ʦͽ��ϵ(��������Ƿ���ʦ������ͽ��)
		"""
		return len( self.prenticeList ) > 0 or self.masterItem["playerDBID"]

	def teach_isTeaching( self ):
		"""
		�Ƿ��ڰ�ʦ��
		���ڿ���Զ�̰�ʦ,���ж��ְ�ʦ��ʽ.���ô���ʱ��Ǳ������첽����°�ʦ��ͻ.
		"""
		return self.queryTemp( "teaching" ) is not None

	def getPrenticeNum( self ):
		return len( self.prenticeList )

	def _getTeachMgr( self ):
		"""
		��ð�ʦ������
		"""
		return BigWorld.globalData["TeachMgr"]

	def hasMaster( self ):
		"""
		�Ƿ����ʦ��
		for real & ghost
		"""
		return self.masterItem["playerDBID"]

	def getMasterMB( self ):
		"""
		���ʦ����base mailbox
		"""
		return self.masterItem["playerBase"]

	def receiveTeachInfo( self, relationItem, targetRelationStatus ):
		"""
		Define method.
		����ʦͽ��Ϣ

		@param relationItem : ���ʦͽ����
		@type relationItem : RELATION_ITEM
		@param relation : ʦ��/ͽ�ܹ�ϵ
		@type relation : UINT16
		"""
		if targetRelationStatus & csdefine.ROLE_RELATION_MASTER:
			self.prenticeList.append( relationItem )
		else:
			self.masterItem = relationItem
			# ���ڴ���Զ�̰�ʦ���п����ڰ�ʦ�ɹ�ʱͽ��û�ܻ�óƺ�(��ϵдdb�ɹ�������Զ��֪ͨͽ�ܼӳƺ�ʱͽ������)��
			# ��ʱ�������һ�£����û�����ϡ�
			if not self.hasTitle( csdefine.TITLE_TEACH_PRENTICE_ID ):
				self.addTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
		if self.query( "teachSpaceKillMonsterTime" ) is None:
			self._setTeachData()

	def teach_onLevelUp( self ):
		"""
		������ı䣬�������ʦͽ��ϵ����֪ͨʦ/ͽ
		"""
		if self.hasMaster():
			if self.level >= csconst.TEACH_END_TEACH_AWARD_LIMIT:
				self.autoTeach_disband()	# ͽ�ܴﵽ55���Զ���ʦ by����
			else:
				masterMB = self.getMasterMB()
				if masterMB and self.level < csconst.TEACH_END_TEACH_AWARD_LIMIT - 4:	# ����50��ʦ�������ܻ�ý���
					masterMB.cell.teach_receiveAward( self.level )
			if self.level % 5 == 0:	# ͽ�ܵȼ�����Ϊ15��20��25��30��35��40��45��50ʱ��ϵͳ���ڵ���������ָ���ȼ�ʱ������Ʒ����������״��IDΪ60101107��
				self._addTeachRewardItems( csdefine.RCG_TEACH_LEVEL_UP )
		if self.query( "teach_register_teachInfo", False ):	# ���ע������ͽ�������Լ�����ͽ��Ϣ
			self._getTeachMgr().onPlayerLevelUp( self.databaseID, self.level )

	def teach_receiveAward( self, level ):
		"""
		Define method.
		ʦ�����ߣ�ͽ�ܵȼ�������ʦ�����ܽ����Ľӿڣ�����level���㽱��

		Param level:ͽ�ܵĵȼ�
		Type level:	UINT8
		"""
		teachCredit = g_teachCreditLoader.getTeachCredit( level )
		exp = g_teachCreditLoader.getExp( level )
		money = g_teachCreditLoader.getMoney( level )
		self.gainMoney( money, csdefine.CHANGE_MONEY_TEACH_REWARD )
		self.addExp( exp, csdefine.CHANGE_EXP_TEACH_REWARD )
		self.addTeachCredit( teachCredit, csdefine.CHANGE_TEACH_CREDIT_REWARD )
		self.statusMessage( csstatus.TEACH_PRENTICE_LEVEL_UP, exp, money, teachCredit )

	def autoTeach_disband( self ):
		"""
		����teach_disband���Զ���ʦ�ӿ�
		��ͽ������ʱ������ by����
		"""
		self.removeTitle( csdefine.TITLE_TEACH_PRENTICE_ID )		# ɾ����Ӧ�ƺ�
		self._removeTeachData()
		self.base.autoTeach_disband( self.masterItem["playerDBID"] )
		self.masterItem = {"playerDBID":0,"playerBase":None}

		# ͽ���Զ���ʦ����50��������
		money = 50 * csconst.TEACH_END_MASTER_MONEY_AWARD
		self.gainMoney( money, csdefine.CHANGE_MONEY_PRENTICEENDTEACH )
		self.addExp( int( 50 * csconst.TEACH_END_MASTER_EXP_AWARD ), csdefine.CHANGE_EXP_PRENTICEENDTEACH )
		self._addTeachRewardItems( csdefine.RCG_TEACH_END_SUC )
		
	def teachEveryDayReward( self ):
		"""
		ʦͽÿ�ս���
		"""
		self._addTeachRewardItems( csdefine.RCG_TEACH_EVERY_DAY )

	def _addTeachRewardItems( self, rewardID ):
		"""
		��óɹ���ʦ����Ʒ
		"""
		awarder = g_rewards.fetch( rewardID, self )
		if awarder is None or len( awarder.items ) <= 0:
			self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		if self.checkItemsPlaceIntoNK_( awarder.items ) != csdefine.KITBAG_CAN_HOLD:
			title = cschannel_msgs.ROLERELATION_INFO_10
			content = cschannel_msgs.ROLERELATION_INFO_11
			if rewardID == csdefine.RCG_TEACH_SUC:		# ��ʦ���ʼ���Ϣ��������ͬ
				title = cschannel_msgs.ROLERELATION_INFO_8
				content = cschannel_msgs.ROLERELATION_INFO_9
			elif rewardID == csdefine.RCG_TEACH_EVERY_DAY:
				title = cschannel_msgs.ROLERELATION_INFO_8
				content = cschannel_msgs.ROLERELATION_INFO_11
			self.mail_send_on_air_withItems( self.getName(), csdefine.MAIL_TYPE_QUICK, title, content, awarder.items )
			self.statusMessage( csstatus.CANT_ADD_TEACH_DONATE_ITEM )
		else:
			awarder.award( self, csdefine.ADD_ITEM_TEACH_SUCCESS )

	def teach_teachPrentice( self, talkEntity ):
		"""
		����ʦnpc�ĵ��ã��ж���ͬ��Ķ����Ƿ����㽨��ʦͽ��ϵ����������������ɹ��������Լ���prenticeBaseMBList���ݣ�ͬʱ����һ����Ӧ�ƺš�

		talkEntity:npc entity
		"""
		if self.level < csconst.TEACH_MASTER_MIN_LEVEL:					# ʦ���ȼ����
			self.statusMessage( csstatus.TEACH_PLAYER_LEVEL_LACK, csconst.TEACH_MASTER_MIN_LEVEL, csconst.TEACH_END_TEACH_LEAST_LEVEL, csconst.TEACH_PRENTICE_LOWER_LIMIT )
			return
		if self.teach_isTeaching():
			HACK_MSG( "player( %s )-->>>teaching" % self.getName() )
			return
		if not self.isInTeam() or self.getTeamCount() != 2:						# ʦ����ͽ����Ӽ��
			self.statusMessage( csstatus.TEACH_PLAYER_NOT_TEAM )
			return
		if self.getPrenticeNum() >= csconst.TEACH_PRENTICE_MAX_COUNT:	# ͽ���������޼��
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			return

		teammateMBs = self.getTeamMemberMailboxs()
		prenticeID = teammateMBs[0].id  == self.id and teammateMBs[1].id or teammateMBs[0].id
		prentice = BigWorld.entities.get( prenticeID )
		if prentice is None:
			self.statusMessage( csstatus.TEACH_PRENTICE_TOO_FAR )
			return
		if self.position.flatDistTo( prentice.position ) > csconst.TEACH_COMMUNICATE_DISTANCE:		# 10������
			self.statusMessage( csstatus.TEACH_PRENTICE_TOO_FAR )
			return
		if prentice.hasMaster():	# ͽ���Ƿ�����ʦ���ļ��
			self.statusMessage( csstatus.TEACH_PRENTICE_HAS_MONSTER ,prentice.getName() )
			return
		prenticeLevel = prentice.level						# ͽ�ܼ�����
		if prenticeLevel < csconst.TEACH_PRENTICE_LOWER_LIMIT or prenticeLevel > csconst.TEACH_PRENTICE_UPPER_LIMIT:
			self.statusMessage( csstatus.TEACH_PLAYER_LEVEL_LACK, csconst.TEACH_MASTER_MIN_LEVEL, csconst.TEACH_END_TEACH_LEAST_LEVEL, csconst.TEACH_PRENTICE_LOWER_LIMIT )
			return
		if prentice.teach_isTeaching():
			return

		prenticeDBID = prentice.databaseID
		prenticeName = prentice.getName()
		self.prenticeList.append( { "playerDBID":prenticeDBID, "playerBase":prentice.base } )
		self._setTeachData()
		prentice.teach_beTeached()							# ֪ͨͽ��cell����ʦͽ��ϵ
		self.base.teach_beginTeach( prenticeDBID, prenticeName, prentice.base )	# ����base���ݲ�д���ݿ�
		self.statusMessage( csstatus.TEACH_BE_MASTER_SUCCESS, prenticeName )	# ֪ͨ�ͻ���
		if self.query( "teach_register_teachInfo", False ):
			self._getTeachMgr().onPrenticeNumChange( self.databaseID, self.getPrenticeNum() )
	
	def onSendTongGrade( self, relationUID, baseMailbox ) :
		"""
		Define method
		"""
		print "cell onReceiveTongGrade"
		baseMailbox.client.onReceiveTongGrade( relationUID, self.tong_grade )

	def teach_beTeached( self ):
		"""
		Define method.
		��ʦ����cell���ã�ʦ�����뽨��ʦͽ��ϵ�ɹ���ͨ���˽ӿ�֪ͨͽ�����ñ�ʾʦͽ��ϵ״̬�����ݣ�����һ����Ӧ�ƺš�
		"""
		teammateMBs = self.getTeamMemberMailboxs()
		masterID = teammateMBs[0].id == self.id and teammateMBs[1].id or teammateMBs[0].id
		master = BigWorld.entities.get( masterID )
		masterName = master.getName()
		self.masterItem = { "playerDBID":master.databaseID,"playerBase":master.base }
		self.addTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
		self._setTeachData()
		self.statusMessage( csstatus.TITLE_ADDED, g_titleLoader.getName( csdefine.TITLE_TEACH_PRENTICE_ID ) % masterName )
		self.statusMessage( csstatus.TEACH_BE_PRENTICE_SUCCESS, masterName )
		self._addTeachRewardItems( csdefine.RCG_TEACH_SUC )
		if self.query( "teach_register_teachInfo", False ):
			self.teach_deregisterPrentice()
			
	def teach_disband( self, playerDBID, playerName ):
		"""
		Define method.
		��ҽ��ʦͽ��ϵ�Ľӿ�
		�����������ʦͽ��ϵ���ݡ�

		Param playerName:	�Է���ҵ�����
		Type playerName:	STRING
		Param playerDBID:	�Է���ҵ�dbid
		Type playerDBID:	DATABASE_ID
		"""
		if self.hasMaster():	# �����ͽ�ܵ���������ϵ
			self.removeTitle( csdefine.TITLE_TEACH_PRENTICE_ID )		# ɾ����Ӧ�ƺ�
			self.masterItem = {"playerDBID":0,"playerBase":None}
			self._removeTeachData()
		else:																# ���������ͽ��
			self.removePrentice( playerDBID )
		self.base.teach_disband( playerDBID )
		self.statusMessage( csstatus.TEACH_RELATION_DISBAND, playerName )	# ֪ͨ���
		title = cschannel_msgs.ROLERELATION_INFO_3
		content = cschannel_msgs.ROLERELATION_INFO_5 + self.getName() + cschannel_msgs.ROLERELATION_INFO_6
		self.mail_send_on_air( playerName, csdefine.MAIL_TYPE_QUICK, title, content )

	def removePrentice( self, prenticeDBID ):
		"""
		�Ƴ�һ��ͽ�����ݡ�
		"""
		for prenticeItem in self.prenticeList:
			if prenticeItem["playerDBID"] == prenticeDBID:
				self.prenticeList.remove( prenticeItem )
				break
		if len( self.prenticeList ) == 0:
			self._removeTeachData()
		if self.query( "teach_register_teachInfo", False ):
			self._getTeachMgr().onPrenticeNumChange( self.databaseID, self.getPrenticeNum() )

	def targetDisbandTeach( self, playerDBID, relation ):
		"""
		Define method.
		�Է����ʦͽ��ϵ

		@param playerDBID : �Է���ҵ�dbid
		@type playerDBID : DATABASE_ID
		@param relation: �Է���ҵ���ݶ���
		"""
		if relation & csdefine.ROLE_RELATION_MASTER:
			self.removeTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
			self._removeTeachData()
			self.masterItem = { "playerDBID":0, "playerBase":None }
			self.base.masterDisbandTeach()
		else:
			self.removePrentice( playerDBID )
			self.base.prenticeDisbandTeach( playerDBID )

	# ---------------------------------------------------------------------------------
	# Զ����ͽ����
	# ---------------------------------------------------------------------------------
	def hadRegisteredTeacher( self ):
		"""
		Define method.
		ȥ��������ѯ�Լ��Ƿ�ע����ͽ�ķ��أ��з������ʾ��ע�ᡣ
		"""
		self.addFlag( csdefine.ROLE_FLAG_REGISTER_MASTER )

	def teach_registerTeacher( self, everPrenticeNum, lastWeekOnlineTime ):
		"""
		ע����ͽ
		@param everPrenticeNum : ��ʦͽ����
		@type everPrenticeNum : INT32
		@param lastWeekOnlineTime : ��������ʱ��
		@type lastWeekOnlineTime : FLOAT
		"""
		if self.hasMaster():
			self.statusMessage( csstatus.TEACH_LIST_MASTER_LEVEL_LACK )
			return
		if self.level < csconst.TEACH_MASTER_MIN_LEVEL:						# ʦ���ȼ����
			self.statusMessage( csstatus.TEACH_LIST_MASTER_LEVEL_LACK )
			return
		if self.getPrenticeNum() >= csconst.TEACH_PRENTICE_MAX_COUNT:		# ͽ���������޼��
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			return
		if self.query( "teach_register_teachInfo", False ):		# �Ѿ�ע�����
			self.statusMessage( csstatus.TEACH_LIST_ALREADY_IN )
			return

		self.set( "teach_register_teachInfo", True )
		self.statusMessage( csstatus.TEACH_LIST_ADD_SUCCESS )
		self._getTeachMgr().register( self.databaseID, self.getName(), self.level, self.raceclass, self.getMyTeachTitle(), self.getPrenticeNum(), self.base, everPrenticeNum,lastWeekOnlineTime )

	def teach_deregisterTeacher( self ):
		"""
		ע����ͽ
		"""
		if not self.query( "teach_register_teachInfo", False ):
			self.statusMessage( csstatus.TEACH_LIST_ISNT_IN )
			return
		self._getTeachMgr().deregister( self.databaseID, 1 )

	def teach_registerPrentice( self, lastWeekOnlineTime ):
		"""
		�����Ҫ��ʦ��ע�ᵽ��ʦ������
		
		@param lastWeekOnlineTime : ��������ʱ��
		@type lastWeekOnlineTime : FLOAT
		"""
		if self.level < csconst.TEACH_PRENTICE_LOWER_LIMIT or self.level > csconst.TEACH_PRENTICE_UPPER_LIMIT:
			self.statusMessage( csstatus.FIND_MASTER_LEVEL_LACK, csconst.TEACH_END_TEACH_LEAST_LEVEL, csconst.TEACH_PRENTICE_LOWER_LIMIT )
			return
		if self.hasMaster():
			self.statusMessage( csstatus.CANT_REGISTER_HAD_MASTER )
			return
		if self.query( "teach_register_teachInfo", False ):
			self.statusMessage( csstatus.TEACH_LIST_ALREADY_IN )
			return

		self.set( "teach_register_teachInfo", True )
		self.statusMessage( csstatus.PRENTICE_REGISTER_SUCCESS )
		playerName = self.getName()
		BigWorld.globalData[csconst.C_PREFIX_GBAE].anonymityBroadcast( cschannel_msgs.BCT_JSGX_FIND_TEACHER % ( playerName, playerName ), [] )
		self._getTeachMgr().register(  self.databaseID, self.getName(), self.level, self.raceclass, self.getMyTeachTitle(), 0, self.base, 0, lastWeekOnlineTime )

	def teach_deregisterPrentice( self ):
		"""
		ע��ͽ�ܹ��浽��ʦ������
		"""
		if not self.query( "teach_register_teachInfo", False ):
			self.statusMessage( csstatus.TEACH_LIST_ISNT_IN )
			return
		self._getTeachMgr().deregister( self.databaseID, 0 )

	def teach_deregisterTeachInfo( self ):
		"""
		Define method.
		������֪ͨע����ʦ��Ϣ
		"""
		self.remove( "teach_register_teachInfo" )

	def teach_queryTeachInfo( self, srcEntityID ):
		"""
		Exposed method.
		��ѯʦͽ�������е���Ӧ��Ϣ
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ������ߣ�%i������%i��Զ�̷�����" % ( srcEntityID, self.id ) )
			return
		self._getTeachMgr().queryTeachInfo( self.base, self.level )

	def teach_remoteTeachReply( self, srcEntityID, agree, prenticeName ):
		"""
		Exposed method.
		ʦ���ظ���ʦ����ı�¶����

		@param agree : �Ƿ�ͬ��
		@type agree : BOOL
		@param prenticeName : ͽ������
		@type prenticeName : STRING
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ������ߣ�%i������%i��Զ�̷�����" % ( srcEntityID, self.id ) )
			return
		if self.getPrenticeNum() >= csconst.TEACH_PRENTICE_MAX_COUNT:
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			self.base.requestBeTeachedResult( csstatus.TEACH_REQUEST_PRENTICE_NUM_LIMIT )
			return

		if agree:	# ��ͽ�ܵ�����д��ͽ�����ݿ�,���ͽ��������֪ͨ��,��cell�������ݿ��ԭ����,����ͬ������ʦ����ͽ�ܵ�����
			self.setTemp( "teaching", True )	# ����һ�����ڰ�ʦ�ı��
			self.base.masterAgreeRemoteTeach( prenticeName )
		else:
			self.base.requestBeTeachedResult( csstatus.TEACH_REQUEST_BE_REFUSED )

	def teach_beginRemoteTeach( self, masterBase, masterDBID, masterName, teacherOrPrenticeAccept ):
		"""
		Define method.
		��ʼԶ�̰�ʦ�����ͽ�������Ƿ��ܹ���ʦ
		@param teacherOrPrenticeAccept: 1 ��ʾʦ����������0��ʾͽ�ܽ�������
		@type teacherOrPrenticeAccept : INT32
		"""
		if self.hasMaster():	# ͽ���Ƿ�����ʦ���ļ��
			masterBase.requestBeTeachedResult( csstatus.TEACH_MASTER_EXIST )
			return
		if self.level < csconst.TEACH_PRENTICE_LOWER_LIMIT or self.level > csconst.TEACH_PRENTICE_UPPER_LIMIT:
			masterBase.requestBeTeachedResult( csstatus.TEACH_REQUEST_LEVEL_LIMIT )
			return

		if teacherOrPrenticeAccept == 1:	# ʦ������������ʾͽ�ܰ�ʦ�ɹ�
			self.statusMessage( csstatus.TEACH_TEACHER_ECCEPT_REQUEST, masterName )
		self.masterItem = { "playerDBID":masterDBID, "playerBase":masterBase }
		self.addTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
		self._setTeachData()
		self.statusMessage( csstatus.TITLE_ADDED, g_titleLoader.getName( csdefine.TITLE_TEACH_PRENTICE_ID ) % masterName )
		#self.statusMessage( csstatus.TEACH_BE_PRENTICE_SUCCESS, masterName )
		self.base.teach_beginRemoteTeach( masterDBID, masterName, masterBase )
		# �п���ʦ��cell�Ѿ������٣��ƺ�����û����ɹ������������߳�ʼ��ʦͽ���ݣ���ô��Ҫ����ʦͽ�ƺ�
		masterBase.cell.teach_remoteTeachForMaster( self.databaseID, self.base, self.getName(), teacherOrPrenticeAccept )
		self._addTeachRewardItems( csdefine.RCG_TEACH_SUC )
		if self.query( "teach_register_teachInfo", False ):
			self.teach_deregisterPrentice()
			
	def _setTeachData( self ):
		"""
		�����ʦͽ��ϵ������һЩ��ʱ��ǣ���ʵ��һЩʦͽ��ϵ���ܽ��еĻ
		"""
		self.set( "teachSpaceKillMonsterTime", 0 )	# �ϴ�ʦͽɱ�ָ����Ĳ���ʱ��
		self.set( "teachEveryDayRewardTime", 0 )	# �ϴ���ȡÿ��ʦͽ����ʱ��

	def _removeTeachData( self ):
		"""
		�Ƴ�ʦͽ��ϵ��ʱ���
		"""
		self.remove( "teachSpaceKillMonsterTime" )	# �ϴ�ʦͽɱ�ָ����Ĳ���ʱ��
		self.remove( "teachEveryDayRewardTime" )	# �ϴ���ȡÿ��ʦͽ����ʱ��

	def teach_remoteTeachForMaster( self, prenticeDBID, prenticeBase, prenticeName, teacherOrPrenticeAccept ):
		"""
		Define method.
		Զ�̰�ʦ�ɹ�,֪ͨʦ����������

		@param prenticeBase : ͽ�ܵ�base mailbox
		@type prenticeBase : MAILBOX
		"""
		self.prenticeList.append( { "playerDBID":prenticeDBID, "playerBase":prenticeBase } )	# ��ͽ��base����ͽ��base�б�
		self._setTeachData()
		if teacherOrPrenticeAccept == 0:	# ͽ�ܽ���������ʾͽ�ܰ�ʦ�ɹ�
			self.statusMessage( csstatus.TEACH_PRENTICE_ACCEPT_REQUEST, prenticeName )
		if self.query( "teach_register_teachInfo", False ):
			self._getTeachMgr().onPrenticeNumChange( self.databaseID, self.getPrenticeNum() )

	def teach_masterEndTeach( self, talkEntity ):
		"""
		����ʦnpc��cell���ã�������Լ���ӵ�ͽ�ܵĹ�ϵ��

		@Param entityID:	npc��id
		@Type entityID:	OBJECT_ID
		"""
		if not self.iAmMaster():
			self.statusMessage( csstatus.TEACH_PRENTICE_NOT_REQUEST )
			return
		if not self.isInTeam():						# ʦ����ͽ����Ӽ��
			self.statusMessage( csstatus.TEACH_PLAYER_NOT_TEAM )
			return
		teamMembers = self.getTeamMemberMailboxs()
		if len( teamMembers ) < 2:				# ʦ����ͽ����Ӽ��
			self.statusMessage( csstatus.TEACH_PLAYER_NOT_TEAM )
			return
		if len( teamMembers ) > 2:
			self.statusMessage( csstatus.TEACH_END_TEAM_MORE_PEOPLE )
			return
		prenticeID = teamMembers[0].id  == self.id and teamMembers[1].id or teamMembers[0].id
		prentice = BigWorld.entities.get( prenticeID )
		if prentice is None:
			self.statusMessage( csstatus.TEACH_PRENTICE_TOO_FAR )
			return
		prenticeDBID = prentice.databaseID
		if not self.isPrentice( prenticeDBID ):
			self.statusMessage( csstatus.TEACH_PRENTICE_NOT_YOUR_PRENTICE )
			return
		if self.position.flatDistTo( prentice.position ) > csconst.TEACH_COMMUNICATE_DISTANCE:		# 10������
			self.statusMessage( csstatus.TEACH_PRENTICE_TOO_FAR )
			return
		prenticeLevel = prentice.level
		if prenticeLevel < csconst.TEACH_END_TEACH_LEAST_LEVEL:			# ͽ�ܵȼ�����ﵽ50�����ܳ�ʦ
			self.statusMessage( csstatus.TEACH_PRENTICE_NOT_GROW_UP )
			return
		self.removePrentice( prenticeDBID )
		if prenticeLevel <= csconst.TEACH_END_TEACH_AWARD_LIMIT:		# ���ͽ�ܵȼ�С��55�����ɻ�ó�ʦ����
			money = prenticeLevel * csconst.TEACH_END_MASTER_MONEY_AWARD
			self.gainMoney( money, csdefine.CHANGE_MONEY_MASTERENDTEACH )
			self.addExp( int( prenticeLevel * csconst.TEACH_END_MASTER_EXP_AWARD ), csdefine.CHANGE_EXP_MASTERENDTEACH )
			self.addTeachCredit( prenticeLevel * csconst.TEACH_END_MASTER_CREDIT_AWARD )
			awarder = g_rewards.fetch( csdefine.RCG_D_TEACH, self )
			if awarder is None or len( awarder.items ) <= 0:
				self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
				return
			awarder.award( self, csdefine.ADD_ITEM_MASTERENDTEACH )	# ��������Ʒ����

		else:
			self.statusMessage( csstatus.TEACH_PRENTICE_LEVEL_NOT_REWARD )
		self.base.masterEndTeach( prenticeDBID )
		prentice.endTeachSuccess()
		self._addTeachRewardItems( csdefine.RCG_TEACH_END_SUC_THK )

	def endTeachSuccess( self ):
		"""
		Define method.
		ʦ����ʦ�ɹ���֪ͨͽ����������

		@param master : ʦ��entity
		"""
		self.removeTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
		self._removeTeachData()
		if self.level < csconst.TEACH_END_TEACH_AWARD_LIMIT:	# ���ͽ�ܵȼ�С��55�����ɻ�ó�ʦ����
			money = self.level * csconst.TEACH_END_MASTER_MONEY_AWARD
			self.gainMoney( money, csdefine.CHANGE_MONEY_PRENTICEENDTEACH )
			self.addExp( int( self.level * csconst.TEACH_END_MASTER_EXP_AWARD ), csdefine.CHANGE_EXP_PRENTICEENDTEACH )
			
		self.base.endTeachSuccess( self.masterItem["playerDBID"] )
		self.masterItem = { "playerDBID":0, "playerBase":None }
		self._addTeachRewardItems( csdefine.RCG_TEACH_END_SUC )

	def autoDisbandSuccess( self, prenticeDBID ):
		"""
		Define mehtod.
		ͽ���Զ���ʦ�ɹ���֪ͨʦ��
		"""
		self.removePrentice( prenticeDBID )
		
	def onTeachLogin( self, playerDBID, playerBase, relationStatus ):
		"""
		Define method.
		��ʦͽ��ϵ�����������

		@param playerDBID : ���dbid
		@param playerBase : ���base mailbox
		@param relationStatus : ��Է���ҹ�ϵ
		"""
		if relationStatus & csdefine.ROLE_RELATION_MASTER:
			for prenticeItem in self.prenticeList:
				if prenticeItem["playerDBID"] == playerDBID:
					prenticeItem["playerBase"] = playerBase
					break
		elif relationStatus & csdefine.ROLE_RELATION_PRENTICE:
			self.masterItem["playerBase"] = playerBase

	def onTeachLogout( self, playerDBID, relationStatus ):
		"""
		Define method.
		��ʦͽ��ϵ�����������

		@param playerDBID : ���dbid
		@param relationStatus : ��Է���ҹ�ϵ
		"""
		if relationStatus & csdefine.ROLE_RELATION_MASTER:
			for prenticeItem in self.prenticeList:
				if prenticeItem["playerDBID"] == playerDBID:
					prenticeItem["playerBase"] = None
					break
		else:
			self.masterItem["playerBase"] = None

	def teach_prenticeCall( self, prenticeName, prenticeDBID, spaceName, lineNumber, position, direction ):
		"""
		Define method
		ͽ���ٻ�ʦ��
		"""
		prenticeMB = self.getPrenticeMbByDBID( prenticeDBID )
		if prenticeMB is None:
			DEBUG_MSG( "prentice( name:%s, dbid:%i )'s mailbox is None" % ( prenticeName, prenticeDBID ) )
			return
		if self.queryTemp( "prenticeCalling", () ):	# ������ڱ����ͽ���ٻ���
			prenticeMB.client.onStatusMessage( csstatus.CANT_CALL_MASTER_BUSY, "" )
			return
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			prenticeMB.client.onStatusMessage( csstatus.CANT_CALL_MASTER_BUSY, "" )
			return
		self.setTemp( "prenticeCalling", ( prenticeName, prenticeDBID, spaceName, lineNumber, position, direction ) )
		self.client.teach_prenticeCall( prenticeName )

	def teach_respondPrenticeCall( self, srcEntityID, answer ):
		"""
		Exposed method.
		ʦ����Ӧͽ�ܵ��ٻ�
		"""
		if self.id != srcEntityID:
			HACK_MSG( "���(%s) srcEntityID(%i) != self.id." % ( self.getName(), srcEntityID ) )
			return
		teleportData = self.popTemp( "prenticeCalling", () )
		if not teleportData:
			return
		prenticeMB = self.getPrenticeMbByDBID( teleportData[1] )
		if prenticeMB is None:
			DEBUG_MSG( "prentice( name:%s, dbid:%i )'s mailbox is None" % ( prenticeName, prenticeDBID ) )
			return
		if not answer:
			prenticeMB.client.onStatusMessage( csstatus.CANT_CALL_MASTER_BUSY, "" )
			return
		self.gotoSpaceLineNumber( teleportData[2], teleportData[3], teleportData[4], teleportData[5] )

	def tong_onChanged( self ):
		"""
		��ɫ���ı�֪ͨ������ϵ
		"""
		self.base.onTongChangeNotifyRelation( self.tongName )

	def tong_onSetTongName( self, tongName ):
		"""
		��ɫ������Ƹı�
		"""
		self.base.onTongChangeNotifyRelation( tongName )


	# ---------------------------------------------------------------------------------
	# ��ҽ��
	# ---------------------------------------------------------------------------------
	def hasAllyRelation( self ):
		"""
		����Ƿ��н�ݹ�ϵ
		"""
		return len( self.allyPlayers ) > 0

	def rlt_requestAlly( self, srcEntityID ):
		"""
		Exposed mehtod.
		����������ֵ�
		"""
		if srcEntityID != self.id:
			return

		if self.queryTemp( "ally_player_count", 0 ):
			#DEBUG_MSG( "---->>>������������" )
			return
		if not self.isInTeam():
			#DEBUG_MSG( "��Ҫ��ݾ�����ֵ����һ��������һ���˲��ܽ�ݡ�111" )
			return
		if not self.isTeamCaptain():
			#DEBUG_MSG( "�öӳ�������˵�ɣ���������һȺ��һ������̫�����ˣ�" )
			return
		if self.hasAllyRelation():
			#DEBUG_MSG( "�������Ҫ�������⣬ÿ��ֻ�ܽ��һ�Ρ����������˭ӵ�н�ݹ�ϵ��" )
			return
		teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
							if e.teamMailbox is not None \
							and e.teamMailbox.id == self.teamMailbox.id \
						]
		teammateList.append( self )
		memberNum = len( teammateList )
		if memberNum < 2:
			self.statusMessage( csstatus.CANNOT_ALLY_NO_PLAYER )
			#DEBUG_MSG( "��Ҫ��ݾʹ�����ֵ���������һ������ô��ݣ�222" )
			return
		if self.getTeamCount() > memberNum:
			self.statusMessage( csstatus.CANNOT_ALLY_LACK_SOME_PLAYER )
			#DEBUG_MSG( "����������û���������Ͽ������" )
			return

		DBIDList = []	# ��ҵ�dbid�б�����baseȥ��֤�������֮���Ƿ���Խ��塣
		for player in teammateList:
			if player.level < csconst.RELATION_ALLY_LEVEL_LACK:
				self.statusMessage( csstatus.CANNOT_ALLY_LACK_LEVEL, player.getName(), csconst.RELATION_ALLY_LEVEL_LACK )
				#DEBUG_MSG( "[%s]�ȼ�̫���ˣ�%i�����ϵ��˲��ܽ�ݣ�" % ( player.getName(), csconst.RELATION_ALLY_LEVEL_LACK ) )
				return
			if player.hasAllyRelation():
				self.statusMessage( csstatus.CANNOT_ALLY_HAD_ALREADY )
				#DEBUG_MSG( "������Ҫ�������⣬ÿ��ֻ�ܽ��һ�Ρ����������˭ӵ�н�ݹ�ϵ��" )
				return
			DBIDList.append( player.databaseID )

		for player in teammateList:
			tempDBIDList = DBIDList[:]
			tempDBIDList.remove( player.databaseID )
			player.base.rlt_requestAlly( self.base, tempDBIDList )
		self.setTemp( "ally_player_count", memberNum )	# ��ݵ������
		self.setTemp( "ally_player_dbid_list", DBIDList )		# ���������ݵ���������б�

	def rlt_allyCheckResult( self, playerDBID, statusID, statusArg ):
		"""
		Define method.
		����������Ļص�
		�ٴμ�飬�������������������������̴��������ݲ��ɹ���

		@param playerDBID : ���dbid�������������ĸ���ҵļ����
		@param statusID : �������uint16
		@param statusArg : status��Ϣ�Ķ��������python
		"""
		ally_player_count = self.queryTemp( "ally_player_count", 0 )
		if ally_player_count == 0:
			#DEBUG_MSG( "---->>>��������Ѿ�ֹͣ��" )
			self.rlt_removeAllyTempData()
			return
		DBIDList = self.queryTemp( "ally_player_dbid_list", [] )
		if playerDBID not in DBIDList:
			self.rlt_removeAllyTempData()
			return
		if not self.isTeamCaptain():
			self.rlt_removeAllyTempData()
			return

		if statusID != csstatus.CAN_ALLY:
			teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
								if e.teamMailbox is not None \
								and e.teamMailbox.id == self.teamMailbox.id \
							]
			self.statusMessage( statusID )	# ֪ͨ�������
			for player in teammateList:
				player.client.onStatusMessage( statusID, "" )
				#DEBUG_MSG( "statusID(%i)���������ͨ������ԭ��֪ͨ���(%s)" % (statusID, player.getName()))
			self.rlt_removeAllyTempData()
			return

		ally_player_count -= 1
		if ally_player_count > 0:
			self.setTemp( "ally_player_count", ally_player_count )
		else:	# ��������һ�����������ô����������
			teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
								if e.teamMailbox is not None \
								and e.teamMailbox.id == self.teamMailbox.id \
							]
			if len( DBIDList ) != len( teammateList ) + 1:
				#DEBUG_MSG( "--->>>������������ˣ���ݲ��ɹ���" )
				self.rlt_removeAllyTempData()
				return

			if self.money < csconst.RELATION_ALLY_COST:
				#DEBUG_MSG( "�������ֽ����ʽ��Ҫ����%i�������Ͻ�Ǯ���㣡" % ( csconst.RELATION_ALLY_COST/10000 ) )
				self.rlt_removeAllyTempData()
				return
			for itemInfo in csconst.RELATION_ALLY_NEED_ITEMS:
				item = self.findItemFromNKCK_( itemInfo[0] )
				if self.iskitbagsLocked() or item is None or item.isFrozen():
					#DEBUG_MSG( "---->>>>findItemFromNKCK_" )
					self.statusMessage( csstatus.CANNOT_ALLY_NO_ITEM )
					self.rlt_removeAllyTempData()
					return

			# ���� �½���� �� �����µĽ�ݳ�Ա����ͬ�Ĵ���
			newPlayerDBIDList = self.queryTemp( "allyNewPlayerDBIDlist", [] )
			if newPlayerDBIDList:
				#DEBUG_MSG( "--->>>join new member..." )
				newAllyPlayer = []
				oldAllyPlayer = []
				for player in teammateList:
					playerDBID = player.databaseID
					if not self.checkAllyByDBID( playerDBID ):
						if player.databaseID not in newPlayerDBIDList:
							#DEBUG_MSG( "--->>>��������ݲ�ƥ�䡣" )
							self.rlt_removeAllyTempData()
							return
						if player.hasAllyRelation():
							self.statusMessage( csstatus.CANNOT_ALLY_HAD_ALREADY )
							#DEBUG_MSG( "������Ҫ�������⣬ÿ��ֻ�ܽ��һ�Σ��³�Ա�Ѿ���ݹ��ˡ�" )
							self.rlt_removeAllyTempData()
							return
						newAllyPlayer.append( player )
					else:
						oldAllyPlayer.append( player )
				if len( newAllyPlayer ) != len( newPlayerDBIDList ):
					self.rlt_removeAllyTempData()
					return
				for player in newAllyPlayer:
					tempDBIDList = DBIDList[:]
					tempDBIDList.remove( player.databaseID )
					player.rlt_allySuccess( tempDBIDList )
				for player in oldAllyPlayer:
					player.rlt_allySuccess( newPlayerDBIDList )
				self.base.rlt_joinNewAllyMember( newPlayerDBIDList )
				self.rlt_removeAllyTempData()
				self.payMoney( csconst.RELATION_ALLY_NEW_COST, csdefine.CHANGE_MONEY_ALLY )
			else:
				#DEBUG_MSG( "---->>>add new relation" )
				# ����Ƿ���������
				for player in teammateList:
					if player.databaseID not in DBIDList:
						#DEBUG_MSG( "��ҶԲ��ϡ�" )
						self.rlt_removeAllyTempData()
						return
					if player.hasAllyRelation():
						#DEBUG_MSG( "������Ҫ�������⣬ÿ��ֻ�ܽ��һ�Ρ����������˭ӵ�н�ݹ�ϵ��" )
						self.rlt_removeAllyTempData()
						return

				# �����������ͨ������ʱ��ݳɹ�
				for player in teammateList:
					tempDBIDList = DBIDList[:]
					tempDBIDList.remove( player.databaseID )
					player.rlt_allySuccess( tempDBIDList )
				self.addTitle( csdefine.TITLE_ALLY_ID )	# ��ý���ƺ�
				#DEBUG_MSG( "--->>>�������ǵĿںš�" )
				DBIDList.remove( self.databaseID )
				self.base.rlt_startAlly( DBIDList )	# �ɶӳ��ѽ�ݹ�ϵд��db
				self.rlt_removeAllyTempData()
				self.payMoney( csconst.RELATION_ALLY_COST, csdefine.CHANGE_MONEY_ALLY )
			for itemInfo in csconst.RELATION_ALLY_NEED_ITEMS:
				self.removeItemTotal( itemInfo[0], itemInfo[1], csdefine.DELETE_ITEM_ALLY )

	def rlt_removeAllyTempData( self ):
		"""
		��������ʱ����
		"""
		self.removeTemp( "ally_player_count" )
		self.removeTemp( "ally_player_dbid_list" )
		self.removeTemp( "allyNewPlayerDBIDlist" )

	def rlt_allySuccess( self, DBIDList ):
		"""
		Define method.
		��ݳɹ�������cell����
		"""
		self.addTitle( csdefine.TITLE_ALLY_ID )	# ��ý���ƺ�
		#DEBUG_MSG( "--->>>�������ǵĿںš�" )
		self.base.rlt_allySuccess( DBIDList )

	def rlt_newMemberJoinAlly( self, srcEntityID ):
		"""
		Exposed method.
		��������µĽ�ݳ�Ա
		"""
		if self.id != srcEntityID:
			return

		if self.queryTemp( "ally_player_count", 0 ):
			#DEBUG_MSG( "---->>>������������" )
			return
		if not self.isInTeam():
			#DEBUG_MSG( "��Ҫ��ݾ�����ֵ����һ��������һ���˲��ܽ�ݡ�111" )
			return
		if not self.isTeamCaptain():
			#DEBUG_MSG( "�öӳ�������˵�ɣ���������һȺ��һ������̫�����ˣ�" )
			return
		teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
							if e.teamMailbox is not None \
							and e.teamMailbox.id == self.teamMailbox.id \
						]
		nearMemberNum = len( teammateList )
		if nearMemberNum < 2:
			self.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "��Ա�����������ǣ��ټ������ֵ��ٹ�����" )
			return
		if self.getTeamCount() > nearMemberNum+1 or nearMemberNum <= len( self.allyPlayers ):
			self.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "��Ա�����������ǣ��ټ������ֵ��ٹ�����" )
			return

		oldAllyDBIDList = []
		oldAllyPlayer = []
		allyDBIDList = []
		newAllyDBIDList = []
		newAllyPlayer = []
		for player in teammateList:
			playerDBID = player.databaseID
			if self.checkAllyByDBID( playerDBID ):
				oldAllyDBIDList.append( playerDBID )
				oldAllyPlayer.append( player )
			else:
				newAllyDBIDList.append( playerDBID )
				newAllyPlayer.append( player )
				if player.level < csconst.RELATION_ALLY_LEVEL_LACK:
					self.statusMessage( csstatus.CANNOT_ALLY_LACK_LEVEL, player.getName(), csconst.RELATION_ALLY_LEVEL_LACK )
					#DEBUG_MSG( "[%s]�ȼ�̫���ˣ�%i�����ϵ��˲��ܽ�ݣ�" % ( player.getName(), csconst.RELATION_ALLY_LEVEL_LACK ) )
					return
				if player.hasAllyRelation():
					self.statusMessage( csstatus.CANNOT_ALLY_HAD_ALREADY )
					#DEBUG_MSG( "������Ҫ�������⣬ÿ��ֻ�ܽ��һ�Σ��³�Ա(%s)�Ѿ���ݹ��ˡ�" % player.getName() )
					return
			allyDBIDList.append( playerDBID )
		if len( oldAllyDBIDList ) != len( self.allyPlayers ):
			self.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "��Ա�����������ǣ��ټ������ֵ��ٹ�����" )
			return

		oldAllyPlayer.append( self )	# �����Լ�
		allyDBIDList.append( self.databaseID )
		for player in oldAllyPlayer:
			player.base.rlt_requestAlly( self.base, newAllyDBIDList )
		for player in newAllyPlayer:
			DBIDList = allyDBIDList[:]
			DBIDList.remove( player.databaseID )
			player.base.rlt_requestAlly( self.base, DBIDList )

		self.setTemp( "allyNewPlayerDBIDlist", newAllyDBIDList )
		self.setTemp( "ally_player_count", len( allyDBIDList ) )
		self.setTemp( "ally_player_dbid_list", allyDBIDList )

	def checkAllyByDBID( self, playerDBID ):
		"""
		�Ƿ��ҵ�����
		"""
		for item in self.allyPlayers:
			if item["playerDBID"] == playerDBID:
				return True
		return False

	def checkAllyByID( self, entityID ):
		for item in self.allyPlayers:
			playerBase = item["playerBase"]
			if playerBase and playerBase.id == entityID:
				return True
		return False

	def receiveAllyInfo( self, relationItem ):
		"""
		Define method.
		������ҽ������

		@param relationItem: {"playerDBID":playerDBID,"playerBase":baseMailbox}
		"""
		self.allyPlayers.append( relationItem )

	def rlt_changeAllyTitle( self, srcEntityID, newTitleName ):
		"""
		Exposed method.
		���������Ľ�ݳƺ�
		"""
		if srcEntityID != self.id:
			return

		if not self.hasAllyRelation():
			return
		if not self.isTeamCaptain():
			return
		if self.money < csconst.ALLY_CHANGE_TITLE_COST:
			#DEBUG_MSG( "��������Ҫ���ѵģ���׼����5������������" )
			return
		teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
							if e.teamMailbox is not None \
							and e.teamMailbox.id == self.teamMailbox.id \
						]
		if len( self.allyPlayers ) > len( teammateList ):
			self.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "�ǲ������ֵ�û�����������Ͽ������" )
			return
		if set( [player.databaseID for player in teammateList] ) != set( [item["playerDBID"] for item in self.allyPlayers] ):
			self.statusMessage( csstatus.ALLY_CANNOT_WRONG_PLAYER )
			#DEBUG_MSG( "��������ô�в���ɵ��ˣ�" )
			return

		# �Ƿ���Υ���ʻ�ļ�飬�ͻ����ȼ��
		if not g_chatProfanity.isPureString( newTitleName ) :
			# "���Ʋ��Ϸ���"
			return
		elif g_chatProfanity.searchNameProfanity( newTitleName ) is not None :
			# "����������н��ôʻ�!"
			return

		self.payMoney( csconst.ALLY_CHANGE_TITLE_COST, csdefine.CHANGE_MONEY_ALLY )
		self.base.rlt_changeAllyTitle( newTitleName )

	def rlt_quitAlly( self, srcEntityID ):
		"""
		Exposed method.
		�˳����
		"""
		if self.id != srcEntityID:
			return

		if not self.hasAllyRelation():
			return

		self.removeTitle( csdefine.TITLE_ALLY_ID )
		self.allyPlayers = []
		self.base.rlt_quitAlly()

	def rlt_memberQuitAlly( self, playerDBID ):
		"""
		Define method.
		�����˳���ݣ������Լ��Ľ�ݹ�ϵ����
		"""
		for index, relationItem in enumerate( self.allyPlayers ):
			if relationItem["playerDBID"] == playerDBID:
				self.allyPlayers.pop( index )
				break

	def rlt_disbandAlly( self ):
		"""
		Define method.
		��ݹ�ϵ��ɢ�ˡ�
		"""
		self.removeTitle( csdefine.TITLE_ALLY_ID )
		self.allyPlayers = []
		self.base.rlt_disbandAlly()

	def onAllyTitleChanged( self, newTitleName ):
		"""
		Define method.
		��ݳƺŸı���
		"""
		if self.title == csdefine.TITLE_ALLY_ID:
			self.titleName = newTitleName

	def teach_enterKillMonsterSpaceSuccess( self ):
		"""
		Define method.
		"""
		localtime = time.localtime()
		# �´��ܲ��븱�����ʱ��
		canJoinTime = 24*3600 - localtime[3] * 3600 - localtime[4] * 60 - localtime[5] + time.time()
		self.set( "teachSpaceKillMonsterTime", int(canJoinTime) )
