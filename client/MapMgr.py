# -*- coding: gb18030 -*-
#
# $Id: MapMgr.py,v 1.18 2008-08-27 09:06:37 huangyongwei Exp $

"""
This module implements the map manager

2007/12/25: writen by huangyongwei
2010.02.06: ���������࣬���������ȫ����̳��� BaseArea
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
# �������
# --------------------------------------------------------------------
class BaseArea( AbstractClass ) :
	__abstract_methods = set()

	def __init__( self, sect, wholeArea ) :
		self.__wholeArea = wholeArea									# ����������
		self.__name = sect.asString										# ��������
		self.__texture = sect.readString( "texture" )					# ������ͼ
		self.__ignore = sect.readBool( "ignore" )						# �Ƿ���ʾ��ͼ
		self.__autoSeekingPath = sect.readString( "autoSeekingPath" )	# �Զ�Ѱ··��
		self.__bgMusics = []											# ����ı�������
		self.__bgSounds = []											# ����ı�����Ч
		self.__effectFalg = Define.MAP_AREA_EFFECT_DEFAULT				# Ĭ��������Ч��
		if sect.has_key( "effectFlag" ):
			self.__effectFalg = sect.readInt( "effectFlag" )
		self.__ceilHeight = 99999.0											# ��ͨ��ͼĬ�ϸ߶ȣ�û������
		self.__floorHeight = -1000.0
		if sect.has_key( "ceilHeight" ):
			self.__ceilHeight = sect.readInt( "ceilHeight" )
		if sect.has_key( "floorHeight" ):
			self.__floorHeight = sect.readInt( "floorHeight" )
		self.worldBound_ = Rect()										# ������Ӿ��Σ��������У�
		self.mapBound_ = Rect()											# ������Ӿ��Σ�����ͼ�У�
		self.mapMapping_ = ( 0, 0 ), ( 0, 1 ), \
							( 1, 1 ), ( 1, 0 )							# ��ͼ��Ч mapping��ע��mapping �� UI �������⣬�������е㲻�ף��������������ȥÿ�ζ����㣩
		self.scales_ = ( 1, 1 )											# ��������ͼ�����ű���

		self.calcWorldBound_( sect )									# �����������е���Ӿ���
		self.calcMapBound_( sect )										# ������������ͼ�ϵ���Ӿ���
		self.__initBGMusics( sect )										# ��ʼ����������
		self.__initBGSounds( sect )										# ��ʼ��������Ч

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def spaceName( self ) :
		"""
		����������������������
		@type				: str
		"""
		if self.__wholeArea is self :			# ȫ��ͼ����Ϊ�Ǵ�����
			return self.__name
		return self.__wholeArea.spaceName

	@property
	def name( self ) :
		"""
		�������������
		@type				: str
		"""
		return self.__name

	@property
	def fullName( self ) :
		"""
		ȫ���ƣ�����������:������
		@type				: str
		"""
		if self.__wholeArea is self :
			return self.__name
		return "%s:%s" % ( self.__wholeArea.name, self.__name )

	@property
	def wholeArea( self ) :
		"""
		������ȫ��ͼ
		@type				: WholeArea
		"""
		return self.__wholeArea

	# ---------------------------------------
	@property
	def autoSeekingPath( self ) :
		"""
		�Զ�Ѱ··��
		@type				: str
		"""
		if self.__autoSeekingPath != "" :
			return self.__autoSeekingPath
		return self.__wholeArea.__autoSeekingPath

	# ---------------------------------------
	@property
	def texture( self ) :
		"""
		��ͼ·�������û����ͼ���򷵻�������������ͼ��
		@type				: str
		"""
		return self.__texture

	@property
	def ignore( self ) :
		"""
		�Ƿ���Ե�ͼ��ͼ������ʾ��ͼ��
		@type				: bool
		"""
		return self.__ignore

	# ---------------------------------------
	@property
	def worldBound( self ) :
		"""
		�����������ϵ���Ӿ���
		@type				: Rect
		"""
		return self.worldBound_

	@property
	def mapBound( self ) :
		"""
		��������ͼ�ϵ���Ӿ���
		@type				: Rect
		"""
		return self.mapBound_

	@property
	def mapMapping( self ) :
		"""
		��ͼ��ͼ�ǿհ������С
		ע��mapping �� UI �������⣬�������е㲻�ף��������������ȥÿ�ζ�����
		"""
		return self.mapMapping_

	@property
	def scales( self ) :
		"""
		ˮƽ����ֱ���ű���
		@type				: tuple
		"""
		return self.scales_

	@property
	def ceilHeight( self ):
		"""
		��ȡ�������������޸߶�
		@type			: int
		"""
		return self.__ceilHeight

	@property
	def floorHeight( self ):
		"""
		��ȡ�������������޸߶�
		@type			: int
		"""
		return self.__floorHeight

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initBGMusics( self, sect ) :
		"""
		��ʼ����������
		"""
		sect = sect["bgMusics"]
		if sect is None : return
		self.__bgMusics = sect.readStrings( "music" )

	def __initBGSounds( self, sect ):
		"""
		��ʼ��������Ч
		"""
		sect = sect["bgSounds"]
		if sect is None: return
		self.__bgSounds = sect.readStrings( "sound" )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def calcWorldBound_( self, sect ) :
		"""
		���㳡���������еľ���
		"""
		pass

	def calcMapBound_( self, sect ) :
		"""
		������������ͼ�ϵ���Ӿ���
		"""
		if self.__texture == "" : return
		mw, mh = sect.readVector2( "mapSize" )							# ��ͼ��ͼ�ǿհ�����С
		if mw == 0.0 or mh == 0.0 :
			raise TypeError( "error size of map '%s', or its space is not exist!" % self.__name )
		tw = 2 ** math.ceil( math.log( mw, 2 ) )						# ��ͼ��ͼ���
		th = 2 ** math.ceil( math.log( mh, 2 ) )						# ��ͼ��ͼ�߶�
		if sect.has_key( "effectiveRect" ) :
			ex, ey, ew, eh = sect.readVector4( "effectiveRect" )		# ��Ч����
			assert ( ex + ew <= mw ) and ( ey + eh <= mh ), \
				"effective rectangle of area '%s' is not valid!" % \
				sect.asWideString
			self.mapBound_.update( ( ex, ey ), ( ew, eh ) )

			# ������ͼ mapping
			left, right = ex / tw, ( ex + ew ) / tw
			top, bottom = ey / th, ( ey + eh ) / th
		else :
			# ������ͼ mapping
			self.mapBound_.updateSize( mw, mh )
			left, right = 0, mw / tw
			top, bottom = 0, mh / th
		self.mapMapping_ = ( left, top ), ( left, bottom ), \
						   ( right, bottom ), ( right, top )

		# �������
		scaleX = self.worldBound_.width / mw
		scaleY = self.worldBound_.height / mh
		self.scales_ = scaleX, scaleY


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isSubArea( self ) :
		"""
		�����Ƿ����������� isWholeArea ��ԣ�
		@rtype				: bool
		@return				: True
		"""
		return self.__wholeArea is not self

	def isWholeArea( self ) :
		"""
		�����Ƿ���ȫ��ͼ���� isSubArea ��ԣ�
		@rtype				: bool
		@return				: False
		"""
		return self.__wholeArea is self

	def hasTexture( self ) :
		"""
		�����Ƿ����Լ�����ͼ
		@param				: bool
		@return				: return True if i have my own texture
		"""
		return self.__texture != ""

	# -------------------------------------------------
	def getMusic( self ) :
		"""
		��ȡ�������ֵ�·��
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
		��ȡ������Ч��·��
		"""
		if len( self.__bgSounds ) > 0 :
			return random.choice( self.__bgSounds )
		if self.isWholeArea():
			return ""
		return self.__wholeArea.getBgSound()

	def getNPCs( self, dspflag ) :
		"""
		��ȡ�����ڵ����� NPC
		"""
		return []

	def getEffectFlag( self ):
		"""
		��ȡ��������Ч��
		"""
		return self.__effectFalg

	# -------------------------------------------------
	def isWorldPointIn( self, point ) :
		"""
		�ж�ĳ�����Ƿ���������
		@type			point : tuple
		@param			point : ��������
		@rtype				  : bool
		@return				  : ��������ĵ����������ϣ��򷵻� True
		"""
		return self.worldBound_.isPointIn( point )

	# -------------------------------------------------
	def worldPoint2TexturePoint( self, point ) :
		"""
		�������ϵ�ĳ�����ʵ����ת��Ϊ������ͼ�ϵ�����
		@type				point : tuple
		@param				point : point in the world ( x, z )
		@rtype					  : tuple
		@return					  : ��ͼ�ϵ�����
		"""
		wx, wy = point[:2]
		if len( point ) > 2 : wy = point[2]				# �������Χ���꣬���� z �����굱��ά�е� y ����
		scaleX, scaleY = self.scales_
		mx = ( wx - self.worldBound_.x ) / scaleX		# ӳ�䵽��ͼ�ϵ����
		my = ( self.worldBound_.maxY - wy ) / scaleY	# ӳ�䵽��ͼ�ϵĶ���
		x = mx - self.mapBound_.x						# �ڴ��ͼ�ϵ����
		y = my - self.mapBound_.y						# �ڴ��ͼ�ϵĶ���
		return Math.Vector2( x, y )

	def texturePoint2WorldPoint( self, point ) :
		"""
		�������ϵ�ĳ����ͼ�ϵ�����ת��Ϊ��������(��ʵ����)
		@type				point : tuple
		@param				point : point in texture ( x, y )
		@rtype					  : tuple
		@return					  : �������꣨��ʵ���꣩
		"""
		x, y = point
		mx = x + self.mapBound_.x
		my = y + self.mapBound_.y
		scaleX, scaleY = self.scales_
		wx = self.worldBound_.x + mx * scaleX
		wy = self.worldBound_.maxY - my * scaleY
		return Math.Vector2( wx, wy )


	# ----------------------------------------------------------------
	# ���󷽷�
	# ----------------------------------------------------------------
	__abstract_methods.add( calcWorldBound_ )
	__abstract_methods.add( getNPCs )


# --------------------------------------------------------------------
# implement area class
# --------------------------------------------------------------------
class SubArea( BaseArea ) :
	"""
	������
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
		����������Ӣ�ı��
		@type				: str
		"""
		return self.wholeArea.spaceLabel

	@property
	def spaceFolder( self ) :
		"""
		�����������ڵļ��ص㣨�����������ڵ��ļ������ƣ�
		@type				: str
		"""
		return self.wholeArea.spaceFolder

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def calcWorldBound_( self, sect ) :
		"""
		���㳡���������еľ���
		"""
		areaPoints = eval( sect.readString( "polygon" ) )
		self.__polygon.update( areaPoints )
		self.worldBound_ = self.__polygon.bound


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isWorldPointIn( self, point ) :
		"""
		�ж�ĳ�����Ƿ���������
		@type			point : tuple
		@param			point : ��������
		@rtype				  : bool
		@return				  : ��������ĵ����������ϣ��򷵻� True
		"""
		return self.__polygon.isPointIn( point )

	def getNPCs( self, dspflag ) :
		"""
		��ȡ�����ڵ�����
		"""
		return self.wholeArea.getNPCs( dspflag )


# --------------------------------------------------------------------
# implement map class
# --------------------------------------------------------------------
class WholeArea( BaseArea ) :
	"""
	������������������Ϊ��ȫ��ͼ����SubArea ������������
	"""
	__cc_space_path	 =  "universes/%s/space.settings"
	__cc_chunk_width = 100.0

	def __init__( self, sect, mapLabel, isSkyArea ) :
		self.__spaceLabel = mapLabel							# ����������Ӣ�ı�ǩ
		self.__spaceFolder = sect.readString( "spaceFolder" )
		BaseArea.__init__( self, sect, self )

		self.__areas = {}										# ���µ�����������
		self.isSkyArea	= isSkyArea							# �Ƿ�Ϊ�������
		
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
		��ʼ������
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
		���㳡���������еľ���
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
		��ǳ�����Ӣ�ı�ǩ
		@type				: str
		"""
		return self.__spaceLabel

	@property
	def spaceFolder( self ) :
		"""
		�������������ļ��е�·��
		@type				: str
		"""
		return self.__spaceFolder

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSubAreas( self ) :
		"""
		������е�������
		@rtype					: dict
		@return					: list of all my SubAreas
		"""
		return self.__areas

	def getSubArea( self, point ) :
		"""
		ͨ��ĳ���ȡ�����ڵ�������
		@type				point : tuple
		@param				point : ��������
		@rtype					  : SubArea
		@return					  : �������ĳ���������ϣ��򷵻ظ������򡣷��򷵻� None
		"""
		pos = 0, 0
		height = 0
		if len( point ) > 2 :
			pos = point[0], point[2]
		for area in self.__areas.itervalues() :
			if area.isWorldPointIn( pos ): # ��Ѱ��ͶӰ����area
				return area
		return None
	# -------------------------------------------------
	def getNPCs( self, dspflag ) :
		"""
		��ȡ�����е����� NPC
		@type				dspflag : int
		@param				dspflag : ���˱��
		@rtype						: dict
		@return						: npcs { npcID : NPCDatasMgr::NPC }
		"""
		return rds.npcDatasMgr.getNPCs( self.spaceLabel, dspflag )

	def setTimeOfDay( self ):
		"""
		���õ�ǰ�����TimeOfDay����
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
	# �����ͼ�Ӱ��
	# -------------------------------------------------
	class Board( object ) :
		"""
		�����ͼ�Ӱ��
		"""
		__slots__ = ( "_Board__nav", "_Board__area" , "pos", "texture", "size", "polygon" )
		def __init__( self, sect ) :
			self.pos = sect.readVector2( "pos" )							# ���λ��
			self.texture = sect.readString( "texture" )						# �����ͼ
			self.size = sect.readVector2( "size" )							# ����С
			verties = sect["polygon"].readVector2s( "item" )				# ��鶥��
			self.polygon = Polygon( verties )								# �������
			self.__nav = sect.asString.split( ":" )							# ���ָ������������
			if len( self.__nav ) == 1 : self.__nav.append( "" )
			self.__area = None

		@property
		def area( self ) :
			if self.__area is None :
				try :
					self.__area = mapMgr.getAreaViaName( *self.__nav )
				except :
					ERROR_MSG( "area '%s' is not exist!" % str( self.__nav ) )	# �Ӱ��ָ������򲻴���
			return self.__area


	# ----------------------------------------------------------------
	# initialize
	# ----------------------------------------------------------------
	def __init__( self, sect, mapLabel ) :
		WholeArea.__init__( self, sect, mapLabel, False )
		self.subBoards = []													# ����������
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
	��ͼ���������
	"""
	__cc_cfg_path	= "config/client/bigmap/bigmaps.xml"	# ��������·��
	__cc_sky_config = "config/client/bigmap/bigmapsky.xml"
	
	def __init__( self ) :
		self.worldArea = None
		self.__wholeAreas = MapList()										# ����ȫ��ͼ{ spaceLabel : map }
		self.__skyAreas = MapList()											# ��յ�ͼ
		self.__oldWholeArea = None
		self.__initialize()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		sect = Language.openConfigSection( self.__cc_cfg_path )
		for tag, mapSect in sect.items() :
			if tag == "world" : continue									# ���������ͼ
			self.__wholeAreas[tag] = WholeArea( mapSect, tag, False )
		self.worldArea = WorldArea( sect["world"], "world" )				# �����ͼ
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
		��ȡ��Ϸ�е�����ȫ��ͼ
		@rtype					: list of WholeArea
		@return					: ȫ��ͼ�б�
		"""
		return self.__wholeAreas.values()[:]

	def getAreas( self ) :
		"""
		��ȡ���е����򣨰���ȫ��ͼ�������ͼ��
		@rtype					: list of WholeArea / SubArea
		@return					: ���������б�
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
		��ȡ��յ�ͼ�б�
		"""
		pass

	# -------------------------------------------------
	def getWholeArea( self, mapLabel, posY = 0 ) :
		"""
		ͨ�������ǩ���ƻ�ȡ��Ӧ��ȫ��ͼ
		@type			mapLabel : str
		@param			mapLabel : ��ͼ��ǩ
		@rtype					 : WholeArea
		@return					 : ��������򷵻ض�Ӧ��ȫ��ͼʵ�������򷵻� None
		"""
		skyArea = self.__skyAreas.get( mapLabel, None) 
		wholeArea = self.__wholeAreas.get( mapLabel, None )
		if skyArea: #������յ�ͼ
			if posY >= skyArea.ceilHeight:
				return skyArea
			if posY < skyArea.ceilHeight and \
			posY >= skyArea.floorHeight:
				if self.__oldWholeArea is None: #�ս�����Ϸ�����ڻ�������ѡ�������ͼ
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
		ͨ����ͼ��ǩ��ĳ���꣬��ȡ��λ������������
		@type			mapLabel : str
		@param			mapLabel : ��ͼ��ǩ
		@type			pos		 : tuple
		@param			pos		 : �������꣨x��y��z��
		@rtype					 : WholeArea / SubArea
		@return					 : ����õ���ĳ���������򷵻ظ������򣬷��򷵻� mapLabel ����Ӧ��ȫ�����У���� mapLabel ����Ӧ�κγ������򷵻� None
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
		ͨ���������ƻ�ȡ����
		@type				spaceLabel : str
		@param				spaceLabel : ����Ӣ������
		@type				subName	   : str
		@param				subName	   : �������ƣ����Ϊ�գ����ȡ��������
		@rtype						   : WholeArea/SubArea
		@return						   : ���س��������������
		"""
		if subName == "" : return self.getWholeArea( spaceLabel )
		return self.getWholeArea( spaceLabel ).getSubAreas()[subName]
	
	def setAreaTimeOfDay( self, spaceLabel ):
		"""
		ͨ��������������TimeOfDay����
		@type				spaceLabel : str
		@return						   : None
		"""
		wholeArea = self.getWholeArea( spaceLabel )
		if wholeArea is None:return
		wholeArea.setTimeOfDay()
	
	def isHasSkyArea( self, spaceLabel ):
		"""
		ͨ��spaceLabel��ѯ�Ƿ�����յ�ͼ
		"""
		return spaceLabel in self.__skyAreas
	
	def getNPCs( self, spaceLabel, curSpaceLabel, isViewSky, dspflag, posY ):
		"""
		��ȡָ����ͼ��npc��Ϣ����պ͵��������
		"""
		skyNPCs = {}
		if spaceLabel == "world": return skyNPCs
		npcs = rds.npcDatasMgr.getNPCs( spaceLabel, dspflag )
		wholeArea = self.getWholeArea( spaceLabel, posY )					#����Ϊ�������յ�
		groundArea = self.__wholeAreas.get( spaceLabel, None )
		for cls, npc in npcs.items():
			pos = npc.position
			if wholeArea.isSkyArea:												#���������
				if curSpaceLabel == spaceLabel:								#��ͬһ����ͼ
					if isViewSky:												# �鿴������յ�ͼ
						if pos[1] > wholeArea.floorHeight and posY > wholeArea.floorHeight:
							skyNPCs[cls] = npc
					elif groundArea and pos[1] > groundArea.floorHeight and pos[1] <= wholeArea.floorHeight:
						skyNPCs[cls] = npc
				elif groundArea and pos[1] > groundArea.floorHeight and pos[1] <= wholeArea.floorHeight:
					skyNPCs[cls] = npc
			else:																#�ڵ���
				if self.isHasSkyArea( spaceLabel ):								#����յ�ͼ
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

