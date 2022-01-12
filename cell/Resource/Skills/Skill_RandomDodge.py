# -*- coding: gb18030 -*-
#
# $Id: Skill_RandomDodge.py,v 1.2 2008-02-28 08:25:56 kebiao Exp $

"""
"""
from Function import newUID
from SpellBase import *
from Skill_Normal import Skill_Normal

class Skill_RandomDodge( Skill_Normal ):
	"""

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

	def springOnCombatCalc( self, caster, receiver, skill ):
		"""
		virtual method.
		��ս������ʱ...����˼��ÿ����ʩչ�ļ��ܵ���Ŀ�����ʱ��Ҫ����ս�����㣬�������attach�ڡ�����ʱ���������ļ����б��е�ÿһ�����ܵĴ˷�����

		�����ڣ�����������ͨ�������߽��������ܹ���ʱ�����ܼ�ֵ+40
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		@param   skill: ����ʵ��
		@type    skill: Entity
		"""
		pass
			
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.HP_Max_value += self._param[0]
		ownerEntity.calcHPMax()
		ownerEntity.appendAttackerCombatCalc( self )
		
	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.HP_Max_value -= self._param[0]
		ownerEntity.calcHPMax()
		ownerEntity.removeAttackerCombatCalc( self.getUID() )
		
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
		obj = Skill_RandomDodge()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj
			
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/08/23 01:53:03  kebiao
# �������
#
# 
#