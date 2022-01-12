# -*- coding: gb18030 -*-
# $Id: Transporter.py,v 1.5 2007-12-15 11:27:37 huangyongwei Exp $

import BigWorld
import NPC
from bwdebug import *
import Resource.TransporterData
class Transporter( NPC.NPC ):
	"""
	Smith
	"""
	
	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�
		
		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		NPC.NPC.onLoadEntityProperties_( self, section )
		
		# name, sign, pos, direction, spaceName
		pos = section.readVector3( "retPos" )
		sign = section.readInt( "sign" )
		name = section.readString( "name" )
		direction = section.readVector3( "retDir" )
		spaceName = section.readString( "space" )
		
		self.setEntityProperty( "range", section.readFloat( "talkRange" ) ) 	# �Ի���Χ
		self.setEntityProperty( "transportSign", sign ) 	# �Ի���Χ
		
		# ����������
		self.setEntityProperty( "isTransportDoor", section.readInt( "transport" ) )
		
		# ע�ᴫ����
		Resource.TransporterData.g_transporterData.register( name, sign, pos, direction, spaceName )

	def initEntity( self, selfEntity ):
		"""
		virtual method.
		��ʼ���Լ���entity������
		"""
		NPC.NPC.initEntity( self, selfEntity )
		
# Transporter.py
