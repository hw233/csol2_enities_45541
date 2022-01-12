# -*- coding:gb18030 -*-

import BigWorld
import csdefine
from bwdebug import *
import random
from Buff_Normal import Buff_Normal
from Function import newUID


class Buff_99025( Buff_Normal ):
	"""
	�����buff���������ڽ�ɫ������ͷ��ģ�ͣ��������ͻ���������ҵ����֡���ᡢ�ƺŵ���Ϣ��
	"""
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.hairModelDict = eval( data["Param1"] )
		self.oldHairModelNum = 0

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.addFlag( csdefine.ROLE_FLAG_HIDE_INFO )
		self.oldHairModelNum = receiver.hairNumber
		try:
			hairModelNum = random.choice( self.hairModelDict[( receiver.getGender(),receiver.getClass() )] )
		except:
			EXCEHOOK_MSG( "player oldHairModelNum:%i" % self.oldHairModelNum )
			hairModelNum = 0
		receiver.hairNumber = hairModelNum
		
	def doReload( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.addFlag( csdefine.ROLE_FLAG_HIDE_INFO )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeFlag( csdefine.ROLE_FLAG_HIDE_INFO )
		receiver.hairNumber = self.oldHairModelNum
		
	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : self.oldHairModelNum }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_99025()
		obj.__dict__.update( self.__dict__ )
		obj.oldHairModelNum = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
		