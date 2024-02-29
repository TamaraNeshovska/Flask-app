import requests
def telegram_funkcija(dics):
    telegram_auth_token = ""
    telegram_group_id = "statisticki_podatoci"

    # msg = "Imajte prekrasen den :) "
    msg = f"Srednata potrosuvacka na soodvetnite starosni grupi e:\nGrupa 18-24: {dics['18-24']}\nGrupa 25-30: {dics['25-30']}\nGrupa 31-36: {dics['31-36']}\nGrupa 37-47: {dics['37-47']}\nGrupa >47: {dics['47>']}"

    def send_msg_on_telegram(message):
        telegram_api_url = f"https://api.telegram.org/bot{telegram_auth_token}/sendMessage?chat_id=@{telegram_group_id}&text={message}"
        telegram_resp =requests.get(telegram_api_url)

        if telegram_resp.status_code ==200:
            print("INFO: notification has been sent to telegram")
        else:
            print("ERROR: could not send a message")
    send_msg_on_telegram(msg)

