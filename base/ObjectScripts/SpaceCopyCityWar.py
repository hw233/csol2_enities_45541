# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyCityWar.py,v 1.1 2008-08-25 09:30:27 kebiao Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
from SpaceCopy import SpaceCopy

class SpaceCopyCityWar( SpaceCopy ):
	"""
	����ƥ��SpaceDomainCopyTeam�Ļ�����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		
		self.roomLevel = section[ "Space" ][ "roomLevel" ].asInt
		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		self.right_playerEnterPoint = ( pos, direction )
		
		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		self.left_playerEnterPoint = ( pos, direction )
		
		if self.getRoomLevel() == 1:
			data = section[ "Space" ][ "defend_playerEnterPoint" ]
			pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
			self.defend_playerEnterPoint = ( pos, direction )
		
	def getRoomName( self ):
		return self.roomName
		
	def getRoomIndex( self ):
		return self.roomIndex
	
	def getRoomLevel( self ):
		return self.roomLevel
		
	def packedDomainData( self, entity ):
		"""
		virtual method.
		�������������ʱ��Ҫ��ָ����domain���������
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'tongDBID' : entity.cellData[ "tong_dbID" ], "ename" : entity.cellData[ "playerName" ], "dbid": entity.databaseID }