# -*-coding: gb18030 -*-
#
#

import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus

from SpaceCopy import SpaceCopy


class SpaceCopyWuDao( SpaceCopy ):
	"""
	�����ḱ���ռ�ȫ��ʵ���ű�
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		
		
	def load( self, section ):
		"""
		�������м�������
		
		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		
		