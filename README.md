# Pixpie Python SDK #

https://www.pixpie.co

## What is it for? ##

Pixpie is a Platform as a Service for image optimization and manipulation.

Python SDK provides API methods implementation to access Pixpie REST API to use it for server-to-server integration. 

## How to start? ##

Check [Getting started](https://pixpie.atlassian.net/wiki/display/DOC/Getting+started) guide and [register](https://cloud.pixpie.co/registration) your account

## Add dependency ##

Include pixpie egg to pip requirements file.

``` gradle

-e git://github.com/PixpieCo/PythonSDK.git#egg=pixpie

``` 

Import API to project files:

``` python

  from pixpie.api import ServerApi
  
``` 

### Authentication ###

To authenticate 

``` python

  pixpieAPI = ServerApi('com.example.SomeApp', '41bc32fde0d3ed6927b6f54sdc')

  # raises RuntimeError('SDK authentication failed')

``` 

### Upload ###

There are a few ways how to upload local images to Pixpie cloud.
- through [Web panel](https://pixpie.atlassian.net/wiki/display/DOC/Upload+image)
- using [REST API](https://pixpie.atlassian.net/wiki/display/DOC/Upload)
- using [SDKs](https://pixpie.atlassian.net/wiki/display/DOC/Client+and+server+SDKs)

``` python
  
  # methods description
  ServerApi.upload_image(local_image_path, inner_path)
  ServerApi.upload_image_async(local_image_path, inner_path)
  
  # call
  result = pixpieAPI.upload_image('/some_local_image/dog.jpg', '/pixpie_path/dog.jpg')
  result = pixpieAPI.upload_image_async('/some_local_image/dog.jpg', '/pixpie_path/dog.jpg')  
  # async - respond as soon as server received image's body, or when image was fully saved 
   
  # check result code
  # response.status_code
  
```

### Get remote (third party) and local (uploaded) images ###

``` python

  ServerApi.get_image_url(self, image_path, width, height, quality, webp=False, crop=CropAlignType.DEFAULT)
  ServerApi.get_remote_image_url(self, url, width, height, quality, webp=False, crop=CropAlignType.DEFAULT)
  
  ServerApi.get_image(self, image_path, width, height, quality, webp=False, crop=CropAlignType.DEFAULT)
  ServerApi.get_remote_image(self, url, width, height, quality, webp=False, crop=CropAlignType.DEFAULT)
  
```

### Delete ###

``` python

  ServerApi.batch_delete(self, images_to_delete, folders_to_delete)

```

- images - list of relative paths of images
- folders - list of relative paths of folders


### List items ###

``` python

  ServerApi.list_items(self, inner_path)

```

- innerPath - relative path to folder in Pixpie cloud

## License

Pixpie Python SDK is available under the Apache 2.0 license.

    Copyright (C) 2015,2016 Pixpie

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

