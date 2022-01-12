# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.5 2008-04-16 05:50:45 phw Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from Space import Space

class SpaceMultiLine( Space ):
	"""
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Space.__init__( self )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, section ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initialized.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" fine
		@type			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		Space.onLoadEntityProperties_( self, section )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		Space.load( self, section )
		self.maxLine = section.readInt( "maxLine" )
		self.initLine = section.readInt( "initLine" )
		self.newLineByPlayerAmount = section.readInt( "newLineByPlayerAmount" )

		if section.has_key( "maxPlayerAmount" ):
			self.maxPlayerAmount = section.readInt( "maxPlayerAmount" )
		else:
			self.maxPlayerAmount = 999999999
			


	#------------------------------------------------------------------------------------------------------------------------------------
	
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
		return {}
		

# SpaceNormal.py
