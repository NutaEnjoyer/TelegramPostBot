import requests
import time
import hashlib


terminal = '1683729523569DEMO'
password = '4jdzbjv3ve9su3f2'


def create_order(amount):

    order_id = str(round(time.time()))

    url = 'https://securepay.tinkoff.ru/v2/Init'

    json = {
        "TerminalKey": terminal,
        "Amount": amount,
        "OrderId": order_id,
        "Description": "Подарочная карта на 1000.00 рублей",
    }

    response = requests.post(url=url, json=json)

    return response.json()


def get_order_info(order_id):
    pre_hash = f'{order_id}{password}{terminal}'.encode()
    hash = hashlib.sha256(pre_hash).hexdigest()
    token = hash

    url = 'https://securepay.tinkoff.ru/v2/CheckOrder'

    json = {
        "TerminalKey": terminal,
        "OrderId": order_id,
        "Token": token,
    }

    response = requests.post(url=url, json=json)

    return response.json()

def confirm_order(payment_id):
    pre_hash = f'{password}{payment_id}{terminal}'.encode()
    hash = hashlib.sha256(pre_hash).hexdigest()
    token = hash

    url = 'https://securepay.tinkoff.ru/v2/Confirm'

    json = {
        "TerminalKey": terminal,
        "PaymentId": payment_id,
        "Token": token,
    }

    response = requests.post(url=url, json=json)

    return response.json()

def main():
    # order = create_order(100000)
    # print(order)
    info = get_order_info('1690316907.1250572')
    print(info)

    # info = confirm_order('3039384086')
    # print(info)



if __name__ == '__main__':
    main()