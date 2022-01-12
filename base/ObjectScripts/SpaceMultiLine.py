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
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
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
		用于在玩家上线时需要在指定的domain额外参数；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return {}
		

# SpaceNormal.py
