# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyCityWar.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

"""
��׼������Ҳ������Ϊ��������
"""

import BigWorld
import Language
from bwdebug import *
import time
import Const
import random
import csstatus
import csdefine
from SpaceCopy import SpaceCopy
import TongBuildingData
tongBuildingDatas = TongBuildingData.instance()
tongBuildingLevel = TongBuildingData.tbl_instance()

# ��������Ĺؼ���ӳ��
keyMapping = {
			csdefine.TONG_BUILDING_TYPE_YSDT 	: "ysdt",	# ���´���
			csdefine.TONG_BUILDING_TYPE_JK 		: "jk",		# ���
			csdefine.TONG_BUILDING_TYPE_SSD 	: "ssd",	# ���޵�
			csdefine.TONG_BUILDING_TYPE_CK 		: "ck",		# �ֿ�
			csdefine.TONG_BUILDING_TYPE_TJP 	: "tjp",	# ������
			csdefine.TONG_BUILDING_TYPE_SD 		: "sd",		# �̵�
			csdefine.TONG_BUILDING_TYPE_YJY 	: "yjy",	# �о�Ժ
			}

# ��� ħ����Ϯ ĳ�����������ӳ��
campaignMonsterIDMapping = {
			50 	: "20754003",
			70 	: "20754004",
			90 	: "20754005",
			110 : "20754006",
			130 : "20754007",
			150 : "20754008",
		}

# ħ����ϮС��
campaignMonsterList = ["20724006", "20744007"]

class SpaceCopyTongTerritory( SpaceCopy ):
	"""
	������
	@ivar domainMB:			һ�����������ԣ���¼����������ռ�mailbox������ĳЩ��Ҫ֪ͨ������ռ�Ĳ������˽ӿ����ΪNone���ʾ��ǰ����ʹ��
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )

		self.buildings = {}							# ��Ὠ����
		self.npcs = {}								# �������NPC
		self.shenshouMB = None  					# ���޵�base mailbox
		self.campaignMonsterRaidNPCMB = None		# �ħ����Ϯ ����base mailbox
		self.campaignMonsterMBList = []				# �ħ����Ϯ С��base mailbox�б�
		self.campaignMonsterNum = 0					# �ħ����Ϯ��ɱ������������ȫ������ɱ���󣬻������
		self._createNewShenShouTimerID = 0			# ѡ���������޺󴴽������޵�һ��ʱ��
		self._npcLocked = False						# �Ƿ���ס��NPC
		self._isFixNagual = True					# �����Ƿ��ڹ̶�ģʽ(������һ���̶�λ�ù���)
		self._isCampaignMonsterRaidOver = True		# ��� ħ����Ϯ�ʱ���Ƿ����
		self.feteThings = []						# �������еĳ�������б�
		self._shenshouReviveTimeID = 0				# ���޸���timerID
		self._protectTongNPCList = []				# �������ɻ��NPC
		self.isUpdateBuildingModel = 0				# �Ƿ���°�Ὠ��ģ��

		# ��cell�ɹ�����֮���Զ����õ����� ���API:addRoutineOnGetCell() by mushuang
		self._routinesOnGetCell = []				# [ ( routine1, ( arg1, arg2, ... ) ), ( routine2, ( arg1, arg2, ... ) ), ... ]

		# ���Լ�ע������
		BigWorld.globalData[ "TongManager" ].onRegisterTerritory( self.params["tongDBID"], self )

	def getbuildingLevelByType( self, buildingType ):
		"""
		����һ��ʵʱӰ��
		"""
		return {
				csdefine.TONG_BUILDING_TYPE_YSDT 	: self.params[ "ysdt_level" ],	# ���´���
				csdefine.TONG_BUILDING_TYPE_JK 		: self.params[ "jk_level" ],	# ���
				csdefine.TONG_BUILDING_TYPE_SSD 	: self.params[ "ssd_level" ],	# ���޵�
				csdefine.TONG_BUILDING_TYPE_CK 		: self.params[ "ck_level" ],	# �ֿ�
				csdefine.TONG_BUILDING_TYPE_TJP 	: self.params[ "tjp_level" ],	# ������
				csdefine.TONG_BUILDING_TYPE_SD 		: self.params[ "sd_level" ],	# �̵�
				csdefine.TONG_BUILDING_TYPE_YJY 	: self.params[ "yjy_level" ],	# �о�Ժ
			}[ buildingType ]

	def activeNagual( self, enemyTongDBID ):
		"""
		��������
		"""
		self._isFixNagual = False
		if self.shenshouMB:
			self.shenshouMB.cell.activeNagual( enemyTongDBID )

	def disableNagual( self ):
		"""
		���޻ָ���������
		"""
		self._isFixNagual = True
		if self.shenshouMB:
			self.shenshouMB.cell.disableNagual()

	def onRobWarStart( self, enemyTongDBID ):
		"""
		define method.
		����Ӷ�ս��ʼ
		"""
		self.activeNagual( enemyTongDBID )

		if hasattr( self, "cell" ):
			DEBUG_MSG( "Notify cell rob war starting directly!" )
			self.cell.onStartRobWar( enemyTongDBID )
		else:
			def __notifyCellOnStartRobWar( enemyTongDBID ):
				"""
				֪ͨcell����ӶῪʼ
				"""
				DEBUG_MSG( "Notify cell rob war starting after get cell!" )
				self.cell.onStartRobWar( enemyTongDBID )

			self.addRoutineOnGetCell( __notifyCellOnStartRobWar, [ enemyTongDBID ] )

	def onRobWarStop( self ):
		"""
		define method.
		����Ӷ�ս����
		"""
		self.disableNagual()

		if hasattr( self, "cell" ):
			self.cell.onEndRobWar()

	def onTongDismiss( self ):
		"""
		define method.
		��ᱻ��ɢ�ˣ�׼�����������������
		"""
		self.banishPlayer()
		self.startCloseCountDownTimer( 30 )

	def getTongTerritoryEntity( self, key ):
		"""
		��ȡ��Ὠ����entity
		"""
		"""
		�Ժ�����ҪӦ��ʵ��
		if key == xxx:
		   return shenshou
		elif key == xxxType:
		   return self.npcs[ key ]
		eilf key == xxxType:
		   return xxxbuild
		"""
		try:
			e = self.npcs[ key ]
		except KeyError:
			ERROR_MSG( " key error! %s" % self.npcs.keys() )
			return None
		return e

	def addRoutineOnGetCell( self, routine, arg ):
		"""
		@addRoutineOnGetCell: ����һ����OnGetCell�е��õ�����
		@routine: Ҫ���õ����̣��˶�������ǿɵ��õ�
		@arg: list, ָ��Ҫ����Ĳ���
		"""
		#self._routinesOnGetCell [ ( routine1, ( arg1, arg2, ... ) ), ( routine2, ( arg1, arg2, ... ) ), ... ]

		assert hasattr( routine, "__call__" ), "routine must be callable!"

		argInTuple = tuple( arg )

		self._routinesOnGetCell.append( ( routine, argInTuple ) )

	def __callRoutinesOnGetCell( self ):
		"""
		�ڳɹ���ȡCell֮������Ѿ�������е�����
		"""
		for element in self._routinesOnGetCell:
			routine = element[ 0 ]
			argInTuple = element[ 1 ]
			try:
				routine( *argInTuple )
			except:
				ERROR_MSG( "Routine: %s failed!"%routine )

		self._routinesOnGetCell = []

	def onGetCell(self):
		"""
		cellʵ�崴�����֪ͨ���ص�callbackMailbox.onSpaceComplete��֪ͨ������ɡ�
		"""
		SpaceCopy.onGetCell( self )
		self.createShenshouOnGetCell()
		self.createBuildingOnGetCell()

		self.__callRoutinesOnGetCell()

	def createBuildingOnGetCell( self ):
		"""
		cellʵ�崴�����֪ͨ���������еĽ�����
		"""
		# �������еĽ���
		buildingConfig = self.getScript().tempDatas[ "buildingConfig" ]
		for key, cnf in buildingConfig.iteritems():
			level = self.params[ key + "_level" ]
			type = tongBuildingDatas[ cnf[1] ][ level ][ "type" ]
			if type == csdefine.TONG_BUILDING_TYPE_SSD:
				continue

			self.buildings[ type ] = \
			self.createNPCObject( self.cell, cnf[1], cnf[0][0], cnf[0][1], {"modelNumber" : tongBuildingDatas[ cnf[1] ][ level ][ 'modelNumber' ], \
									 "tempMapping" : { "buildingType" : type } } )

		# �������е�NPC
		npcConfig = self.getScript().tempDatas[ "npcConfig" ]
		for key, cnf in npcConfig.iteritems():	# ����NPC
			level = self.params[ key + "_level" ]
			if level <= 0:
				continue
			param = { "ownTongDBID" : self.params["tongDBID"], "locked" : self._npcLocked, "spawnPos" : cnf[0][0] }
			if key == "ysdt" or key == "jk":
				param[ "locked" ] = False
			self.npcs[ key ] = self.createNPCObject( self.cell, cnf[1], cnf[0][0], cnf[0][1], param )

	def onBuildingLevelChanged( self, tongLevel ):
		"""
		define method.
		�ı�һ��������ļ���
		"""
		INFO_MSG( "TONG: Update tong building , tong level is %i" % ( tongLevel ) )
		self.isUpdateBuildingModel = True
		for buildingType in self.buildings:
			buildingLevel = tongBuildingLevel.getBuildingLevel( tongLevel, buildingType )
			data = tongBuildingDatas[ buildingType ][ buildingLevel ]
			self.buildings[ buildingType ].setModelNumber( data[ 'modelNumber' ] )
			self.onBuildingTypeChanged( buildingType, buildingLevel )

	def onBuildingTypeChanged( self, buildingType, currentLevel ):
		"""
		������н������ı��� �������߽���
		"""
		key = keyMapping[ buildingType ]
		self.params[ key + "_level" ] = currentLevel
		DEBUG_MSG( "TONG:building %s changed, currentLevel:%d" % ( key, currentLevel ) )

		if buildingType == csdefine.TONG_BUILDING_TYPE_SSD: # ���޵�
			self.updateShenShouLevel( currentLevel )

	def createShenshouOnGetCell( self ):
		"""
		cellʵ�崴�����֪ͨ ��������
		"""
		# ��������
		if self.params[ "shenshouType" ] > 0:
			if self.params[ "shenshouReviveTime" ] <= 0:
				self.onCreateShenShou()
			else:
				self.reviveNagual( self.params[ "shenshouReviveTime" ] - time.time() )

	def reviveNagual( self, shenshouReviveTime ):
		"""
		define method.
		���ޱ�ɱ�ˣ� �����������
		"""
		DEBUG_MSG( "reviveNagual->shenshouReviveTime %i" % shenshouReviveTime )
		if self.shenshouMB:
			WARNING_MSG( "reviveNagual: shenshou is live." )
			return

		if shenshouReviveTime <= 0:
			shenshouReviveTime = 1

		if self._shenshouReviveTimeID > 0:
			self.delTimer( self._shenshouReviveTimeID )
		self._shenshouReviveTimeID = self.addTimer( shenshouReviveTime, 0, 0 )

	def updateShenShouLevel( self, tongLevel ):
		"""
		���°�����޼���
		"""
		if self.shenshouMB:
			self.shenshouMB.updateLevel( tongLevel )
			if tongLevel <= 0:
				self.shenshouMB = None	# ����С��0 ��ɾ��

	def onShenShouDestroy( self ):
		"""
		define method.
		����������
		"""
		self.shenshouMB = None

		# ������������Ӷ�ս�ڼ䱻������֪ͨ�Ӷ�ս������������һ��ս�������ˡ�
		if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
			BigWorld.globalData[ "TongManager" ].onRobWarOver( self.params["tongDBID"] )

	def lockTerritoryNPC( self ):
		"""
		define method.
		��ס����������NPC  ���ٺ��κ��˶Ի�
		"""
		self._npcLocked = True
		for key, npc in self.npcs.iteritems():
			if key != "ysdt" and key != "jk":
				npc.cell.lock()

	def unLockTerritoryNPC( self ):
		"""
		define method.
		����ס����������NPC  ����������˶Ի�
		"""
		self._npcLocked = False
		for key, npc in self.npcs.iteritems():
			if key != "ysdt" and key != "jk":
				npc.cell.unlock()

	def onTongSelectNewShenShou( self, shenShouType, isReviveing ):
		"""
		define method.
		���ѡ����һ���µ�����
		@param isReviveing	: �����Ƿ��ڸ�����
		"""
		if self.shenshouMB:
			self.shenshouMB.updateLevel( 0 )	# ��������0�����Զ�����

		# ���޲��ڸ����ڼ�ſ��Դ���
		if not isReviveing:
			if self._createNewShenShouTimerID <= 0:
				self._createNewShenShouTimerID = self.addTimer( 0.5, 1, 0 )

		self.params[ "shenshouType" ] = shenShouType

	def onCreateShenShou( self ):
		"""
		ѡ�񴴽�����ʱ��ص�
		"""
		# ��������
		shenshou_config = self.getScript().tempDatas[ "shenshou_config" ]
		state = { "spawnPos" : shenshou_config[0][0], \
				  "randomWalkRange" : 6.0, \
				  "level" : self.params[ "ssd_level" ], \
				  "ownTongDBID" : self.params["tongDBID"], \
				  "fixPlace" : shenshou_config[0][0], \
				  "fixDirection" : shenshou_config[0][1], \
				  "tempMapping" : { "spaceClassName" : self.getScript().className, "fixModel" : self._isFixNagual, \
				  "shenshouType" : self.params[ "shenshouType" ] } }

		self.shenshouMB = self.createNPCObject( self.cell, shenshou_config[1][ self.params[ "shenshouType" ] ], \
							shenshou_config[0][0], shenshou_config[0][1], state )

		if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):	 # �������û�д�����ɾ�֪ͨ�Ӷ�ս��ʼ������
			BigWorld.globalData[ "TongManager" ].onRegisterTerritory( self.params["tongDBID"], self )

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )
		if id == self._createNewShenShouTimerID:
			self.delTimer( self._createNewShenShouTimerID )
			self._createNewShenShouTimerID = 0
			self.onCreateShenShou()
		elif id == self._shenshouReviveTimeID:
			self.delTimer( self._shenshouReviveTimeID )
			self._shenshouReviveTimeID = 0
			self.onCreateShenShou()

	def onInitTongItems( self, sdLevel, reset ):
		"""
		��ʼ���̵���Ʒ
		"""
		npc = self.getTongTerritoryEntity( "sd" )
		if npc:
			npc.cell.initTongItems( sdLevel, reset )

	def onRegisterTongItem( self, itemID, amount ):
		"""
		define method.
		����ر������� ����������з�����Ʒע�ᵽ��ص�NPC
		"""
		npc = self.getTongTerritoryEntity( "sd" )
		if npc:
			npc.cell.onRegisterTongItem( itemID, amount )

	#---------------------------------------------------���ħ����Ϯ�------------------------------------------------

	def startCampaign_monsterRaid( self, monsterLevel ):
		"""
		define method.
		��ʼ ħ����Ϯ�
		"""
		if not self._isCampaignMonsterRaidOver:
			return

		self._isCampaignMonsterRaidOver = False

		shenshouID = 0
		if self.shenshouMB:
			shenshouID = self.shenshouMB.id

		# ��������
		config = self.getScript().tempDatas[ "campaign_monsterRaid_pos" ]
		state = { "spawnPos" : config[0], \
				  "randomWalkRange" : 6.0, \
				  "level" : monsterLevel, \
				  "tempMapping" : { "shenshouID" : shenshouID } \
				}

		self.campaignMonsterRaidNPCMB = self.createNPCObject( self.cell, campaignMonsterIDMapping[ monsterLevel ], config[0], config[1], state )

		# ˢ��С��
		configs = self.getScript().tempDatas[ "campaign_monsterRaid_poss" ]
		for e in configs:
			state = { "spawnPos" : e[0], \
		  			  "randomWalkRange" : 6.0, \
		  			  "level" : monsterLevel, \
		  			  "tempMapping" : { "shenshouID" : shenshouID } \
					}
			self.campaignMonsterMBList.append( self.createNPCObject( self.cell, random.choice( campaignMonsterList ), e[0], e[1], state ) )
		self.activeNagual( -1 )

	def overCampaign_monsterRaid( self ):
		"""
		define method.
		���� ħ����Ϯ�
		"""
		if self._isCampaignMonsterRaidOver:
			return

		self._isCampaignMonsterRaidOver = True
		if self.campaignMonsterRaidNPCMB and hasattr( self.campaignMonsterRaidNPCMB, "cell" ) and self.campaignMonsterRaidNPCMB.cell:
			self.campaignMonsterRaidNPCMB.cell.remoteScriptCall( "campaignOver", () )

		# С����ʧ
		for e in self.campaignMonsterMBList:
			if e and hasattr( e, "cell" ) and e.cell:
				e.cell.remoteScriptCall( "campaignOver", () )

		# ����һЩ���������� by mushuang
		self.campaignMonsterRaidNPCMB = None
		self.campaignMonsterMBList = []
		self.campaignMonsterNum = 0

		self.disableNagual()

	def onCappaign_monsterRaidComplete( self, level, bossName ):
		"""
		define method.
		�������� ħ����Ϯ�
		"""
		self.campaignMonsterNum += 1
		if self.campaignMonsterNum != len( self.getScript().tempDatas[ "campaign_monsterRaid_poss" ] ) + 1:	# ħ����Ϯ������ɱ��boss������С�֣������
			return

		if self._isCampaignMonsterRaidOver:
			return

		BigWorld.globalData[ "TongManager" ].onCappaign_monsterRaidComplete( self.params["tongDBID"] )
		self._isCampaignMonsterRaidOver = True
		self.campaignMonsterRaidNPCMB = None
		self.campaignMonsterMBList = []
		self.campaignMonsterNum = 0
		self.disableNagual()
		pos = list( self.getScript().tempDatas[ "campaign_monsterRaid_box_pos" ] )
		monsterID = campaignMonsterIDMapping[ level ]
		boxIDs = list( self.getScript().tempDatas[ "campaign_monster_box_drops" ][ monsterID ] )

		if len( pos ) < len( boxIDs ):
			ERROR_MSG( "box the pos config amount < box is drop amount" )
			return

		for x in xrange( len( boxIDs ) ):
			d = pos.pop( random.randint( 0, len( pos ) - 1 ) )
			params = {
				"tempMapping" : { "bossName" : bossName, "tongDBID" : self.params["tongDBID"] },
				"lifetime" : csdefine.PRIZE_DURATION,
			}
			self.cell.createNPCObject( boxIDs.pop( random.randint( 0, len( boxIDs ) - 1 ) ), d[0], d[1], params )


	#---------------------------------------------------------������-----------------------------------------

	def onStartTongFete( self ):
		"""
		define method.
		��ʼ�������ˣ�  ��ؿ���Ϊ�û��һЩ��Ӧ��׼��
		�磺Ͷ�źó����������
		"""
		self.cell.onStartTongFete()
		self.castFeteThing()
		self.getTongTerritoryEntity( "ysdt" ).cell.openFete()

	def onOverTongFete( self ):
		"""
		define method.
		����������
		"""
		self.cell.onOverTongFete()
		self.getTongTerritoryEntity( "ysdt" ).cell.closeFete()
		self.destroyFeteThing()

	def onTongFeteComplete( self ):
		"""
		define method.
		�������ɹ������
		"""
		# ˢ����NPC
		feteRewardNPCData = self.getScript().tempDatas[ "feteDatas" ][ "feteRewardNPC" ]
		self.createNPCObject( self.cell, feteRewardNPCData[0], feteRewardNPCData[1][0], feteRewardNPCData[1][1], { "ownTongDBID":self.params["tongDBID"], "tempMapping" : { "tongDBID" : self.params["tongDBID"] } } )
		self.onOverTongFete()

	def castFeteThing( self ):
		"""
		Ͷ�ż�����س������
		"""
		# ˢ��¯
		feteThingDatas = self.getScript().tempDatas[ "feteDatas" ][ "feteThingDatas" ]
		for thingID, posData in feteThingDatas.iteritems():
			self.feteThings.append( self.createNPCObject( self.cell, thingID, posData[0], posData[1], { "tempMapping" : { "tongDBID" : self.params["tongDBID"] } } ) )

	def destroyFeteThing( self ):
		"""
		�������м����������
		"""
		for e in self.feteThings:
			e.destroyCellEntity()
		self.feteThings = []

	#--------------------------------------�������-----------------------------------------------------------------------
	def onProtectTongStart( self, protectType ):
		"""
		define method.
		��ʼ��������ˣ�  ��ؿ���Ϊ�û��һЩ��Ӧ��׼��
		�磺Ͷ�ź����й����
		"""
		objScript = self.getScript()
		if protectType == csdefine.PROTECT_TONG_NORMAL:
			npcID = objScript.tempDatas[ "protectTong" ][ "npcID" ]
			posdatas = objScript.tempDatas[ "protectTong" ][ "pos" ]
		elif protectType == csdefine.PROTECT_TONG_MID_AUTUMN:
			npcID = objScript.tempDatas[ "protectTong" ][ "protectTongMidAutumnNPCID" ]
			posdatas = objScript.tempDatas[ "protectTong" ][ "midAutumnPos" ]
		else:
			ERROR_MSG( "δ֪������������:( %i ),ʹ��Ĭ������( %i )���á�" % ( protectType, csdefine.PROTECT_TONG_NORMAL ) )
			npcID = objScript.tempDatas[ "protectTong" ][ "npcID" ]
			posdatas = objScript.tempDatas[ "protectTong" ][ "pos" ]

		for posData in posdatas:
			state = { "spawnPos" : posData[0], \
						#"uname" : "�ط�ͳ˧", \
						"randomWalkRange" : 6.0, \
						"tempMapping" : { "spaceClassName" : objScript.className }, \
						"level" : 0 \
					}
			self._protectTongNPCList.append( self.createNPCObject( self.cell, npcID, posData[0], posData[1], state ) )
		BigWorld.globalData["ProtectTong"].receiveMonsterCount( len( self._protectTongNPCList ) )

	def onProtectTongEnd( self ):
		"""
		define method.
		�����������
		"""
		for npc in self._protectTongNPCList:
			try:
				npc.cell.onProtectTongOver()
			except:
				pass

		self._protectTongNPCList = []

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		��ҽ����˿ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		if not self.isUpdateBuildingModel and params[ "tongDBID" ] == self.params["tongDBID"]:
			self.onBuildingLevelChanged( params[ "tongLevel" ] )	# ����һ���Ǳ������û����ʱ�������������ڵĽ���ģ��ûͬ������
		for npc in self.npcs.itervalues() :							# ��������ص���ҷ���npc���ݣ��Ա��ڴ��ͼ���ܿ���
			baseMailbox.client.tong_receiveTerritoryNPCData( self.params["tongDBID"], npc.className )
	
	# ---------------------------------------------��������̳�--------------------------------------------
	def onInitTongSpecialItems( self, tongLevel, reset ):
		"""
		��ʼ���̵���Ʒ
		"""
		npc = self.getTongTerritoryEntity( "yjy" )
		if npc:
			npc.cell.initTongSpecialItems( tongLevel, reset )
	
	def onAddSpecialItemReward( self, itemID, amount ):
		"""
		���������Ʒע��
		"""
		npc = self.getTongTerritoryEntity( "yjy" )
		if npc:
			npc.cell.onRegisterTongSpecialItem( itemID, amount )
	
	def onSellSpecialItems( self, playerID, itemID, amount ):
		"""
		������������Ʒ�ص�
		"""
		npc = self.getTongTerritoryEntity( "yjy" )
		if npc:
			npc.cell.onSellSpecialItems( playerID, itemID, amount )
#
# $Log: not supported by cvs2svn $
#
#
