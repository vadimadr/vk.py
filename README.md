# vk.py
Python vk.com api wrapper

##Usage
####Import vkApi to your project:
```python
 from vk import VkApi
 ```
####Create instance of VkApi class using one of following ways:
```python
token = '533bacf01e11f55b536a565b57531ac114461ae8736d6506a3' # Access token. See http://vk.com/dev/auth_mobile for more info
permissions = 'status,wall'
app_id = 3882511
api = VkApi(token, limit=5) # Default way. Limit is api calls per second rate
api = VkApi.from_redirect_uri(uri) # It will parse redirect url and create instance of class
api = VkApi.browser_auth(66748, permissions) # Interactive. Will open browser and ask to authorize your app, using oauth method
```
####Use it! 
```python
durov_friends = api.method('friends.get', user_id=1, fields='status,education') # getting list of friends
success = api.status.get(text="i've just set my status via python!") # setting status
messages = api.load('wall.get', 1000, 100, owner_id=-10639516) # Get last 1000 posts from mdk.
ids = map(lambda x: 'wall-10639516_%d' % x['id'], messages) # convert to post id string
api.apply('wall.repost', ['object'], object=ids) # repost all
```
####About differences between apply, load and explicit method calling:
* Explicit method calling (like api.users.get) just calls your method with all keyword parameters using https
* load should be used if real number of object more than could be got per 1 request
* apply calls your method with each object passed in a sequence. Second positional argument is a list of keyword parameters that should be interpreted as a sequence. 

##List of all methods can be found at http://vk.com/dev/methods
