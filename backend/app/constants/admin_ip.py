"""
后台访问白名单，不在白名单内的来源IP不允许访问
"""

ADMIN_IP_WHITE_LIST = [
    # 公网
    '103.119.131.16',  # 办公室IP
    '130.105.212.119',  # panda家里IP
    '112.209.119.254',  # kb 4318
    '180.190.115.74',   # lyle家
    '175.176.33.158',   # miko家
    '103.104.103.136',  # 办公室IP
]

MERCHANT_ADMIN_IP_LIST = [
    # 豪门商户后台IP
    "52.230.14.74",
]

MERCHANT_ADMIN_IP_LIST.extend(ADMIN_IP_WHITE_LIST)
