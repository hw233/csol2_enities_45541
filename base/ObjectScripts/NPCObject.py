# -*- coding: gb18030 -*-
#
# $Id: NPCObject.py,v 1.10 2008-04-16 05:51:18 phw Exp $

"""
implement npc base class map script
2007/07/14: writen by huangyongwei
"""

import random
from bwdebug import *
from ObjectScripts.GameObject import GameObject
import csdefine
import csconst

class NPCObject( GameObject ) :
	def __init__( self ) :
		GameObject.__init__( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, section ) :
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		GameObject.onLoadEntityProperties_( self, section )

		self.setEntityProperty( "uname", 		section.readString( "uname" ) )					# 中文名称
		self.setEntityProperty( "title",		section.readString( "title" ) )					# 头衔

		flagSection = section["flags"]
		flag = 0
		if flagSection:
			flags = flagSection.readInts( "item" )
			for v in flags: flag |= 1 << v
		# entity的标志集合，如是否可交易、是否有任务、是否能合成装备等等；ENTITY_FLAG_*
		self.setEntityProperty( "flags",	flag )

		self.setEntityProperty( "walkSpeed",	int( section.readFloat( "walkSpeed" ) * csconst.FLOAT_ZIP_PERCENT ) )				# 走速度
		self.setEntityProperty( "runSpeed",		int( section.readFloat( "runSpeed" ) * csconst.FLOAT_ZIP_PERCENT ) )				# 跑速度
		
		modelNumbers = [ e.lower() for e in section["modelNumber"].readStrings( "item" ) ]				# 模型编号列表
		self.setEntityProperty( "modelNumber",	modelNumbers )
		
		modelScales = section[ "modelScale" ].readStrings( "item" )    # 模型使用比例列表
		self.setEntityProperty( "modelScale",	modelScales )
		if section.has_key( "nameColor" ):
			nameColor = section.readInt( "nameColor" )					#头顶名称颜色标记
			self.setEntityProperty( "nameColor",	nameColor )

	# -------------------------------------------------
	def onCreateEntityInitialized_( self, entity ) :
		"""
		virtual method. Template method, it will be called when an entity is created.
		you can override it, and initialize entity use your own datas
		"""
		GameObject.onCreateEntityInitialized_( self, entity )


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
		GameObject.load( self, section )

	# -------------------------------------------------
	def createLocalBase( self, param = None ) :
		"""
		create an entity and loacte it in the map
		@type				param	   : dict
		@param				param	   : property dictionary
		@rtype						   : Entity
		@return						   : return a new entity
		"""
		if param is None:
			param = {}
		
		if not param.has_key( "modelNumber" ): # 如果外部有定义则不处理
			modelNumbers = self.getEntityProperty( "modelNumber" )
			modelScales = self.getEntityProperty( "modelScale" )
			if len( modelNumbers ):
				index = random.randint( 0, len(modelNumbers) - 1 )
				param["modelNumber"] = modelNumbers[ index ]
				if len( modelScales ) ==  1:
					param["modelScale"] = float( modelScales[ 0 ] )
				elif len( modelScales ) >= ( index + 1 ):
					param["modelScale"] = float( modelScales[ index ] )
				else:
					param["modelScale"] = 1.0
			else:
				param["modelNumber"] = ""
				param["modelScale"] = 1.0
		elif not param.has_key( "modelScale" ):# 如果外部有定义则不处理
			if self.hasEntityProperty( "modelScale" ):
				modelScales = self.getEntityProperty( "modelScale" )
				if len( modelScales ) == 1:
					param["modelScale"] = float( modelScales[ 0 ] )
				else:
					param["modelScale"] = 1.0
			else:
				param["modelScale"] = 1.0

		return GameObject.createLocalBase( self, param )

	def createBaseAnywhere( self, param = None, callback = None ) :
		"""
		create an entity and loacte it in the map
		@type				param	   : dict
		@param				param	   : property dictionary
		"""
		if param is None:
			param = {}
		
		if not param.has_key( "modelNumber" ): # 如果外部有定义那么不进行更新
			modelNumbers = self.getEntityProperty( "modelNumber" )
			if len( modelNumbers ):
				param["modelNumber"] = modelNumbers[ random.randint( 0, len(modelNumbers) - 1 ) ]
			else:
				param["modelNumber"] = ""
		GameObject.createBaseAnywhere( self, param, callback )
