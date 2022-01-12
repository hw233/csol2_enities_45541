# -*- coding: gb18030 -*-
#
from NPCObject import NPCObject
import csdefine

class CollectPoint( NPCObject ):
	"""
	CollectPoint基础类
	"""
	
	def __init__( self ):
		"""
		"""
		
		NPCObject.__init__( self )
	
	# ----------------------------------------------------------------
	# overrite method / protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, sect ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initializes.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" file
		@ptype			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		NPCObject.onLoadEntityProperties_( self, sect )
		# 注：下面的属性不需要读取，在创建的时候由出生点配置直接传进来
		#self.setEntityProperty( "rediviousTime", sect.readFloat( "rediviousTime" ) )	# 用于隐藏一段时间后恢复显示
