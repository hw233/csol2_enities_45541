# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpellBase import Buff
from Function import newUID

class Buff_Individual ( Buff ):
	"""
	��Ҹ�����ص�buff�����ĳ��buff����Ҫ����һЩ���ÿ����ҵĸ��Ի����ݣ���ô��̳д�buff
	���̳д�buff��Ҳ����ȡ������ʩ��ֱ�Ӵ�����Ҹ��Ի����ݻ��������ʵ�������⣬�����CSOL-10239
	by mushuang
	"""
	def __init__( self ):
		"""
		"""
		self._packedIndividualData = {}
	
	def __clone( self ):
		"""
		��¡����
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )
		return obj
		
	
	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�
		
		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		
		
		ע��:������client����û��ʲô������Ҫ������䣬���Ǹ��ٽ�������˷�����Ȼ��BigWorld��������һ�Σ����Ա��������
		���ǰ�����ȷ�Ĳ�����д�������������BigWorldΪʲô��Ҫ�ڿͻ��˵��ô˷����Լ��˷�����������ݱ������������
		�������ﱸעһ�£�лл�� by mushuang
		"""
		DEBUG_MSG( "client addToDict called!"  )
		
		
		# ����Ư��ƿ������������ݵ�������û��ʲôʵ�����壬ԭ����˷�����ע��
		if isDebuged:
			 self._packedIndividualData[ "debug2011-1-17 16:15" ] = \
			 "If you saw this data somewhere else, it means BigWorld spreads data using this method!"
		
		return { "param" : self._packedIndividualData }
	
	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		ע��:�����̳��ˡ�Buff_Individual���࣬һ����Ҫ�������������
		
		@type data: dict
		"""
		obj = self.__clone()
		
		DEBUG_MSG( "Restoreing object of class: %s"%obj.__class__ )
		
		# ���������ġ���ͬ���������ݡ���ȷ���õ������ֶ���ȥ
		for key,val in data["param"].iteritems():
			assert hasattr( obj, key ),"Can't find attribute: %s in this object!"%key
			DEBUG_MSG( "Setting attr:%s to %s"%( key, val ) )
			setattr( obj, key, val )		
			
		return obj
	

	