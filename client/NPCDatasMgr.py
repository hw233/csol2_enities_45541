# -*- coding: gb18030 -*-
#
# $Id: NPCDatasMgr.py,v 1.23 2008-07-09 08:32:49 zhangyuxing Exp $

"""
用于给client提供服务器NPC配置信息（坐标，任务...等属性）
2008/03/08 : writen by zhangyuxing( named: NpcProperty )
2008/03/24 : renamed to 'NPCDatasMgr' by huangyongwei
"""

import Math
import BigWorld
from bwdebug import *
from MapMgr import mapMgr
from config.client import NpcDatasSource
from config.NPCDatas import NPCDatas
from config.client import NPCSigns


# --------------------------------------------------------------------
# 实现 NPC 类
# --------------------------------------------------------------------
class NPC :
	def __init__( self, npcID, refData, mgr ) :
		self.__refData = refData							# 这里不保存所有属性，通过引用指向NpcsDatas数据源，是因为 NPC 太多，这样可以节省空间
		self.__mgr = mgr
		self.__npcID = npcID


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def id( self ) :
		"""
		@type				: str
		@param				: NPC ID
		"""
		return self.__npcID

	@property
	def className( self ) :
		"""
		@type				: str
		@param				: NPC className，即 NPC ID
		"""
		return self.__npcID

	@property
	def name( self ) :
		"""
		@type				: str
		@param				: NPC 名字
		"""
		return self.__refData[ "entityName" ]

	@property
	def nickname( self ) :
		"""
		@type				: str
		@param				: NPC的简称
		"""
		return self.__refData.get( "nickname", "" )

	@property
	def displayOnClient( self ) :
		"""
		@type				: str
		@param				: NPC 名字
		"""
		return self.__refData["displayOnClient" ]

	@property
	def entityName( self ) :
		"""
		@type				: str
		@param				: NPC 名字
		"""
		return self.__refData["entityName" ]

	@property
	def title( self ) :
		"""
		@type				: str
		@param				: NPC 头衔
		"""
		return self.__refData[ "title" ]

	@property
	def position( self ) :
		"""
		@type				: Vector3
		@param				: NPC 位置
		"""
		return self.__mgr.getNPCPosition( self.__npcID )

	@property
	def quest_start( self ) :
		"""
		@type				: list
		@param				: NPC 可以发放的任务
		"""
		return self.__refData["quests"][ "quest_start" ]

	@property
	def quest_end( self ) :
		"""
		@type				: list
		@param				: 可以在 NPC 上提交的任务
		"""
		return self.__refData["quests"][ "quest_end" ]


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getName( self ) :
		"""
		@rtype				: str
		@return				: NPC 名字
		"""
		return self.__refData[ "entityName" ]


	def getPosition( self, spaceLabel ) :
		"""
		@type				: Vector3
		@param				: NPC 位置
		"""
		return self.__mgr.getNPCPosition( self.__npcID, spaceLabel )


# --------------------------------------------------------------------
# 实现 NPC 管理类
# --------------------------------------------------------------------
class NPCDatasMgr :
	__inst			= None

	def __init__( self ) :
		assert NPCDatasMgr.__inst is None
		self.__npcsData = NpcDatasSource.Datas
		self.__npcPosData= NPCDatas.Datas
		self.__spaceNames = {}					# 区域名称
		self.__npcSigns = NPCSigns.Datas					# NPC功能图标
		self.__initialize()


	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = NPCDatasMgr()
		return SELF.__inst


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		for area in mapMgr.getWholeAreas() :
			self.__spaceNames[area.spaceLabel] = area.name


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getNPCData( self, npcID ) :
		"""
		获取所有 NPC 配置文件字典数据
		@rtype					: list
		@return					: 所有 NPC 配置文件的 Section
		"""
		return self.__npcsData[npcID]

	def getNPC( self, npcID ) :
		"""
		根据 npcID 获取 NPC
		@type			npcID : str
		@param			nocID : NPC ID
		@rtype				  : NPC
		@return				  : 该 module 开始处的 NPC 实例
		"""
		if self.__npcsData.has_key( npcID ):
			return NPC( npcID, self.__npcsData[npcID], self )
		else:
			return None

	def getNPCs( self, spaceLabel = None, displayFlag = 255 ) :
		"""
		获取所有 NPC
		displayFlag:
			00000001：显示在大地图上
			00000010：显示的等级提示上
			00000100：显示在大地图的 NPC 搜索窗口上
		"""
		npcs = {}
		if spaceLabel is None :												# 如果没有提供 space 标签
			for id, npcData in self.__npcsData.iteritems() :					# 则获取所有 space 下的 NPC
				if npcData[ "displayOnClient" ] & displayFlag :
					npcs[id] = NPC( id, npcData, self )
		elif self.__npcPosData.has_key( spaceLabel ):
			for npcID in self.__npcPosData[ spaceLabel ]:
				if not self.__npcsData.has_key( npcID ):
					continue
				npcData = self.__npcsData[ npcID ]
				if npcData[ "displayOnClient"]  & displayFlag:
					npcs[npcID] = NPC( npcID, npcData, self )
		return npcs

	def getNPCPosition( self, npcID, spaceLabel = None ) :
		"""
		通过区域标签和 NPC ID 获取 NPC 的位置
		@type				npcID	   : str
		@param				npcID	   : npc ID
		@type				spaceLabel : str
		@param				spaceLabel : 区域标签, 如果为 None，则在玩家当前所属区域
		@rtype						   : Vector3
		"""
		try:
			return Math.Vector3( self.__npcPosData[ spaceLabel ][ npcID ][ "position" ] ) #先按照spaceLabel查找
		except KeyError, key:
			#所有space查找， PS：npcID在所有spaces里面是唯一的
			for spcNpcDat in self.__npcPosData.itervalues( ):
				try:
					return Math.Vector3( spcNpcDat[ npcID ][ "position" ] )
				except:
					continue
		except:
			return Math.Vector3( 0,0,0 )

	def getNPCSpaceLabel( self, npcID ) :
		"""
		通过区域标签和 NPC ID 获取 NPC 的位置
		@type				npcID	   : str
		@param				npcID	   : npc ID
		@type				spaceLabel : str
		@param				spaceLabel : 区域标签, 如果为 None，则在玩家当前所属区域
		@rtype						   : Vector2   (str(spaceLabel), str(spaceName))
		"""
		for spaceLable in self.__npcPosData:
			if self.__npcPosData[ spaceLable ].has_key( npcID ):
				npcPosition = self.__npcPosData[ spaceLable ][ npcID ]["position"]
				for area in mapMgr.getWholeAreas():
					if area.spaceLabel == spaceLable:
						subArea = area.getSubArea( npcPosition )	# 通过某点获取它所在的子区域
						if subArea is not None:
							return ( spaceLable, subArea.spaceName + "-" + subArea.name)
						else:
							return ( spaceLable, area.name)
		return ( "", "" )

	def getNPCSignFile( self, npcID ) :
		"""
		获取NPC功能图标的存放路径
		@param		npcID	:	NPC className
		@type		npcID	:	str
		@rtype				:	str
		"""
		return self.__npcSigns.get( npcID, "" )

	def getMonsters( self, minLevel, maxLevel, dsplayFlag = 255 ) :
		"""
		（该函数是从 Helper.py 移动到此处的）
		获取指定等级段下玩家可攻击的所有怪物( 由于怪物数据比较庞大，所以每次使用的时候，再去读 section )
		注：结果包括最大等级，例如：倘若 minLevel = 10, maxLevel = 11 则获取的是 10、11 级的所有可攻击怪物
			如果 minLevel == maxLevel 则只获取一个等级的可攻击怪物
		@type				minLevel   : int
		@param				minLevel   : 最小等级
		@type				maxLevel   : int
		@param				maxLevel   : 最大等级
		@type				dsplayFlag : int
		@param				dsplayFlag : 表示在获取在哪显示的怪物，默认 255 表示全部，1 表示在小地图，2 表示显示在等级提示的怪物
		@rtype						   : dict
		@return						   : 某等级段下的所有怪物( 一个临时的怪物类实例列表 ){ level1 : [monster, ……], leve2 : [monster, ……], …… }
									   : monster.id : 怪物 ID，monster.name : 怪物名称
		"""
		monsters = {}
		for l in xrange( minLevel, maxLevel + 1 ) : monsters[l] = []

		class Monster( object ) : 										# 临时怪物类
			__slots__ = ["level","id", "name", "level", "area", "position"]
			def __init__( self, id, dat ) :
				self.id = id
				self.name = dat['entityName']
				self.level = dat['level']
				self.area = self.getArea()
				self.position = self.getPosition()
			getArea = lambda self : npcDatasMgr.getNPCSpaceLabel( self.id )[1]
			getPosition = lambda self : npcDatasMgr.getNPCPosition( self.id )

		def flagVerify( monsterID ) :
			monster = npcDatasMgr.getNPC( monsterID )
			if monster:
				return monster.displayOnClient & dsplayFlag
			return False

		for id, dat in self.__npcsData.iteritems():
			level = dat['level']
			if level >= minLevel and level <= maxLevel:
				isShow = (dat['displayOnClient'] & dsplayFlag)
				if level != 0 and isShow:
					if Monster( id , dat ).area == "": continue
					monsters[level].append( Monster( id, dat ) )
		return monsters


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
npcDatasMgr = NPCDatasMgr.instance()
