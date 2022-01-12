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
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。
		
		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		NPC.NPC.onLoadEntityProperties_( self, section )
		
		# name, sign, pos, direction, spaceName
		pos = section.readVector3( "retPos" )
		sign = section.readInt( "sign" )
		name = section.readString( "name" )
		direction = section.readVector3( "retDir" )
		spaceName = section.readString( "space" )
		
		self.setEntityProperty( "range", section.readFloat( "talkRange" ) ) 	# 对话范围
		self.setEntityProperty( "transportSign", sign ) 	# 对话范围
		
		# 传送器类型
		self.setEntityProperty( "isTransportDoor", section.readInt( "transport" ) )
		
		# 注册传送器
		Resource.TransporterData.g_transporterData.register( name, sign, pos, direction, spaceName )

	def initEntity( self, selfEntity ):
		"""
		virtual method.
		初始化自己的entity的数据
		"""
		NPC.NPC.initEntity( self, selfEntity )
		
# Transporter.py
