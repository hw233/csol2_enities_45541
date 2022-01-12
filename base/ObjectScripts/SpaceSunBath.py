# -*- coding: gb18030 -*-
#
# $Id: SpaceMultiLine.py,v 1.8 2008-04-16 05:51:18 phw Exp $

"""
"""
import BigWorld
import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from SpaceMultiLine import SpaceMultiLine

class SpaceSunBath( SpaceMultiLine ):
	"""
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceMultiLine.__init__( self )
		self._sunBathSpellIDList = {}	# 日光浴场景中所有副本中的所有贝壳的ID列表
		self._spellRefreshTime = 0		# 贝壳刷新间隔时间
		self._spellNum = 0				# 贝壳刷新数量
	
	def onLoadEntityProperties_( self, section ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initialized.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" fine
		@type			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		SpaceMultiLine.onLoadEntityProperties_( self, section )

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceMultiLine.load( self, section )
		
		if section.has_key( "spellRefreshTime" ):	# 读取贝壳刷新时间
			self._spellRefreshTime = section.readInt( "spellRefreshTime" )
		
		if section.has_key( "spellNum" ):	# 读取贝壳刷新数量
			self._spellNum = section.readInt( "spellNum" )
		