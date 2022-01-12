# -*- coding: gb18030 -*-


import Resource
import Language
import csdefine
import BigWorld
import csstatus
from SmartImport import smartImport
from bwdebug import *

g_aiActions = Resource.AIData.aiAction_instance()
g_aiConditions = Resource.AIData.aiConditon_instance()
g_aiTemplates = Resource.AIData.aiTemplate_instance()
g_aiDatas = Resource.AIData.aiData_instance()
g_npcaiDatas = Resource.AIData.NPCAI_instance()

def updateAIBase( folderName ):
	"""
	"""
	AIActionPath	= "config/AITest/%s/AIAction.xml"%( folderName )
	AIConditionPath	= "config/AITest/%s/AICondition.xml"%( folderName )
	"""
	update AIActions
	"""
	#g_aiActions.load( "config/server/ai/AIAction.xml" )	# 初始化数据
	sect = Language.openConfigSection( AIActionPath )
	assert sect is not None, "open %s false." % AIActionPath

	for childSect in sect.values():
		id = childSect["id"].asInt
		scriptName = childSect["scriptName"].asString
		print "AITest.%s."%folderName + scriptName
		try:
			AIMod = smartImport( "config.AITest.%s."%folderName + scriptName )
		except ImportError, err:
			ERROR_MSG( err )
			continue
		g_aiActions._AIDatas[id] = AIMod
		# 清除缓冲
		Language.purgeConfig( AIActionPath )

	"""
	update AIConditions
	"""
	#g_aiConditions.load( "config/server/ai/AICondition.xml" )	# 初始化数据
	sect = Language.openConfigSection( AIConditionPath )
	assert sect is not None, "open %s false." % AIConditionPath

	for childSect in sect.values():
		id = childSect["id"].asInt
		scriptName = childSect["scriptName"].asString
		print "config.AITest.%s."%folderName + scriptName
		AIMod = smartImport( "config.AITest.%s."%folderName + scriptName )
		g_aiConditions._AIDatas[id] = AIMod
	Language.purgeConfig( AIConditionPath )
	


def updateMonsterAI( srcEntity, folderName, monsterName ):
	
	monsterName = str( monsterName )
	monsterAIPath 	= "config/AITest/%s/%s.xml"%( folderName, monsterName )
	AIDataPath 		= "config/AITest/%s/AIData.xml"%( folderName )
	AITempletPath 	= "config/AITest/%s/AITemplet.xml"%( folderName )
	"""
	update AITemplet
	"""
	g_aiTemplates._AIDatas = {}
	g_aiTemplates.load( AITempletPath )
	
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_AI_REPLACE_AITEMPLET, str( ( monsterName, )) )
	
	"""
	update AIData
	"""
	g_aiDatas._AIDatas = {}
	g_aiDatas.load( AIDataPath )
	
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_AI_REPLACE_AIDATAS, str( ( monsterName, )) )
	"""
	update monster AI
	"""
	monsterAISect 	= Language.openConfigSection( monsterAIPath )
	npcID = monsterName
	aiData = {}
	
	if npcID not in g_npcaiDatas._AIDatas:
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_AI_NOT_EXIST, str( ( monsterName, )) )
	
	g_npcaiDatas._AIDatas[ npcID ] = aiData
	csection = Language.openConfigSection( monsterAIPath )
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
		if not hasAI:
			g_npcaiDatas._AIDatas.pop( npcID )
	except KeyError, errstr:
		ERROR_MSG( "load NPCAI error! use the default AI. %s" % errstr )
		g_npcaiDatas._AIDatas.pop( npcID )
		srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_AI_CONFIG_WRONG, str( ( monsterName, )) )

	for i in BigWorld.entities.values():
		if hasattr( i, "className" ) and i.className == npcID:
			if i.isReal():
				clearDict(i.attrFreeStateGenericAIs)
				clearDict(i.attrAttackStateGenericAIs)
				clearDict(i.attrSchemeAIs)
				clearDict(i.attrSpecialAIs)
				clearDict(i.triggersTable)
				i.getScript()._initAI( i )
	
	srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_AI_FINISH, str( ( monsterName, )) )

	Language.purgeConfig( monsterAIPath )


def clearDict( d ):
	for i in d.keys():
		del d[i]


def AIDataQuery( type, scriptName ):
	"""
	查询当前配置中某一条AI的使用情况 	type: condition 或者 action
	eg:AIDataQuery( "action", "AIAction78" )
	"""
	g_npcaiDatas = Resource.AIData.NPCAI_instance()
	g_npcaiDatas.load( "config/server/gameObject/NPCAI.xml" )	# 初始化数据
	dict = {}
	for className in g_npcaiDatas._AIDatas.keys():
		for i in xrange(1,6):
			datas = g_npcaiDatas._AIDatas[className][i]
			if datas == [] or datas is None:
				continue
			for j in xrange( len(datas) ):
				ai = datas[j]["data"]
				if type == "action":
					for ac in ai._actions:
						if ac.__class__.__name__ == scriptName:
							if not dict.has_key( ai.getID() ):
								dict[ai.getID()] = []
							dict[ai.getID()].append( className )
							dict[ai.getID()] = {}.fromkeys( dict[ai.getID()] ).keys()		# 去除列表中的重复元素
				if type == "condition":
					for ac in ai._conditions:
						if ac.__class__.__name__ == scriptName:
							if not dict.has_key( ai.getID() ):
								dict[ai.getID()] = []
							dict[ai.getID()].append( className )
							dict[ai.getID()] = {}.fromkeys( dict[ai.getID()] ).keys()		# 去除列表中的重复元素
	return dict