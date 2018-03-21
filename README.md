# Assignment 2

## Made By Himanshu Bhatia

We made a proxy server which acts as intermediate between server and client and hence controls the actions of client as well as provides fast service by stroring frequently used files in it.


### First part:

	Proxy server without cache.
	
	In this part we implemented simple proxy server which don't cache the files received from server but simply send it to client and on 		requesting again from it, it will again ask to server.


	Flow:

	Client -> Proxy -> Server (Request)
	Server -> Proxy -> Client (File)



### Second part:
	
	Added cache feature in proxy server.

	In this part cache feature was added in proxy server by which we were checking whether the file is there in cache or not as well as not 	modified in the server then only we were sending the file in cache. Otherwise we were requesting the server for the file and sending it 	to client.

	The cache size is limited and after the cache is full and if we want to insert any file in it then we will remove the file which was 		least recently used (LRU). We can also use other cache replacement policies.

	Flow:

	Client -> Proxy -> (If in cache and not modified in server return) else -> Server (Request)
	Server -> Proxy -> (If not in cache and space available then add it if not space remove LRU file and add it) -> Client (File)

### How to run the code?

>>> python server.py [port number] in one terminal tab
>>> python proxy.py in another terminal tab
>>> curl -iv --raw --proxy http://localhost:19999 http://localhost:[port number]/[file name] in other tab
