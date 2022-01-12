# -*- coding: gb18030 -*-

# this module implement the VehicleTrainer class
# written by gjx 2009-06-13
#
# 从Trainer再抽象出VehicleTrainer是有必要的，客户端需要
# 根据不同类型的训练师来进行相应的界面表现。

from Trainer import Trainer

class VehicleTrainer( Trainer ) :
	pass