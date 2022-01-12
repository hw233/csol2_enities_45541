# -*- coding: gb18030 -*-

import Language
from bwdebug import *

from ObjectScripts.GameObjectFactory import g_objFactory

import csconst

class TimerEvent( object ):
	def __init__( self, index, config ):
		object.__init__( self )
		self.index = index
	
	def initData( self, config ):
		self.eventTime = config[ "time" ].asFloat
	
	def do( self, controlEntity ):
		pass
	
	def check( self, controlEntity ):
		return True
	
	def initControl( self, controlEntity ):
		controlEntity.addTimer( self.eventTime, 0, self.index )

class ChatMsg( TimerEvent ):
	"""
	广播
	"""
	def __init__( self, index, config ):
		TimerEvent.__init__( self, index, config )
		self.msg = ""
		
	def initData( self, config ):
		TimerEvent.initData( config )
		self.msg = config[ "data" ].asString
	
	def do( self, controlEntity ):
		if self.msg:
			BigWorld.globalData[csconst.C_PREFIX_GBAE].anonymityBroadcast( self.msg, [] )

class SpawnControl( TimerEvent ):
	"""
	刷怪
	"""
	def __init__( self, index, config ):
		TimerEvent.__init__( self, index, config )
		self.spawnDict = {}
		
	def initData( self, config ):
		TimerEvent.initData( config )
		for spData in config[ "data" ].values():
			className, num = spData.asString.split( ";" )
			self.spawnDict[ className ] = num
	
	def do( self, controlEntity ):
		for className, num in self.spawnDict.iteritems():
			for i in xrange( num ):
				e = g_objFactory.getObject( className ).createEntity( self.spaceID, self.position, self.direction, d )
				controlEntity.spawnList.append( e )


KEY_TO_OBJECT = {
	"CHAT"	:	ChatMsg, 
	"SP"	:	SpawnControl,
}

class TimerEventConfig:
	"""
	NPC对话内容加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert TimerEventConfig._instance is None
		# key == npcID
		# value == DialogManager()
		self._datas = {}
		TimerEventConfig._instance = self

	def load( self, configFilePath ):
		"""
		初始化所有配置
		"""
		for configFileName in Language.searchConfigFile( [ configFilePath ], ".xml" ):
			configSection = Language.openConfigSection(configFileName)
			if configSection is None:
				ERROR_MSG( "Space config file %s not find." % configFileName )
				continue
			self._initConfig( configFileName, configSection )
			Language.purgeConfig( configFileName )
	
	def _initConfig( self, configFileName, configSection ):
		eventList = []
		for config in configSection.values():
			type = config[ "type" ].asString
			object = KEY_TO_OBJECT[ type ]( len( eventList ), configSection )
			eventList.append( object )
		self._datas[ configFileName ] = object

	def initControl( self, cEntity ):
		eventList =  self.get( cEntity.configName )
		for e in eventList:
			e.initControl( cEntity )
	
	def doEvent( self, cEntity, index ):
		eventList =  self.get( cEntity.configName )
		if eventList and len( eventList ) > index:
			e = eventList[ index ]
			if e.check( cEntity ):
				e.do( cEntity )

	def get( self, configName ):
		try:
			return self._datas[configName]
		except KeyError:
			return None

	@staticmethod
	def instance():
		"""
		"""
		if TimerEventConfig._instance is None:
			TimerEventConfig._instance = TimerEventConfig()
		return TimerEventConfig._instance

g_timerEventConfig = TimerEventConfig.instance()