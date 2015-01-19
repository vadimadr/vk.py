# PyVk
Python vk.com api wrapper

##Usage
1. Import vkApi to your project:
```python
 from vk_api import VkApi
 ```
2. Create instance of VkApi class using one of following ways:
```python
token = '533bacf01e11f55b536a565b57531ac114461ae8736d6506a3' # Access token. See http://vk.com/dev/auth_mobile for more info
permissions = 'video,messages'
app_id = 3882511
api = VkApi(token, limit=5) # Default way. Limit is api calls per second rate
api = VkApi.from_redirect_uri(uri) # It will parse redirect url and create instance of class
api = VkApi.browser_auth(66748, permissions) # Interactive. Will open browser and ask to authorize your app, using oauth method
```
3. Use it! 
```python
durov_friends = api.method('users.get', user_id='durov', fields='status,education') # getting list of friends
success = api.method('status.set', text="i've just set my status via python!") # setting status
messages = api.load('wall.get', 1000, 100, owner_id=-10639516) # Get last 1000 posts from mdk.
ids = map(lambda x: 'wall-10639516_%d' % x['id'], messages) # convert to post id string
api.execute('wall.repost', ['object'], object=ids) # repost all
```
4. about differences between execute, load and method:
method just calls your method with all key word parameters using https
load should be used if real number of object more than could be got per 1 request
execute will apply your method to every object marked as list_var. Second parameter is a list of vars that should interpreted as list of params. 
