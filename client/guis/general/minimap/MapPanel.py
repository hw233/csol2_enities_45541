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
	转换*.chunk的文件名的前8个字符为int16列表；
	如：chunkID2int16( "fff1ffba" ) -> (-15, -70)

	@param: chunkID: *.chunk名称的前8个字符串，如："fff1ffba"
	@return: 包含2个int16的tuple，如：(-15, -70)
	"""
	# phw：以下代码在winxp平台下测试正常，如果哪天发现数据不正常了，
	# 很可能是int()里的调用数值与我当前用的“>”方式不匹配，改成“<”可能就正常了，
	# 当前运行在intel体系的win/linux系列都是一致的，应该不会有问题；
	return struct.unpack( ">hh", struct.pack( ">I", int( chunkID, 16 ) ) )

def int16s2ChunkID( int16s ):
	"""
	chunkID2Int16s()的逆向函数；
	转换一个int16的列表值（只能有两个int16的值）为chunkID；
	如：int16s2ChunkID( (-15, -70) ) -> "fff1ffba"

	@param: 包含2个int16值的tuple或list
	@return: 转换后的16进制字符串（小写）
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

	cc_map_folder		= "space/%s/minimaps/"							# 地图路径
	cc_provider_width	= 512											# 要提取来显示的区域的大小
	cc_map_width		= 128.0											# 每小片贴图大小，也是每 chunk 以贴图表示的大小（正方形）
	cc_chunk_width		= 100.0											# chunk 大小（正方形）
	cc_skyConfigs = "config/client/bigmap/minimapsky.xml"				# 天空地图配置

	cc_baseScale = cc_chunk_width / cc_map_width						# chunk大小 与贴图大小的比例尺
	cc_edges = int( cc_provider_width / cc_map_width )					# 显示区域内，垂直或水平方向上，有多少片贴图
	cc_ltCount = cc_edges / 2 - 1										# 如果以小片贴图数量组成一个坐标系，坐标系原点左边的贴图数量
	cc_chunkRng = ( -cc_ltCount, cc_ltCount + 2 )						# 提取 chunk 的索引范围
	cc_cacheRng = ( cc_chunkRng[0] - 1, cc_chunkRng[1] + 1 )			# 提取缓存 chunk 的索引范围(缓存贴图要往外取一行一列)
	cc_textureSize = cc_edges * cc_map_width, cc_edges * cc_map_width	# 显示全部贴图的 GUI 的大小

	__cc_trap_handle_delay = 1.0										# 延迟处理 Trap 的时间

	def __init__( self, panel ) :
		Control.__init__( self, panel )
		self.__cPoint = Math.Vector2( self.size )		# 中心点位置
		self.__cPoint *= 0.5
		self.__radius = self.__cPoint.x					# 可视范围半径
		self.__pointer = panel.pointer					# 角色标记
		self.__camera = panel.camera					# 相机标记
		self.__basePos = ( 0, 0, 0 )					# 地图圆心位置
		self.__scale = 1								# 地图比例尺
		self.__scaleCBID = 0							# 逐渐缩放的 callback ID
		self.__delaycbid = 0

		self.__mapFolder = ""							# 地图路径
		self.__mp = panel.mp							# 地图 UI
		self.__isSkyMin = False
		self.__mtp = BigWorld.PyMergerTextureProvider( \
			self.cc_provider_width, self.cc_provider_width )
		self.__currChunk = ( 0, 0 )						# 当前所在的 chunk

		self.__pyNPCSigns = {}							# NPC signs
		self.__pyTMSigns = {}							# 队友 sings（独立处理队友）
		self.__pyRoleSigns = {}							# 非队友玩家
		self.__pyMSTSigns = {}							# Monster signs
		self.__pySMSTSigns = {}							# 护送NPC
		self.__pyResSigns = {}							# 资源点NPC
		self.__pySigns = (	\
			self.__pyNPCSigns, \
			self.__pyMSTSigns, \
			self.__pyRoleSigns, \
			self.__pySMSTSigns, \
			self.__pyResSigns,	\
			)

		self.__visibleFlags = {}						# 各种类型entity的显示标记{ "npc": True, "monster": False, ... }
		self.__viewInfoKey = "entitySigns"				# 该键是在配置：config/client/viewinfosetting.xml 中的主键，标记是否要显示各类型标记

		#self.__autoPathPosList = []						# 保存自动寻路路径点
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
		self.__triggers["EVT_ON_TEAM_MEMBER_REJOIN"] = self.__onTMRejoin					# 队员下线后重上
		self.__triggers["EVT_ON_FAMILY_CHALLENGING"] = self.__familyChallengeStart			# 家族挑战中
		self.__triggers["EVT_ON_FAMILY_CHALLENGE_OVER"] = self.__familyChallengeOver		# 家族挑战结束
		self.__triggers["EVT_ON_TONG_ROB_WAR_BEING"] = self.__tongRobWarBeing
		self.__triggers["EVT_ON_TONG_ROB_WAR_OVER"] = self.__tongRobWarOver
		self.__triggers["EVT_ON_NPC_QUEST_STATE_CHANGED"] = self.updateNPCsQuestState
		self.__triggers["EVT_ON_BOX_QUEST_INDEX_TASK_STATE_CHANGED"] = self.updateQuestBoxState
		self.__triggers["EVT_ON_VIEWINFO_CHANGED"] = self.__onViewInfoChanged				# 显示/隐藏小地图上的entity图标
		self.__triggers["EVT_ON_START_AUTORUN"] = self.__startAutorun						# 开始自动寻路
		self.__triggers["EVT_ON_STOP_AUTORUN"] = self.__stopAutorun							# 结束自动寻路
		self.__triggers["EVT_ON_RES_ENTER_WORLD"] = self.__onResEnterWorld 					# 资源点进入视线
		self.__triggers["EVT_ON_RES_LEAVE_WORLD"] = self.__onResLeaveWorld					# 资源点离开视线
		self.__triggers["EVT_ON_RES_VISIBLE_STATUS"] = self.__onResModelStatus				# 资源点模型是否隐藏
		self.__triggers["EVT_ON_DEAD_WATCHER_STATE_CHANGED"] = self.__onDeadWatcherStateChanged	# 玩家的死亡观察者状态改变
		self.__triggers["EVT_ON_PLAYER_ENTER_SPACE"] = self.__onPlayerEnterSpace			# 玩家传送到一个新的空间时调用
		self.__triggers["EVT_ON_ENTITY_UTYPE_CHANGED"] = self.__onEntityUtypeChanged				# NPC和Monster类型转换回调
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
		获取地图的可视范围
		"""
		width = self.width / self.__scale
		height = self.height / self.__scale
		return width, height

	def __getChunkPos( self, chunk ) :
		"""
		获取指定 chunk 所在的世界坐标
		"""
		return chunk[0] * self.cc_chunk_width, chunk[1] * self.cc_chunk_width

	# -------------------------------------------------
	def __getLocateChunk( self, ppos ) :
		"""
		根据给定坐标，找出坐标处的 chunk
		"""
		cx = int( divmod( ppos[0], self.cc_chunk_width )[0] )
		cz = int( divmod( ppos[2], self.cc_chunk_width )[0] )
		return cx, cz

	def __setChunkIDs( self, r_chunkIDs, r_cacheIDs ) :
		"""
		获取当前要显示的所有 chunk 和 需要缓存的 chunk
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
		获取角色当前所在 chunk 在地图镜面 UI 中的位置
		"""
		chunkPos = self.__getChunkPos( self.__currChunk )
		left = chunkPos[0] - self.cc_chunk_width * self.cc_ltCount
		top = chunkPos[1] + self.cc_chunk_width * ( self.cc_ltCount + 1 )
		return left, top

	def __worldPos2MapPos( self, pos ) :
		"""
		将世界坐标转换为地图镜面 UI 中坐标（不算缩放和地图 mapping 偏移）
		"""
		left, top = self.__getMapLocation()
		x = ( pos[0] - left ) / self.cc_baseScale
		y = ( top - pos[2] ) / self.cc_baseScale
		return Math.Vector2( x, y )

	def __worldPos2MapLoaction( self, pos, mappingBound = None ) :
		"""
		将世界坐标转换为地图镜面中的坐标（计算缩放和地图 mapping 偏移）
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
		重新组合地图切片
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
		通过 UV 值来移动地图
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
		更新地图
		"""
		oldFolder = self.__mapFolder
		if mapFolder == "" : return
		if smapLoader.isHasSameMap( mapFolder ):							#将不同地图相同小地图资源指向相同路径
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
		根据角色的面向，旋转角色指针的方向
		"""
		util.rotateGui( self.__pointer, player.yaw )
		util.rotateGui( self.__camera, BigWorld.camera().direction.yaw )


	# -------------------------------------------------
	# about entities
	# -------------------------------------------------
	def __setNPCSignStyle( self, pySign, npc ) :
		"""
		根据不同种类的 NPC 设置其样式
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
		根据资源点类型设置样式
		"""
		if resPoint is None:return
		reqSkID = resPoint.reqSkillID
		pySign.texture = self.res_skill_map.get( reqSkID, "" )

	def __locateSign( self, pySign, signType, mappingBound = None ) :
		"""
		设置 entity 标记的位置
		"""
		entity = pySign.mapEntity
		pos = entity.position
		point = self.__worldPos2MapLoaction( pos, mappingBound )
		if not entity.inWorld or \
		self.__cPoint.distTo( point ) > self.__radius or \
		self.__checkPySign( pos ):										# 距离大于半径或者不符合显示条件
			pySign.visible = False										# 则隐藏标记
		else :															# 否则
			pySign.center, pySign.middle = point						# 显示，并设置标记位置
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
		区分空中与地面的位置
		符合不显示的条件返回True，否则返回False
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
		设置队友位置
		"""
		pySign.visible = False											# 暂时隐藏队友标记
		teammate = pySign.teammate										# 队友
		pos = teammate.position											# 队友位置
		entity = pySign.mapEntity										# 队友 entity
		if entity :														# 如果队友 entity 存在
			if entity.id in self.__pyRoleSigns : return					# 帮会掠夺战标记优先显示
			player = BigWorld.player()
			if player.getSpaceLabel() == teammate.spaceLabel :			# 如果角色与队友在同一个 space
				pos = entity.position									# 则获取队友的实时坐标
			else : return												# 不在同一个space，不显示队友标记
		else : return													# 如果找不到队友的 entity，返回

		point = self.__worldPos2MapLoaction( pos, mappingBound )
		if self.__cPoint.distTo( point ) > self.__radius :				# 队友离开了小地图
			pySign.setStyle( TeammateSign.ST_OUTSIDE )
			yaw = csarithmetic.getYawOfV2( point - self.__cPoint )		# 平移坐标系原点到中心点后，队友标记向量偏角
			point.x = self.__radius * math.sin( yaw )					# 新坐标系下标记的 X 轴坐标
			point.y = self.__radius * math.cos( yaw )					# 新坐标系下标记的 Y 轴坐标
			point += self.__cPoint										# 实际位置等于平移坐标系后的坐标加上中心偏移
			pySign.center, pySign.middle = point
			x = point.x - self.__cPoint.x
			y = self.__cPoint.y - point.y
			direct = csarithmetic.getYawOfV2( ( x, y ) )				# 计算队友标记的方向
			pySign.direction = direct
		else :															# 队友在小地图内
			pySign.setStyle( TeammateSign.ST_INSIDE )
			pySign.center, pySign.middle = point
		pySign.visible = self.__visibleFlags["teammate"]

	def __locateSigns( self ) :
		"""
		设置所有 entity 标记的位置
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
		重新分布自动寻路点
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
		屏幕分辨率改变时被调用
		"""
		self.__mp.texture = self.__mtp

	def __onEntityTrapIn( self, entity ) :
		"""
		有一个 entity 进入陷阱时被调用
		"""
		entityType = entity.utype
		if entityType == csdefine.ENTITY_TYPE_ROLE :
			self.__addRoleSign( entity )
			return
		pySign = None
		if entityType == csdefine.ENTITY_TYPE_NPC :
			className = entity.className
			npcData = rds.npcDatasMgr.getNPC( className )					#不可见
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
			npcData = rds.npcDatasMgr.getNPC( className )					#不可见
			if npcData and npcData.displayOnClient <= 0 and \
			entity.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
				return
			pySign = Sign( self, entity )
			fixLoop = entity.className[4:5] in ["2", "4"]			# 当怪物是头领、精英、BOSS时，使用动态图标
			pySign.setStyle( Sign.ST_MONSTER, fixLoop )
			self.__pyMSTSigns[entity.id] = pySign
			signType = "monster"									# 家族挑战再判断是否是帮会掠夺战，如果两种都是，那最终显
		elif entityType == csdefine.ENTITY_TYPE_COLLECT_POINT:		#采集资源点
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
		当entity的utype改变时调用 只处理了NPC和Monster两种类型的转换
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
		获取玩家标记类型
		当需添加一个新类型的玩家标记时，只需在这个接口里
		加入相应的标记返回值，同时记得在Sign类中添加对应的标记类型即可。
		另外需要注意的是标记的优先显示，越上面的标记类型，优先级越高，
		所以同时是几种类型时，显示的将是最上面的那个类型。
		@param		role : 需要获取标记类型的玩家
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
				role.id != player.id: #同一个帮会,绿色
					return Sign.ST_ROLE, False
				else:
					if role.tong_dbID == dTongDBID: #防守方
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
		if player.tong_isRobWarEnemyTong( role.tong_dbID ) :		# 帮会掠夺战敌对成员
			return Sign.ST_FAMILY_ENEMY, False
		spaceType = player.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_ROLE_COMPETITION :		# 个人竞技
			if not ( role.isPlayer() or role.isDeadWatcher() ) :
				return Sign.ST_FAMILY_ENEMY, False
		elif spaceType == csdefine.SPACE_TYPE_TEAM_COMPETITION :	# 组队竞技
			if not ( role.isPlayer() or player.isTeamMember( role.id ) or role.isDeadWatcher() ) :
				return Sign.ST_FAMILY_ENEMY, False
		elif spaceType == csdefine.SPACE_TYPE_TONG_COMPETITION :	# 帮会竞技
			if not ( role.isPlayer() or role.isDeadWatcher() ) :
				if player.tong_isTongMember( role ) :
					return Sign.ST_TONG_ENEMY, False
				else :
					return Sign.ST_FAMILY_ENEMY, False
		return None, False											# 不需显示标记的玩家

	def __addRoleSign( self, role ) :
		"""
		添加一个玩家标记
		@param		role : 要添加标记的玩家
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
		根据玩家间的关系重新设置标记类型
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
		有一个 entity 离开陷阱时被调用
		"""
		id = entity.id
		for pySigns in self.__pySigns :
			if id in pySigns :
				pySigns.pop( id ).dispose()

	# -------------------------------------------------
	def __gradualChangeScale( self, value, delta ) :
		"""
		处理动画缩放地图效果
		"""
		scale = self.__scale + delta
		if delta > 0 : scale = min( value, scale )			# 说明增长
		else : scale = max( value, scale )					# 说明减少
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
		加入一个队员时被调用
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
		一个队员离开时被调用
		"""
		if entityID in self.__pyTMSigns.keys() :
			self.__pyTMSigns.pop( entityID ).dispose()
		role = BigWorld.entities.get( entityID, None )	# 队友离开队伍后
		if role : self.__onEntityTrapIn( role )			# 将其当普通角色处理

	def __onTMRejoin( self, oldEntityID, newEntityID ) :
		"""
		队员重新加入
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
		家族挑战开始，设置敌对家族成员标记
		"""
		entity = BigWorld.entities.get( entityID, None )
		if entity is None : return
		self.__addRoleSign( entity )

	def __familyChallengeOver( self, entityID ) :
		"""
		家族挑战结束，恢复敌对家族成员标记
		"""
		self.__resetRoleSigns()

	#--------------------------------------------------
	def __tongRobWarBeing( self, entity ) :
		"""
		帮会掠夺战开始，显示敌对帮会成员标记
		"""
		self.__addRoleSign( entity )

	def __tongRobWarOver( self, entity ) :
		"""
		帮会掠夺战结束，取消敌对帮会成员标记
		"""
		self.__resetRoleSigns()

	# -------------------------------------------------
	def __startAutorun( self, dstPos ) :
		"""
		开始寻路时被调用
		"""
		self.autoPathPosList = list( BigWorld.player().getAutoRunPathLst( ) ) # 获取路径点
		self.__autoPathLine.visible = True
		self.__locateAutoPath()

	def __stopAutorun( self, success ) :
		"""
		结束寻路时被调用
		"""
		self.__autoPathLine.visible = False
		self.__autoPathLine.clearNodes()
		if hasattr(self,"autoPathPosList"):
			del self.autoPathPosList

	def __onResEnterWorld( self, resEntity ):
		"""
		资源点进入视线
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_ENTER_WORLD", resEntity )

	def __onResLeaveWorld( self, resEntity ):
		"""
		资源点离开视线
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
		if value : return									# 如果是显示，则在自动刷新中执行
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
		玩家的死亡观察者状态发生改变
		"""
		self.__addRoleSign( role )

	def __onPlayerEnterSpace( self ) :
		"""
		玩家进入了一个新的空间
		"""
		BigWorld.callback( 1.0, self.__refreshRolesSign )					# 玩家传送到一个新的空间后刷一遍玩家标记，这样做的原因是：
																			# 如果两个玩家在组队竞技副本里时是在AOI范围里的，这是同时
																			# 传送出副本，在外面也是处于AOI范围之内的，则不会触发enterWorld
																			# 和leaveWorld方法，导致小地图上还有敌对玩家的紫色标记。
																			# 使用callback是因为调用到这个方法时，当前地图的数据可能还没更新
																			# 到客户端

	def __refreshRolesSign( self ) :
		"""
		刷新一遍周围的玩家标记
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
		获取鼠标击中的 entity sign
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
		清空队伍成员标记
		"""
		for entityID in self.__pyTMSigns.keys():
			self.__pyTMSigns.pop( entityID ).dispose()
			role = BigWorld.entities.get( entityID, None )
			if role :
				self.__onEntityTrapIn( role )

	def clearAllSigns( self ) :
		"""
		清除小地图上的所有标记
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
		获取 entity 描述
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
		获取 entity 描述
		"""
		entity = BigWorld.entities.get( self.mapEntity_.objectID, None )
		if entity :
			name = entity.getName()
			title = entity.getTitle()
			if title : return "%s【%s】@B" % ( name, title )
			return "%s@B" % name
		else :
			return "%s@B" % self.mapEntity_.getName()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setStyle( self, style ) :
		"""
		根据队友是否在地图范围内设置队友标记的样式
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