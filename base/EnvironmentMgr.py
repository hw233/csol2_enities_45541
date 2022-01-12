# -*- coding: gb18030 -*-
#
#
import BigWorld
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

"""
����ĳ����ؼ���: new_year_env
����ĳ����ؼ���: mid_autumn
"""

class EnvironmentMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.registerGlobally( "EnvironmentMgr", self._onRegisterManager )
		self.envMBGroup = {}			#such as { 1 :[ envMB01, envMB02, ], 2 : [], ... }
		self.currAcitivitys = set([])


	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register EnvironmentMgr Fail!" )
			self.registerGlobally( "EnvironmentMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["EnvironmentMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("EnvironmentMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
					  	"newYear_env_start" : "onNewYearEnvShowStart",
						"newYear_env_end" :	"onNewYearEnvShowEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		crond.addAutoStartScheme( "newYear_env_start", self, "onNewYearEnvShowStart" )


	def addToMgr( self, envMB, festival_key ):
		"""
		define method
		"""
		if not festival_key in self.envMBGroup:
			self.envMBGroup[festival_key] = []
		
		self.envMBGroup[festival_key].append( envMB )
		
		if festival_key in self.currAcitivitys:
			envMB.cell.setVisible( True )
	
	def onNewYearEnvShowStart( self ):
		"""
		��ʾ���곡�����
		"""
		for i in self.envMBGroup["new_year_env"]:
			i.createCellEnviObject()
		self.currAcitivitys.add( "new_year_env" )
			
			
	
	def onNewYearEnvShowEnd( self ):
		"""
		���ع��곡�����
		"""
		for i in self.envMBGroup["new_year_env"]:
			i.destroyCellEnviObject()
		
		self.currAcitivitys.remove( "new_year_env" )