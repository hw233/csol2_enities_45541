# -*- coding: gb18030 -*-

class Quest:
	def __init__( self ):
		self._id = 0
		self._title = ""
		self._level = 0
		self.msg_objective 		= ""	# 任务目标描述
		self.msg_detail 		= ""	# 任务故事内容描述对白
		self.msg_log_detail 	= ""	# 任务详细故事描述，玩家任务日志窗口版
		self.msg_incomplete 	= ""	# 任务目标未完成时对话
		self.msg_precomplete 	= ""	# 任务目标完成时对话
		self.msg_complete 		= ""	# 交任务后说的话(可以用于承上启下作用)
		self.voe_detail			= ""	# 任务描述语音提示
		self.voe_incomplete		= ""	# 未完成语音提示
		self.voe_precomplete	= ""	# 已完成语音提示
		self.voe_complete		= ""	# 已完成语音提示
		self.taskIndexMonsters	= {}	# 任务目标显示名称entity列表

	def init( self, section ):
		"""
		virtual method.
		@param section: 任务配置文件section
		@type  section: pyDataSection
		"""
		formatStr = lambda string : "".join( [ e.strip( "\t " ) for e in string.splitlines(True) ] )

		self._id = section["id"].asInt
		
		self._title = section.readString( "title" )
		self._level = section.readInt( "level" )

		self.msg_log_detail		= formatStr( section.readString( "msg_log_detail" ) )
		self.msg_objective		= formatStr( section.readString( "msg_objective" ) )
		self.msg_detail			= formatStr( section.readString( "msg_detail" ) )
		self.msg_incomplete		= formatStr( section.readString( "msg_incomplete" ) )
		self.msg_precomplete	= formatStr( section.readString( "msg_precomplete" ) )
		self.msg_complete		= formatStr( section.readString( "msg_complete" ) )
		self.voe_detail			= formatStr( section.readString( "voe_detail" ) )			# 任务描述语音提示
		self.voe_incomplete		= formatStr( section.readString( "voe_incomplete" ) )		# 未完成语音提示
		self.voe_precomplete	= formatStr( section.readString( "voe_precomplete" ) )		# 已完成语音提示
		self.voe_complete		= formatStr( section.readString( "voe_complete" ) )		# 已完成语音提示

		if section.has_key( "tasks" ):
			for sec in section["tasks"].values():
				taskIdx = sec.readInt( "index" )
				snMonsters = []
				if sec.has_key( "snMonsters" ) and len( sec.readString( "snMonsters" ) ) > 0:
					snMonsters = sec.readString( "snMonsters" ).split( ";" )
				self.taskIndexMonsters[taskIdx] = snMonsters

	def getID( self ):
		"""
		取得任务ID号(questID)
		"""
		return self._id

	def getTitle( self ):
		return self._title

	def getLevel( self, player = None ):
		"""
		取得任务等级
		"""
		return self._level

	def getTaskIndexs( self ):
		"""
		取得所有任务目标index
		"""
		return self.taskIndexMonsters.keys()

	def getTaskIndexMonsters( self, taskIndex ):
		"""
		取得任务目标未完成需显示名称entity列表
		"""
		return self.taskIndexMonsters.get( taskIndex, [] )