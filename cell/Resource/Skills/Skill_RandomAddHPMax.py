# -*- coding: gb18030 -*-
#
# $Id: Skill_RandomAddHPMax.py,v 1.2 2007-08-23 01:32:36 kebiao Exp $

"""
"""
from Function import newUID
from SpellBase import *
from Skill_Normal import Skill_Normal

class Skill_RandomAddHPMax( Skill_Normal ):
	"""
	1001	�������� +$1	150	50	10.00%	50	90

	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Skill_Normal.__init__( self )
		self._param = 0
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.MP_Max_value += self._param
		ownerEntity.calcMPMax()
		
	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.MP_Max_value -= self._param
		ownerEntity.calcMPMax()
		
	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�
		
		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : self._param }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		"""
		obj = Skill_RandomAddHPMax()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj
			
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/08/15 04:58:55  kebiao
# �������
#
# 
#