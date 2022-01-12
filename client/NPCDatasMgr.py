# -*- coding: gb18030 -*-
#
# $Id: NPCDatasMgr.py,v 1.23 2008-07-09 08:32:49 zhangyuxing Exp $

"""
���ڸ�client�ṩ������NPC������Ϣ�����꣬����...�����ԣ�
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
# ʵ�� NPC ��
# --------------------------------------------------------------------
class NPC :
	def __init__( self, npcID, refData, mgr ) :
		self.__refData = refData							# ���ﲻ�����������ԣ�ͨ������ָ��NpcsDatas����Դ������Ϊ NPC ̫�࣬�������Խ�ʡ�ռ�
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
		@param				: NPC className���� NPC ID
		"""
		return self.__npcID

	@property
	def name( self ) :
		"""
		@type				: str
		@param				: NPC ����
		"""
		return self.__refData[ "entityName" ]

	@property
	def nickname( self ) :
		"""
		@type				: str
		@param				: NPC�ļ��
		"""
		return self.__refData.get( "nickname", "" )

	@property
	def displayOnClient( self ) :
		"""
		@type				: str
		@param				: NPC ����
		"""
		return self.__refData["displayOnClient" ]

	@property
	def entityName( self ) :
		"""
		@type				: str
		@param				: NPC ����
		"""
		return self.__refData["entityName" ]

	@property
	def title( self ) :
		"""
		@type				: str
		@param				: NPC ͷ��
		"""
		return self.__refData[ "title" ]

	@property
	def position( self ) :
		"""
		@type				: Vector3
		@param				: NPC λ��
		"""
		return self.__mgr.getNPCPosition( self.__npcID )

	@property
	def quest_start( self ) :
		"""
		@type				: list
		@param				: NPC ���Է��ŵ�����
		"""
		return self.__refData["quests"][ "quest_start" ]

	@property
	def quest_end( self ) :
		"""
		@type				: list
		@param				: ������ NPC ���ύ������
		"""
		return self.__refData["quests"][ "quest_end" ]


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getName( self ) :
		"""
		@rtype				: str
		@return				: NPC ����
		"""
		return self.__refData[ "entityName" ]


	def getPosition( self, spaceLabel ) :
		"""
		@type				: Vector3
		@param				: NPC λ��
		"""
		return self.__mgr.getNPCPosition( self.__npcID, spaceLabel )


# --------------------------------------------------------------------
# ʵ�� NPC ������
# --------------------------------------------------------------------
class NPCDatasMgr :
	__inst			= None

	def __init__( self ) :
		assert NPCDatasMgr.__inst is None
		self.__npcsData = NpcDatasSource.Datas
		self.__npcPosData= NPCDatas.Datas
		self.__spaceNames = {}					# ��������
		self.__npcSigns = NPCSigns.Datas					# NPC����ͼ��
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
		��ȡ���� NPC �����ļ��ֵ�����
		@rtype					: list
		@return					: ���� NPC �����ļ��� Section
		"""
		return self.__npcsData[npcID]

	def getNPC( self, npcID ) :
		"""
		���� npcID ��ȡ NPC
		@type			npcID : str
		@param			nocID : NPC ID
		@rtype				  : NPC
		@return				  : �� module ��ʼ���� NPC ʵ��
		"""
		if self.__npcsData.has_key( npcID ):
			return NPC( npcID, self.__npcsData[npcID], self )
		else:
			return None

	def getNPCs( self, spaceLabel = None, displayFlag = 255 ) :
		"""
		��ȡ���� NPC
		displayFlag:
			00000001����ʾ�ڴ��ͼ��
			00000010����ʾ�ĵȼ���ʾ��
			00000100����ʾ�ڴ��ͼ�� NPC ����������
		"""
		npcs = {}
		if spaceLabel is None :												# ���û���ṩ space ��ǩ
			for id, npcData in self.__npcsData.iteritems() :					# ���ȡ���� space �µ� NPC
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
		ͨ�������ǩ�� NPC ID ��ȡ NPC ��λ��
		@type				npcID	   : str
		@param				npcID	   : npc ID
		@type				spaceLabel : str
		@param				spaceLabel : �����ǩ, ���Ϊ None��������ҵ�ǰ��������
		@rtype						   : Vector3
		"""
		try:
			return Math.Vector3( self.__npcPosData[ spaceLabel ][ npcID ][ "position" ] ) #�Ȱ���spaceLabel����
		except KeyError, key:
			#����space���ң� PS��npcID������spaces������Ψһ��
			for spcNpcDat in self.__npcPosData.itervalues( ):
				try:
					return Math.Vector3( spcNpcDat[ npcID ][ "position" ] )
				except:
					continue
		except:
			return Math.Vector3( 0,0,0 )

	def getNPCSpaceLabel( self, npcID ) :
		"""
		ͨ�������ǩ�� NPC ID ��ȡ NPC ��λ��
		@type				npcID	   : str
		@param				npcID	   : npc ID
		@type				spaceLabel : str
		@param				spaceLabel : �����ǩ, ���Ϊ None��������ҵ�ǰ��������
		@rtype						   : Vector2   (str(spaceLabel), str(spaceName))
		"""
		for spaceLable in self.__npcPosData:
			if self.__npcPosData[ spaceLable ].has_key( npcID ):
				npcPosition = self.__npcPosData[ spaceLable ][ npcID ]["position"]
				for area in mapMgr.getWholeAreas():
					if area.spaceLabel == spaceLable:
						subArea = area.getSubArea( npcPosition )	# ͨ��ĳ���ȡ�����ڵ�������
						if subArea is not None:
							return ( spaceLable, subArea.spaceName + "-" + subArea.name)
						else:
							return ( spaceLable, area.name)
		return ( "", "" )

	def getNPCSignFile( self, npcID ) :
		"""
		��ȡNPC����ͼ��Ĵ��·��
		@param		npcID	:	NPC className
		@type		npcID	:	str
		@rtype				:	str
		"""
		return self.__npcSigns.get( npcID, "" )

	def getMonsters( self, minLevel, maxLevel, dsplayFlag = 255 ) :
		"""
		���ú����Ǵ� Helper.py �ƶ����˴��ģ�
		��ȡָ���ȼ�������ҿɹ��������й���( ���ڹ������ݱȽ��Ӵ�����ÿ��ʹ�õ�ʱ����ȥ�� section )
		ע������������ȼ������磺���� minLevel = 10, maxLevel = 11 ���ȡ���� 10��11 �������пɹ�������
			��� minLevel == maxLevel ��ֻ��ȡһ���ȼ��Ŀɹ�������
		@type				minLevel   : int
		@param				minLevel   : ��С�ȼ�
		@type				maxLevel   : int
		@param				maxLevel   : ���ȼ�
		@type				dsplayFlag : int
		@param				dsplayFlag : ��ʾ�ڻ�ȡ������ʾ�Ĺ��Ĭ�� 255 ��ʾȫ����1 ��ʾ��С��ͼ��2 ��ʾ��ʾ�ڵȼ���ʾ�Ĺ���
		@rtype						   : dict
		@return						   : ĳ�ȼ����µ����й���( һ����ʱ�Ĺ�����ʵ���б� ){ level1 : [monster, ����], leve2 : [monster, ����], ���� }
									   : monster.id : ���� ID��monster.name : ��������
		"""
		monsters = {}
		for l in xrange( minLevel, maxLevel + 1 ) : monsters[l] = []

		class Monster( object ) : 										# ��ʱ������
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
