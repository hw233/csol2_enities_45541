# -*- coding: utf-8 -*-
# This is an example of how to place an Entity in the world via BigBang. On the
# Entity panel, select Creature and place the Entity in the world by pressing
# enter. The placeholder model refered to by modelName() will be placed into the
# BigBang representation of the world and the Entity will be placed into the
# appropriate chunk file when the world is saved. Game script can then be used
# to load the entities into the game world. See BigWorld.fetchEntitiesFromChunks
# in BaseApp's Python API.

import ResMgr
import Function
import NPCModelLoader

g_models = NPCModelLoader.instance


keyname2name = []				# [ (keyname, name), ... ]
keyname2modelNumber = { }		# { npcID : modelNumber, ...}

# 以下两个变量用于其它的分类SpawnPoint
keyname2name_npc = []			# like as keyname2name
keyname2name_monster = []		# like as keyname2name

def initNpcs():
	fileSect = ResMgr.openSection( "entities/common/config/gameObject/objPath.xml" )
	paths = [ e for e in fileSect.readStrings( "path" ) ]		# 取得所有的配置路径
	files = Function.searchFile( paths, ".xml" )
	if fileSect.has_key( "files" ):
		files.extend( fileSect["files"].readStrings( "path" ) )

	for filename in files:
		npcSec = ResMgr.openSection( filename )
		if npcSec is None:
			print "--> Error: file open fault.", filename
			continue
			
		if npcSec.childName( 0 ) == "row":
			for index in xrange( len( npcSec ) ):
				initNPCData( npcSec.child( index ) )
		else:
			initNPCData( npcSec )
		ResMgr.purge( filename )
	print "-->len( keyname2name_npc ) = %i, len( keyname2name_monster ) = %i" % (len( keyname2name_npc ), len( keyname2name_monster ))
	print "\n--> init npc model finish.\n"

def initNPCData( dataSection ):
	"""
	@param dataSection: 一个完整的NPC数据的section
	"""
	# keyname2name
	name = dataSection.readString( "uname" )
	if len( name ) == 0:
		print "--> Error: spawn config has no 'uname' section. ignore", dataSection.readString( "className" )
		return
	className = dataSection["className"].asString
	m = (className, className + " " + name)
	keyname2name.append( m )
	if dataSection.readString( "EntityType" ) in ["Monster", "QuestMonster"]:
		#print "--> %s is monster." % className
		keyname2name_monster.append( m )
	else:
		keyname2name_npc.append( m )

	# keyname2modelNumber
	modelNumber = dataSection["modelNumber"].readString( "item" )	# 读取第一个模型
	if len( modelNumber ) == 0:
		modelNumber = "GW0001"
		
	keyname2modelNumber[className] = modelNumber


# init all models
initNpcs()

class SpawnPoint:
	def modelName( self, props ):
		modelNumber = keyname2modelNumber[ props["entityName"] ]
		#print "modelNumber -------------------->", modelNumber
		if len( modelNumber ):
			models = g_models.getModelSources( modelNumber )
			#print "models -------------------->", models
			if len( models ) == 1:
				return models[0]
			else:
				return "monster/gw0001/gw0001.model"	# "helpers/props/standin.model"
		else:
			return "monster/gw0001/gw0001.model"	# "helpers/props/standin.model"

	def getEnums_entityName( self ):
		#return (("", "测试"), )	# 崩溃
		return keyname2name

# SpawnPoint.py
