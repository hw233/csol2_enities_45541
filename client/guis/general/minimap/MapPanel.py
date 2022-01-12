# -*- coding: gb18030 -*-
#
# $Id: MapPanel.py,v 1.31 2008-09-03 03:25:31 huangyongwei Exp $

"""
implement piece of map's panel class

2007.12.21 : writen by huangyongwei( named MapsPanel )
2008.01.15 : rewriten by huangyongwei( use PyTextureProvider )
"""

import time
import math
import struct
import Math
import ResMgr
import csarithmetic
import csdefine
import csconst
import Language
from bwdebug import *
from event import EventCenter as ECenter
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from NPCQuestSignMgr import npcQSignMgr
from config.client.labels import minmap as lbs_MinMap
from cscustom import Polygon
from SameMiniMapLoader import SameMiniMapLoader
smapLoader = SameMiniMapLoader.instance()
from Function import Functor
from config.client.SpaceHeightConfig import Datas as spaceHeightDatas

# --------------------------------------------------------------------
# global methods
# --------------------------------------------------------------------
def chunkID2Int16s( chunkID ):
	"""
	ת��*.chunk���ļ�����ǰ8���ַ�Ϊint16�б�
	�磺chunkID2int16( "fff1ffba" ) -> (-15, -70)

	@param: chunkID: *.chunk���Ƶ�ǰ8���ַ������磺"fff1ffba"
	@return: ����2��int16��tuple���磺(-15, -70)
	"""
	# phw�����´�����winxpƽ̨�²���������������췢�����ݲ������ˣ�
	# �ܿ�����int()��ĵ�����ֵ���ҵ�ǰ�õġ�>����ʽ��ƥ�䣬�ĳɡ�<�����ܾ������ˣ�
	# ��ǰ������intel��ϵ��win/linuxϵ�ж���һ�µģ�Ӧ�ò��������⣻
	return struct.unpack( ">hh", struct.pack( ">I", int( chunkID, 16 ) ) )

def int16s2ChunkID( int16s ):
	"""
	chunkID2Int16s()����������
	ת��һ��int16���б�ֵ��ֻ��������int16��ֵ��ΪchunkID��
	�磺int16s2ChunkID( (-15, -70) ) -> "fff1ffba"

	@param: ����2��int16ֵ��tuple��list
	@return: ת�����16�����ַ�����Сд��
	"""
	return "%08x" % ( struct.unpack( ">I", struct.pack( ">hh", *int16s ) )[0] )


# --------------------------------------------------------------------
# implement map panel
# --------------------------------------------------------------------
class MapPanel( Control ) :
	cc_show_entities = [
		csdefine.ENTITY_TYPE_ROLE,
		csdefine.ENTITY_TYPE_NPC,
		csdefine.ENTITY_TYPE_MONSTER,
		csdefine.ENTITY_TYPE_SLAVE_MONSTER,
		csdefine.ENTITY_TYPE_CONVOY_MONSTER,
		csdefine.ENTITY_TYPE_VEHICLE_DART
		]

	res_skill_map = { 790001001: "maps/entity_signs/kuang_shi_001.dds",
					790002001: "maps/entity_signs/can_jian_001.dds",
					790003001: "maps/entity_signs/shi_ti_001.dds",
					790004001: "maps/entity_signs/sui_shi_001.dds",
					790005001: "maps/entity_signs/shu_zhi_001.dds",
		}

	cc_map_folder		= "space/%s/minimaps/"							# ��ͼ·��
	cc_provider_width	= 512											# Ҫ��ȡ����ʾ������Ĵ�С
	cc_map_width		= 128.0											# ÿСƬ��ͼ��С��Ҳ��ÿ chunk ����ͼ��ʾ�Ĵ�С�������Σ�
	cc_chunk_width		= 100.0											# chunk ��С�������Σ�
	cc_skyConfigs = "config/client/bigmap/minimapsky.xml"				# ��յ�ͼ����

	cc_baseScale = cc_chunk_width / cc_map_width						# chunk��С ����ͼ��С�ı�����
	cc_edges = int( cc_provider_width / cc_map_width )					# ��ʾ�����ڣ���ֱ��ˮƽ�����ϣ��ж���Ƭ��ͼ
	cc_ltCount = cc_edges / 2 - 1										# �����СƬ��ͼ�������һ������ϵ������ϵԭ����ߵ���ͼ����
	cc_chunkRng = ( -cc_ltCount, cc_ltCount + 2 )						# ��ȡ chunk ��������Χ
	cc_cacheRng = ( cc_chunkRng[0] - 1, cc_chunkRng[1] + 1 )			# ��ȡ���� chunk ��������Χ(������ͼҪ����ȡһ��һ��)
	cc_textureSize = cc_edges * cc_map_width, cc_edges * cc_map_width	# ��ʾȫ����ͼ�� GUI �Ĵ�С

	__cc_trap_handle_delay = 1.0										# �ӳٴ��� Trap ��ʱ��

	def __init__( self, panel ) :
		Control.__init__( self, panel )
		self.__cPoint = Math.Vector2( self.size )		# ���ĵ�λ��
		self.__cPoint *= 0.5
		self.__radius = self.__cPoint.x					# ���ӷ�Χ�뾶
		self.__pointer = panel.pointer					# ��ɫ���
		self.__camera = panel.camera					# ������
		self.__basePos = ( 0, 0, 0 )					# ��ͼԲ��λ��
		self.__scale = 1								# ��ͼ������
		self.__scaleCBID = 0							# �����ŵ� callback ID
		self.__delaycbid = 0

		self.__mapFolder = ""							# ��ͼ·��
		self.__mp = panel.mp							# ��ͼ UI
		self.__isSkyMin = False
		self.__mtp = BigWorld.PyMergerTextureProvider( \
			self.cc_provider_width, self.cc_provider_width )
		self.__currChunk = ( 0, 0 )						# ��ǰ���ڵ� chunk

		self.__pyNPCSigns = {}							# NPC signs
		self.__pyTMSigns = {}							# ���� sings������������ѣ�
		self.__pyRoleSigns = {}							# �Ƕ������
		self.__pyMSTSigns = {}							# Monster signs
		self.__pySMSTSigns = {}							# ����NPC
		self.__pyResSigns = {}							# ��Դ��NPC
		self.__pySigns = (	\
			self.__pyNPCSigns, \
			self.__pyMSTSigns, \
			self.__pyRoleSigns, \
			self.__pySMSTSigns, \
			self.__pyResSigns,	\
			)

		self.__visibleFlags = {}						# ��������entity����ʾ���{ "npc": True, "monster": False, ... }
		self.__viewInfoKey = "entitySigns"				# �ü��������ã�config/client/viewinfosetting.xml �е�����������Ƿ�Ҫ��ʾ�����ͱ��

		#self.__autoPathPosList = []						# �����Զ�Ѱ··����
		self.__autoPathLine = GUI.load( "guis/common/pathui.gui" )
		self.__autoPathLine.visible = False
		lineWidth = 6.0
		self.__autoPathLine.lineWidth = lineWidth
		w, h = self.__autoPathLine.size
		self.__autoPathLine.perLen = w / h * lineWidth
		#self.__autoPathLine.innerColour = 255, 255, 0, 255
		#self.__autoPathLine.edgeColour = 255, 0, 0, 100
		self.__autoPathLine.clearNodes()
		panel.addChild( self.__autoPathLine )

		self.__triggers = {}
		self.__registerTriggers()
		self.__initVisibleFlags()


	def reset( self ) :
		self.__basePos = ( 0, 0, 0 )
		self.__scale = 1
		self.__currChunk = ( 0, 0 )

		self.clearAllSigns()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		self.__triggers["EVT_ON_ENTITY_ENTER_WORLD"] = self.__onEntityTrapIn
		self.__triggers["EVT_ON_ENTITY_LEAVE_WORLD"] = self.__onEntityTrapOut
		self.__triggers["EVT_ON_TEAM_DISBANDED"] = self.clearTeammates
		self.__triggers["EVT_ON_TEAM_MEMBER_ADDED"] = self.__onMemberJoinIn
		self.__triggers["EVT_ON_TEAM_MEMBER_LEFT"] = self.__onMemberLeft
		self.__triggers["EVT_ON_TEAM_MEMBER_REJOIN"] = self.__onTMRejoin					# ��Ա���ߺ�����
		self.__triggers["EVT_ON_FAMILY_CHALLENGING"] = self.__familyChallengeStart			# ������ս��
		self.__triggers["EVT_ON_FAMILY_CHALLENGE_OVER"] = self.__familyChallengeOver		# ������ս����
		self.__triggers["EVT_ON_TONG_ROB_WAR_BEING"] = self.__tongRobWarBeing
		self.__triggers["EVT_ON_TONG_ROB_WAR_OVER"] = self.__tongRobWarOver
		self.__triggers["EVT_ON_NPC_QUEST_STATE_CHANGED"] = self.updateNPCsQuestState
		self.__triggers["EVT_ON_BOX_QUEST_INDEX_TASK_STATE_CHANGED"] = self.updateQuestBoxState
		self.__triggers["EVT_ON_VIEWINFO_CHANGED"] = self.__onViewInfoChanged				# ��ʾ/����С��ͼ�ϵ�entityͼ��
		self.__triggers["EVT_ON_START_AUTORUN"] = self.__startAutorun						# ��ʼ�Զ�Ѱ·
		self.__triggers["EVT_ON_STOP_AUTORUN"] = self.__stopAutorun							# �����Զ�Ѱ·
		self.__triggers["EVT_ON_RES_ENTER_WORLD"] = self.__onResEnterWorld 					# ��Դ���������
		self.__triggers["EVT_ON_RES_LEAVE_WORLD"] = self.__onResLeaveWorld					# ��Դ���뿪����
		self.__triggers["EVT_ON_RES_VISIBLE_STATUS"] = self.__onResModelStatus				# ��Դ��ģ���Ƿ�����
		self.__triggers["EVT_ON_DEAD_WATCHER_STATE_CHANGED"] = self.__onDeadWatcherStateChanged	# ��ҵ������۲���״̬�ı�
		self.__triggers["EVT_ON_PLAYER_ENTER_SPACE"] = self.__onPlayerEnterSpace			# ��Ҵ��͵�һ���µĿռ�ʱ����
		self.__triggers["EVT_ON_ENTITY_UTYPE_CHANGED"] = self.__onEntityUtypeChanged				# NPC��Monster����ת���ص�
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __initVisibleFlags( self ) :
		self.__visibleFlags["npc"] = rds.viewInfoMgr.getSetting( self.__viewInfoKey, "npc" )
		self.__visibleFlags["teammate"] = rds.viewInfoMgr.getSetting( self.__viewInfoKey, "teammate" )
		self.__visibleFlags["monster"] = rds.viewInfoMgr.getSetting( self.__viewInfoKey, "monster" )
		self.__visibleFlags["enemyRole"] = True
		self.__visibleFlags["convoyNPC"] = True
		self.__visibleFlags["respoint"] = True

	# -------------------------------------------------
	# about map
	# -------------------------------------------------
	def __getViewSize( self ) :
		"""
		��ȡ��ͼ�Ŀ��ӷ�Χ
		"""
		width = self.width / self.__scale
		height = self.height / self.__scale
		return width, height

	def __getChunkPos( self, chunk ) :
		"""
		��ȡָ�� chunk ���ڵ���������
		"""
		return chunk[0] * self.cc_chunk_width, chunk[1] * self.cc_chunk_width

	# -------------------------------------------------
	def __getLocateChunk( self, ppos ) :
		"""
		���ݸ������꣬�ҳ����괦�� chunk
		"""
		cx = int( divmod( ppos[0], self.cc_chunk_width )[0] )
		cz = int( divmod( ppos[2], self.cc_chunk_width )[0] )
		return cx, cz

	def __setChunkIDs( self, r_chunkIDs, r_cacheIDs ) :
		"""
		��ȡ��ǰҪ��ʾ������ chunk �� ��Ҫ����� chunk
		"""
		chunk_x, chunk_z = self.__currChunk
		chunkRng = xrange( *self.cc_chunkRng )
		for r in xrange( *self.cc_cacheRng ) :
			for c in xrange( *self.cc_cacheRng ) :
				cpos = chunk_x + c, chunk_z - r
				chunkID = int16s2ChunkID( cpos )
				r_cacheIDs.append( chunkID )
				if r in chunkRng and c in chunkRng :
					r_chunkIDs.append( chunkID )

	# ---------------------------------------
	def __getMapLocation( self ) :
		"""
		��ȡ��ɫ��ǰ���� chunk �ڵ�ͼ���� UI �е�λ��
		"""
		chunkPos = self.__getChunkPos( self.__currChunk )
		left = chunkPos[0] - self.cc_chunk_width * self.cc_ltCount
		top = chunkPos[1] + self.cc_chunk_width * ( self.cc_ltCount + 1 )
		return left, top

	def __worldPos2MapPos( self, pos ) :
		"""
		����������ת��Ϊ��ͼ���� UI �����꣨�������ź͵�ͼ mapping ƫ�ƣ�
		"""
		left, top = self.__getMapLocation()
		x = ( pos[0] - left ) / self.cc_baseScale
		y = ( top - pos[2] ) / self.cc_baseScale
		return Math.Vector2( x, y )

	def __worldPos2MapLoaction( self, pos, mappingBound = None ) :
		"""
		����������ת��Ϊ��ͼ�����е����꣨�������ź͵�ͼ mapping ƫ�ƣ�
		"""
		if mappingBound is None :
			mappingBound = util.getGuiMappingBound( self.cc_textureSize, self.__mp.mapping )
		point = self.__worldPos2MapPos( pos )
		point -= ( mappingBound[0], mappingBound[2] )
		point = point.scale( self.scale )
		return point

	# -------------------------------------------------
	def __recombineMaps( self, mapFolder, chunkIDs, cacheIDs, isSkyMin ) :
		"""
		������ϵ�ͼ��Ƭ
		"""
		mapFiles = []
		cacheFiles = []
		folder = self.cc_map_folder % mapFolder
		if isSkyMin:
			folder += "tiankong/"
		for index, chunkID in enumerate( cacheIDs ) :
			mapPath = folder + "%so.dds" % chunkID
			if chunkID in chunkIDs :
				mapFiles.append( mapPath )
			cacheFiles.append( mapPath )
		self.__mtp.update( mapFiles, cacheFiles )

	def __setMapUV( self, isSwitch = False ) :
		"""
		ͨ�� UV ֵ���ƶ���ͼ
		"""
		x, y = self.__worldPos2MapPos( self.__basePos )
		viewSize = self.__getViewSize()
		left = x - viewSize[0] / 2
		right = left + viewSize[0]
		top = y - viewSize[1] / 2
		bottom = top + viewSize[1]
		if isSwitch:
			self.__delaycbid = BigWorld.callback( 1.0, Functor( self.__setMapUVDelay, left, right, top, bottom ) )
			return
		self.__mp.mapping = util.getGuiMapping( self.cc_textureSize, left, right, top, bottom )
		self.__locateSigns()

	def __setMapUVDelay( self, left, right, top, bottom ):
		if self.__mtp.bgLoaded:
			self.__mp.texture = self.__mtp
		self.__mp.mapping = util.getGuiMapping( self.cc_textureSize, left, right, top, bottom )
		self.__locateSigns()

	# ---------------------------------------
	def __updateMap( self, mapFolder, ppos ) :
		"""
		���µ�ͼ
		"""
		oldFolder = self.__mapFolder
		if mapFolder == "" : return
		if smapLoader.isHasSameMap( mapFolder ):							#����ͬ��ͼ��ͬС��ͼ��Դָ����ͬ·��
			mapFolder = smapLoader.getMapPath( mapFolder )
		self.__basePos = ppos
		skyConfigs = Language.openConfigSection( self.cc_skyConfigs )
		oldChunk = self.__currChunk
		self.__currChunk = self.__getLocateChunk( ppos )
		isSkyMin = False
		isSwitch = False
		if skyConfigs is None:
			ERROR_MSG( "get skyconfig error", mapFolder )
		if skyConfigs.has_key( mapFolder ):
			skySect = skyConfigs[mapFolder]
			ceilHeight = skySect["ceilHeight"].asInt
			floorHeight = skySect["floorHeight"].asInt
			points = eval( skySect.readString( "polygon" ) )
			polygon = Polygon( [] )
			polygon.update( points )
			if polygon.isPointIn( (ppos[0], ppos[2]) ):
				oldSkyMin = self.__isSkyMin
				if ppos[1] < ceilHeight and ppos[1] >= floorHeight:
					isSkyMin = self.__isSkyMin
				else:
					isSkyMin = ppos[1] >= ceilHeight
					self.__isSkyMin = isSkyMin
				if oldChunk != self.__currChunk or oldSkyMin != self.__isSkyMin:
					isSwitch = True
					chunkIDs, cacheIDs = [], []
					self.__setChunkIDs( chunkIDs, cacheIDs )
					self.__recombineMaps( mapFolder, chunkIDs, cacheIDs, isSkyMin )
				self.__setMapUV( isSwitch )
				return
		self.__mapFolder = mapFolder
		if oldFolder != mapFolder or oldChunk != self.__currChunk :
			isSwitch = True
			chunkIDs, cacheIDs = [], []
			self.__setChunkIDs( chunkIDs, cacheIDs )
			self.__recombineMaps( mapFolder, chunkIDs, cacheIDs, isSkyMin )
		self.__setMapUV( isSwitch )
		if hasattr(self,"autoPathPosList" ):
			self.__locateAutoPath()

	def __rotatePointer( self, player ) :
		"""
		���ݽ�ɫ��������ת��ɫָ��ķ���
		"""
		util.rotateGui( self.__pointer, player.yaw )
		util.rotateGui( self.__camera, BigWorld.camera().direction.yaw )


	# -------------------------------------------------
	# about entities
	# -------------------------------------------------
	def __setNPCSignStyle( self, pySign, npc ) :
		"""
		���ݲ�ͬ����� NPC ��������ʽ
		"""
		id = npc.questStates

		signStr = npcQSignMgr.getSignBySignID( id )

		SignDict = {
			"normalStart": Sign.ST_Q_TAKE, \
			"normalFinish" : Sign.ST_Q_FINISH, \
			"normalIncomplete" : Sign.ST_Q_INCOMPLETE,\
			"fixloopStart":Sign.ST_Q_TAKE,\
			"qstTalk"	: Sign.ST_Q_TALK_BUB,\
			}
		if signStr not in SignDict:
			pySign.setStyle( Sign.ST_NPC, True )
		else:
			pySign.setStyle( SignDict[signStr], "fixloop" in signStr )

	def __setResSignStyle( self, pySign, resPoint ):
		"""
		������Դ������������ʽ
		"""
		if resPoint is None:return
		reqSkID = resPoint.reqSkillID
		pySign.texture = self.res_skill_map.get( reqSkID, "" )

	def __locateSign( self, pySign, signType, mappingBound = None ) :
		"""
		���� entity ��ǵ�λ��
		"""
		entity = pySign.mapEntity
		pos = entity.position
		point = self.__worldPos2MapLoaction( pos, mappingBound )
		if not entity.inWorld or \
		self.__cPoint.distTo( point ) > self.__radius or \
		self.__checkPySign( pos ):										# ������ڰ뾶���߲�������ʾ����
			pySign.visible = False										# �����ر��
		else :															# ����
			pySign.center, pySign.middle = point						# ��ʾ�������ñ��λ��
			player = BigWorld.player()
			curWholeArea = player.getCurrWholeArea()
			if curWholeArea is None:return
			floorHeight = curWholeArea.floorHeight
			if signType == "respoint":
				model = pySign.mapEntity.model
				if model:
					modelVisible = model.visible
					pySign.visible = self.__visibleFlags[signType] and modelVisible and \
					pos[1] >= floorHeight
			else:
				pySign.visible = self.__visibleFlags[signType] and pos[1] >= floorHeight

	def __checkPySign( self, pos ):
		"""
		���ֿ���������λ��
		���ϲ���ʾ����������True�����򷵻�False
		@return True/False
		"""
		player = BigWorld.player()
		spaceLabel = player.getSpaceLabel()
		if spaceLabel in spaceHeightDatas.keys():
			if Math.Vector3( pos ).y >= spaceHeightDatas.get( spaceLabel, 0.0 ) and \
			player.position.y < spaceHeightDatas.get( spaceLabel, 0.0 ):
				return True
			if Math.Vector3( pos ).y < spaceHeightDatas.get( spaceLabel, 0.0 ) and \
			player.position.y >= spaceHeightDatas.get( spaceLabel, 0.0 ):
				return True
		return False

	def __locateTeammateSign( self, pySign, mappingBound = None ) :
		"""
		���ö���λ��
		"""
		pySign.visible = False											# ��ʱ���ض��ѱ��
		teammate = pySign.teammate										# ����
		pos = teammate.position											# ����λ��
		entity = pySign.mapEntity										# ���� entity
		if entity :														# ������� entity ����
			if entity.id in self.__pyRoleSigns : return					# ����Ӷ�ս���������ʾ
			player = BigWorld.player()
			if player.getSpaceLabel() == teammate.spaceLabel :			# �����ɫ�������ͬһ�� space
				pos = entity.position									# ���ȡ���ѵ�ʵʱ����
			else : return												# ����ͬһ��space������ʾ���ѱ��
		else : return													# ����Ҳ������ѵ� entity������

		point = self.__worldPos2MapLoaction( pos, mappingBound )
		if self.__cPoint.distTo( point ) > self.__radius :				# �����뿪��С��ͼ
			pySign.setStyle( TeammateSign.ST_OUTSIDE )
			yaw = csarithmetic.getYawOfV2( point - self.__cPoint )		# ƽ������ϵԭ�㵽���ĵ�󣬶��ѱ������ƫ��
			point.x = self.__radius * math.sin( yaw )					# ������ϵ�±�ǵ� X ������
			point.y = self.__radius * math.cos( yaw )					# ������ϵ�±�ǵ� Y ������
			point += self.__cPoint										# ʵ��λ�õ���ƽ������ϵ��������������ƫ��
			pySign.center, pySign.middle = point
			x = point.x - self.__cPoint.x
			y = self.__cPoint.y - point.y
			direct = csarithmetic.getYawOfV2( ( x, y ) )				# ������ѱ�ǵķ���
			pySign.direction = direct
		else :															# ������С��ͼ��
			pySign.setStyle( TeammateSign.ST_INSIDE )
			pySign.center, pySign.middle = point
		pySign.visible = self.__visibleFlags["teammate"]

	def __locateSigns( self ) :
		"""
		�������� entity ��ǵ�λ��
		"""
		mappingBound = util.getGuiMappingBound( self.cc_textureSize, self.__mp.mapping )
		if self.__visibleFlags["npc"] :
			for pySign in self.__pyNPCSigns.itervalues() :
				self.__locateSign( pySign, "npc", mappingBound )
		if self.__visibleFlags["monster"] :
			for pySign in self.__pyMSTSigns.itervalues() :
				self.__locateSign( pySign, "monster", mappingBound )
		if self.__visibleFlags["enemyRole"] :
			for pySign in self.__pyRoleSigns.itervalues() :
				self.__locateSign( pySign, "enemyRole", mappingBound )
		if self.__visibleFlags["teammate"] :
			for pySign in self.__pyTMSigns.itervalues() :
				self.__locateTeammateSign( pySign, mappingBound )
		if self.__visibleFlags["convoyNPC"] :
			for pySign in self.__pySMSTSigns.itervalues() :
				self.__locateSign( pySign, "convoyNPC", mappingBound )
		if self.__visibleFlags["respoint"]:
			for pySign in self.__pyResSigns.itervalues():
				self.__locateSign( pySign, "respoint", mappingBound )

	def __locateAutoPath( self ) :
		"""
		���·ֲ��Զ�Ѱ·��
		"""
		lPosLst = []
		for wPos in self.autoPathPosList:
			lPos = self.__worldPos2MapLoaction( wPos )
			
			lPosLst.append( ( lPos[0], -lPos[1] ) )
		self.__autoPathLine.setCircleClip( ( self.__cPoint[0], -self.__cPoint[1] ), self.__radius )
		self.__autoPathLine.setNodes( lPosLst )

	# ---------------------------------------
	def __onResolutionChanged( self, preReso ) :
		"""
		��Ļ�ֱ��ʸı�ʱ������
		"""
		self.__mp.texture = self.__mtp

	def __onEntityTrapIn( self, entity ) :
		"""
		��һ�� entity ��������ʱ������
		"""
		entityType = entity.utype
		if entityType == csdefine.ENTITY_TYPE_ROLE :
			self.__addRoleSign( entity )
			return
		pySign = None
		if entityType == csdefine.ENTITY_TYPE_NPC :
			className = entity.className
			npcData = rds.npcDatasMgr.getNPC( className )					#���ɼ�
			if npcData and npcData.displayOnClient <= 0 and \
			entity.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
				return
			pySign = Sign( self, entity )
			self.__setNPCSignStyle( pySign, entity )
			self.__pyNPCSigns[entity.id] = pySign
			signType = "npc"
		elif entityType in [ csdefine.ENTITY_TYPE_CONVOY_MONSTER, csdefine.ENTITY_TYPE_VEHICLE_DART ] :
			pySign = Sign( self, entity )
			pySign.setStyle( Sign.ST_CONVOY_NPC, False )
			self.__pySMSTSigns[entity.id] = pySign
			signType = "convoyNPC"
		elif entityType in [ csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_SLAVE_MONSTER ] :
			className = entity.className
			npcData = rds.npcDatasMgr.getNPC( className )					#���ɼ�
			if npcData and npcData.displayOnClient <= 0 and \
			entity.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
				return
			pySign = Sign( self, entity )
			fixLoop = entity.className[4:5] in ["2", "4"]			# ��������ͷ�졢��Ӣ��BOSSʱ��ʹ�ö�̬ͼ��
			pySign.setStyle( Sign.ST_MONSTER, fixLoop )
			self.__pyMSTSigns[entity.id] = pySign
			signType = "monster"									# ������ս���ж��Ƿ��ǰ���Ӷ�ս��������ֶ��ǣ���������
		elif entityType == csdefine.ENTITY_TYPE_COLLECT_POINT:		#�ɼ���Դ��
			modelVisible = False
			model = entity.model
			if model:
				modelVisible = model.visible
			pySign = Sign( self, entity )
			pySign.visible = modelVisible
			self.__setResSignStyle( pySign, entity )
			pySign.setStyle( Sign.ST_RES_POINT, False )
			self.__pyResSigns[entity.id] = pySign
			signType = "respoint"
		else :
			return
		if pySign:
			pySign.visible = False
			self.addPyChild( pySign )
			self.__locateSign( pySign, signType )
			
		self.resort()
		
	def __onEntityUtypeChanged( self, entity ):
		"""
		��entity��utype�ı�ʱ���� ֻ������NPC��Monster�������͵�ת��
		"""
		entityType = entity.utype
		if entityType == csdefine.ENTITY_TYPE_NPC :
			for objID, pySign in self.__pyMSTSigns.iteritems() :
				if objID  == entity.id :
					self.__setNPCSignStyle( pySign, entity )
		elif entityType in [ csdefine.ENTITY_TYPE_MONSTER, csdefine.ENTITY_TYPE_SLAVE_MONSTER ] :
			for objID, pySign in self.__pyNPCSigns.iteritems() :
				if objID  == entity.id :
					fixLoop = entity.className[4:5] in ["2", "4"]		
					pySign.setStyle( Sign.ST_MONSTER, fixLoop )

	def __getRoleSignType( self, role ) :
		"""
		��ȡ��ұ������
		�������һ�������͵���ұ��ʱ��ֻ��������ӿ���
		������Ӧ�ı�Ƿ���ֵ��ͬʱ�ǵ���Sign������Ӷ�Ӧ�ı�����ͼ��ɡ�
		������Ҫע����Ǳ�ǵ�������ʾ��Խ����ı�����ͣ����ȼ�Խ�ߣ�
		����ͬʱ�Ǽ�������ʱ����ʾ�Ľ�����������Ǹ����͡�
		@param		role : ��Ҫ��ȡ������͵����
		@type		role : ENTITY
		@return		tuple : ( signStype, isFixLoop )
		"""
		player = BigWorld.player()
		cwTongInfos = player.tongInfos
		pTongDBID = player.tong_dbID
		dTongDBID = 0
		if cwTongInfos.has_key( "defend" ):
			dTongDBID = cwTongInfos["defend"]
		if player.tong_isCityWarTong( role.tong_dbID ):
			if dTongDBID > 0:
				if pTongDBID == role.tong_dbID and \
				role.id != player.id: #ͬһ�����,��ɫ
					return Sign.ST_ROLE, False
				else:
					if role.tong_dbID == dTongDBID: #���ط�
						return Sign.ST_FAMILY_ENEMY, False
					else:
						if pTongDBID == dTongDBID:
							return Sign.ST_FAMILY_ENEMY, False
						else:
							return Sign.ST_MONSTER, False
			else:
				if role.tong_dbID == pTongDBID and \
				role.id != player.id:
					return Sign.ST_ROLE, False
				else:
					return Sign.ST_MONSTER, False
		if player.tong_isRobWarEnemyTong( role.tong_dbID ) :		# ����Ӷ�ս�жԳ�Ա
			return Sign.ST_FAMILY_ENEMY, False
		spaceType = player.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_ROLE_COMPETITION :		# ���˾���
			if not ( role.isPlayer() or role.isDeadWatcher() ) :
				return Sign.ST_FAMILY_ENEMY, False
		elif spaceType == csdefine.SPACE_TYPE_TEAM_COMPETITION :	# ��Ӿ���
			if not ( role.isPlayer() or player.isTeamMember( role.id ) or role.isDeadWatcher() ) :
				return Sign.ST_FAMILY_ENEMY, False
		elif spaceType == csdefine.SPACE_TYPE_TONG_COMPETITION :	# ��Ὰ��
			if not ( role.isPlayer() or role.isDeadWatcher() ) :
				if player.tong_isTongMember( role ) :
					return Sign.ST_TONG_ENEMY, False
				else :
					return Sign.ST_FAMILY_ENEMY, False
		return None, False											# ������ʾ��ǵ����

	def __addRoleSign( self, role ) :
		"""
		���һ����ұ��
		@param		role : Ҫ��ӱ�ǵ����
		@type		role : ENTITY
		"""
		pySign = self.__pyRoleSigns.get( role.id, None )
		signStype, isFixLoop = self.__getRoleSignType( role )
		if pySign is not None  :
			INFO_MSG("Role %d has been exist ! Maybe it hadn't been removed when traped out!" % role.id )
			if signStype is not None :
				pySign.setStyle( signStype, isFixLoop )
			else :
				self.__pyRoleSigns.pop( role.id ).dispose()
		elif signStype is not None :
			pySign = Sign( self, role )
			pySign.setStyle( signStype, isFixLoop )
			pySign.visible = False
			self.__pyRoleSigns[ role.id ] = pySign
			self.addPyChild( pySign )
			self.__locateSign( pySign, "enemyRole" )
			self.resort()

	def __resetRoleSigns( self ) :
		"""
		������Ҽ�Ĺ�ϵ�������ñ������
		"""
		for roleID, pySign in self.__pyRoleSigns.items() :
			role = pySign.mapEntity
			signStype, isFixLoop = self.__getRoleSignType( role )
			if signStype is not None :
				pySign.setStyle( signStype, isFixLoop )
			else :
				self.__pyRoleSigns.pop( role.id ).dispose()

	def __onEntityTrapOut( self, entity ) :
		"""
		��һ�� entity �뿪����ʱ������
		"""
		id = entity.id
		for pySigns in self.__pySigns :
			if id in pySigns :
				pySigns.pop( id ).dispose()

	# -------------------------------------------------
	def __gradualChangeScale( self, value, delta ) :
		"""
		���������ŵ�ͼЧ��
		"""
		scale = self.__scale + delta
		if delta > 0 : scale = min( value, scale )			# ˵������
		else : scale = max( value, scale )					# ˵������
		self.__setMapUV()
		self.__scale = scale
		if scale == value :
			BigWorld.cancelCallback( self.__scaleCBID )
			self.__scaleCBID = 0
		else :
			self.__scaleCBID = BigWorld.callback( 0.02, Functor( self.__gradualChangeScale, value, delta ) )

	# -------------------------------------------------
	def __onMemberJoinIn( self, member ) :
		"""
		����һ����Աʱ������
		"""
		objID = member.objectID
		if objID in self.__pyNPCSigns.keys() :
			self.__pyNPCSigns.pop( objID ).dispose()
		pySign = TeammateSign( self, member )
		self.addPyChild( pySign )
#		self.__locateTeammateSign( pySign )
		self.__pyTMSigns[objID] = pySign
		self.resort()

	def __onMemberLeft( self, entityID ) :
		"""
		һ����Ա�뿪ʱ������
		"""
		if entityID in self.__pyTMSigns.keys() :
			self.__pyTMSigns.pop( entityID ).dispose()
		role = BigWorld.entities.get( entityID, None )	# �����뿪�����
		if role : self.__onEntityTrapIn( role )			# ���䵱��ͨ��ɫ����

	def __onTMRejoin( self, oldEntityID, newEntityID ) :
		"""
		��Ա���¼���
		"""
		teammate = self.__pyTMSigns.get( oldEntityID, None )
		if teammate is not None :
			del self.__pyTMSigns[ oldEntityID ]
			self.__pyTMSigns[ newEntityID ] = teammate
		else :
			teammate = BigWorld.player().teamMember[ newEntityID ]
			self.__onMemberJoinIn( teammate )
			INFO_MSG( "Teammate %d is not in teammate array!" % oldEntityID )

	# -------------------------------------------------
	def __familyChallengeStart( self, entityID ) :
		"""
		������ս��ʼ�����õжԼ����Ա���
		"""
		entity = BigWorld.entities.get( entityID, None )
		if entity is None : return
		self.__addRoleSign( entity )

	def __familyChallengeOver( self, entityID ) :
		"""
		������ս�������ָ��жԼ����Ա���
		"""
		self.__resetRoleSigns()

	#--------------------------------------------------
	def __tongRobWarBeing( self, entity ) :
		"""
		����Ӷ�ս��ʼ����ʾ�ж԰���Ա���
		"""
		self.__addRoleSign( entity )

	def __tongRobWarOver( self, entity ) :
		"""
		����Ӷ�ս������ȡ���ж԰���Ա���
		"""
		self.__resetRoleSigns()

	# -------------------------------------------------
	def __startAutorun( self, dstPos ) :
		"""
		��ʼѰ·ʱ������
		"""
		self.autoPathPosList = list( BigWorld.player().getAutoRunPathLst( ) ) # ��ȡ·����
		self.__autoPathLine.visible = True
		self.__locateAutoPath()

	def __stopAutorun( self, success ) :
		"""
		����Ѱ·ʱ������
		"""
		self.__autoPathLine.visible = False
		self.__autoPathLine.clearNodes()
		if hasattr(self,"autoPathPosList"):
			del self.autoPathPosList

	def __onResEnterWorld( self, resEntity ):
		"""
		��Դ���������
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_ENTER_WORLD", resEntity )

	def __onResLeaveWorld( self, resEntity ):
		"""
		��Դ���뿪����
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_LEAVE_WORLD", resEntity )

	def __onResModelStatus( self, resID, isVisible ):
		pySign = self.__pyResSigns.get( resID, None )
		if pySign:
			pySign.visible = isVisible

	def __onViewInfoChanged( self, infoKey, itemKey, oldValue, value ) :
		"""
		"""
		if self.__viewInfoKey != infoKey : return
		self.__visibleFlags[itemKey] = value
		if value : return									# �������ʾ�������Զ�ˢ����ִ��
		if itemKey == "teammate" :
			self.__setTMSignsVisible( value )
		elif itemKey == "npc" :
			self.__setNPCSignsVisible( value )
		elif itemKey == "monster" :
			self.__setMSTSignsVisible( value )
		else:
			ERROR_MSG( "Unknow system option found! key:%s_%s" % ( str( infoKey ), str( itemKey ) ) )

	def __setTMSignsVisible( self, visible ) :
		"""
		"""
		for pySign in self.__pyTMSigns.itervalues() :
			pySign.visible = visible

	def __setNPCSignsVisible( self, visible ) :
		"""
		"""
		for pySign in self.__pyNPCSigns.itervalues() :
			pySign.visible = visible

	def __setMSTSignsVisible( self, visible ) :
		"""
		"""
		for pySign in self.__pyMSTSigns.itervalues() :
			pySign.visible = visible

	def __onDeadWatcherStateChanged( self, role, isDeadWatcher ) :
		"""
		��ҵ������۲���״̬�����ı�
		"""
		self.__addRoleSign( role )

	def __onPlayerEnterSpace( self ) :
		"""
		��ҽ�����һ���µĿռ�
		"""
		BigWorld.callback( 1.0, self.__refreshRolesSign )					# ��Ҵ��͵�һ���µĿռ��ˢһ����ұ�ǣ���������ԭ���ǣ�
																			# ��������������Ӿ���������ʱ����AOI��Χ��ģ�����ͬʱ
																			# ���ͳ�������������Ҳ�Ǵ���AOI��Χ֮�ڵģ��򲻻ᴥ��enterWorld
																			# ��leaveWorld����������С��ͼ�ϻ��еж���ҵ���ɫ��ǡ�
																			# ʹ��callback����Ϊ���õ��������ʱ����ǰ��ͼ�����ݿ��ܻ�û����
																			# ���ͻ���

	def __refreshRolesSign( self ) :
		"""
		ˢ��һ����Χ����ұ��
		"""
		for entity in BigWorld.entities.values() :
			if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
				self.__addRoleSign( entity )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	# -------------------------------------------------
	def update( self, mapFolder, player ) :
		self.__updateMap( mapFolder, player.position )
		self.__rotatePointer( player )

	# -------------------------------------------------
	def onEnterWorld( self ) :
		self.__initVisibleFlags()

	def onEnterArea( self, newArea ) :
		pass

	def updateNPCsQuestState( self, entity, id ) :
		pySign = self.__pyNPCSigns.get( entity.id, None )
		if pySign is None : return
		self.__setNPCSignStyle( pySign, entity  )

	def updateQuestBoxState( self, entity, state ) :
		pass

	# -------------------------------------------------
	def getHitSigns( self ) :
		"""
		��ȡ�����е� entity sign
		"""
		pySigns = []
		for pySign in self.__pyTMSigns.itervalues() :
			if pySign.isMouseHit() :
				pySigns.append( pySign )
		for pySign in self.__pyNPCSigns.itervalues() :
			if pySign.visible and pySign.isMouseHit() :
				pySigns.append( pySign )
		for pySign in self.__pySMSTSigns.itervalues() :
			if pySign.visible and pySign.isMouseHit() :
				pySigns.append( pySign )
		for pySign in self.__pyMSTSigns.itervalues() :
			if pySign.visible and pySign.isMouseHit() :
				pySigns.append( pySign )
		for pySign in self.__pyRoleSigns.itervalues() :
			if pySign.visible and pySign.isMouseHit() :
				pySigns.append( pySign )
		return pySigns

	# ------------------------------------------------
	def clearTeammates( self ):
		"""
		��ն����Ա���
		"""
		for entityID in self.__pyTMSigns.keys():
			self.__pyTMSigns.pop( entityID ).dispose()
			role = BigWorld.entities.get( entityID, None )
			if role :
				self.__onEntityTrapIn( role )

	def clearAllSigns( self ) :
		"""
		���С��ͼ�ϵ����б��
		"""
		for id in self.__pyNPCSigns.keys():
			self.__pyNPCSigns.pop( id ).dispose()

		for id in self.__pySMSTSigns.keys():
			self.__pySMSTSigns.pop( id ).dispose()

		for id in self.__pyMSTSigns.keys():
			self.__pyMSTSigns.pop( id ). dispose()

		for id in self.__pyTMSigns.keys():
			self.__pyTMSigns.pop( id ).dispose()

		for id in self.__pyRoleSigns.keys():
			self.__pyRoleSigns.pop( id ).dispose()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getScale( self ) :
		return self.__scale

	def _setScale( self, value ) :
		if self.__scaleCBID != 0 : return
		if value == self.__scale : return
		delta = ( value - self.__scale ) / 8.0
		self.__gradualChangeScale( value, delta )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	scale = property( _getScale, _setScale )



# --------------------------------------------------------------------
# implement sign
# --------------------------------------------------------------------
class Sign( Control ) :
	ST_ROLE			= 0x00
	ST_TEAMMATE		= 0x01
	ST_MONSTER		= 0x02
	ST_NPC			= 0x03
	ST_Q_TAKE		= 0x04
	ST_Q_INCOMPLETE	= 0x05
	ST_Q_FINISH		= 0x06
	ST_TONG_ENEMY	= 0x07
	ST_FAMILY_ENEMY	= 0x08
	ST_CONVOY_NPC	= 0x09
	ST_RES_POINT 		= 0x0a
	ST_Q_TALK_BUB	= 0x0b

	def __init__( self, pyMap, mapEntity ) :
		self.sign_ = GUI.Simple( "" )
		self.sign_.tiled = True
		Control.__init__( self, self.sign_ )
		self.setToDefault()
		self.__pyMap = pyMap
		self.mapEntity_ = mapEntity

		self.crossFocus = True

	def dispose( self ) :
		self.mapEntity_ = None
		Control.dispose( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getDescription_( self ) :
		"""
		��ȡ entity ����
		"""
		name = self.mapEntity_.getName()
		title = self.mapEntity_.getTitle()
		dsp = name
		if title :
			dsp += ( lbs_MinMap.MapPanel_tipsTitle % title )
		dsp += "@B"
		return dsp

	# -------------------------------------------------
	def onMouseEnter_( self ) :
		pySigns = self.__pyMap.getHitSigns()
		tips = "@A{C}"
		for pySign in pySigns :
			tips += pySign.getDescription_()
		if self.mapEntity_.utype == csdefine.ENTITY_TYPE_COLLECT_POINT:
			tips += "%s@B"%self.mapEntity_.getName()
		px, py, pz = self.mapEntity_.position
		tips += "%d, %d" % ( px, pz )
		toolbox.infoTip.showESignTips( self, tips )

	def onMouseLeave_( self ) :
		toolbox.infoTip.hide()

	# -------------------------------------------------
	def setStyle( self, style , isFixLoop) :
		if style == self.ST_ROLE :
			self.texture = "maps/entity_signs/role.texanim"
			self.sign_.tileWidth = 16
			self.sign_.tileHeight = 16
			self.sign_.tiled = True
			self.size = ( 16, 16 )
		elif style == Sign.ST_TEAMMATE :
			pass
		elif style == self.ST_MONSTER :
			if isFixLoop :
				self.texture = "maps/entity_signs/ani_monster.texanim"
			else :
				self.texture = "maps/entity_signs/static_monster.texanim"
			self.sign_.tileWidth = 16
			self.sign_.tileHeight = 16
			self.sign_.tiled = True
			self.size = ( 16, 16 )
		elif style == self.ST_NPC :
			self.texture = "maps/entity_signs/static_npc.texanim"
			self.sign_.tileWidth = 16
			self.sign_.tileHeight = 16
			self.sign_.tiled = True
			self.size = ( 16, 16 )
		elif style == self.ST_Q_TAKE :
			if isFixLoop:
				self.texture = "maps/entity_signs/s_marks_special.texanim"
			else:
				self.texture = "maps/entity_signs/s_marks_general.texanim"
			self.sign_.tileWidth = 32
			self.sign_.tileHeight = 32
			self.sign_.tiled = True
			self.size = ( 32, 32 )
		elif style == self.ST_Q_INCOMPLETE :
			self.texture = "maps/entity_signs/f_marks_incomplete.texanim"
			self.sign_.tileWidth = 32
			self.sign_.tileHeight = 32
			self.sign_.tiled = True
			self.size = ( 32, 32 )
		elif style == self.ST_Q_FINISH :
			if isFixLoop:
				self.texture = "maps/entity_signs/f_marks_special.texanim"
			else:
				self.texture = "maps/entity_signs/f_marks_general.texanim"
			self.sign_.tileWidth = 32
			self.sign_.tileHeight = 32
			self.sign_.tiled = True
			self.size = ( 32, 32 )
		elif style == self.ST_TONG_ENEMY :
			self.texture = "maps/entity_signs/rob_war_enemy_tong_member.texanim"
			self.sign_.tileWidth = 16
			self.sign_.tileHeight = 16
			self.sign_.tiled = True
			self.size = ( 16, 16 )
		elif style == self.ST_FAMILY_ENEMY :
			self.texture = "maps/entity_signs/family_challenge_enemy_family_member.texanim"
			self.sign_.tileWidth = 16
			self.sign_.tileHeight = 16
			self.sign_.tiled = True
			self.size = ( 16, 16 )
		elif style == self.ST_CONVOY_NPC :
			self.texture = "maps/entity_signs/convoy_npc.texanim"
			self.sign_.tileWidth = 16
			self.sign_.tileHeight = 16
			self.sign_.tiled = True
			self.size = ( 16, 16 )
		elif style == self.ST_RES_POINT:
			self.sign_.tileWidth = 16
			self.sign_.tileHeight = 16
			self.sign_.tiled = False
			self.size = ( 16, 16 )
		elif style == self.ST_Q_TALK_BUB:
			self.texture = "maps/entity_signs/f_marks_talk.texanim"
			self.sign_.tileWidth = 32
			self.sign_.tileHeight = 32
			self.sign_.tiled = True
			self.size = ( 32, 32 )

	# ----------------------------------------------------------------
	# property method
	# ----------------------------------------------------------------
	def _getEntity( self ) :
		return self.mapEntity_

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	mapEntity = property( _getEntity )


# --------------------------------------------------------------------
# implement sign for teammate
# --------------------------------------------------------------------
class TeammateSign( Sign ) :
	ST_INSIDE		= 0x10
	ST_OUTSIDE		= 0x11

	def __init__( self, pyMap, mapEntity ) :
		Sign.__init__( self, pyMap, mapEntity )
		self.posZ = 0.8
		self.__angle = 0.0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getDescription_( self ) :
		"""
		��ȡ entity ����
		"""
		entity = BigWorld.entities.get( self.mapEntity_.objectID, None )
		if entity :
			name = entity.getName()
			title = entity.getTitle()
			if title : return "%s��%s��@B" % ( name, title )
			return "%s@B" % name
		else :
			return "%s@B" % self.mapEntity_.getName()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setStyle( self, style ) :
		"""
		���ݶ����Ƿ��ڵ�ͼ��Χ�����ö��ѱ�ǵ���ʽ
		"""
		if style == self.ST_INSIDE :
			self.texture = "maps/entity_signs/teammate.texanim"
			self.sign_.tiled = True
			self.sign_.tileWidth = 16
			self.sign_.tileHeight = 16
			self.size = ( 12, 12 )
		else :
			self.texture = "maps/entity_signs/teammate/00.dds"
			self.sign_.tiled = False
			self.sign_.size = 32, 32
		self.__angle = 0.0


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getTeammate( self ) :
		return self.mapEntity_

	def _getEntity( self ) :
		return BigWorld.entities.get( self.mapEntity_.objectID, None )

	# ---------------------------------------
	def _getDirection( self ) :
		return self.__angle

	def _setDirection( self, radian ) :
		self.__angle = radian
		util.rotateGui( self.sign_, radian )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	teammate = property( _getTeammate )
	mapEntity = property( _getEntity )
	direction = property( _getDirection, _setDirection )