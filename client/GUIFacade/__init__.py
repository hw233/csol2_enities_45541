# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.38 2008-06-09 09:24:00 kebiao Exp $

"""
GUIFacade Ӧ�ü�������facade�ļ��ϣ�Ҳ��GUIע����Ϣ�ĵط���ͬʱ������entity������Ϣ�ĵط���
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
	ÿһ����ɫ������Ϸ�󶼱������������÷���,ȷ�������¿�ʼ,������������е����ݡ�
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
