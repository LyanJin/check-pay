import time

import requests


def while_check(url, loop=0, delta=0.1):
    idx = 1
    while True:
        rst = requests.get(url)
        try:
            data = rst.json()
        except:
            data = rst.text
        print(url)
        print(idx, rst.status_code, data)
        time.sleep(delta)
        if idx >= loop:
            break
        idx += 1


if __name__ == '__main__':
    # domain = 'epay1001.com'
    domain = 'epay12306.com'

    check_times = 6

    while_check('https://backoffice.{}/api/backoffice/v1/health/check'.format(domain), check_times)
    while_check('https://merchantoffice.{}/api/merchantoffice/v1/health/check'.format(domain), check_times)
    while_check('https://callback.{}/api/callback/v1/health/check'.format(domain), check_times)
    while_check('https://gateway.{}/api/gateway/v1/health/check'.format(domain), check_times)

    while_check('https://cashier-test.{}/api/cashier/v1/health/check'.format(domain), check_times)
    while_check('https://cashier-qf2.{}/api/cashier/v1/health/check'.format(domain), check_times)
    while_check('https://cashier-qf3.{}/api/cashier/v1/health/check'.format(domain), check_times)
    while_check('https://zyproxy01.{}/api/cashier/v1/health/check'.format(domain), check_times)
    while_check('https://cop.{}/api/cashier/v1/health/check'.format(domain), check_times)

    while_check('https://cashier-test.{}/api/cashier/v1/health/load/balance/check'.format(domain), check_times)
    while_check('https://cashier-qf2.{}/api/cashier/v1/health/load/balance/check'.format(domain), check_times)
    while_check('https://cashier-qf3.{}/api/cashier/v1/health/load/balance/check'.format(domain), check_times)
    while_check('https://zyproxy01.{}/api/cashier/v1/health/load/balance/check'.format(domain), check_times)
    while_check('https://cop.{}/api/cashier/v1/health/load/balance/check'.format(domain), check_times)

    #
    # while_check('https://cashier-test.{}/api/cashier/v1/health/domain/check'.format(domain))
    # while_check('https://cashier-qf2.{}/api/cashier/v1/health/domain/check'.format(domain))
    # while_check('https://cashier-qf3.{}/api/cashier/v1/health/domain/check'.format(domain))
    #
    # while_check('https://backoffice.{}/api/backoffice/v1/health/http/proxy/check'.format(domain))
    # while_check('https://backoffice.{}/api/backoffice/v1/health/update/channel/limit/cache'.format(domain))
