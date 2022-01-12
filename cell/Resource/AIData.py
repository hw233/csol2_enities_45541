# -*- coding: gb18030 -*-

# $Id: AIData.py,v 1.5 2008-05-17 11:52:44 huangyongwei Exp $

# ------------------------------------------------
# from engine
import Language
from bwdebug import *
# ------------------------------------------------
# from common
import csdefine
from SmartImport import smartImport

# ------------------------------------------------

class AIData_Action:
	"""
	AI动作配置加载类
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert AIData_Action._instance is None
		# key(AI id) ：value (instance of AIAction)
		self._AIDatas = {}
		AIData_Action._instance = self

	def load( self, configPath ):
		"""
		加载AI配置
		"""
		sect = Language.openConfigSection( configPath )
		assert sect is not None, "open %s false." % configPath

		for childSect in sect.values():
			id = childSect["id"].asInt
			scriptName = childSect["scriptName"].asString
			try:
				AIMod = smartImport( "Resource.AI." + scriptName )
			except ImportError, err:
				ERROR_MSG( "%s, id: %i."%( err, id ) )
				continue
			assert not self._AIDatas.has_key( id ), "id %i scriptName: %s is exist already in. reading file %s" % ( id, scriptName, childSect.asString )
			self._AIDatas[id] = AIMod
		# 清除缓冲
		Language.purgeConfig( configPath )

	def __getitem__( self, key ):
		"""
		取得AI实例
		"""
		assert key in self._AIDatas, "AIAction %i not find!" % key
			
		return self._AIDatas[key]

	def has( self, AIkey ):
		"""
		"""
		return AIkey in self._AIDatas

	@staticmethod
	def instance():
		"""
		"""
		if AIData_Action._instance is None:
			AIData_Action._instance = AIData_Action()
		return AIData_Action._instance

class AIData_Condition:
	"""
	AI条件配置加载类
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert AIData_Condition._instance is None
		# key(AI id) ：value (instance of AIAction)
		self._AIDatas = {}
		AIData_Condition._instance = self

	def load( self, configPath ):
		"""
		加载AI配置
		"""
		sect = Language.openConfigSection( configPath )
		assert sect is not None, "open %s false." % configPath

		for childSect in sect.values():
			id = childSect["id"].asInt
			scriptName = childSect["scriptName"].asString
			try:
				AIMod = smartImport( "Resource.AI." + scriptName )
			except Exception, errstr:
				assert False, "Load AIConditions %s, is error! err:%s" % ( "Resource.AI." + scriptName, errstr )
			assert not self._AIDatas.has_key( id ), "id %i is exist already in. reading file %s" % ( id, childSect.asString )
			self._AIDatas[id] = AIMod
		# 清除缓冲
		Language.purgeConfig( configPath )

	def __getitem__( self, key ):
		"""
		取得AI实例
		"""
		assert key in self._AIDatas, "AICondition %i not find!" % key
		
		return self._AIDatas[key]

	def has( self, AIkey ):
		"""
		"""
		return AIkey in self._AIDatas

	@staticmethod
	def instance():
		"""
		"""
		if AIData_Condition._instance is None:
			AIData_Condition._instance = AIData_Condition()
		return AIData_Condition._instance

class AIData_Template:
	"""
	AI模板配置加载类
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert AIData_Template._instance is None
		# key(AI id) ：value (instance of AIAction)
		self._AIDatas = {}
		AIData_Template._instance = self

	def load( self, configPath ):
		"""
		加载AI配置
		"""
		sect = Language.openConfigSection( configPath )
		assert sect is not None, "open %s false." % configPath

		for childSect in sect.values():
			id = childSect["id"].asInt
			scriptName = childSect["scriptName"].asString
			name = childSect["name"].asString
			try:
				AIMod = smartImport( "Resource.AI." + scriptName )
			except ImportError, err:
				EXCEHOOK_MSG( "Loading AITemplate[%i] ... %s, its class is not exist!" % ( id, "Resource.AI." + scriptName ) )
				continue
			assert not self._AIDatas.has_key( id ), "id %i is exist already in. reading file %s" % ( id, childSect.asString )

			conditions = []
			actions = []
			self._AIDatas[id] = { "name" : name, "script" : AIMod, "conditions" : conditions, "actions" : actions }
			cndmod = aiConditon_instance()
			for cndsec in childSect["Condition"].values():
				conditions.append( cndmod[ cndsec.asInt ] )
			actmod = aiAction_instance()
			for actsec in childSect["Action"].values():
				try:
					actions.append( actmod[ actsec.asInt ] )
				except:
					EXCEHOOK_MSG()
		# 清除缓冲
		Language.purgeConfig( configPath )

	def __getitem__( self, key ):
		"""
		取得AI实例
		"""
		assert key in self._AIDatas, "AITemplate %i not find!" % key
		
		return self._AIDatas[key]

	def has( self, AIkey ):
		"""
		"""
		return AIkey in self._AIDatas

	@staticmethod
	def instance():
		"""
		"""
		if AIData_Template._instance is None:
			AIData_Template._instance = AIData_Template()
		return AIData_Template._instance

class AIData:
	"""
	AI模板配置加载类
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert AIData._instance is None
		# key(AI id) ：value (instance of AIAction)
		self._AIDatas = {}
		AIData._instance = self

	def load( self, configPath ):
		"""
		加载AI配置
		"""
		sect = Language.openConfigSection( configPath )
		assert sect is not None, "open %s false." % configPath

		for childSect in sect.values():
			id = childSect["id"].asInt
			templetID = childSect["templetID"].asInt
			mod = aiTemplate_instance()
			try:
				templateInst = mod[ templetID ][ "script" ]()
			except TypeError, errstr:
				EXCEHOOK_MSG( "%s script %s" % ( errstr, mod[ templetID ][ "script" ] ) )
				continue
			templateInst.init( childSect )
			self._AIDatas[id] = templateInst
		# 清除缓冲
		Language.purgeConfig( configPath )

	def __getitem__( self, key ):
		"""
		取得AI实例
		"""
		assert key in self._AIDatas, "AIData %i not find!" % key
		
		return self._AIDatas[key]

	def has( self, AIkey ):
		"""
		"""
		return AIkey in self._AIDatas

	@staticmethod
	def instance():
		"""
		"""
		if AIData._instance is None:
			AIData._instance = AIData()
		return AIData._instance


class NPCAIData:
	"""
	npcAI的相关数据
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert NPCAIData._instance is None
		# key(AI id) ：value (instance of AIAction)
		self._AIDatas = {}
		NPCAIData._instance = self
		self.comboAIActivate = 0

	def load( self, configPath ):
		"""
		加载AI配置
		"""
		sect = Language.openConfigSection( configPath )
		assert sect is not None, "open %s false." % configPath
		g_aiDatas = aiData_instance()

		for childSect in sect.values():
			npcID = childSect[ "npcID" ].asString
			aiData = {}
			self._AIDatas[ npcID ] = aiData
			csection = childSect[ "AIProperty" ]
			aiData[ csdefine.AI_TYPE_GENERIC_ATTACK ] = []
			hasAI = False
			try:
				for sec in csection[ "commonAI_fightState" ].values():
					aiID = sec[ "AIid" ].asInt
					level = sec[ "grade" ].asInt
					aiData[ csdefine.AI_TYPE_GENERIC_ATTACK ].append( { "type" : csdefine.AI_TYPE_GENERIC_ATTACK, "level" : level, "data" : g_aiDatas[ aiID ] } )
					hasAI = True

				aiData[ csdefine.AI_TYPE_GENERIC_FREE ] = []
				for sec in csection[ "commonAI_usualState" ].values():
					aiID = sec[ "AIid" ].asInt
					level = sec[ "grade" ].asInt
					aiData[ csdefine.AI_TYPE_GENERIC_FREE ].append( { "type" : csdefine.AI_TYPE_GENERIC_FREE, "level" : level, "data" : g_aiDatas[ aiID ] } )
					hasAI = True

				aiData[ csdefine.AI_TYPE_SCHEME ] = []
				for sec in csection[ "configAI" ].values():
					aiID = sec[ "AIid" ].asInt
					level = sec[ "grade" ].asInt
					aiData[ csdefine.AI_TYPE_SCHEME ].append( { "type" : csdefine.AI_TYPE_SCHEME, "level" : level, "data" : g_aiDatas[ aiID ] } )
					hasAI = True

				aiData[ csdefine.AI_TYPE_SPECIAL ] = []
				for sec in csection[ "specificAI" ].values():
					aiID = sec[ "AIid" ].asInt
					level = sec[ "grade" ].asInt
					aiData[ csdefine.AI_TYPE_SPECIAL ].append( { "type" : csdefine.AI_TYPE_SPECIAL, "level" : level, "data" : g_aiDatas[ aiID ] } )
					hasAI = True

				aiData[ csdefine.AI_TYPE_EVENT ] = []
				for sec in csection[ "event" ].values():
						eventID = sec[ "eventID" ].asInt
						for s in sec["AIProperty"].values():
							aiID = s[ "AIid" ].asInt
							level = s[ "grade" ].asInt
							aiData[ csdefine.AI_TYPE_EVENT ].append( { "eventID" : eventID, "level" : level, "data" : g_aiDatas[ aiID ] } )
							hasAI = True

				aiData[ csdefine.AI_TYPE_COMBO ] = []
				if csection.has_key( "comboAI" ):
					for sec in csection[ "comboAI" ].values():
						level = sec[ "grade" ].asInt
						for subsec in sec[ "comboItem" ].values():
							comboID = subsec[ "comboID" ].asInt
							activeRate = subsec[ "activeRate" ].asFloat
							for s in subsec["AIProperty"].values():
								aiID = s.asInt
								aiData[ csdefine.AI_TYPE_COMBO ].append( { "level": level, "comboID": comboID, "activeRate":activeRate, "data": g_aiDatas[ aiID] } )
								hasAI = True

				aiData[ csdefine.AI_TYPE_COMBO_ACTIVERATE ] = 0
				if csection.has_key( "comboActiveRate"):
					activeRate = csection[ "comboActiveRate" ].asFloat
					aiData[ csdefine.AI_TYPE_COMBO_ACTIVERATE ] = activeRate

				if not hasAI:
					self._AIDatas.pop( npcID )
					continue
			except KeyError, errstr:
				ERROR_MSG( "load NPCAI error! use the default AI.npcID: %s, %s" % ( npcID, errstr ) )
				self._AIDatas.pop( npcID )
				continue

		# 清除缓冲
		Language.purgeConfig( configPath )

	def __getitem__( self, key ):
		"""
		取得AI实例
		"""
		assert key in self._AIDatas, "NPCAI %i not find!" % key
		
		return self._AIDatas[key]

	def has( self, key ):
		"""
		"""
		return key in self._AIDatas

	@staticmethod
	def instance():
		"""
		"""
		if NPCAIData._instance is None:
			NPCAIData._instance = NPCAIData()
		return NPCAIData._instance

def aiAction_instance():
	return AIData_Action.instance()
def aiConditon_instance():
	return AIData_Condition.instance()
def aiTemplate_instance():
	return AIData_Template.instance()
def aiData_instance():
	return AIData.instance()

def NPCAI_instance():
	return NPCAIData.instance()


# $Log: not supported by cvs2svn $
# Revision 1.4  2008/05/16 07:43:56  kebiao
# no message
#
# Revision 1.3  2008/05/15 09:03:44  kebiao
# 修改NPCAI加载方式
#
# Revision 1.2  2008/05/04 09:05:43  kebiao
# 改变AI初始化
#
# Revision 1.1  2008/04/22 04:14:51  kebiao
# no message
#
#