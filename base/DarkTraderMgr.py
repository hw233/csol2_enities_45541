# -*- coding: gb18030 -*-
#
# Ͷ�����˹����� 2008-12-25 SongPeifang
#
import Love3
import csdefine
import BigWorld
import cschannel_msgs
import random
import Math
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from Love3 import g_DarkTraderDatas
from csconst import g_maps_info
from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objects = GameObjectFactory.instance()


DARK_TRADER_BEGIN 	= 0					#Ͷ�����˿�ʼ�
DARK_TRADER_RELOAD = 1					#Ͷ�����˽����

class DarkTraderMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self._npcClassName = None

		# Ͷ�����˵�className Ŀǰֻ����һ��Ͷ�����ˣ����ǲ��ų��պ�߻������������˵Ŀ���
		if g_DarkTraderDatas._DarkTraderDatas == None or len( g_DarkTraderDatas._DarkTraderDatas ) == 0:
			ERROR_MSG( "Ͷ�����˳�����Ʒ���ñ����ô�����ȡ����" )
		else:
			# Ͷ�����˵�className
			self._npcClassName = g_DarkTraderDatas._DarkTraderDatas.keys()[0]
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "DarkTraderMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register DarkTraderMgr Fail!" )
			self.registerGlobally( "DarkTraderMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["DarkTraderMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("DarkTraderMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"DarkTraderMgr_createNPC" : "onStart",
						"DarkTraderMgr_end" : "onEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def onStart( self ):
		"""
		define method.
		Ͷ������ˢ��
		"""
		npcSpaceName = self.genDarkTraderMap()			# �������Ͷ�����˿���ˢ���ĵ�ͼspaceName
		if not g_maps_info.has_key( npcSpaceName ):
			ERROR_MSG( "���е�ͼ��Ϣ���ɴ��󣬵�ͼ�б��ѹ��ڣ�" )
			return
		npcSpaceNameCh = g_maps_info[ npcSpaceName ]	# ��ͼ�����������硰������
		npcPosition = self.genDarkTraderPosition( npcSpaceName )	# ��������������
		npcDirection = ( 0, 0, 0 )
		space = g_objects.getObject( npcSpaceName )
		maxLine = 1
		if hasattr( space, "maxLine" ):
			maxLine = space.maxLine

		# ������ڶ����ߣ� ÿ���߶�ˢ
		for line in xrange( maxLine ):
			BigWorld.globalData["SpaceManager"].createNPCObjectFormBase( npcSpaceName, \
																		self._npcClassName, \
																		npcPosition, \
																		npcDirection, \
																		{ "_lineNumber_" : line + 1 } )

		g_DarkTraderDatas.genCollectGoodID( self._npcClassName, npcSpaceName )	# ���ݵ�ͼ����Ͷ�����˴˴��չ�����Ʒ��
		npcCurrGoodName = g_DarkTraderDatas._currentGoodName		# Ŀ����֪ͨȫ��������Ͷ�������չ�����Ʒ
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_HSSR_TRADER_SITE_NOTIFY % ( npcSpaceNameCh, npcPosition[0], npcPosition[2], npcCurrGoodName ), [] )
		INFO_MSG( "DarkTraderMgr.", "start", "" )


	def onEnd( self ):
		"""
		define method
		"""
		INFO_MSG( "DarkTraderMgr.", "end", "" )

	def genDarkTraderMap( self ):
		"""
		����Ͷ������NPC�ĵ�ͼ
		"""
		dark_trader_maps = g_DarkTraderDatas._DarkTraderMaps
		index = random.randint( 0, len( dark_trader_maps ) - 1 )
		spaceName = dark_trader_maps[index]
		return spaceName

	def genDarkTraderPosition( self, spaceName ):
		"""
		����Ͷ�����˵�λ������
		"""
		# �������������δȷ����Ҫ��߻����ۣ���ʱд������
		x = random.randint( -3,3 )
		y = 3	# ���϶�����3�ױ����������
		z = random.randint( -3,3 )
		npcPosition = (0,0,0)
		posList = g_DarkTraderDatas._DarkTraderPositions[spaceName]
		index = random.randint( 0,len( posList ) - 1 )
		npcPosition = posList[index] + Math.Vector3( x, y, z )
		return npcPosition