# -*- coding: gb18030 -*-
#
# $Id: Buff_1001.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import random
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_127006( Buff_Normal ):
	"""
	example: ������͵���ĳ��Ԫ�ؿ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		self._type = 0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )

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
		self._type = random.randint(0, 3)
		
		if self._type == 0:
			receiver.elem_huo_derate_ratio_base -= self._p1
			receiver.calcElemHuoDerateRatio()				# �����Ԫ�ؿ���
		elif self._type == 1:
			receiver.elem_xuan_derate_ratio_base -= self._p1
			receiver.calcElemXuanDerateRatio()				# ������Ԫ�ؿ���
		elif self._type == 2:
			receiver.elem_lei_derate_ratio_base -= self._p1
			receiver.calcElemLeiDerateRatio()				# ������Ԫ�ؿ���
		elif self._type == 3:
			receiver.elem_bing_derate_ratio_base -= self._p1
			receiver.calcElemBingDerateRatio()				# �����Ԫ�ؿ���

		buffData[ "skill" ] = self.createFromDict( self.addToDict() )
		
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
		self.doBegin( receiver, buffData )

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
		if self._type == 0:
			receiver.elem_huo_derate_ratio_base += self._p1
			receiver.calcElemHuoDerateRatio()				# �����Ԫ�ؿ���
		elif self._type == 1:
			receiver.elem_xuan_derate_ratio_base += self._p1
			receiver.calcElemXuanDerateRatio()				# ������Ԫ�ؿ���
		elif self._type == 2:
			receiver.elem_lei_derate_ratio_base += self._p1
			receiver.calcElemLeiDerateRatio()				# ������Ԫ�ؿ���
		elif self._type == 3:
			receiver.elem_bing_derate_ratio_base += self._p1
			receiver.calcElemBingDerateRatio()				# �����Ԫ�ؿ���

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�
		
		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : self._type }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		"""
		obj = Buff_127006()
		obj.__dict__.update( self.__dict__ )
		obj._type = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj
		
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#