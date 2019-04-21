from imgurpython import ImgurClient
from config import client_id, client_secret, album_id, access_token, refresh_token

def pic_to_web(pic):
    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    config = {
        'album': album_id,
        'name': 'test-name!',
        'title': 'test-title',
        'description': 'test-description'
    }
    print("Uploading image... ")
    image = client.upload_from_path(pic, config=config, anon=False)
    print(image['link'])
    return image['link']
    print("Done")

if __name__ == "__main__":       
    pic_to_web()