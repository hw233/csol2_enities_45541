# -*- coding: gb18030 -*-
#
from NPCObject import NPCObject
import csdefine

class CollectPoint( NPCObject ):
	"""
	CollectPoint������
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
		# ע����������Բ���Ҫ��ȡ���ڴ�����ʱ���ɳ���������ֱ�Ӵ�����
		#self.setEntityProperty( "rediviousTime", sect.readFloat( "rediviousTime" ) )	# ��������һ��ʱ���ָ���ʾ
