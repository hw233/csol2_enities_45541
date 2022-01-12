# -*- coding: gb18030 -*-
import BigWorld
import csdefine

from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
from Love3 import g_spaceCopyData

class SpaceViewerInterface:
	def __init__( self ):
		pass
	
	def spaveViewerIsViewer( self ):
		return self.queryTemp( "isViewer", False )
	
	def spaceViewerEnterState( self ):
		# define method
		# ���븱���۲���״̬
		actPet = self.pcg_getActPet()
		if actPet: actPet.entity.withdraw( csdefine.PET_WITHDRAW_GMWATCHER )
		self.effectStateInc( csdefine.EFFECT_STATE_WATCHER )
		self.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		self.setTemp( "watch_state", True )
	
	def spaceViewerLeaveState( self ):
		# define method
		# �˳������۲���״̬
		self.effectStateDec( csdefine.EFFECT_STATE_WATCHER )
		self.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		self.removeTemp( "watch_state" )
		self.removeTemp( "isViewer" )
	
	def spaceViewerReqSpaceInfos( self, spaceName ):
		# define method
		# ��ѯ����������Ϣ
		pass
	
	def spaceViewerEnter( self, spaceKey, spaceID ):
		# define method
		# ���븱��
		sMailBox = BigWorld.cellAppData["spaceID.%i" % spaceID]
		self.setTemp( "isViewer", True )
		birthInfos = self.__getSpaceBirthInfos( spaceKey )
		if not birthInfos:
			WARNING_MSG( "SpaceCopyInfos.xml file not has %s infos!!!"%spaceKey )
			return
			
		sMailBox.teleportEntity( birthInfos[ "birthPos" ], birthInfos[ "birthDirection" ], self.base )
	
	def __getSpaceBirthInfos( self, spaceKey ):
		return g_spaceCopyData[ spaceKey ]
	
	def spaceViewerReInfos( self, exposed, spaceKey ):
		# deinf method
		# ����һ����������Ϣ
		BigWorld.globalData[ "SpaceViewerMgr" ].requestSpaceInfos( spaceKey, self.base )