# -*- coding: gb18030 -*-

class Quest:
	def __init__( self ):
		self._id = 0
		self._title = ""
		self._level = 0
		self.msg_objective 		= ""	# ����Ŀ������
		self.msg_detail 		= ""	# ����������������԰�
		self.msg_log_detail 	= ""	# ������ϸ�������������������־���ڰ�
		self.msg_incomplete 	= ""	# ����Ŀ��δ���ʱ�Ի�
		self.msg_precomplete 	= ""	# ����Ŀ�����ʱ�Ի�
		self.msg_complete 		= ""	# �������˵�Ļ�(�������ڳ�����������)
		self.voe_detail			= ""	# ��������������ʾ
		self.voe_incomplete		= ""	# δ���������ʾ
		self.voe_precomplete	= ""	# �����������ʾ
		self.voe_complete		= ""	# �����������ʾ
		self.taskIndexMonsters	= {}	# ����Ŀ����ʾ����entity�б�

	def init( self, section ):
		"""
		virtual method.
		@param section: ���������ļ�section
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
		self.voe_detail			= formatStr( section.readString( "voe_detail" ) )			# ��������������ʾ
		self.voe_incomplete		= formatStr( section.readString( "voe_incomplete" ) )		# δ���������ʾ
		self.voe_precomplete	= formatStr( section.readString( "voe_precomplete" ) )		# �����������ʾ
		self.voe_complete		= formatStr( section.readString( "voe_complete" ) )		# �����������ʾ

		if section.has_key( "tasks" ):
			for sec in section["tasks"].values():
				taskIdx = sec.readInt( "index" )
				snMonsters = []
				if sec.has_key( "snMonsters" ) and len( sec.readString( "snMonsters" ) ) > 0:
					snMonsters = sec.readString( "snMonsters" ).split( ";" )
				self.taskIndexMonsters[taskIdx] = snMonsters

	def getID( self ):
		"""
		ȡ������ID��(questID)
		"""
		return self._id

	def getTitle( self ):
		return self._title

	def getLevel( self, player = None ):
		"""
		ȡ������ȼ�
		"""
		return self._level

	def getTaskIndexs( self ):
		"""
		ȡ����������Ŀ��index
		"""
		return self.taskIndexMonsters.keys()

	def getTaskIndexMonsters( self, taskIndex ):
		"""
		ȡ������Ŀ��δ�������ʾ����entity�б�
		"""
		return self.taskIndexMonsters.get( taskIndex, [] )