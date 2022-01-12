# -*- coding: gb18030 -*-

import time
import Language
import BigWorld
from bwdebug import *
import Function
from SpaceDomain import SpaceDomain
from interface.ImpPlanesSpaceDomain import ImpPlanesSpaceDomain
import csdefine

class SpaceDomainPlanes( SpaceDomain, ImpPlanesSpaceDomain ):
	"""
	λ���ͼdomain
	"""
	def __init__( self ):
		super( SpaceDomainPlanes, self ).__init__()
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_PLANES
	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		��������һ�����򿪷ŵģ� ��˲������½���ܹ�����һ��
		�����Լ������ĸ����У� ���������Ӧ�÷��ص���һ�ε�½�ĵط�
		"""
		baseMailbox.logonSpaceInSpaceCopy()