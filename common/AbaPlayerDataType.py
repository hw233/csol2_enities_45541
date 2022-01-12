# -*- coding: gb18030 -*-
#
#

from bwdebug import *
import BigWorld
import csdefine
import csconst
import csstatus



class AbaPlayerDataType( dict ):
	"""
	�����̨�����������Ϣ����
	"""
	def __init__( self ):
		"""
		"""
		pass


	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		abaPlayerList = []
		dAbaPlayers = { "items":abaPlayerList }
		for playerDBID, abaPlayerItem in obj.iteritems():
			abaPlayerList.append( abaPlayerItem )
		return dAbaPlayers


	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = AbaPlayerDataType()
		for abaPlayerItem in dict[ "items" ]:
			playerDBID = abaPlayerItem[ "playerDBID" ]
			obj[ playerDBID ] = abaPlayerItem
		return obj


	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, AbaPlayerDataType )


	def isPlayerExist( self, playerDBID ):
		"""
		����Ƿ��Ѿ����ڣ������������������
		"""
		return self.has_key( playerDBID )


	def addPlayer( self, playerDBID, playerName, playerInitBuyPoint, tongDBID, tongName, baseMailbox  ):
		"""
		����һ���������
		"""
		self[ playerDBID ] = { "playerDBID":playerDBID,
								"playerName":playerName,
								"buyPoints":playerInitBuyPoint,
								"killNum":0,
								"beKilledNum":0,
								"tongDBID":tongDBID,
								"tongName":tongName,
								"baseMB":baseMailbox,
							}
		baseMailbox.client.tong_updateAbaBuyPoint( playerInitBuyPoint )

	def updateRecord( self, killerDBID, beKillerDBID ):
		"""
		��ҵ�ս����������仯

		@param killerDBID : ɱ���ߵ�dbid
		@type killerDBID : DATABASE_ID
		@param beKillerDBID : ��ɱ�ߵ�dbid
		@type beKillerDBID : DATABASE_ID
		"""
		self[ killerDBID ][ "killNum" ] += 1
		self[ beKillerDBID ][ "beKilledNum" ] += 1

		for playerItem in self.itervalues():	# ������ң�����ս����
			if playerItem["baseMB"]:
				playerItem["baseMB"].client.updatePlayerAbaRecord( self[killerDBID]["playerName"], self[killerDBID]["killNum"], self[killerDBID]["beKilledNum"], self[killerDBID]["tongDBID"] )
				playerItem["baseMB"].client.updatePlayerAbaRecord( self[beKillerDBID]["playerName"],self[beKillerDBID]["killNum"],self[beKillerDBID]["beKilledNum"],self[beKillerDBID]["tongDBID"] )

	def logonAgain( self, playerDBID, baseMailbox, tongDBID ):
		"""
		������µ�¼
		"""
		self[ playerDBID ][ "baseMB" ] = baseMailbox
		self[ playerDBID ][ "tongDBID" ] = tongDBID
		playerInitBuyPoint = self[ playerDBID ]["buyPoints"]
		baseMailbox.client.tong_updateAbaBuyPoint( playerInitBuyPoint )
	
	def endEnter( self,round,persistTime):
		"""
		�����볡ʱ��ú�������������
		"""
		for key,info in self.iteritems():
			playerBase = info["baseMB"]
			if not playerBase:
				continue
			level = BigWorld.entities[ playerBase.id ].getLevel()
			playerBase.client.tong_onInitRemainAbaTime( persistTime,round )		# ��ʼ����ҿͻ�����̨������:��̨��ʣ��ʱ��
			BigWorld.globalData["TongManager"].recordJoinPlayer( info["playerName"],playerBase,level )
			
			player = BigWorld.entities[ playerBase.id ]
			player.lockPkMode()
			player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG )	#ǿ����ҽ�����pk ״̬

	def updatePlayerAbaRecord( self, baseMailbox, playerDBID ):
		"""
		��ս������µ�ָ����ҿͻ���

		@param baseMailbox : ���base mailbox
		@param baseMailbox : MAILBOX
		"""
		for playerDBID, abaPlayerItem in self.iteritems():
			baseMailbox.client.updatePlayerAbaRecord( abaPlayerItem["playerName"], abaPlayerItem["killNum"], abaPlayerItem["beKilledNum"], abaPlayerItem["tongDBID"] )

		for playerItem in self.itervalues():	# ͬʱ�����Լ�����Ϣ���¸��������
			if playerItem["baseMB"]:
				playerItem["baseMB"].client.updatePlayerAbaRecord( self[playerDBID]["playerName"], self[playerDBID]["killNum"], self[playerDBID]["beKilledNum"], self[playerDBID]["tongDBID"] )

	def removePlayer( self, playerDBID ):
		"""
		�Ƴ�һ���������
		"""
		if self.has_key( playerDBID ):
			del self[ playerDBID ]


	def playerLeave( self, playerDBID ):
		"""
		����뿪������tongDBID��Ϊ���ж�--�Ƿ�������г�Ա�뿪�����ǣ�Ҫ������������

		@param playerDBID : ���dbid
		@param playerDBID : DATABASE_ID
		"""
		self[ playerDBID ][ "tongDBID" ] = 0
		self[ playerDBID ][ "baseMB" ] = None

	def isTongAllPlayerLeave( self, tongDBID ):
		"""
		�Ƿ�������г�Ա�뿪��
		"""
		for playerItem in self.itervalues():
			if playerItem["tongDBID"] == tongDBID:
				return False
		return True


	def getPlayerTongDBID( self, playerDBID ):
		"""
		�����ҵİ��dbid
		"""
		return self[ playerDBID ][ "tongDBID" ]


	def getPlayerTongName( self, playerDBID ):
		"""
		����ҵ�dbid�����ҵİ������
		"""
		return self[ playerDBID ][ "tongName" ]


	def updateTongAbaPoint( self, tongName, point,tongDBID ):
		"""
		���°����ֵ�ÿһ����ҵĿͻ���
		"""
		for playerItem in self.itervalues():
			if playerItem["baseMB"]:
				playerItem["baseMB"].client.updateTongAbaPoint( tongName, point, tongDBID )


	def onTongAbaOver( self, awardLevel, winnerTongDBID ):
		"""
		��̨������������������Ҽ�����Ӧ��������������Ҽ����޵�buff

		@param awardLevel : �����ִΣ��ݴ˾�����������
		@type awardLevel : INT8
		@param winnerDBID : ʤ������dbid
		@type winnerDBID : DATABASE_ID
		"""
		for playerItem in self.itervalues():
			playerBase = playerItem["baseMB"]
			if playerBase is None:
				continue

			if BigWorld.entities.has_key( playerBase.id ):
				player = BigWorld.entities[ playerBase.id ]
					
				if playerItem["tongDBID"] == winnerTongDBID and winnerTongDBID != 0:
					if not BigWorld.globalData.has_key("TongAba_signUp_one"):		# �����ֻ��һ����ᱨ�������������ʤ����
						winExp =  ( int( pow( player.level,1.2 ) * 5 ) + 25 ) * 70 * ( 4 * awardLevel + 6 )	# ��ʤ��������ֵ
						player.addExp( winExp,csdefine.REWARD_TONG_ABA_EXP )
					if awardLevel == csdefine.ABATTOIR_FINAL or BigWorld.globalData.has_key("TongAba_signUp_one"):		# �����ֻ��һ����ᱨ���������ͬ������ھ���
						if BigWorld.globalData.has_key( "tongAbattoirChampionDBID" ):
							temp = BigWorld.globalData[ "tongAbattoirChampionDBID" ]
							temp.append( player.databaseID )
							BigWorld.globalData[ "tongAbattoirChampionDBID" ] = temp
					
				player.unLockPkMode()
				player.setPkMode( player.id, csdefine.PK_CONTROL_PROTECT_PEACE )
				player.lockPkMode()
				player.client.tong_onTongAbaOver()
	
	def onTelportPlayer( self ):
		"""
		����뿪�����Ĵ���
		"""
		for playerItem in self.itervalues():
			playerBase = playerItem["baseMB"]
			if playerBase is None:
				continue
			
			if BigWorld.entities.has_key( playerBase.id ):
				BigWorld.entities[ playerBase.id ].tong_onAbattoirOver()
			else:
				playerBase.cell.tong_onAbattoirOver()

	def spellProtect( self ):
		"""
		�����޵�buff
		"""
		for playerItem in self.itervalues():
			playerBase = playerItem["baseMB"]
			if playerBase is None:
				continue

			if BigWorld.entities.has_key( playerBase.id ):
				player = BigWorld.entities[ playerBase.id ]
				player.spellTarget( 122156001, player.id )		# ����Ҽ����޵�buff
			else:
				playerBase.cell.remoteCall( "spellTarget", ( 122156001, playerBase.id ) )

	def hasPlayer( self ):
		"""
		�������Ƿ������
		"""
		for playerItem in self.itervalues():
			if playerItem["baseMB"] is not None:
				return True
		return False


instance = AbaPlayerDataType()
