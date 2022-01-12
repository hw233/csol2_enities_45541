# -*- coding: gb18030 -*-
#
#$Id:$

"""
14:23 2008-9-11,by wangshufeng
"""
"""
2010.11
������̨��ֲΪ�����̨ by cxm
"""
import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus
import Const
import time
from SpaceCopyTeam import SpaceCopyTeam


GO_OUT_TIMER = 11
END_ENTER_TIMER = 1111

class SpaceCopyTongAba( SpaceCopyTeam ):
	"""
	�����̨�������ռ�
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		self.right_playerEnterPoint = ()	# ��̨������right�������
		self.left_playerEnterPoint = ()		# ��̨������left�������
		self.right_chapmanPoint = ()		# ( position, direction )��right�����˵�λ��
		self.left_chapmanPoint = ()			# ( position, direction )��left�����˵�λ��
		self.left_relivePoints = []			# left�������
		self.right_relivePoints = []		# right�������


	def load( self, section ):
		"""
		�������м�������

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeam.load( self, section )

		# right�������
		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_playerEnterPoint = ( pos, direction )
		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_playerEnterPoint = ( pos, direction )

		# right������NPCλ��
		data = section[ "Space" ][ "right_chapmanPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_chapmanPoint = ( pos, direction )

		# left�������
		data = section[ "Space" ][ "left_relivePoint1" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_relivePoints.append( ( pos, direction ) )
		data = section[ "Space" ][ "left_relivePoint2" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_relivePoints.append( ( pos, direction ) )
		data = section[ "Space" ][ "left_relivePoint3" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_relivePoints.append( ( pos, direction ) )

		# right�������
		data = section[ "Space" ][ "right_relivePoint1" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_relivePoints.append( ( pos, direction ) )
		data = section[ "Space" ][ "right_relivePoint2" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_relivePoints.append( ( pos, direction ) )
		data = section[ "Space" ][ "right_relivePoint3" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_relivePoints.append( ( pos, direction ) )

		# left������NPCλ��
		data = section[ "Space" ][ "left_chapmanPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_chapmanPoint = ( pos, direction )

		# ս�����˵�NPCID
		self.chapmanNPCID = section[ "Space" ][ "chapmanNPCID" ].asString
		# ��������С��������
		self.enterLimitLevel = section[ "Space" ][ "enterLimitLevel" ].asInt
		# ĳ�˱�ɱ�۳�������
		self.bekillPunish = section[ "Space" ][ "bekillPunish" ].asInt
		# ����ʼ�ܻ���
		self.initTotalMark = section[ "Space" ][ "initTotalMark" ].asInt
		# ��ҵ�һ�ν���ĳ�ʼ�������
		self.playerInitBuyMark = section[ "Space" ][ "playerInitBuyMark" ].asInt
		# �������һ�����ӹ������
		self.playerOnDiedAddBuyMark = section[ "Space" ][ "playerOnDiedAddBuyMark" ].asInt


	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		DEBUG_MSG( "---------->>>" )
		# ����ս������NPC
		selfEntity.createNPCObject( self.chapmanNPCID, self.right_chapmanPoint[0], self.right_chapmanPoint[1], { "tempMapping" : {"isRight" : True } } )
		selfEntity.createNPCObject( self.chapmanNPCID, self.left_chapmanPoint[0], self.left_chapmanPoint[1], { "tempMapping" : {"isRight" : False } } )

		BigWorld.globalData["TongManager"].requestAbaData( selfEntity.base )


	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'tongDBID' : entity.tong_dbID }


	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		info = time.localtime()

		if entity.tong_grade <= 0 or entity.tong_dbID <= 0:
			return csstatus.SPACE_MISS_NOTTONG
		elif entity.level < self.enterLimitLevel:
			return csstatus.TONG_NO_WAR_LEVEL
		return csstatus.SPACE_OK


	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "tongName" ] = entity.tongName
		packDict[ "playerName" ] = entity.getName()
		packDict[ "playerDBID" ] = entity.databaseID
		return packDict


	def isTongPunish( self, selfEntity, tongDBID ):
		"""
		����Ƿ��ڱ��ͷ�״̬

		@param selfEntity : �ű���Ӧ��entity
		@type selfEntity : ENTITY
		@param tongDBID : ����dbid
		@type tongDBID : DATABASE_ID
		"""
		return False


	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.tong_onEnterAbaSpace()
		if selfEntity.queryTemp( "createTime", 0 ) == 0:
			selfEntity.setTemp("createTime", BigWorld.time() )
			restTime = 5 * 60 - selfEntity.getAbaTimeInfo()
			selfEntity.addTimer( restTime, 0, END_ENTER_TIMER )
		playerDBID = params[ "playerDBID" ]
		tongDBID = params[ "tongDBID" ]
		tongName = params[ "tongName" ]
		playerName = params[ "playerName" ]

		tongDBID1 = selfEntity.params["tongDBID1"]
		tongDBID2 = selfEntity.params["tongDBID2"]

		if tongDBID == selfEntity.params["tongDBID1"]:
			tongName = selfEntity.params["tongName1"]
		elif tongDBID == selfEntity.params["tongDBID2"]:
			tongName = selfEntity.params["tongName2"]

		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID ):		# ������û�б��������
			if tongDBID not in selfEntity.abaPointRecord:				# �����û�л��ּ�¼��û�а����ҽ���������
				selfEntity.abaPointRecord[ tongDBID ] = self.initTotalMark
			selfEntity.abaPlayers.updateTongAbaPoint( tongName,selfEntity.abaPointRecord[ tongDBID ], tongDBID )
			BigWorld.globalData[ "TongManager" ].addEnterTong( tongDBID )

		if tongDBID1 != 0:
			if selfEntity.abaPointRecord.has_key( tongDBID1 ):
				baseMailbox.client.updateTongAbaPoint( selfEntity.params["tongName1"], selfEntity.abaPointRecord[ tongDBID1 ], selfEntity.params["tongDBID1"] )
			else:
				baseMailbox.client.updateTongAbaPoint( selfEntity.params["tongName1"], 0, selfEntity.params["tongDBID1"] )
		if tongDBID2 != 0:
			if selfEntity.abaPointRecord.has_key( tongDBID2 ):
				baseMailbox.client.updateTongAbaPoint( selfEntity.params["tongName2"], selfEntity.abaPointRecord[ tongDBID2 ], selfEntity.params["tongDBID2"] )
			else:
				baseMailbox.client.updateTongAbaPoint( selfEntity.params["tongName2"], 0, selfEntity.params["tongDBID2"] )

		if selfEntity.abaPlayers.isPlayerExist( playerDBID ):				# ��������������
			selfEntity.abaPlayers.logonAgain( playerDBID, baseMailbox, tongDBID )	# ������ҵ�mailbox��tongDBID
		else:
			selfEntity.abaPlayers.addPlayer( playerDBID, playerName, self.playerInitBuyMark, tongDBID, tongName, baseMailbox )	# ��һ�ν��������

		# ��ÿһ�����븱������Ҹ���ս������ֹ�����Ƚ�������ҿ��������������ҵĻ�������
		for player in selfEntity.abaPlayers.keys():
			selfEntity.abaPlayers.updatePlayerAbaRecord( selfEntity.abaPlayers[player]["baseMB"], selfEntity.abaPlayers[player]["playerDBID"] )

		player = baseMailbox.cell
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[ baseMailbox.id  ]

		if tongDBID == selfEntity.params["tongDBID1"]:	# ʵ�ڸ��Ӱ�
			if selfEntity.params["isRight"]:
				player.setTemp( "aba_right", True )
			else:
				player.setTemp( "aba_right", False )
		else:
			if selfEntity.params["isRight"]:
				player.setTemp( "aba_right", False )
			else:
				player.setTemp( "aba_right", True )

		player.setTemp( "tong_aba_sclass", selfEntity.className )			# ����������ڸ����Ľű����֣��Ա���Һ͸�������ͬһ��serverʱ�����һظ���

		player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
		player.lockPkMode()														#����pkģʽ����������

		player.addHP( player.HP_Max )
		player.addMP( player.MP_Max )

		BigWorld.globalData[ "TongManager" ].onMemberEnter( tongDBID )

	def endEnter( self,selfEntity ):
		persistTime = selfEntity.getAbaTimeInfo()
		round = selfEntity.getAbaRound()
		selfEntity.abaPlayers.endEnter( round,persistTime )

		if self.isCurrentAbaOver( selfEntity ):
			return
		#if len( selfEntity.abaPointRecord ) == 1:		# ֻ��һ����������������ǰ�����ó�����
		#	self.onTongAbaOver( selfEntity )
		#	return
		tongDBID1 = selfEntity.params["tongDBID1"]
		tongDBID2 = selfEntity.params["tongDBID2"]

		if BigWorld.globalData.has_key("TongAba_signUp_one"):		# ֻ��һ����ᱨ�����볡�������Ͻ�����ǰ����
			selfEntity.setTemp( "tongAbaOver", True )
			if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ):
				BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID1 )
				return
			else:
				selfEntity.abaPlayers.onTongAbaOver( selfEntity.abaRound, tongDBID1 )
				BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpace( tongDBID1,True )
				selfEntity.addTimer( 2, 0, GO_OUT_TIMER )		# 2���Ӻ󣬰��˴��ͳ�ȥ
				return

		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) or selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):	# �����������븱����������һ���ڱ�����ʼǰ���ܹ��ˣ���ǰ�����ó�����
			selfEntity.setTemp( "tongAbaOver", True ) 	# ��¼����ս���Ѿ�����
			selfEntity.abaPlayers.spellProtect()
			selfEntity.addTimer( 2, 0, GO_OUT_TIMER )		# 2���Ӻ󣬰��˴��ͳ�ȥ
			if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and not selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
				selfEntity.abaPlayers.onTongAbaOver( selfEntity.abaRound, tongDBID2 )
				BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpace( tongDBID2,True )
				#BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID1 )
			elif not selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
				selfEntity.abaPlayers.onTongAbaOver( selfEntity.abaRound, tongDBID1 )
				BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpace( tongDBID1,True )
				#BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID2 )
			elif selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
				BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpaceNoWinner( tongDBID1,tongDBID2,True )
				#BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID1 )
				#BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID2 )

	def isCurrentAbaOver( self, selfEntity ):
		"""
		�Ƿ񱾸���ս���Ѿ�����
		"""
		return selfEntity.queryTemp( "tongAbaOver", False )

	def isAllAbaOver( self ):
		"""
		�Ƿ���̨��ʱ���Ѿ�������
		"""
		return BigWorld.globalData["tongAbaStep"]


	def packedSpaceDataOnLeave( self, entity ):
		"""
		��ȡentity�뿪ʱ�������ڵ�space�����뿪��space��Ϣ�Ķ��������
		@param entity: ��Ҫ��space entity�����뿪��space��Ϣ(onLeave())��entity��ͨ��Ϊ��ң�
		@return: dict������Ҫ�뿪��space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ�Ƚ��뿪����������뵱ǰ��¼����ҵ����֣��������Ҫ������ҵ�playerName����
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnLeave( self, entity )
		packDict[ "playerDBID" ] = entity.databaseID
		packDict[ "playerName" ] = entity.playerName
		packDict[ "tongDBID" ] = entity.tong_dbID
		return packDict

	def onLeaveCommon( self, selfEntity, baseMailbox, params  ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params  )
		player = baseMailbox.cell
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[ baseMailbox.id  ]
			player.unLockPkMode()		# ����pkģʽ���ҵ�/û�ҵ�playerEntity�Ľ�������ֿ�������setPkMode������unLockPkMode֮ǰִ�У�
		else:
			player.unLockPkMode()		# ����pkģʽ
		player.setSysPKMode( 0 )

		playerDBID = params["playerDBID"]
		tongDBID = params["tongDBID"]
		player.addHP( player.HP_Max )
		player.addMP( player.MP_Max )
		player.tong_clearWarItems()
		#player.spellTarget( 122155001, player.id )

		baseMailbox.client.tong_onLeaveWarSpace()

		if not self.isCurrentAbaOver( selfEntity ):
			BigWorld.globalData[ "TongManager" ].onMemberLeave( tongDBID )
		BigWorld.globalData["TongManager"].recordRound( playerDBID, csdefine.MATCH_TYPE_TONG_ABA, selfEntity.getAbaRound(), baseMailbox )

		selfEntity.abaPlayers.playerLeave( playerDBID )		# ����뿪�������

		if selfEntity.getAbaTimeInfo() >= 5 * 60:
			baseMailbox.client.onStatusMessage( csstatus.TONG_COMPETETION_LEAVE,"" )

		if tongDBID == selfEntity.params["tongDBID1"]:
			tongName = selfEntity.params["tongName1"]
		elif tongDBID == selfEntity.params["tongDBID2"]:
			tongName = selfEntity.params["tongName2"]

		# �Ƿ�����Ա��;ȫ���뿪��������ǰ�����ı���
		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID ):
			selfEntity.abaPlayers.updateTongAbaPoint( tongName, -1 , tongDBID )
			DEBUG_MSG( "--------->>>time", BigWorld.time() )
			if selfEntity.getAbaTimeInfo() >= 5 * 60:			# �ڱ��������У����һ������ܹ��ˣ���ǰ��������
				self.onTongAbaOver( selfEntity )
			else:
				BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID )

	def onPlayerDied( self, selfEntity, killerDBID, killer, beKillerDBID, beKiller ):
		"""
		������������¼������
		"""
		# ���ս���Ѿ����� ��ô�������ټ������
		if self.isCurrentAbaOver( selfEntity ) or self.isAllAbaOver():
			return

		kTongDBID = selfEntity.abaPlayers.getPlayerTongDBID( killerDBID )
		bkTongDBID = selfEntity.abaPlayers.getPlayerTongDBID( beKillerDBID )

		# ���Լ������ɱ�Ĳ��۷�
		if kTongDBID == bkTongDBID:
			return

		# ������ҵ�ս������
		selfEntity.abaPlayers.updateRecord( killerDBID, beKillerDBID )
		# ��ɱ�ߣ����ӹ�����Ʒ�Ļ���
		self.changeAbaBuyPoints( selfEntity, beKiller, beKillerDBID, self.playerOnDiedAddBuyMark )

		# �ü����˱�ɱ��,�۳�100��
		selfEntity.abaPointRecord[ bkTongDBID ] -= self.bekillPunish
		tongName = selfEntity.abaPlayers.getPlayerTongName( beKillerDBID )
		if selfEntity.abaPointRecord[ bkTongDBID ] <= 0:
			selfEntity.abaPointRecord[ bkTongDBID ] = 0
			self.onTongAbaOver( selfEntity )
			selfEntity.abaPlayers.updateTongAbaPoint( tongName, -1,bkTongDBID )
		else:
			selfEntity.abaPlayers.updateTongAbaPoint( tongName, selfEntity.abaPointRecord[ bkTongDBID ],bkTongDBID )

		# ֪ͨ��Щ����Աĳĳ��ɱ������ɱ��ĳĳ
		self.sendTongWarPlayerDieInfo( False, bkTongDBID, beKillerDBID )
		if kTongDBID > 0:
			self.sendTongWarPlayerDieInfo( True, kTongDBID, killerDBID )

	def sendTongWarPlayerDieInfo( self, isKiller, tongDBID, playerDBID ):
		"""
		֪ͨĳ��� ĳ����Աɱ��һ������,���߱�����ɱ��
		"""
		k = "tong.%i" % tongDBID
		try:
			tongMailbox = BigWorld.globalData[ k ]
		except KeyError:
			ERROR_MSG( "tong %s not found." % k )
			return
		tongMailbox.onWarKillerPlayer( isKiller, playerDBID )		# ʹ��ͳһ�Ľӿڣ��������¶���

	def onTongAbaOver( self, selfEntity ):
		"""
		��̨�������ˣ�����Ҽ�����Ӧ������֪ͨ������
		"""
		if self.isCurrentAbaOver( selfEntity ):
			return
		#if self.isAllAbaOver():
		#	return
		selfEntity.setTemp( "tongAbaOver", True ) 	# ��¼����ս���Ѿ�����
		selfEntity.abaPlayers.spellProtect()
		winnerDBID = self.getWinnerDBID( selfEntity )
		if winnerDBID != 0:
			BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpace( winnerDBID, False )				# ֪ͨ��̨��������ĳ��ս����ǰ������
		else:
			tongDBID1 = selfEntity.params["tongDBID1"] #selfEntity.abaPointRecord.keys()
			tongDBID2 = selfEntity.params["tongDBID2"]
			BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpaceNoWinner( tongDBID1, tongDBID2, False )				# ֪ͨ��̨��������ĳ��ս��������,û��ʤ����

		selfEntity.abaPlayers.onTongAbaOver( selfEntity.abaRound, winnerDBID )

		selfEntity.addTimer( 2 * 60, 0, GO_OUT_TIMER )		# 2���Ӻ󣬰��˴��ͳ�ȥ

	def getWinnerDBID( self, selfEntity ):
		"""
		ȡʤ������dbid
		"""
		winnerDBID = 0
		tongDBID1 = selfEntity.params["tongDBID1"]
		tongDBID2 = selfEntity.params["tongDBID2"]
		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and not selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
			winnerDBID = tongDBID2
			return winnerDBID
		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ) and not selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ):
			winnerDBID = tongDBID1
			return winnerDBID
		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
			return winnerDBID


		pointList = selfEntity.abaPointRecord.values()
		# ���2�����嶼��
		pointReverseDict = dict( map( None, selfEntity.abaPointRecord.values(), selfEntity.abaPointRecord.keys() ) )
		if pointList[0] > pointList[1]:
			winnerDBID = pointReverseDict[pointList[0]]
		elif pointList[0] < pointList[1]:
			winnerDBID = pointReverseDict[pointList[1]]
		return winnerDBID

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == END_ENTER_TIMER:
			self.endEnter( selfEntity )
		elif userArg == GO_OUT_TIMER:
			selfEntity.abaPlayers.onTelportPlayer()
			selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )		# ��Ҫ�ӳ�10s�رո���
			return
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

		tongAbaOverTimer = selfEntity.queryTemp( "tongAbaOverTimer" )
		if tongAbaOverTimer == id:
			selfEntity.cancel( selfEntity.queryTemp( "tongAbaOverTimer" ) )
			checkPlayerCount = selfEntity.queryTemp( "checkPlayerCount", 0 )
			if checkPlayerCount <= 0:
				self.onTongAbaOver( selfEntity )
				# ��⵽û����,��ô�رո���
				if not selfEntity.abaPlayers.hasPlayer():
					selfEntity.base.closeSpace( True )
				else:
					selfEntity.setTemp( "checkPlayerCount", 1 )
					selfEntity.setTemp( "tongAbaOverTimer", selfEntity.addTimer( 2 * 60, 0, 1 ) )
			elif checkPlayerCount == 1:
				# ����3���Ӻ� ��������Ƿ��Զ��뿪 ����ֱ���߳�
				selfEntity.setTemp( "checkPlayerCount", 2 )
				selfEntity.setTemp( "tongAbaOverTimer", selfEntity.addTimer( 1 * 60, 0, 1 ) )
			elif checkPlayerCount == 2:
				selfEntity.base.closeSpace( True )

	def onPlayerRelive( self, selfEntity, playerID, playerDBID ):
		"""
		��������ص��� ��Ҫ���ڸ��������� ��ɫδ��� ������ʩ���޵�BUFF��
		�Ƚ�ɫ����� �ᴦ���ޱ���״̬�� ����
		�ص��������� ������������¼���
		"""
		if self.isCurrentAbaOver( selfEntity ) or self.isAllAbaOver():
			if BigWorld.entities.has_key( playerID ):
				BigWorld.entities[ playerID ].spellTarget( 122156001, playerID )
			else:
				try:
					selfEntity.abaPlayers[ playerDBID ][ "baseMB" ].cell.spellTarget( 122156001, playerID )
				except:
					DEBUG_MSG( "-------->>>player's databaseID( %i ) not in the space." % playerDBID )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		if not killer:	# û�ҵ�ɱ���ߣ�����������������ֱ�ӷ���
			DEBUG_MSG( "player( %s ) has been killed,can't find killer." % role.getName() )
			return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if role.tong_dbID == killer.tong_dbID:
				role.calcPkValue( killer )
			else:
				spaceBase = role.getCurrentSpaceBase()
				spaceEntity = BigWorld.entities.get( spaceBase.id )
				if spaceEntity and spaceEntity.isReal():
					self.onPlayerDied( spaceEntity, killer.databaseID, killer, role.databaseID, role )
				else:
					spaceBase.cell.remoteScriptCall( "onPlayerDied", ( killer.databaseID, killer, role.databaseID, role ) )
				#role.tong_warItemsDropOnDied()

	def onNPCDealItemChangeAbaMark( self, selfEntity, player, databaseID, mark, state ):
		"""
		����NPC���������Ʒ���µĻ��ָı�
		"""
		ret = 1
		if state == 0: # �������1��ս����Ʒ
			if selfEntity.abaPlayers[ databaseID ]["buyPoints"] < mark:
				ret = 0
			else:
				self.changeAbaPointRecord( selfEntity, databaseID, player.tong_dbID, -mark )
				self.changeAbaBuyPoints( selfEntity, player, databaseID, -mark )
			player.onTongAbaBuyFromNPCCallBack( ret )
			#----------------------------------------------------------------
		elif state == 1: # �������1������ս����Ʒ
			if selfEntity.abaPlayers[ databaseID ]["buyPoints"] < mark:
				ret = 0
			else:
				self.changeAbaPointRecord( selfEntity, databaseID, player.tong_dbID, -mark )
				self.changeAbaBuyPoints( selfEntity, player, databaseID, -mark )
			player.onTongAbaBuyArrayFromNPCCallBack( ret )
			#----------------------------------------------------------------
		elif state == 2: # ��ҳ�����ս����Ʒ ���ӻ���
			self.changeAbaPointRecord( selfEntity, databaseID, player.tong_dbID, mark )

	def changeAbaPointRecord( self, selfEntity, databaseID, tongDBID, mark ):
		"""
		�����ֱ��
		"""
		tongName = selfEntity.abaPlayers.getPlayerTongName( databaseID )
		selfEntity.abaPointRecord[ tongDBID ] += mark
		if selfEntity.abaPointRecord[ tongDBID ] <= 0:
			selfEntity.abaPointRecord[ tongDBID ] = 0
			self.onTongAbaOver( selfEntity )
			selfEntity.abaPlayers.updateTongAbaPoint( tongName, -1,tongDBID )
			return

		selfEntity.abaPlayers.updateTongAbaPoint( tongName, selfEntity.abaPointRecord[ tongDBID ],tongDBID )

	def changeAbaBuyPoints( self, selfEntity, player, databaseID, mark ):
		"""
		��ɫ�Ĺ������
		"""
		selfEntity.abaPlayers[ databaseID ]["buyPoints"] += mark
		player.client.tong_updateAbaBuyPoint( selfEntity.abaPlayers[ databaseID ]["buyPoints"] )
