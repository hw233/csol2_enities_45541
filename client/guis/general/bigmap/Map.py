# -*- coding: gb18030 -*-
#
# $Id: Map.py,v 1.35 2008-08-27 09:04:16 huangyongwei Exp $

"""
implement full map class

2008.01.03 : wirten by huangyongwei
"""

import BigWorld
import Math
import csconst
import csdefine
import event.EventCenter as ECenter
import GUIFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from WorldSubBoard import WorldSubBoard
from NPCQuestSignMgr import npcQSignMgr
from config.client.ResDatas import Datas as ResDatas
from config.client.labels import BigMap as lbs_BigMap
from config.client.SpecialQuestSign import Datas as QuestDatas

class Map( Control ) :
	res_skill_map = { 790001001: "maps/entity_signs/kuang_shi_001.dds",
				790002001: "maps/entity_signs/can_jian_001.dds",
				790003001: "maps/entity_signs/shi_ti_001.dds",
				790004001: "maps/entity_signs/sui_shi_001.dds",
				790005001: "maps/entity_signs/shu_zhi_001.dds",
		}
	def __init__( self, mp ) :
		Control.__init__( self, mp )
		self.focus = True
		self.moveFocus = True
		self.__pyPointer = PyGUI( mp.pointer )
		self.__pyCamera = PyGUI( mp.camera )

		self.__pyNPCSigns = {}								# ���� NPC ��־: { NPC ID : pySign }
		self.__hlPySign = None								# ��ǰ�Ӿ���λ�� NPC

		self.__pyTMateSigns = {}							# ���ѱ�־
		self.__pyTmpSigns = []								# ������ʱ��ɾ���ı�־���Ա��´�����
		self.__pyResSigns = {}								# ��Դ��
		self.__pyWorldBoards = []							# �����ͼ���
		self.__pyQuestSign = {}								# �����־

		self.__autoPathPosList = []							# �����Զ�Ѱ··����
		self.__autoPathLine = GUI.load( "guis/common/pathui.gui" )
		self.__autoPathLine.visible = False
		lineWidth = 8.0
		self.__autoPathLine.lineWidth = lineWidth
		w, h = self.__autoPathLine.size
		self.__autoPathLine.perLen = w / h * lineWidth
		self.__autoPathLine.cornerFill = True
		#self.__autoPathLine.innerColour = 255, 255, 0, 255
		#self.__autoPathLine.edgeColour = 255, 0, 0, 100
		self.__autoPathLine.clearNodes()
		mp.addChild( self.__autoPathLine )
		self.__resIDs = []
		for reslist in ResDatas.values():
			self.__resIDs += reslist

		self.__currArea = None								# ��ɫ��ǰ���ڵ�����
		self.__viewArea = None								# ��ǰ��ʾ������
		self.__viewSize = self.size							# ��ǰ��ʾ����Ĵ�С
		self.__scale = 1									# ��ǰ����������

		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		�����ؼ��¼�
		"""
		Control.generateEvents_( self )
		self.__onWorldAreaSelected = self.createEvent_( "onWorldAreaClick" )				# ��ý���ʱ������

	@property
	def onWorldAreaClick( self ) :
		return self.__onWorldAreaSelected


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TEAM_MEMBER_ADDED"] = self.__onMemberJoinIn					# ���Ѽ���ʱ������
		self.__triggers["EVT_ON_TEAM_MEMBER_LEFT"] = self.__onMemberLeft					# ��Ա���ʱ������
		self.__triggers["EVT_ON_TEAM_MEMBER_REJOIN"] = self.__onTMRejoin					# ��Ա���ߺ�����
		self.__triggers["EVT_ON_QUEST_TASK_STATE_CHANGED"] = self.__updateNPCsQuestState	# ����״̬�ı�ʱ������
		self.__triggers["EVT_ON_TEAM_DISBANDED"] = self.__clearTMateSigns					# �����ɢʱ��ն��ѱ��
		self.__triggers["EVT_ON_START_AUTORUN"] = self.__startAutorun						# ��ʼ�Զ�Ѱ·
		self.__triggers["EVT_ON_STOP_AUTORUN"] = self.__stopAutorun							# �����Զ�Ѱ·
		self.__triggers["EVT_ON_RES_ENTER_WORLD"] = self.__onResEnterWorld 					# ��Դ���������
		self.__triggers["EVT_ON_RES_LEAVE_WORLD"] = self.__onResLeaveWorld					# ��Դ���뿪����
		self.__triggers["EVT_ON_RES_VISIBLE_STATUS"] = self.__onResModelStatus				# ��Դ��ģ���Ƿ�����
		self.__triggers["EVT_ON_ADD_TONG_TERRITORY_NPC"] = self.__onTongTerritoryAddNPC		# ����������һ���µ�NPC���
		self.__triggers["EVT_ON_ADD_QUEST_SIGN"] = self.__onAddQuestSign					# ���ָ�������־
		self.__triggers["EVT_ON_REMOVE_QUEST_SIGN"] = self.__onRemoveQuestSign				# ɾ��ָ�������־
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# ----------------------------------------------------------------
	def __getSign( self, entity ) :
		"""
		���һ����־
		"""
		if len( self.__pyTmpSigns ) :
			pySign = self.__pyTmpSigns.pop()
			pySign.resetMapEntity( entity )
			pySign.visible = True
			return pySign
		return Sign( self, entity )

	def __addNPCSigns( self ) :
		"""
		��ӵ�ǰ��ʾ�������µ����� NPC ��־
		"""
		self.__clearNPCSigns()						# ����ϴε����� NPC ��־
		npcs = self.__getSpaceNPCSigns()			# ��ȡ��ǰ��ʾ�����µ����� NPC
		for npcID, npc in npcs.iteritems() :
			if not int( npcID ) in self.__resIDs:
				pySign = self.__getSign( npc )
				self.__pyNPCSigns[npcID] = pySign
				self.addPyChild( pySign )
				self.__resetNPCSign( pySign )

	def __addNPCSign( self, npcID ) :
		"""
		���ָ����NPC����ͼ��
		"""
		if self.__pyNPCSigns.has_key( npcID ) :
			return
		npc = rds.npcDatasMgr.getNPC( npcID )
		if npc is not None :
			pySign = self.__getSign( npc )
			self.__pyNPCSigns[npcID] = pySign
			self.addPyChild( pySign )
			self.__resetNPCSign( pySign )
		else :
			ERROR_MSG( "---->>> NPCDatasMgr can't find npc %s" % npcID )

	def __clearNPCSigns( self ) :
		"""
		������� NPC ��־
		"""
		self.__hlPySign = None
		for pySign in self.__pyNPCSigns.itervalues() :
			pySign.visible = False
		self.__pyTmpSigns += self.__pyNPCSigns.values()
		self.__pyNPCSigns = {}

	def __clearTMateSigns( self ) :
		"""
		������ж��ѱ�־
		"""
		for pySign in self.__pyTMateSigns.itervalues() :
			pySign.visible = False
		self.__pyTmpSigns += self.__pyTMateSigns.itervalues()
		self.__pyTMateSigns = {}

	def __getSpaceNPCSigns( self ) :
		"""
		��ȡ���ڵ�ͼ��NPC����
		"""
		spaceLabel = self.__viewArea.spaceLabel
		player = BigWorld.player()
		curSpaceLabel = player.getSpaceLabel()
		posY = 0
		if curSpaceLabel == spaceLabel:
			posY = player.position[1]
		viewWholeArea = self.__viewArea.wholeArea
		isViewSky = viewWholeArea.isSkyArea															#�鿴��ͼ�Ƿ�Ϊ���е�ͼ
		npcs = rds.mapMgr.getNPCs( spaceLabel, curSpaceLabel, isViewSky, 1, posY )					# ��ȡ��ǰ��ʾ�����µľ�̬ NPC
		if player.getSpaceLabel() == spaceLabel :
			try :											# ��ȡ���ڵ�ͼ�Ķ�̬NPC����
				tongDBID = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, \
					csconst.SPACE_SPACEDATA_TONG_TERRITORY_TONGDBID ) )
				npcIDs = player.tong_getTerritoryNPCs( tongDBID )
				for npcID in npcIDs :
					if npcID in npcs :
						continue
					npc = rds.npcDatasMgr.getNPC( npcID )
					if npc is not None :
						npcs[npcID] = npc
					else :
						ERROR_MSG( "---->>> NPCDatasMgr can't find npc %s" % npcID )
			except ValueError :
				pass
		return npcs
				

	# -------------------------------------------------
	def __relocateSign( self, pySign ) :
		"""
		���ݱ�־��Ӧ�� entity ��λ�ú����ű��������ñ�־��λ��
		"""
		pos = Math.Vector3( 0,0,0 )
		if pySign.style == Sign.ST_TEAMMATE or pySign.style == Sign.ST_QUEST_SIGN:					# ����Ƕ��ѻ�����Ϊ��־
			pos = pySign.mapEntity.getPosition()
		else :
			pos = pySign.mapEntity.getPosition( self.viewArea.spaceLabel )
		if pos is None:return
		player = BigWorld.player()
		point = self.__viewArea.worldPoint2TexturePoint( pos )
		pySign.center = point[0] * self.__scale
		pySign.middle = point[1] * self.__scale
		mapLabel = player.getSpaceLabel()


	# ---------------------------------------
	def __resetNPCSign( self, pySign ) :
		"""
		���� NPC ������״̬������ NPC ��־����ʾ��ʽ
		"""
		signID = 0
		SignDict = {
			"normalFinish"	   : Sign.ST_Q_FINISH_Y,\
			"normalStart"	   : Sign.ST_Q_TAKE_Y,\
			"normalIncomplete" : Sign.ST_Q_INCOMPLETE,\
			"fixloopStart"	   : Sign.ST_Q_FIXLOOP,\
			"directFinish"	   : Sign.ST_Q_FINISH_Y,\
			"qstTalk"		   : Sign.ST_Q_TALK_BUB,\
			}
		for entity in BigWorld.entities.values() :
			if not hasattr( entity, "getName" ) : continue
			if entity.getName() != pySign.ename : continue
			signID = getattr( entity, "questStates", None )
			if signID is None : continue
		if npcQSignMgr.getSignBySignID( signID ) == "":
			pySign.setStyle( Sign.ST_NPC )
			self.__relocateSign( pySign )
		else:
			signStr = npcQSignMgr.getSignBySignID(  signID )
			pySign.setStyle( SignDict[signStr] )
			self.__relocateSign( pySign )

	def __resetResSign( self, pySign ):
		"""
		������Դ������������ʽ
		"""
		resEntity = pySign.mapEntity
		className = getattr( resEntity, "className", None)
		if className is None:return
		reqSkID = resEntity.reqSkillID
		pySign.texture = self.res_skill_map.get( reqSkID, "" )
		self.__relocateResSign( pySign )

	def __relocateResSign( self, pySign ):
		player = BigWorld.player()
		mapEntity = pySign.mapEntity
		pos = mapEntity.position
		model = mapEntity.model
		modelVisible = False
		if model:
			modelVisible = model.visible
		if self.__viewArea:
			point = self.__viewArea.worldPoint2TexturePoint( pos )
			pySign.center = point[0] * self.__scale
			pySign.middle = point[1] * self.__scale
		mapLabel = player.getSpaceLabel()
		ppos = player.position
		curArea = player.getCurrWholeArea()
		floorHeight = 0.0
		if curArea:
			floorHeight = curArea.floorHeight
			pySign.visible = pos[1] > floorHeight and modelVisible		#�����ͼ

	def __resetNPCSigns( self ) :
		"""
		�������� NPC ��־����ʽ
		"""
		for pySign in self.__pyNPCSigns.itervalues() :
			self.__resetNPCSign( pySign )

	def __resetResSigns( self ):
		"""
		����������Դ���־
		"""
		for pySign in self.__pyResSigns.itervalues() :
			self.__resetResSign( pySign )

	def __reloadTMateSigns( self ) :
		"""
		���¼��ض��ѱ�־��λ��
		"""
		player = BigWorld.player()
		for pySign in self.__pyTMateSigns.itervalues() :
			pySign.visible = False
			if self.__viewArea is None : continue
			#if not pySign.online : continue
			teamMate = pySign.mapEntity
			if not teamMate.online : continue
			# �������ͬһ��space���򷵻ء�����ͬ��ͼ��ͬ���ߣ����߲�ͬ�İ����أ�
			if player.spaceID != teamMate.spaceID: continue
			teammateArea = rds.mapMgr.getArea( teamMate.spaceLabel, teamMate.position )
			if teammateArea is None : continue
			if teammateArea == self.__viewArea :
				self.__relocateSign( pySign )
			elif teammateArea.wholeArea == self.__viewArea.wholeArea :						# ����������ڳ����뵱ǰ������ͬ
				if self.__viewArea.isWholeArea() or not self.__viewArea.hasTexture() :		# �����ͬһ���� �� ��ǰ��ʾ����Ȼ�����򣬵����õ���ȫ��ͼ
					self.__relocateSign( pySign )
					
	def __reloadQuestSign( self ):
		"""
		���¼��������־��λ��
		"""
		for pySign in self.__pyQuestSign.itervalues() :
			pySign.visible = False
			if self.__viewArea is None : continue
			spaceLabel = self.__viewArea.spaceLabel
			if spaceLabel == pySign.mapEntity.spaceLabel:
				self.__relocateSign( pySign )
				pySign.visible = True

	# -------------------------------------------------
	def __reloadAutoPath( self ) :
		"""
		��ʾ�Զ�Ѱ·��
		"""
		self.__autoPathLine.clearNodes()
		viewArea = self.__viewArea
		currArea = self.__currArea
		if viewArea is None : return
		if currArea == viewArea or currArea.wholeArea == viewArea :
			for wPos in self.__autoPathPosList :
				lPos = self.__viewArea.worldPoint2TexturePoint( wPos ) * self.__scale
				self.__autoPathLine.pushNode( ( lPos[0], -lPos[1] ) )

	def __onResEnterWorld( self, resEntity ):
		"""
		��Դ���������
		"""
		if resEntity.utype == csdefine.ENTITY_TYPE_COLLECT_POINT:
			modelVisible = False
			model = resEntity.model
			pySign = Sign( self, resEntity )
			pySign.setStyle( Sign.ST_RES_POINT )
			self.__pyResSigns[resEntity.id] = pySign
			self.addPyChild( pySign )
			self.__resetResSigns()

	def __onResLeaveWorld( self, resEntity ):
		"""
		��Դ���뿪����
		"""
		pyResSign = self.__pyResSigns.get( resEntity.id, None )
		if pyResSign:
			pyResSign.dispose()

	def __onResModelStatus( self, resID, isVisible ):
		"""
		��Դ��ģ������
		"""
		pySign = self.__pyResSigns.get( resID, None )
		if pySign:
			pySign.visible = isVisible

	def __onTongTerritoryAddNPC( self, tongDBID, npcID ) :
		"""
		��ǰ��ͼ����һ��NPC���
		"""
		if self.__viewArea is None:return
		if BigWorld.player().getSpaceLabel() == self.__viewArea.spaceLabel :
			self.__addNPCSign( npcID )

	# -------------------------------------------------
	def __resetMap( self, area ) :
		"""
		����ָ����������������ͼ
		"""
		oldArea = self.__viewArea
		self.__viewArea = area
		if self.texture != area.texture :
			self.texture = area.texture
			size = area.mapBound.size
			self.__viewSize = size
			self.size = size
			self.mapping = area.mapMapping
			self.__scale = 1
			self.__addNPCSigns()				#�л���պ͵����ͼʱ����������npc��ʶ
		if oldArea is None or area.spaceName != oldArea.spaceName :
			self.__addNPCSigns()
			self.__reloadTMateSigns()
			self.__reloadQuestSign()
			for pyResSign in self.__pyResSigns.itervalues():
				pyResSign.dispose()
		self.__reloadAutoPath()
		

	# -------------------------------------------------
	def __setWorldAreasBoards( self ) :
		"""
		���������ͼ���Ӱ��
		"""
		boards = rds.mapMgr.worldArea.subBoards
		for board in boards :
			pyBoard = WorldSubBoard( board )
			self.addPyChild( pyBoard )
			pyBoard.pos = board.pos
			pyBoard.onLClick.bind( self.__onWorldAreaClick )
			self.__pyWorldBoards.append( pyBoard )

	def __clearWorldBoards( self ) :
		"""
		������������ͼ���
		"""
		for pyBoard in self.__pyWorldBoards :
			self.delPyChild( pyBoard )
			pyBoard.dispose()
		self.__pyWorldBoards = []

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRMouseDown_( self, mods ) :
		Control.onRMouseDown_( self, mods )
		return False

	def onLClick_( self, mods ) :
		"""
		��������ͼ�ý�ɫʹ�õ���ϵͳ�ܵ����λ��
		"""
		if self.__currArea.wholeArea == self.__viewArea.wholeArea :
			x, z = self.getMouseInWorldPoint()
			worldPos = Math.Vector3( x, 0.0, z )
			player = BigWorld.player()
			player.autoRun( worldPos )

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onEnterArea( self, area ) :
		"""
		����ɫ����ĳ������ʱ������
		"""
		self.__currArea = area

	def onWindowShowed( self ) :
		"""
		�����ͼ��ʾʱ������
		"""
		for ent in BigWorld.entities.values() :
			npcID = getattr( ent, "className", None )
			pyNpcSign = self.__pyNPCSigns.get( npcID, None )
			if pyNpcSign :
				self.__resetNPCSign( pyNpcSign )
		self.__resetResSigns()
		self.__triggers["EVT_ON_ENTITY_ENTER_WORLD"] = self.__onEntityEnterWorld
		self.__triggers["EVT_ON_ENTITY_LEAVE_WORLD"] = self.__onEntityLeaveWorld
		ECenter.registerEvent( "EVT_ON_ENTITY_ENTER_WORLD", self )
		ECenter.registerEvent( "EVT_ON_ENTITY_LEAVE_WORLD", self )

	def onWindowHidded( self ) :
		"""
		�����ͼ����ʱ������
		"""
		ECenter.unregisterEvent( "EVT_ON_ENTITY_ENTER_WORLD", self )
		ECenter.unregisterEvent( "EVT_ON_ENTITY_LEAVE_WORLD", self )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def __onEntityEnterWorld( self, entity ) :
		"""
		entity ��������ʱ������
		"""
		npcID = getattr( entity, "className", None )
		pyNpcSign = self.__pyNPCSigns.get( npcID, None )
		if pyNpcSign : self.__resetNPCSign( pyNpcSign )

	def __onEntityLeaveWorld( self, entity ) :
		"""
		entity �뿪����ʱ������
		"""
		npcID = getattr( entity, "className", None )
		pySign = self.__pyNPCSigns.get( npcID, None )
		if pySign : self.__resetNPCSign( pySign )
	
	def __onAddQuestSign( self, questID ):
		"""
		��������־
		"""
		if self.__pyQuestSign.has_key( questID ):
			return
		if QuestDatas.has_key( questID ):		
			spaceLabel = QuestDatas[questID][0]
			pos = QuestDatas[questID][1]
			questObj = QuestObj( questID, spaceLabel, pos )			
			pySign = Sign( self, questObj )
			pySign.setStyle( Sign.ST_QUEST_SIGN )
			self.addPyChild( pySign )
			self.__pyQuestSign[questID] = pySign
			self.__reloadQuestSign()
	
	def __onRemoveQuestSign( self, questID ):
		"""
		ɾ�������־
		"""
		if questID in self.__pyQuestSign:
			pySign = self.__pyQuestSign.pop( questID )
			self.delPyChild( pySign )
			self.__reloadQuestSign()

	def __onMemberJoinIn( self, mate ) :
		"""
		������һ������ʱ������
		"""
		objID = mate.objectID
		if self.__pyTMateSigns.has_key( objID ) :
			return
		pySign = self.__getSign( mate )
		pySign.setStyle( Sign.ST_TEAMMATE )
		self.addPyChild( pySign )
		self.__pyTMateSigns[objID] = pySign
		self.__reloadTMateSigns()

	def __onMemberLeft( self, objID ) :
		"""
		��һ�������뿪ʱ������
		"""
		if objID in self.__pyTMateSigns :
			pySign = self.__pyTMateSigns.pop( objID )
			self.delPyChild( pySign )
			self.__pyTmpSigns.append( pySign )
		self.__reloadTMateSigns()

	def __onTMRejoin( self, oldEntityID, newEntityID ) :
		"""
		��Ա���¼���
		"""
		teammate = self.__pyTMateSigns.get( oldEntityID, None )
		if teammate is not None :
			del self.__pyTMateSigns[ oldEntityID ]
			self.__pyTMateSigns[ newEntityID ] = teammate
		else :
			teammate = BigWorld.player().teamMember[ newEntityID ]
			self.__onMemberJoinIn( teammate )
			INFO_MSG( "Teammate %d is not in teammate array!" % oldEntityID )

	def __updateNPCsQuestState( self, questID, taskIndex ) :
		"""
		��ĳ������״̬�ı�ʱ������
		"""
		for pySign in self.__pyNPCSigns.itervalues() :
			self.__resetNPCSign( pySign )

	# -------------------------------------------------
	def __startAutorun( self, dstPos ) :
		"""
		��ʼѰ·�Ǳ�����
		"""
		self.__autoPathPosList = list( BigWorld.player().getAutoRunPathLst( ) )# ��ȡ·����
		self.__autoPathLine.visible = True
		self.__reloadAutoPath()

	def __stopAutorun( self, success ) :
		"""
		����Ѱ·ʱ������
		"""
		self.__autoPathLine.visible = False
		self.__autoPathLine.clearNodes()
		self.__autoPathPosList = []

	# -------------------------------------------------
	def __onWorldAreaClick( self, pyBoard ) :
		"""
		��������ͼ����ʱ������
		"""
		self.onWorldAreaClick( pyBoard.area )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setArea( self, area ) :
		"""
		��������
		"""
		oldArea = self.__viewArea
		if oldArea == area : return
		self.__resetMap( area )
		if area == self.__currArea or area == self.__currArea.wholeArea :
			self.__pyPointer.visible = True
			self.__pyCamera.visible = True
		else :
			self.__pyPointer.visible = False
			self.__pyCamera.visible = False
		self.__clearWorldBoards()							# ��������ͼ�������Ӱ��
		if area.spaceLabel == "world" :						# ���������ʾΪ�����ͼ
			self.__setWorldAreasBoards()					# ���������ͼ���Ӱ��

	# -------------------------------------------------
	def showNPCs( self ) :
		"""
		��ʾ���� NPC
		"""
		for pySign in self.__pyNPCSigns.itervalues() :
			pySign.visible = True

	def hideNPCs( self ) :
		"""
		�������� NPC
		"""
		for pySign in self.__pyNPCSigns.itervalues() :
			pySign.visible = False

	# -------------------------------------------------
	def update( self, player ) :
		"""
		���µ�ͼ�ϵĸ�������
		"""
		if self.__viewArea is None : return
		ppos = player.position
		x, y = self.__viewArea.worldPoint2TexturePoint( ppos )
		self.__pyPointer.center = x*self.__scale
		self.__pyPointer.middle = y*self.__scale
		self.__pyCamera.center = x * self.__scale
		self.__pyCamera.middle = y * self.__scale
		util.rotateGui( self.__pyPointer.getGui(), player.yaw )
		util.rotateGui( self.__pyCamera.getGui(), BigWorld.camera().direction.yaw )
		self.__reloadTMateSigns()
		self.__reloadQuestSign()
		if self.__viewArea == player.getCurrWholeArea() or \
			self.__viewArea == player.getCurrArea() :
				self.__pyPointer.visible = True
		else :
			self.__pyPointer.visible = False

	def onLeaveWorld( self ) :
		"""
		��յ�ͼ��������
		"""
		#self.__clearNPCSigns()
		self.__clearTMateSigns()

	# -------------------------------------------------
	def getMouseInWorldPoint( self ) :
		"""
		��ȡ���λ������ʵ��ͼ�ϵ���������λ��
		"""
		if self.__viewArea is None : return ( 0, 0 )
		point = Math.Vector2( self.mousePos ) / self.__scale
		return self.__viewArea.texturePoint2WorldPoint( point )

	def highlightNPC( self, npc ) :
		"""
		ͻ����ʾĳ�� NPC
		"""
		if self.__hlPySign is not None :
			self.__hlPySign.stopAnimation()
		for pySign in self.__pyNPCSigns.itervalues() :
			if pySign.ename == npc.getName() :
				pySign.playAnimation()
				self.__hlPySign = pySign
				break


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getViewArea( self ) :
		return self.__viewArea

	def _getViewSize( self ) :
		return self.__viewSize

	def _getScale( self ) :
		return self.__scale

	def _setScale( self, scale ) :
		if self.__viewArea is None :
			self.__scale = 1
			return
		self.__scale = scale
		self.width = self.__viewSize[0] * scale
		self.height = self.__viewSize[1] * scale
		self.__resetNPCSigns()
		self.__reloadAutoPath()
		self.__resetResSigns()
		for pyBoard in self.__pyWorldBoards :
			pyBoard.scale = scale

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	viewArea = property( _getViewArea )								# ��ǰ��ʾ������
	viewSize = property( _getViewSize )								# ��ǰ��ʾ����Ĵ�С
	scale = property( _getScale, _setScale )						# ��ǰ���ű���



# --------------------------------------------------------------------
# implement sign class
# --------------------------------------------------------------------
class Sign( Control ) :
	ST_NPC				= 0				# ��ͨ NPC
	ST_Q_TAKE_Y			= 1				# ������ɽӵ� NPC
	ST_Q_INCOMPLETE		= 2				# ������û�ύ NPC
	ST_Q_FINISH_Y		= 3				# ����������ύ�� NPC
	ST_Q_TAKE_B			= 4				# QUEST_STYLE_DIRECT_FINISH , QUEST_STYLE_FIXED_LOOP �������� ������ɽӵ� NPC
	ST_Q_FINISH_B		= 5				# QUEST_STYLE_DIRECT_FINISH , QUEST_STYLE_FIXED_LOOP �������� ����������ύ�� NPC
	ST_TEAMMATE			= 6				# ����
	ST_Q_FIXLOOP		= 7				# �̻�����
	ST_RES_POINT		= 8				# ��Դ��
	ST_Q_TALK_BUB		= 9				#����Ի�ð��
	ST_QUEST_SIGN		= 10			#������˸��־������ĳЩ�칬����ָ������Ŀ�꣩

	__cg_pySigns = []

	def __init__( self, pyMap, mapEntity ) :
		Sign.__cg_pySigns.append( self )
		self.__sign = GUI.Simple( "" )
		self.__sign.tiled = True
		Control.__init__( self, self.__sign )
		self.setToDefault()
		self.crossFocus = True
		self.__pyMap = pyMap
		self.__mapEntity = mapEntity
		self.__style = self.ST_NPC


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getHitedSigns( self ) :
		"""
		��ȡ�����е����е�
		"""
		pySigns = []
		for pySign in Sign.__cg_pySigns :
			if not pySign.visible : continue
			if pySign.isMouseHit() :
				pySigns.append( pySign )
		return sorted( pySigns, key = lambda pySign : pySign.posZ )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		pySigns = self.__getHitedSigns()
		tips = "@A{C}"
		for pySign in pySigns :
			name = pySign.__mapEntity.getName()
			title = pySign.__mapEntity.title
			tip = name
			if title :
				tip += ( lbs_BigMap.Map_tipTitle % title )
			tips += ( tip + "@B" )
		px, py, pz = self.__mapEntity.position
		tips += "%d, %d" % ( px, pz )
		toolbox.infoTip.showESignTips( self, tips )

	def onMouseLeave( self ) :
		toolbox.infoTip.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetMapEntity( self, mapEntity ) :
		"""
		���ö�Ӧ�� entity
		"""
		self.__mapEntity = mapEntity

	def setStyle( self, style, isFixLoop = False ) :
		"""
		�������
		"""
		self.posZ = 1.0
		if style == self.ST_NPC :
			self.texture = "maps/entity_signs/static_npc.texanim"
			self.__sign.tileWidth = 16
			self.__sign.tileHeight = 16
			self.size = ( 16, 16 )
		elif style == self.ST_Q_TAKE_Y :
			self.texture = "maps/entity_signs/s_marks_general.texanim"
			self.__sign.tileWidth = 32
			self.__sign.tileHeight = 32
			self.__sign.tiled = True
			self.size = ( 32, 32 )
		elif style == self.ST_Q_INCOMPLETE :
			self.texture = "maps/entity_signs/f_marks_incomplete.texanim"
			self.__sign.tileWidth = 32
			self.__sign.tileHeight = 32
			self.__sign.tiled = True
			self.size = ( 32, 32 )
		elif style == self.ST_Q_FINISH_Y :
			self.texture = "maps/entity_signs/f_marks_general.texanim"
			self.__sign.tileWidth = 32
			self.__sign.tileHeight = 32
			self.__sign.tiled = True
			self.size = ( 32, 32 )
		elif style == self.ST_Q_FIXLOOP:
			self.texture = "maps/entity_signs/s_marks_special.texanim"
			self.__sign.tileWidth = 32
			self.__sign.tileHeight = 32
			self.__sign.tiled = True
			self.size = ( 32, 32 )
		elif style == self.ST_TEAMMATE :
			self.texture = "maps/entity_signs/teammate.texanim"
			self.__sign.tileWidth = 16
			self.__sign.tileHeight = 16
			self.__sign.tiled = True
			self.size = ( 16, 16 )
			self.posZ = 0.8
		elif style == self.ST_RES_POINT:
			self.__sign.tileWidth = 16
			self.__sign.tileHeight = 16
			self.__sign.tiled = False
			self.size = ( 16, 16 )
			self.posZ = 0.8
		elif style == self.ST_Q_TALK_BUB:
			self.texture = "maps/entity_signs/f_marks_talk.texanim"
			self.__sign.tileWidth = 32
			self.__sign.tileHeight = 32
			self.__sign.tiled = True
			self.size = ( 32, 32 )
			self.posZ = 0.8
		elif style == self.ST_QUEST_SIGN :
			self.texture = "guis/general/minimap/flash_fd_tower.texanim"
			self.__sign.tileWidth = 32
			self.__sign.tileHeight = 32
			self.__sign.tiled = True
			self.size = ( 32, 32 )
		parent = self.getGui().parent
		if parent : parent.reSort()
		self.__style = style

	# -------------------------------------------------
	def playAnimation( self ) :
		"""
		������ͼ����
		"""
		if self.__style == self.ST_NPC :
			self.texture = "maps/entity_signs/ani_npc.texanim"

	def stopAnimation( self ) :
		"""
		ֹͣ��ͼ�����Ĳ���
		"""
		if self.__style == self.ST_NPC :
			self.texture = "maps/entity_signs/static_npc.texanim"

	def setArea( self, area ):
		"""
		��������������
		"""
		self.__area = area

	def getArea( self ):
		"""
		��ȡ��������
		"""
		return self.__area


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def style( self ) :
		return self.__style

	@property
	def mapEntity( self ) :
		return self.__mapEntity

	@property
	def ename( self ) :
		return self.__mapEntity.getName()

	@property
	def online( self ) :
		return BigWorld.entities.get( self.__mapEntity.objectID, None ) is not None
		
class QuestObj:
	def __init__( self, questID, spaceLabel, pos ) :
		self.position = pos
		self.objectID = questID
		self.title = ""
		self.spaceLabel = spaceLabel
		
	def getPosition( self ):
		return self.position
		
	def getName( self ):
		nameStr = ""
		questTypeStr = GUIFacade.getQuestTypeStr( self.objectID )[1]
		questName, questLevel = GUIFacade.getQuestLogTitle( self.objectID )
		nameStr += "%s:%s(%s)" % ( questTypeStr, questName, questLevel )
		return nameStr
