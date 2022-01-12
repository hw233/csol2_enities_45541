# -*- coding: gb18030 -*-
import BigWorld

import csdefine
import csconst
from bwdebug import INFO_MSG
from interface.CampActivityMgr import CampActivityMgr
from interface.CampTurnWarManager import CampTurnWarManager
from interface.CampYingXiongCopyMgr import CampYingXiongCopyMgr
from interface.CampFengHuoLianTianMgr import CampFengHuoLianTianMgr

class CampMgr( BigWorld.Base, CampActivityMgr, CampTurnWarManager, CampYingXiongCopyMgr, CampFengHuoLianTianMgr ):
	# ��Ӫ������
	def __init__( self ):
		BigWorld.Base.__init__( self )
		CampActivityMgr.__init__( self )
		CampTurnWarManager.__init__( self )
		CampYingXiongCopyMgr.__init__( self )
		CampFengHuoLianTianMgr.__init__( self )
		self.registerGlobally( "CampMgr", self._onRegisterManager )
		self.initData()
	
	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register CampMgr Fail!" )
			self.registerGlobally( "CampMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["CampMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("CampMgr Create Complete!")
			self.registerCrond()
	
	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		CampActivityMgr.registerCrond( self )
	
	def initData( self ):
		"""
		init global data
		"""
		BigWorld.globalData[ "CAMP_TAOISM_MORALE" ] = self.taoismMorale
		BigWorld.globalData[ "CAMP_DEMON_MORALE" ] = self.demonMorale
			
	def addMorale( self, camp, morale ):
		"""
		define method.
		�����Ӫʿ����morale����Ϊ����
		"""
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			self.taoismMorale += morale
			BigWorld.globalData[ "CAMP_TAOISM_MORALE" ] = self.taoismMorale
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			self.demonMorale += morale
			BigWorld.globalData[ "CAMP_DEMON_MORALE" ] = self.demonMorale
			
	def onTimer( self, timerID, cbID ):
		"""
		"""
		CampActivityMgr.onTimer( self, timerID, cbID )
		CampYingXiongCopyMgr.onTimer( self, timerID, cbID )
		CampFengHuoLianTianMgr.onTimer( self, timerID, cbID )
		