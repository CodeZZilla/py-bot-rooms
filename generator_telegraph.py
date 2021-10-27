import api
from telegraph import Telegraph

telegraph = Telegraph()

telegraph.create_account(short_name='rooms', author_name='Rooms Bot')


def get_url_by_id_apartment(id_apartment):
    apartment = api.find_apartment(id_apartment)[0]
    img_html = ''
    for img in apartment["images"]:
        img_html = img_html + f'<img src="{img}">'
    p_text = f'<p>{apartment["category"]} {apartment["propertyType"]} ({apartment["type"]})</p>'
    p_date = f'<p>Дата публикации: {apartment["creationDate"]}</p>'
    p_rooms = f'<p>Комнат: {apartment["rooms"]}</p>'
    p_price = f'<p>Цена: {apartment["price"]["value"]} {apartment["price"]["currency"]}</p>'
    p_location = f'<p>Локация: {apartment["location"]["country"]} {apartment["location"]["region"]} ' \
                 f'{apartment["location"]["locationName"]} {apartment["location"]["subLocationName"]} ' \
                 f'{apartment["location"]["nonAdminSubLocality"]} {apartment["location"]["address"]} ' \
                 f'{apartment["location"]["house"]} \n Метро: {apartment["location"]["metro"]["name"]} ' \
                 f'{apartment["location"]["metro"]["distance"]}</p>'
    p_number = f'<p>Номер телефона: {apartment["salesAgent"]["phone"]}</p>'
    a_url = f'<a href="{apartment["url"]}">ССЫЛКА</a>'
    p_description = f'<p>{apartment["description"]}</p>'
    response = telegraph.create_page(
        apartment['category'] + ' ' + apartment['propertyType'],
        html_content=p_text + p_date + p_rooms + p_price + p_location + p_number + p_description + a_url + img_html
    )
    return f'https://telegra.ph/{response["path"]}'

