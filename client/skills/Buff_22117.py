# -*- coding: gb18030 -*-
#
# $Id: Spell_Teach.py,v 1.6 2008-07-15 04:08:27 kebiao Exp $

"""
SpellTeach�����ࡣ
"""
import math
from bwdebug import *
from SpellBase import *
from Function import Functor
import BigWorld
import skills as Skill
import csdefine
import csstatus
import csconst
import csstatus_msgs as StatusMsgs

class Buff_22117( Buff ):
	"""
	�౶���齱�� ɱ��ʱ�������������õľ�����Ǳ�����һ��
	"""
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Buff.__init__( self )
		self.param = 0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def getDescription( self ):
		sexp = str( self.param["p1"] ) + "%"
		return self._datas[ "Description" ] % sexp
		
	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_22117()
		obj.__dict__.update( self.__dict__ )
		obj.param = data["param"]
		return obj

#
# $Log: not supported by cvs2svn $
#
#