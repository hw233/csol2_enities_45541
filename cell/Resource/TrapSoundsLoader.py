# -*- coding: gb18030 -*-


from bwdebug import *
import csdefine
import csconst
import Language
import random

class TrapSoundsLoader:
	"""
	������Ч���ݼ���
	"""
	_instance = None
	def __init__( self ):
		assert self._instance is None,"Just allow one instance exist!"
		TrapSoundsLoader._instance = self
		
		self._datas = {}	# ������Ч���� {className:{"questID":xxxx,"questStatus":xx,"trapRange":xx,....} }

	def load( self, xmlPath = "" ):
		"""
		����xml�ļ�����
		"""
		section = Language.openConfigSection( xmlPath )
		assert section is not None,"open file( path:%s ) error:not exist!" % xmlPath
		successCount = 0
		failedCount = 0
		for node in section.values():
			className = node.readString( "className" )
			questID = node.readInt( "questID" )
			questStatus = node.readInt( "questStatus" )
			trapRange = node.readInt( "trapRange" )
			soundEvent = node.readString( "soundEvent" )
			if className is None or questID is None or questStatus is None or trapRange is None or soundEvent is None:
				ERROR_MSG( "--->>>read data,when failedCount:%i,successCount:%i." % ( failedCount, successCount ) )
				failedCount += 1
				continue
			self._datas[className] = {"questID":questID, "questStatus":questStatus, "trapRange":trapRange, "soundEvent":soundEvent}
			successCount += 1
		INFO_MSG( "------>>>successCount:%i;failedCount:%i." % ( successCount, failedCount ) )
	
	def getSoundInfo( self, className ):
		"""
		��ȡ��Ч����
		"""
		if self.hasSoundInfo( className ):
			return self._datas[className]
	
	def hasSoundInfo( self, className ):
		"""
		�����Ƿ�������Ч
		"""
		return className in self._datas
	
	def getTrapRange( self, className ):
		"""
		������巶Χ
		"""
		if self.hasSoundInfo( className ):
			return self.getSoundInfo( className )["trapRange"]
	
	@classmethod
	def instance( self ):
		"""
		"""
		if TrapSoundsLoader._instance is None:
			TrapSoundsLoader._instance = TrapSoundsLoader()
		return TrapSoundsLoader._instance

g_trapSoundsLoader = TrapSoundsLoader.instance()