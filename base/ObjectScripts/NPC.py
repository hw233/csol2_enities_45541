# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.1 2008-03-28 07:31:07 kebiao Exp $

"""
NPC�Ļ���
"""
from bwdebug import *
from Monster import Monster
import csdefine

class NPC( Monster ):
	"""
	NPC�Ļ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.__init__( self )
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�
		
		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		Monster.onLoadEntityProperties_( self, section )


# NPC.py
