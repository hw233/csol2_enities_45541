# -*- coding: gb18030 -*-
#
# $Id: Space.py,v 1.10 2008-07-23 03:14:04 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import csdefine
import csconst
from bwdebug import *
from Space import Space

class SpaceMultiLine( Space ):
	"""
	用于控制SpaceNormal entity的脚本，所有有需要的SpaceNormal方法都会调用此脚本(或继承于此脚本的脚本)的接口
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Space.__init__( self )

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		Space.load( self, section )
		self.maxLine = section.readInt( "maxLine" )
		
	def packedDomainData( self, entity ):
		"""
		子类不允许继承这个接口， 请继承packedDomainData_
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		"""
		params = Space.packedDomainData( self, entity )
		lineNumber = entity.queryTemp( "lineNumber", -1 )
		ignoreFullRule = entity.queryTemp( "ignoreFullRule", False )
		currSpaceClassName = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		currSpaceLineNumber = entity.getCurrentSpaceLineNumber()
		
		# 如果有指定线号则添加标记
		if lineNumber != -1:
			params[ "lineNumber" ] = lineNumber
			
		# 忽略满员规则
		if ignoreFullRule:
			params[ "ignoreFullRule" ] = True
		
		params[ "currSpaceClassName" ] = currSpaceClassName
		params[ "currSpaceLineNumber" ] = currSpaceLineNumber
		params.update( self.packedMultiLineDomainData( entity ) )
		return params

	def packedMultiLineDomainData( self, entity ):
		"""
		virtual method.
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		return {}
		
		
#
# $Log: not supported by cvs2svn $
#
