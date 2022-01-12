# -*- coding: gb18030 -*-
#
# $Id: MapMgr.py,v 1.18 2008-08-27 09:06:37 huangyongwei Exp $

"""
This module implements the map manager

2007/12/25: writen by huangyongwei
2010.02.06: 重整区域类，让子区域和全区域继承于 BaseArea
"""

import math
import random
import Math
import ResMgr
import Language
import utils
import BigWorld
from bwdebug import *
from cscollections import MapList
from cscustom import Polygon
from cscustom import Rect
from AbstractTemplates import Singleton
from AbstractTemplates import AbstractClass
from gbref import rds
import Define


# --------------------------------------------------------------------
# 区域基类
# --------------------------------------------------------------------
class BaseArea( AbstractClass ) :
	__abstract_methods = set()

	def __init__( self, sect, wholeArea ) :
		self.__wholeArea = wholeArea									# 所属父区域
		self.__name = sect.asString										# 区域名称
		self.__texture = sect.readString( "texture" )					# 区域贴图
		self.__ignore = sect.readBool( "ignore" )						# 是否不显示地图
		self.__autoSeekingPath = sect.readString( "autoSeekingPath" )	# 自动寻路路径
		self.__bgMusics = []											# 区域的背景音乐
		self.__bgSounds = []											# 区域的背景音效
		self.__effectFalg = Define.MAP_AREA_EFFECT_DEFAULT				# 默认无区域效果
		if sect.has_key( "effectFlag" ):
			self.__effectFalg = sect.readInt( "effectFlag" )
		self.__ceilHeight = 99999.0											# 普通地图默认高度，没有配置
		self.__floorHeight = -1000.0
		if sect.has_key( "ceilHeight" ):
			self.__ceilHeight = sect.readInt( "ceilHeight" )
		if sect.has_key( "floorHeight" ):
			self.__floorHeight = sect.readInt( "floorHeight" )
		self.worldBound_ = Rect()										# 区域外接矩形（在世界中）
		self.mapBound_ = Rect()											# 区域外接矩形（在贴图中）
		self.mapMapping_ = ( 0, 0 ), ( 0, 1 ), \
							( 1, 1 ), ( 1, 0 )							# 贴图有效 mapping（注：mapping 是 UI 表现问题，放这里有点不妥，但放这里可以免去每次都计算）
		self.scales_ = ( 1, 1 )											# 世界与贴图的缩放比例

		self.calcWorldBound_( sect )									# 计算在世界中的外接矩形
		self.calcMapBound_( sect )										# 计算区域在贴图上的外接矩形
		self.__initBGMusics( sect )										# 初始化背景音乐
		self.__initBGSounds( sect )										# 初始化背景音效

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def spaceName( self ) :
		"""
		区域所属场景的中文名称
		@type				: str
		"""
		if self.__wholeArea is self :			# 全地图被认为是大区域
			return self.__name
		return self.__wholeArea.spaceName

	@property
	def name( self ) :
		"""
		区域的中文名称
		@type				: str
		"""
		return self.__name

	@property
	def fullName( self ) :
		"""
		全名称：所属场景名:区域名
		@type				: str
		"""
		if self.__wholeArea is self :
			return self.__name
		return "%s:%s" % ( self.__wholeArea.name, self.__name )

	@property
	def wholeArea( self ) :
		"""
		所属的全地图
		@type				: WholeArea
		"""
		return self.__wholeArea

	# ---------------------------------------
	@property
	def autoSeekingPath( self ) :
		"""
		自动寻路路径
		@type				: str
		"""
		if self.__autoSeekingPath != "" :
			return self.__autoSeekingPath
		return self.__wholeArea.__autoSeekingPath

	# ---------------------------------------
	@property
	def texture( self ) :
		"""
		贴图路径（如果没有贴图，则返回所属场景的贴图）
		@type				: str
		"""
		return self.__texture

	@property
	def ignore( self ) :
		"""
		是否忽略地图贴图（不显示地图）
		@type				: bool
		"""
		return self.__ignore

	# ---------------------------------------
	@property
	def worldBound( self ) :
		"""
		区域在世界上的外接矩形
		@type				: Rect
		"""
		return self.worldBound_

	@property
	def mapBound( self ) :
		"""
		区域在贴图上的外接矩形
		@type				: Rect
		"""
		return self.mapBound_

	@property
	def mapMapping( self ) :
		"""
		地图贴图非空白区域大小
		注：mapping 是 UI 表现问题，放这里有点不妥，但放这里可以免去每次都计算
		"""
		return self.mapMapping_

	@property
	def scales( self ) :
		"""
		水平、垂直缩放比例
		@type				: tuple
		"""
		return self.scales_

	@property
	def ceilHeight( self ):
		"""
		获取场景缓冲区上限高度
		@type			: int
		"""
		return self.__ceilHeight

	@property
	def floorHeight( self ):
		"""
		获取场景缓冲区上限高度
		@type			: int
		"""
		return self.__floorHeight

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initBGMusics( self, sect ) :
		"""
		初始化背景音乐
		"""
		sect = sect["bgMusics"]
		if sect is None : return
		self.__bgMusics = sect.readStrings( "music" )

	def __initBGSounds( self, sect ):
		"""
		初始化背景音效
		"""
		sect = sect["bgSounds"]
		if sect is None: return
		self.__bgSounds = sect.readStrings( "sound" )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def calcWorldBound_( self, sect ) :
		"""
		计算场景在世界中的矩形
		"""
		pass

	def calcMapBound_( self, sect ) :
		"""
		计算区域在贴图上的外接矩形
		"""
		if self.__texture == "" : return
		mw, mh = sect.readVector2( "mapSize" )							# 地图贴图非空白区大小
		if mw == 0.0 or mh == 0.0 :
			raise TypeError( "error size of map '%s', or its space is not exist!" % self.__name )
		tw = 2 ** math.ceil( math.log( mw, 2 ) )						# 地图贴图宽度
		th = 2 ** math.ceil( math.log( mh, 2 ) )						# 地图贴图高度
		if sect.has_key( "effectiveRect" ) :
			ex, ey, ew, eh = sect.readVector4( "effectiveRect" )		# 有效区域
			assert ( ex + ew <= mw ) and ( ey + eh <= mh ), \
				"effective rectangle of area '%s' is not valid!" % \
				sect.asWideString
			self.mapBound_.update( ( ex, ey ), ( ew, eh ) )

			# 计算贴图 mapping
			left, right = ex / tw, ( ex + ew ) / tw
			top, bottom = ey / th, ( ey + eh ) / th
		else :
			# 计算贴图 mapping
			self.mapBound_.updateSize( mw, mh )
			left, right = 0, mw / tw
			top, bottom = 0, mh / th
		self.mapMapping_ = ( left, top ), ( left, bottom ), \
						   ( right, bottom ), ( right, top )

		# 计算比例
		scaleX = self.worldBound_.width / mw
		scaleY = self.worldBound_.height / mh
		self.scales_ = scaleX, scaleY


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isSubArea( self ) :
		"""
		返回是否是子区域（与 isWholeArea 相对）
		@rtype				: bool
		@return				: True
		"""
		return self.__wholeArea is not self

	def isWholeArea( self ) :
		"""
		返回是否是全地图（与 isSubArea 相对）
		@rtype				: bool
		@return				: False
		"""
		return self.__wholeArea is self

	def hasTexture( self ) :
		"""
		返回是否有自己的贴图
		@param				: bool
		@return				: return True if i have my own texture
		"""
		return self.__texture != ""

	# -------------------------------------------------
	def getMusic( self ) :
		"""
		获取背景音乐的路径
		@rtype				: str
		@return				: music name
		"""
		if len( self.__bgMusics ) > 0 :
			return random.choice( self.__bgMusics )
		if self.isWholeArea() :
			return ""
		return self.__wholeArea.getMusic()

	def getBgSound( self ):
		"""
		获取背景音效的路径
		"""
		if len( self.__bgSounds ) > 0 :
			return random.choice( self.__bgSounds )
		if self.isWholeArea():
			return ""
		return self.__wholeArea.getBgSound()

	def getNPCs( self, dspflag ) :
		"""
		获取区域内的所有 NPC
		"""
		return []

	def getEffectFlag( self ):
		"""
		获取区域特殊效果
		"""
		return self.__effectFalg

	# -------------------------------------------------
	def isWorldPointIn( self, point ) :
		"""
		判断某个点是否在区域上
		@type			point : tuple
		@param			point : 世界坐标
		@rtype				  : bool
		@return				  : 如果给出的点落在区域上，则返回 True
		"""
		return self.worldBound_.isPointIn( point )

	# -------------------------------------------------
	def worldPoint2TexturePoint( self, point ) :
		"""
		将区域上的某点的真实坐标转换为其在贴图上的坐标
		@type				point : tuple
		@param				point : point in the world ( x, z )
		@rtype					  : tuple
		@return					  : 贴图上的坐标
		"""
		wx, wy = point[:2]
		if len( point ) > 2 : wy = point[2]				# 如果是三围坐标，则以 z 轴坐标当二维中的 y 轴算
		scaleX, scaleY = self.scales_
		mx = ( wx - self.worldBound_.x ) / scaleX		# 映射到贴图上的左距
		my = ( self.worldBound_.maxY - wy ) / scaleY	# 映射到贴图上的顶距
		x = mx - self.mapBound_.x						# 在大地图上的左距
		y = my - self.mapBound_.y						# 在大地图上的顶距
		return Math.Vector2( x, y )

	def texturePoint2WorldPoint( self, point ) :
		"""
		将区域上的某点贴图上的坐标转换为世界坐标(真实坐标)
		@type				point : tuple
		@param				point : point in texture ( x, y )
		@rtype					  : tuple
		@return					  : 世界坐标（真实坐标）
		"""
		x, y = point
		mx = x + self.mapBound_.x
		my = y + self.mapBound_.y
		scaleX, scaleY = self.scales_
		wx = self.worldBound_.x + mx * scaleX
		wy = self.worldBound_.maxY - my * scaleY
		return Math.Vector2( wx, wy )


	# ----------------------------------------------------------------
	# 抽象方法
	# ----------------------------------------------------------------
	__abstract_methods.add( calcWorldBound_ )
	__abstract_methods.add( getNPCs )


# --------------------------------------------------------------------
# implement area class
# --------------------------------------------------------------------
class SubArea( BaseArea ) :
	"""
	子区域
	"""
	def __init__( self, sect, wholeArea ) :
		self.__polygon = Polygon( [] )
		BaseArea.__init__( self, sect, wholeArea )

	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "SubArea(%s)" % self.fullName


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def spaceLabel( self ) :
		"""
		所属场景的英文标记
		@type				: str
		"""
		return self.wholeArea.spaceLabel

	@property
	def spaceFolder( self ) :
		"""
		所属场景所在的加载点（场景配置所在的文件夹名称）
		@type				: str
		"""
		return self.wholeArea.spaceFolder

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def calcWorldBound_( self, sect ) :
		"""
		计算场景在世界中的矩形
		"""
		areaPoints = eval( sect.readString( "polygon" ) )
		self.__polygon.update( areaPoints )
		self.worldBound_ = self.__polygon.bound


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isWorldPointIn( self, point ) :
		"""
		判断某个点是否在区域上
		@type			point : tuple
		@param			point : 世界坐标
		@rtype				  : bool
		@return				  : 如果给出的点落在区域上，则返回 True
		"""
		return self.__polygon.isPointIn( point )

	def getNPCs( self, dspflag ) :
		"""
		获取区域内的所有
		"""
		return self.wholeArea.getNPCs( dspflag )


# --------------------------------------------------------------------
# implement map class
# --------------------------------------------------------------------
class WholeArea( BaseArea ) :
	"""
	场景（在这里它被认为是全地图区域，SubArea 是它的子区域）
	"""
	__cc_space_path	 =  "universes/%s/space.settings"
	__cc_chunk_width = 100.0

	def __init__( self, sect, mapLabel, isSkyArea ) :
		self.__spaceLabel = mapLabel							# 所属场景的英文标签
		self.__spaceFolder = sect.readString( "spaceFolder" )
		BaseArea.__init__( self, sect, self )

		self.__areas = {}										# 其下的所有子区域
		self.isSkyArea	= isSkyArea							# 是否为天空区域
		
		self.__initAreas( sect )

	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "WholeArea(%s)" % self.spaceLabel


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initAreas( self, sect ) :
		"""
		初始化场景
		"""
		subSect = sect["areas"]
		if subSect is None : return
		for tag, pyDs in subSect.items() :
			area = SubArea( pyDs, self )
			self.__areas[area.name] = area
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def calcWorldBound_( self, sect ) :
		"""
		计算场景在世界中的矩形
		"""
		spaceConfig = self.__cc_space_path % self.__spaceFolder
		spSect = ResMgr.openSection( spaceConfig )
		if spSect is None :
			ERROR_MSG( "get space bound error:", spaceConfig )
			return
		cleft = spSect["bounds"].readFloat( "minX" )
		cright = spSect["bounds"].readFloat( "maxX" )
		ctop = spSect["bounds"].readFloat( "maxY" )
		cbottom = spSect["bounds"].readFloat( "minY" )
		left = cleft * self.__cc_chunk_width
		right = ( cright + 1 ) * self.__cc_chunk_width
		top = ( ctop + 1 ) * self.__cc_chunk_width
		bottom = cbottom * self.__cc_chunk_width
		self.worldBound_.updateByBound( left, right, bottom, top )
		ResMgr.purge( spaceConfig )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def spaceLabel( self ) :
		"""
		标记场景的英文标签
		@type				: str
		"""
		return self.__spaceLabel

	@property
	def spaceFolder( self ) :
		"""
		场景配置所在文件夹的路径
		@type				: str
		"""
		return self.__spaceFolder

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSubAreas( self ) :
		"""
		获得所有的子区域
		@rtype					: dict
		@return					: list of all my SubAreas
		"""
		return self.__areas

	def getSubArea( self, point ) :
		"""
		通过某点获取它所在的子区域
		@type				point : tuple
		@param				point : 世界坐标
		@rtype					  : SubArea
		@return					  : 如果落在某个子区域上，则返回该子区域。否则返回 None
		"""
		pos = 0, 0
		height = 0
		if len( point ) > 2 :
			pos = point[0], point[2]
		for area in self.__areas.itervalues() :
			if area.isWorldPointIn( pos ): # 搜寻在投影区的area
				return area
		return None
	# -------------------------------------------------
	def getNPCs( self, dspflag ) :
		"""
		获取场景中的所有 NPC
		@type				dspflag : int
		@param				dspflag : 过滤标记
		@rtype						: dict
		@return						: npcs { npcID : NPCDatasMgr::NPC }
		"""
		return rds.npcDatasMgr.getNPCs( self.spaceLabel, dspflag )

	def setTimeOfDay( self ):
		"""
		设置当前区域的TimeOfDay功能
		"""
		spaceConfig = self.__cc_space_path % self.__spaceFolder
		spSect = ResMgr.openSection( spaceConfig )
		if spSect is None:return
		skyConfig = spSect.readString( "timeOfDay" )
		if skyConfig is None:
			ERROR_MSG( "get sky environments error:", spaceConfig )
			return
		skySect = ResMgr.openSection( skyConfig )
		if skySect is None:return
		if skySect.has_key( "day_night_cycle" ):
			ndCSect = skySect["day_night_cycle"]
			startTime = ndCSect.readFloat( "starttime" )
			BigWorld.timeOfDay( startTime )
# --------------------------------------------------------------------
# implement world map
# --------------------------------------------------------------------
class WorldArea( WholeArea ) :
	__cc_cfg_path	= "config/client/bigmap/world_areas.xml"

	# -------------------------------------------------
	# 世界地图子板块
	# -------------------------------------------------
	class Board( object ) :
		"""
		世界地图子版块
		"""
		__slots__ = ( "_Board__nav", "_Board__area" , "pos", "texture", "size", "polygon" )
		def __init__( self, sect ) :
			self.pos = sect.readVector2( "pos" )							# 板块位置
			self.texture = sect.readString( "texture" )						# 板块贴图
			self.size = sect.readVector2( "size" )							# 板块大小
			verties = sect["polygon"].readVector2s( "item" )				# 板块顶点
			self.polygon = Polygon( verties )								# 板块区域
			self.__nav = sect.asString.split( ":" )							# 板块指向的区域的名称
			if len( self.__nav ) == 1 : self.__nav.append( "" )
			self.__area = None

		@property
		def area( self ) :
			if self.__area is None :
				try :
					self.__area = mapMgr.getAreaViaName( *self.__nav )
				except :
					ERROR_MSG( "area '%s' is not exist!" % str( self.__nav ) )	# 子板块指向的区域不存在
			return self.__area


	# ----------------------------------------------------------------
	# initialize
	# ----------------------------------------------------------------
	def __init__( self, sect, mapLabel ) :
		WholeArea.__init__( self, sect, mapLabel, False )
		self.subBoards = []													# 所有子区域
		areaSect = Language.openConfigSection( self.__cc_cfg_path )
		for subSect in areaSect.values() :
			self.subBoards.append( WorldArea.Board( subSect ) )
		Language.purgeConfig( self.__cc_cfg_path )

	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "WorldArea(%s)" % self.name


# --------------------------------------------------------------------
# implement map manager class
# --------------------------------------------------------------------
class MapMgr( Singleton ) :
	"""
	地图区域管理器
	"""
	__cc_cfg_path	= "config/client/bigmap/bigmaps.xml"	# 区域配置路径
	__cc_sky_config = "config/client/bigmap/bigmapsky.xml"
	
	def __init__( self ) :
		self.worldArea = None
		self.__wholeAreas = MapList()										# 所有全地图{ spaceLabel : map }
		self.__skyAreas = MapList()											# 天空地图
		self.__oldWholeArea = None
		self.__initialize()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		sect = Language.openConfigSection( self.__cc_cfg_path )
		for tag, mapSect in sect.items() :
			if tag == "world" : continue									# 区别开世界地图
			self.__wholeAreas[tag] = WholeArea( mapSect, tag, False )
		self.worldArea = WorldArea( sect["world"], "world" )				# 世界地图
		Language.purgeConfig( self.__cc_cfg_path )
		skySect = Language.openConfigSection( self.__cc_sky_config )
		for tag, mapSect in skySect.items() :
			self.__skyAreas[tag] = WholeArea( mapSect, tag, True )
		Language.purgeConfig( self.__cc_sky_config )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getWholeAreas( self ) :
		"""
		获取游戏中的所有全地图
		@rtype					: list of WholeArea
		@return					: 全地图列表
		"""
		return self.__wholeAreas.values()[:]

	def getAreas( self ) :
		"""
		获取所有的区域（包括全地图和区域地图）
		@rtype					: list of WholeArea / SubArea
		@return					: 所有区域列表
		"""
		areas = []
		for label, warea in self.__wholeAreas.items() :
			areas.append( warea )
			areas += warea.getSubAreas().values()
			if self.__skyAreas.has_key( label ):
				skyArea = self.__skyAreas[label]
				areas.append( skyArea )
				areas += skyArea.getSubAreas().values()
		return areas
	
	def getSkyAreas( self, mapLabel ):
		"""
		获取天空地图列表
		"""
		pass

	# -------------------------------------------------
	def getWholeArea( self, mapLabel, posY = 0 ) :
		"""
		通过区域标签名称获取对应的全地图
		@type			mapLabel : str
		@param			mapLabel : 地图标签
		@rtype					 : WholeArea
		@return					 : 如果存在则返回对应的全地图实例，否则返回 None
		"""
		skyArea = self.__skyAreas.get( mapLabel, None) 
		wholeArea = self.__wholeAreas.get( mapLabel, None )
		if skyArea: #存在天空地图
			if posY >= skyArea.ceilHeight:
				return skyArea
			if posY < skyArea.ceilHeight and \
			posY >= skyArea.floorHeight:
				if self.__oldWholeArea is None: #刚进入游戏可能在缓冲区，选择地面贴图
					return wholeArea
				else:
					return self.__oldWholeArea
			if wholeArea and posY < skyArea.floorHeight and \
			posY >= wholeArea.floorHeight:
				return wholeArea
		else:
		 	return wholeArea

	def getArea( self, mapLabel, pos ) :
		"""
		通过地图标签和某坐标，获取该位置所属的区域
		@type			mapLabel : str
		@param			mapLabel : 地图标签
		@type			pos		 : tuple
		@param			pos		 : 世界坐标（x，y，z）
		@rtype					 : WholeArea / SubArea
		@return					 : 如果该点在某子区域内则返回该子区域，否则返回 mapLabel 所对应的全区域中，如果 mapLabel 不对应任何场景，则返回 None
		"""
		wholeArea = self.getWholeArea( mapLabel, pos[1] )
		self.__oldWholeArea = wholeArea
		if wholeArea is None :
			return None
		area = wholeArea.getSubArea( pos )
		if area is not None :
			return area
		return wholeArea

	def getAreaViaName( self, spaceLabel, subName = "" ) :
		"""
		通过区域名称获取区域
		@type				spaceLabel : str
		@param				spaceLabel : 场景英文名称
		@type				subName	   : str
		@param				subName	   : 区域名称，如果为空，则获取场景区域
		@rtype						   : WholeArea/SubArea
		@return						   : 返回场景区域或子区域
		"""
		if subName == "" : return self.getWholeArea( spaceLabel )
		return self.getWholeArea( spaceLabel ).getSubAreas()[subName]
	
	def setAreaTimeOfDay( self, spaceLabel ):
		"""
		通过区域名称设置TimeOfDay功能
		@type				spaceLabel : str
		@return						   : None
		"""
		wholeArea = self.getWholeArea( spaceLabel )
		if wholeArea is None:return
		wholeArea.setTimeOfDay()
	
	def isHasSkyArea( self, spaceLabel ):
		"""
		通过spaceLabel查询是否有天空地图
		"""
		return spaceLabel in self.__skyAreas
	
	def getNPCs( self, spaceLabel, curSpaceLabel, isViewSky, dspflag, posY ):
		"""
		获取指定地图的npc信息，天空和地面的区分
		"""
		skyNPCs = {}
		if spaceLabel == "world": return skyNPCs
		npcs = rds.npcDatasMgr.getNPCs( spaceLabel, dspflag )
		wholeArea = self.getWholeArea( spaceLabel, posY )					#可能为地面和天空的
		groundArea = self.__wholeAreas.get( spaceLabel, None )
		for cls, npc in npcs.items():
			pos = npc.position
			if wholeArea.isSkyArea:												#在天空区域
				if curSpaceLabel == spaceLabel:								#在同一个地图
					if isViewSky:												# 查看的是天空地图
						if pos[1] > wholeArea.floorHeight and posY > wholeArea.floorHeight:
							skyNPCs[cls] = npc
					elif groundArea and pos[1] > groundArea.floorHeight and pos[1] <= wholeArea.floorHeight:
						skyNPCs[cls] = npc
				elif groundArea and pos[1] > groundArea.floorHeight and pos[1] <= wholeArea.floorHeight:
					skyNPCs[cls] = npc
			else:																#在地面
				if self.isHasSkyArea( spaceLabel ):								#有天空地图
					skyArea = self.__skyAreas.get( spaceLabel )
					if skyArea.floorHeight > pos[1] and pos[1] > wholeArea.floorHeight:
						skyNPCs[cls] = npc
				elif pos[1] > wholeArea.floorHeight:
					skyNPCs[cls] = npc
		return skyNPCs

# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
mapMgr = MapMgr()

