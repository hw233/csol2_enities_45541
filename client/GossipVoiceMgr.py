# -*- coding: gb18030 -*-
#
# $Id: GossipVoiceMgr.py

"""
"""

import Language
import ResMgr
from bwdebug import *
from gbref import rds
from event import EventCenter as ECenter

class GossipVoiceMgr :
	__inst = None

	def __init__( self ) :
		assert GossipVoiceMgr.__inst is None, "you should use 'instance()' method to access GossipVoiceMgr singleton instance."

		self._qstDatas = {}
		self._optDatas = {}
		self.__initialize()

	@classmethod
	def instance( SELF ) :
		if not SELF.__inst :
			SELF.__inst = GossipVoiceMgr()
		return SELF.__inst
	
	def __initialize( self ):
		qstSect = Language.openConfigSection( "config/client/questsounds.xml" )
		optSect = Language.openConfigSection( "config/client/optionsounds.xml" )
		if qstSect:
			for node in qstSect.values():
				qstID = node.readInt( "questID" )
				state = node.readString( "state" )
				clsName = node.readString( "npcClsName" )
				voicePath = node.readString( "voicePath" )
				if qstID in self._qstDatas:
					self._qstDatas[qstID].update( {state: ( clsName, voicePath ) } )
				else:
					self._qstDatas[qstID] = {state:( clsName, voicePath ) }
		if optSect:
			for node in optSect.values():
				clsName = node.readString( "npcClsName" )
				title = node.readString( "title" )
				voicePath = node.readString( "voicePath" )
				if clsName in self._optDatas:
					self._optDatas[clsName].update( {title: voicePath } )
				else:
					self._optDatas[clsName] = {title: voicePath }
	
	def getQuestVoice( self, qstID, state, clsName ):
		"""
		获取任务选项语音
		"""
		qstData = self._qstDatas.get( qstID, None )
		if qstData:
			qstVoice = qstData.get( state, None )
			if qstVoice and qstVoice[0] == clsName:
				return qstVoice[1]
	
	def getOptionVoice( self, clsName, title ):
		"""
		获取对话选项语音
		"""
		optData = self._optDatas.get( clsName, None )
		if optData:
			optVoice = optData.get( title, None )
			return optVoice

# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
gossipVoiceMgr = GossipVoiceMgr.instance()