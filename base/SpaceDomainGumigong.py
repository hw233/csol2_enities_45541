# -*- coding: gb18030 -*-
#

from SpaceDomainCopyTeam import SpaceDomainCopyTeam


class SpaceDomainGumigong(SpaceDomainCopyTeam):
	"""
	�����
	"""
	def __init__( self ):
		SpaceDomainCopyTeam.__init__(self)


	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT = None
		"""

		baseMailbox.logonSpaceInSpaceCopy()


