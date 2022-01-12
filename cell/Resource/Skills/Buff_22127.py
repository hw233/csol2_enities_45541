# -*- coding: gb18030 -*-
#
# $Id: Buff_108001.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csstatus
import csdefine
import random
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

										 
class Buff_22127( Buff_Normal ):
	"""
	example:����

	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.currModelNumber = ""
		self.currModelScale = 1.0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = dict[ "Param1" ]
		self._p2 = float( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 1 )

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		
		buffData[ "skill" ] = self.createFromDict( self.addToDict() )
		self = buffData[ "skill" ]
		
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.begin_body_changing( self._p1, self._p2 )
		else:
			self.currModelNumber = receiver.modelNumber
			self.currModelScale = receiver.modelScale
			receiver.modelNumber = self._p1
			receiver.modelScale = self._p2

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.begin_body_changing( self._p1, self._p2 )
		else:
			self.currModelNumber = receiver.modelNumber
			self.currModelScale = receiver.modelScale
			receiver.modelNumber = self._p1
			receiver.modelScale = self._p2

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.end_body_changing( receiver.id, "" )
		else:
			receiver.modelNumber = self.currModelNumber
			receiver.modelScale = self.currModelScale

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�
		
		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : { "currModelNumber" : self.currModelNumber, "currModelScale" : self.currModelScale } }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		"""
		obj = Buff_22127()
		obj.__dict__.update( self.__dict__ )
		self.currModelNumber = data["param"]["currModelNumber"]
		self.currModelScale = data["param"]["currModelScale"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
#
# $Log: not supported by cvs2svn $
#
# 
#