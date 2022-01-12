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
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		GameObject.onLoadEntityProperties_( self, section )

		self.setEntityProperty( "uname", 		section.readString( "uname" ) )					# ��������
		self.setEntityProperty( "title",		section.readString( "title" ) )					# ͷ��

		flagSection = section["flags"]
		flag = 0
		if flagSection:
			flags = flagSection.readInts( "item" )
			for v in flags: flag |= 1 << v
		# entity�ı�־���ϣ����Ƿ�ɽ��ס��Ƿ��������Ƿ��ܺϳ�װ���ȵȣ�ENTITY_FLAG_*
		self.setEntityProperty( "flags",	flag )

		self.setEntityProperty( "walkSpeed",	int( section.readFloat( "walkSpeed" ) * csconst.FLOAT_ZIP_PERCENT ) )				# ���ٶ�
		self.setEntityProperty( "runSpeed",		int( section.readFloat( "runSpeed" ) * csconst.FLOAT_ZIP_PERCENT ) )				# ���ٶ�
		
		modelNumbers = [ e.lower() for e in section["modelNumber"].readStrings( "item" ) ]				# ģ�ͱ���б�
		self.setEntityProperty( "modelNumber",	modelNumbers )
		
		modelScales = section[ "modelScale" ].readStrings( "item" )    # ģ��ʹ�ñ����б�
		self.setEntityProperty( "modelScale",	modelScales )
		if section.has_key( "nameColor" ):
			nameColor = section.readInt( "nameColor" )					#ͷ��������ɫ���
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
		
		if not param.has_key( "modelNumber" ): # ����ⲿ�ж����򲻴���
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
		elif not param.has_key( "modelScale" ):# ����ⲿ�ж����򲻴���
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
		
		if not param.has_key( "modelNumber" ): # ����ⲿ�ж�����ô�����и���
			modelNumbers = self.getEntityProperty( "modelNumber" )
			if len( modelNumbers ):
				param["modelNumber"] = modelNumbers[ random.randint( 0, len(modelNumbers) - 1 ) ]
			else:
				param["modelNumber"] = ""
		GameObject.createBaseAnywhere( self, param, callback )
