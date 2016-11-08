import time
import requests
import hashlib

from enum import Enum

PATH_AUTH_SDK = 'authentication/token/server_sdk'

PATH_IMAGE_UPLOAD = 'images/upload'
PATH_IMAGE_UPLOAD_ASYNC = 'async/images/upload'

PATH_GET_IMAGE = 'local'
PATH_GET_REMOTE_IMAGE = 'remote'

PATH_BATCH_DELETE = 'storage/delete/batch'
PATH_LIST_ITEMS = 'storage/list'

sdk_version = '1.0.0'


class CropAlignType(Enum):

    DEFAULT = ''
    TOP = 'top'
    BOTTOM = 'bottom'
    RIGHT = 'right'
    LEFT = 'left'
    TOP_RIGHT = 'top_right'
    TOP_LEFT = 'top_left'
    BOTTOM_RIGHT = 'bottom_right'
    BOTTOM_LEFT = 'bottom_left'

class ServerApi(object):

    def __init__(self, reverse_url_id, secret_key, salt='yuuRiesahs3niet7thac', scheme='https', host='api.pixpie.co', port=9443):
        self.reverse_url_id = reverse_url_id
        self.secret_key = secret_key
        self.salt = salt
        self.address = scheme + '://' + host + ':' + str(port)
        self.__authenticate()

    # relative image_path in Pixpie system
    def get_image_url(self, image_path, width, height, quality, webp=False, crop=CropAlignType.DEFAULT):
        return self.__generate_url(PATH_GET_IMAGE, image_path, width, height, quality, webp, crop)

    def get_image(self, image_path, width, height, quality, webp=False, crop=CropAlignType.DEFAULT):
        return requests.get(self.get_image_url(image_path, width, height, quality, webp, crop))

    # full URL with http:// or https://
    def get_remote_image_url(self, url, width, height, quality, webp=False, crop=CropAlignType.DEFAULT):
        return self.__generate_url(PATH_GET_REMOTE_IMAGE, url, width, height, quality, webp, crop)

    def get_remote_image(self, url, width, height, quality, webp=False, crop=CropAlignType.DEFAULT):
        return requests.get(self.get_image_url(url, width, height, quality, webp, crop))

    def upload_image(self, local_image_path, inner_path):

        url = self.__join_url(self.address, PATH_IMAGE_UPLOAD, self.reverse_url_id, inner_path)

        files = {'image': open(local_image_path, 'rb')}

        return self.__do_authorized_post(url, files)

    def upload_image_async(self, local_image_path, inner_path):

        url = self.__join_url(self.address, PATH_IMAGE_UPLOAD_ASYNC, self.reverse_url_id, inner_path)
        files = {'image': open(local_image_path, 'rb')}

        return self.__do_authorized_post(url, files)

    def list_items(self, inner_path):
        url = self.__join_url(self.address, PATH_LIST_ITEMS, self.reverse_url_id, inner_path)

        headers = self.__get_authorization_header()
        response = requests.get(url, headers=headers)
        return response

    def batch_delete(self, images_to_delete, folders_to_delete):
        url = self.__join_url(self.address, PATH_BATCH_DELETE, self.reverse_url_id)

        json_data = {'images': images_to_delete, 'folders': folders_to_delete}

        return self.__do_authorized_delete(url, json_data)

    def dir_exists(self, parent_folder, inner_folder):

        response = self.list_items(parent_folder)

        if response.status_code == 403 or response.status_code == 404 or response.status_code == 500:
            return None

        if response.status_code == 200:
            response_new = response.json()
            return inner_folder in response_new['folders']

    def __authenticate(self):
        timestamp = int(time.time())

        m = hashlib.sha256()
        m.update(self.secret_key)
        m.update(self.salt)
        m.update(str(timestamp))

        url = self.__join_url(self.address, PATH_AUTH_SDK)
        req_params = {'reverseUrlId': self.reverse_url_id, 'hash': m.hexdigest(),
                      'timestamp': timestamp, 'serverSdkType': 2, 'sdkVersion': sdk_version}

        response = requests.post(url, params=req_params)

        if response.status_code != 200:
            raise RuntimeError('SDK authentication failed')

        auth_response = response.json()

        self.auth_token = auth_response['authToken']
        self.cdn_url = auth_response['cdnUrl']

    def __get_authorization_header(self):
        return {'pixpieAuthToken': self.auth_token}

    def __do_authorized_post_action(self, url, files=None, json=None):
        if files:
            return requests.post(url, headers=self.__get_authorization_header(), files=files)
        elif json:
            return requests.post(url, headers=self.__get_authorization_header(), json=json)
        else:
            return requests.post(url, headers=self.__get_authorization_header())

    def __do_authorized_post(self, url, files=None, json=None):

        response = self.__do_authorized_post_action(url, files, json)

        if response.status_code == 403:
            self.__authenticate()
            response = self.__do_authorized_post_action(url, files, json)

        return response

    def __do_authorized_delete(self, url, json=None):

        response = requests.delete(url, headers=self.__get_authorization_header(), json=json)

        if response.status_code == 403:
            self.__authenticate()
            response = requests.delete(url, headers=self.__get_authorization_header(), json=json)

        return response

    def __generate_url(self, path, image_path, width, height, quality, webp=False, crop=CropAlignType.DEFAULT):

        if webp:
            img_type = 'webp'
        else:
            img_type = 'def'

        params_string = ''

        params_string = self.__append_params_string('w_', width, params_string)
        params_string = self.__append_params_string('h_', height, params_string)
        params_string = self.__append_params_string('q_', quality, params_string)

        params_string = self.__append_crop(crop, params_string, width, height)

        if params_string == '':
            params_string = 'w_0,h_0'

        url = self.__join_url(self.cdn_url, path, img_type, params_string, image_path)

        print('Pixpie url: ' + url)

        return url

    def __append_params_string(self, param_prefix, param_value, params_string):

        if param_value is not None and param_value is not 0 and param_value is not '':
            if params_string is not '':
                params_string += ','
            params_string += param_prefix + str(param_value)

        return params_string

    def __append_crop(self, crop, params_string, width, height):
        if (width is not None and width is not 0 and width is not '') or (height is not None and height is not 0 and height is not ''):
            if crop.value is not '':
                params_string += ',' + 'c_' + crop.value
        return params_string

    def __join_url(self, *args):
        return '/'.join(args)