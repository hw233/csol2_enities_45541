# -*- coding: gb18030 -*-
#
# $Id: TongSpecialChapman.py



import BigWorld
from bwdebug import *
import csdefine
import csstatus
from NPC import NPC

class TongSpecialChapman( NPC ):
	"""
	����������� 
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�
		
		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		NPC.onLoadEntityProperties_( self, section )

# NPC.py
