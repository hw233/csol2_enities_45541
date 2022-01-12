# -*- coding: gb18030 -*-
#
# WX������ 2009-10-07 SongPeifang
#

from csconst import g_maps_info
from bwdebug import *
from CrondDatas import CrondDatas
import BigWorld
import Love3

g_CrondDatas = CrondDatas.instance()


class WXActivityMgr:

	def __init__(self):
		"""
		������������ħ���������ˡ�����ʦ�����ش󽫡�Х���
		�Ļ��������
		"""
		#self.noticeMsg 		= ""
		#self.startMsg 			= ""
		#self.endMgs 			= ""
		#self.globalFlagKey		= ""
		#self.managerName 		= ""
		#self.crondNoticeKey	= ""
		#self.crondStartKey		= ""
		#self.crondEndKey		= ""
		#self._monsClassName	= ""
		#self.spaceName			= ""
		#self.position			= ( 0, 0, 0 )
		#self.direction			= ( 0, 0, 0 )
		self.initActivity()
		self.registerGlobally( self.managerName, self._onRegisterManager )


	def initActivity( self ):
		"""
		"""
		BigWorld.globalData[ self.globalFlagKey ] = False


	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register %s Fail!" % self.managerName )
			self.registerGlobally( self.managerName, self._onRegisterManager )
		else:
			BigWorld.globalData[self.managerName] = self		# ע�ᵽ���еķ�������
			INFO_MSG( "%s Create Complete!" % self.managerName )
			self.registerCrond()


	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
					  	self.crondNoticeKey : "onStartNotice",
					  	self.crondStartKey : "onStart",
						self.crondEndKey :	"onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )


	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		if self.noticeMsg != "":
			Love3.g_baseApp.anonymityBroadcast( self.noticeMsg, [] )


	def onStart( self ):
		"""
		define method.
		����ˢ��
		"""
		self.spawnMonster()


	def spawnMonster( self ):
		"""
		"""
		if not g_maps_info.has_key( self.spaceName ):
			ERROR_MSG( "%s��ͼ��Ϣ���ɴ��󣬻��ߵ�ͼ�б��ѹ��ڣ�" % self.managerName )
			return
		npcSpaceNameCh = g_maps_info[ self.spaceName ]	# ��ͼ�����������硰������
		if not BigWorld.globalData.has_key( self.globalFlagKey ) or BigWorld.globalData[self.globalFlagKey] == False:
			BigWorld.globalData["SpaceManager"].createCellNPCObjectFormBase( self.spaceName, self._monsClassName, self.position, self.direction, {"spawnPos" : self.position} )
		BigWorld.globalData[ self.globalFlagKey ] = True
		if self.startMsg != "":
			Love3.g_baseApp.anonymityBroadcast( self.startMsg, [] )


	def onEnd( self ):
		"""
		define method
		"""
		if self.endMgs != "":
			Love3.g_baseApp.anonymityBroadcast( self.endMgs, [] )
		
		BigWorld.globalData[ self.globalFlagKey ] = False