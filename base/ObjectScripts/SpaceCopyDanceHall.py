# -*- coding: gb18030 -*-
#
# $Id: Space.py,v 1.8 2008-04-16 05:51:18 phw Exp $

"""
"""
import BigWorld
import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyDanceHall( SpaceCopy ):
	"""
	���ڿ���SpaceNormal entity�Ľű�����������Ҫ��SpaceNormal����������ô˽ű�(��̳��ڴ˽ű��Ľű�)�Ľӿ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
