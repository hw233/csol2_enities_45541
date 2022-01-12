# -*- coding: gb18030 -*-
# $Id: Smith.py,v 1.8 2007-10-29 04:27:18 yangkai Exp $

import BigWorld
from bwdebug import *
import NPC
import GUIFacade
import csstatus

class Smith( NPC.NPC ):
	"""An Founder class for client.
	铸造师NPC
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )


#
# $Log: not supported by cvs2svn $
# Revision 1.7  2007/06/19 08:53:15  huangyongwei
# 删除了 onOperatorMsg 函数，用统一消息实现同样功能
#
# Revision 1.6  2007/06/15 00:47:48  huangyongwei
# MERGE_STUFF_NEED_MATERIAL
# MERGE_STUFF_TYPE_ERROR
#
# 改为在 csstatus 中定义
#
# Revision 1.5  2007/06/14 10:32:35  huangyongwei
# 整理了全局宏定义
#
# Revision 1.4  2007/06/14 00:40:15  kebiao
# 材料合成
#
# Revision 1.3  2007/05/11 04:22:36  panguankong
# 修改显示提示
#
# Revision 1.2  2007/05/10 03:05:05  fangpengjun
# from Intensify_const import *
#
# Revision 1.1  2007/05/05 08:25:03  panguankong
# 添加文件
#
#