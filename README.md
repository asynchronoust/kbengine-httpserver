# kbengine-httpserver
asynchronous httpserver for kbengine using fd operation api of kbengine 

为kbengine写的http server 框架。站在巨人肩膀上面，借鉴收纳了[tornado](https://github.com/tornadoweb/tornado) 和 [sanic](https://github.com/huge-success/sanic)的代码特性

## features
* 异步httpserver
* 内嵌于kbengine引擎
* 使用 kbengine 提供的 `registerReadFileDescriptor` `deregisterReadFileDescriptor` 等和读写文件描述符的API
* 类tornado 和 sanic 的用法，结合两个框架的内容

# Quick Start

类似于python tornado的使用方式，看下面的例子


```
from httpserver.app import Application, RequestHandler


class IndexHandler(RequestHandler):

    def get(self, *args, **kwargs):
        print("index, get")
        self.write_text("index ok")


class HomeHandler(RequestHandler):

    def get(self, *args, **kwargs):
        print("home, get")
        self.write_text("home ok")

    def post(self, *args, **kwargs):
        # DEBUG_MSG("post body, %s" % str(self.request.json))
        self.write_json(self.request.json)

url_map = [
    ("/index", IndexHandler),
    ("/home", HomeHandler)
]
app = Application(url_map)
app.run("0.0.0.0", 9191)

```

主要使用步骤：

* 继承`RequestHandler`类，需要实现哪个HTTP method就赋写哪个函数(这些和tornado的使用方式类似)
    * get, post, put, delete 等等
* 此类有`self.request`成员属性是Request对象，可以获取请求的各种数据。更多具体请看Request对象源码。此对象借鉴了`sanic`框架的思路
    * `request.json`
    * `request.args`: 
        * args.get(key)
        * args.get_list(key)
    * `request.query_string`
    * `request.path`
* 回给客户端请求使用下面几个函数。可以在去做一个异步的操作，然后在回调函数中去给client 回http包
    * write_json
    * write_text
    * write_raw
* 定义 url 和 handler的对应关系，示例中的 `url_map`
* 生成app实例，app.run() 就运行起此httpserver

**说明：**

* 现在没有出pip包，如果要放到工程里面的话，直接把`httpserver`目录拷贝到自己工程中`assets/scripts/server_common`目录下面

# 完善与改进

* 现在的router还不完善，url中现在只支持具体的url，不支持url中带不定参数给handler函数，也不支持url正则匹配
* 如果要做 html template渲染，直接使用jinja2的包即可，自己封装一下渲染后的结果然后`write_text`









