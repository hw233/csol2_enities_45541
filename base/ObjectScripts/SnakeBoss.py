# -*- coding: gb18030 -*-
#
# 2009-05-25 SongPeifang
#
"""
SnakeBoss��
"""

from Monster import Monster
import Love3
import csdefine
import BigWorld

class SnakeBoss( Monster ):
	"""
	�������ű�
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Monster.__init__( self )