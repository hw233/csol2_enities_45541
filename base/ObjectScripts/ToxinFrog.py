# -*- coding: gb18030 -*-
#
# 2009-05-25 SongPeifang
#
"""
ToxinFrog��
"""

from Monster import Monster
import Love3
import csdefine
import BigWorld

class ToxinFrog( Monster ):
	"""
	ǧ�궾�ܽű�
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Monster.__init__( self )

	def onFrogDieNotify( self, notifyStr ):
		"""
		����֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( notifyStr, [] )