# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.5 2008-02-22 01:40:03 yangkai Exp $

"""
"""
from ItemDataList import ItemDataList

def instance():
	return ItemDataList.instance()


#
# $Log: not supported by cvs2svn $
# Revision 1.4  2007/10/29 04:30:39  yangkai
# 删除：
# from OMergeMachine import OMergeMachine
#
# Revision 1.3  2007/01/23 04:06:03  kebiao
# 增加  OMergeMachine 支持
#
# Revision 1.2  2006/08/18 07:01:46  phw
# 加入：from EquipEffects import EquipEffects
#
# Revision 1.1  2006/08/09 08:21:30  phw
# no message
#
#