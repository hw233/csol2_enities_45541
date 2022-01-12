# -*- coding: gb18030 -*-

import re
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyCityWarFinal( SpaceCopy ):
	"""
	�����ս����
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )

	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.enterPosMapping = {}

	def load( self, section ):
		"""
		�������м�������
		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		
		spaceData = section[ "Space" ]

		# �سǰ�����λ��
		defend_tong_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["defend_tong_enterPos"].asString ) )
		defend_league_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["defend_league_enterPos"].asString ) )
		
		# ���ǰ�����λ��
		attack_tong_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["attack_tong_enterPos"].asString ) )
		attack_leftLeague_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["attack_leftLeague_enterPos"].asString ) )
		attack_rightLeague_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["attack_rightLeague_enterPos"].asString ) )

		self.enterPosMapping = { 1: defend_tong_enterPos,
								 2: defend_league_enterPos,
								 3: attack_tong_enterPos,
								 4: attack_leftLeague_enterPos,
								 5: attack_rightLeague_enterPos,
								}
		

	def getEnterPos( self, posNo ):
		"""
		����λ�ñ�Ż�ȡ����λ�úͳ���
		"""
		return self.enterPosMapping[ posNo ]