# -*- coding: gb18030 -*-

# ------------------------------------------------
# from common
import csdefine
import Language
from SmartImport import smartImport
from bwdebug import *
# ------------------------------------------------
# from cell
import Resource.CopyStage.CopyEvent.CopyStageEvent as CopyStageEvent
import Resource.CopyStage.CopyStageBase as CopyStageBase

# ------------------------------------------------

class CopyStageData_Action:
	"""
	�����ؿ�����-��Ϊ������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert CopyStageData_Action._instance is None
		# key(Action id) ��value (Mod, subclass of CopyStageAction)
		self._CopyStageDatas = {}
		CopyStageData_Action._instance = self
	
	def load( self, configPath ):
		"""
		���������ļ�
		"""
		sect = Language.openConfigSection( configPath )
		assert sect is not None, "open %s false." % configPath
		
		for childSect in sect.values():
			id = childSect["id"].asInt
			scriptName = childSect["scriptName"].asString
			try:
				CopyStageMod = smartImport( "Resource.CopyStage." + scriptName )
			except ImportError, err:
				ERROR_MSG( "%s, id: %i."%( err, id ) )
				continue
			assert not self._CopyStageDatas.has_key( id ), "id %i scriptName: %s is exist already in. reading file %s" % ( id, scriptName, childSect.asString )
			self._CopyStageDatas[id] = CopyStageMod
		# �������
		Language.purgeConfig( configPath )
	
	def __getitem__( self, key ):
		"""
		ȡ��actionʵ��
		"""
		assert key in self._CopyStageDatas, "CopyStageAction %i not find!" % key
		
		return self._CopyStageDatas[key]
	
	def has( self, key ):
		"""
		"""
		return key in self._CopyStageDatas
	
	@staticmethod
	def instance():
		"""
		"""
		if CopyStageData_Action._instance is None:
			CopyStageData_Action._instance = CopyStageData_Action()
		return CopyStageData_Action._instance

class CopyStageData_Condition:
	"""
	�����ؿ�����-����������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert CopyStageData_Condition._instance is None
		# key(Condition id) ��value (Mod, subclass of CopyStageCondition)
		self._CopyStageDatas = {}
		CopyStageData_Condition._instance = self
	
	def load( self, configPath ):
		"""
		���������ļ�
		"""
		sect = Language.openConfigSection( configPath )
		assert sect is not None, "open %s false." % configPath
		
		for childSect in sect.values():
			id = childSect["id"].asInt
			scriptName = childSect["scriptName"].asString
			try:
				CopyStageMod = smartImport( "Resource.CopyStage." + scriptName )
			except Exception, errstr:
				assert False, "Load CopyStageConditions %s, is error! err:%s" % ( "Resource.CopyStage." + scriptName, errstr )
			assert not self._CopyStageDatas.has_key( id ), "id %i is exist already in. reading file %s" % ( id, childSect.asString )
			self._CopyStageDatas[id] = CopyStageMod
		# �������
		Language.purgeConfig( configPath )
	
	def __getitem__( self, key ):
		"""
		ȡ��conditionʵ��
		"""
		assert key in self._CopyStageDatas, "CopyStageCondition %i not find!" % key
		
		return self._CopyStageDatas[key]
	
	def has( self, key ):
		"""
		"""
		return key in self._CopyStageDatas
	
	@staticmethod
	def instance():
		"""
		"""
		if CopyStageData_Condition._instance is None:
			CopyStageData_Condition._instance = CopyStageData_Condition()
		return CopyStageData_Condition._instance

def copyStageAction_instance():
	return CopyStageData_Action.instance()
def copyStageConditon_instance():
	return CopyStageData_Condition.instance()

