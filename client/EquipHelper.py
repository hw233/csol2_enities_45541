# -*- coding: gb18030 -*-

"""
仅限客户端使用的装备数值助手类 by mushuang
"""

# @calcIntensifyInc: 计算某装备属性因强化导致的加值
# @x: EquipExp对象的绑定方法
# @return: 装备因强化导致的加值
calcIntensifyInc = lambda x: x( ignoreObey = True, ignoreZipPercent = True, ignoreWieldCalc = True ) - x( ignoreObey = True, ignoreIntensify = True, ignoreZipPercent = True, ignoreWieldCalc = True )

# @calcObeyInc: 计算某装备属性因认主导致的价值
# @x: EquipExp对象的绑定方法
# @return: 装备因认主导致的加值
calcObeyInc = lambda x: x( ignoreIntensify = True, ignoreZipPercent = True, ignoreWieldCalc = True ) - x( ignoreIntensify = True, ignoreObey = True, ignoreZipPercent = True, ignoreWieldCalc = True )

# @calcTotal: 计算某装备属性的总值（即，包含基本属性以及强化、认主之后的加值）
# @x: EquipExp对象的绑定方法
# @return: 某装备属性的总值
calcTotal = lambda x: x( ignoreZipPercent = True, ignoreWieldCalc = True )