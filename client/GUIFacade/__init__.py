# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.38 2008-06-09 09:24:00 kebiao Exp $

"""
GUIFacade 应该即是所有facade的集合，也是GUI注册消息的地方，同时是其它entity发布消息的地方。
"""
import BigWorld as bw
from event.EventCenter import *
from GossipFacade import *
from QuestFacade import *
from QuestLogFacade import *
from LearnSkillFacade import *
from TeamFacade import *
from MerchantFacade import *
from ItemsBagFacade import *
from RoleFacade import *
from SwapInvoiceFacade import *
from BDuffFacade import *
from FriendFacade import *
from BankFacade import *
from TongFacade import *
from RewardQuestLogFacade import *

def modelReset():
	"""
	每一个角色进入游戏后都必须调用这个重置方法,确保是重新开始,而不会残留旧有的数据。
	"""
	GossipFacade.reset()
	QuestFacade.reset()
	QuestLogFacade.reset()
	LearnSkillFacade.reset()
	TeamFacade.reset()
	MerchantFacade.reset()
	ItemsBagFacade.reset()
	RoleFacade.reset()
	SwapInvoiceFacade.reset()
	BDuffFacade.reset()
	FriendFacade.reset()
	BankFacade.reset()
	TongFacade.reset()
	RewardQuestLogFacade.reset()

# init in first import
modelReset()
