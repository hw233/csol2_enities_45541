# -*- coding: gb18030 -*-
#
# $Id: Spell_Teleport.py,v 1.3 2007-12-17 01:36:36 kebiao Exp $

"""
���ͼ��ܻ���
"""

from SpellBase import *
import csstatus
import BigWorld
import csconst

class Spell_Teleport( Spell ):
	"""
	���ͼ��ܻ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self._map = "" #��ͼ����
		self._direction = ( 0.0, 0.0, 0.0 ) #����
		self._position = ( 0.0, 0.0, 0.0 ) #λ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._map =  dict[ "param1" ]   	#��ͼ����
		s = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) .split(";") 	#λ��
		self._position = ( float( s[0] ), float( s[1] ), float( s[2] ), ) #��ô�� ������ͳһ�����ù����µ�
		s = ( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else "" ) .split(";") 	#����
		self._direction =  ( float( s[0] ), float( s[1] ), float( s[2] ), )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		spaceLabel = BigWorld.getSpaceDataFirstForKey( receiver.spaceID, csconst.SPACE_SPACEDATA_KEY )
		if spaceLabel == self._map:
			receiver.position = self._position
			return
		receiver.gotoSpace( self._map, self._position, self._direction )

# $Log: not supported by cvs2svn $
# Revision 1.2  2007/12/06 04:21:33  kebiao
# �޸Ķ�ȡ���÷�ʽ
#
# Revision 1.1  2007/12/03 06:29:01  kebiao
# no message
#