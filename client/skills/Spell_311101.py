# -*- coding: gb18030 -*-
#
# $Id: Spell_311101.py,v 1.3 2008-03-10 01:01:25 kebiao Exp $

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus


class Spell_311101( Spell ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/01/05 03:47:30  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
# Revision 1.1  2008/01/04 03:41:01  kebiao
# no message
#
#