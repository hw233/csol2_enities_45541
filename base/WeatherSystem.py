# -*- coding: gb18030 -*-
#
# $Id: WeatherSystem.py,v 1.5 2007-09-24 07:07:59 phw Exp $

"""	  
HZM ����ϵͳ��BASE����
"""

import BigWorld
from interface.GameObject import GameObject

class WeatherSystem( BigWorld.Base, GameObject ):
	"""
	HZM ����ϵͳ���BASE����
	"""
	def __init__( self, cellargs=None ):
		BigWorld.Base.__init__( self )
		GameObject.__init__( self )

	def __del__( self ):
		BigWorld.Base.__del__( self )

# WeatherSystem.py


#
# $Log: not supported by cvs2svn $
# Revision 1.4  2005/03/29 10:21:37  huangzhiming
# ��һ�����µ�PYTHON�淶�޸����ĵ�
#
# Revision 1.3  2005/03/29 07:23:18  huangzhiming
# ��PYTHON�淶�����޸ģ�δȫ�����
#
# Revision 1.2  2005/03/29 03:06:30  huangzhiming
# ����LOG
#
