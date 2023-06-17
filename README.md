> [HTTP2解析工具：HTTP2Parser](https://github.com/OzTamir/HTTP2Parser)
>
> [HTTP2库：dpkt.http2](https://gendignoux.com/blog/2017/05/30/dpkt-parsing-http2.html)
>
> [dpkt库定义说明](http://blog.chinaunix.net/uid-16865301-id-97353.html0)
>
> [HTTP2格式](http://www.blogjava.net/yongboy/archive/2015/03/20/423655.html)
>
> [HTTP2头压缩机制HPack](https://imququ.com/post/header-compression-in-http2.html)
>
> [HTTP2帧](https://halfrost.com/http2-http-frames-definitions/#toc-1)
>
> [Hypertext Transfer Protocol Version 2（RFC 7540）](https://httpwg.org/specs/rfc7540.html)
>
> [\_\_new\_\_与\_\_init\_\_的区别](https://zhuanlan.zhihu.com/p/35943253)
>
> [HTTP2更加详细介绍](https://github.com/halfrost/Halfrost-Field/blob/master/contents/Protocol)

## HTTP2解析

- 前言
- 一、HTTP2协议
- 二、HTTP2流与帧
  - 2.1 HTTP2流
  - 2.2 HTTP2帧
- 三、HTTP2头压缩机制
- 四、HTTP2帧详解
- 五、小结



### 前言

扩展HTTP2Parser源码使之具有解析HTTP2为可理解的格式。HTTP2的头压缩机制等，无法直接编码得到可理解的文本格式。并且，Python没有很好可用的解析库，当然，这有可能是我没找到。

在搜寻解析库过程中，发现dpkt已经实现http2协议，然而未找到Demo，仅阅读了dpkt.http2源码，没有发现其中解析的代码，所以没有进一步研究，感兴趣可以研究一下，也许可以实现呢！

最后回到HTTP2Parser项目研究并扩展



### 一、HTTP2协议

HTTP/2 enables a more efficient use of network resources and a reduced perception of latency by introducing <font color='#C660FB'>header field compression</font> and <font color='#C660FB'>allowing multiple concurrent exchanges</font> on the same connection.

Connection 连接:1 个 TCP 连接，包含 1 个或者多个 stream。所有通信都在一个 TCP 连接上完成，此连接可以承载任意数量的双向数据流。

Stream 数据流：一个双向通信的数据流，包含 1 条或者多条 Message。每个数据流都有一个唯一的标识符和可选的优先级信息，用于承载双向消息。

Message 消息：对应 HTTP/1.1 中的请求 request 或者响应 response，包含 1 条或者多条 Frame。

Frame 数据帧：最小通信单位，以二进制压缩格式存放内容。来自不同数据流的帧可以交错发送，然后再根据每个帧头的数据流标识符重新组装。

![img](https://pggo.oss-cn-beijing.aliyuncs.com/img/130_1.svg)

```
+-----------------------------------------------+
|                Length (24)                    |
+---------------+---------------+---------------+
|  Type (8)     |  Flags (8)    |
+-+-------------+---------------+-------------------------------+
|R|                Stream Identifier (31)                       |
+=+=============================================================+
|                  Frame Payload (0...)                       ...
+---------------------------------------------------------------+
```



### 二、HTTP2流与帧

#### 2.1 HTTP2流

见一

#### 2.2 HTTP2帧

（1）DATA 帧

DATA 帧(类型 = 0x0)可以传输与流相关联的任意可变长度的八位字节序列。例如，使用一个或多个 DATA 帧来承载 HTTP 请求或响应有效载荷。DATA 帧也可以包含填充。可以将填充添加到 DATA 帧用来模糊消息的大小。填充是一种安全的功能；

帧格式：

```
 +---------------+
 |Pad Length? (8)|
 +---------------+-----------------------------------------------+
 |                            Data (*)                         ...
 +---------------------------------------------------------------+
 |                           Padding (*)                       ...
 +---------------------------------------------------------------+
```

（2）HEADERS 帧

Flag字段有效

HEADERS 帧 (类型 = 0x1) 用于打开一个流，另外还带有 header block fragment 头块片段。HEADERS 帧可以在“空闲”，“保留(本地)”，“打开”或“半关闭(远程)”状态的流上发送。此帧专门用来传递 HTTP header(相当于 HTTP/1.1 中的 start line + header) 的。

```
+---------------+
|Pad Length? (8)|
+-+-------------+-----------------------------------------------+
|E|                 Stream Dependency? (31)                     |
+-+-------------+-----------------------------------------------+
|  Weight? (8)  |
+-+-------------+-----------------------------------------------+
|                   Header Block Fragment (*)                 ...
+---------------------------------------------------------------+
|                           Padding (*)                       ...
+---------------------------------------------------------------+
```

（3） PRIORITY 帧

没有定义任何 flag 标志

PRIORITY 帧(类型 = 0x2)指定了 stream 流的发送方的建议优先级。它可以在任何流的状态下发送，包括空闲或关闭的流。

```
+-+-------------------------------------------------------------+
|E|                  Stream Dependency (31)                     |
+-+-------------+-----------------------------------------------+
|   Weight (8)  |
+-+-------------+
```

（4）RST_STREAM 帧

没有定义任何 flag 标志

> 在 HTTP 1.X 中，一个连接同一时间内只发送一个请求，如果需要中途中止，直接关闭连接即可。但是在 HTTP/2 中，多个 Stream 会共享同一个连接。如果关闭连接会影响其他的 Stream 流，RST_STREAM 帧也就出现了，它允许立刻中止一个未完成的流。

RST_STREAM帧(类型 = 0x3)允许立即终止一个 stream 流。发送 RST_STREAM 以请求取消一个流或指示已发生错误的情况。

```
+---------------------------------------------------------------+
|                        Error Code (32)                        |
+---------------------------------------------------------------+
```

（5）SETTINGS 帧

SETTINGS 帧(类型 = 0x4)传递影响端点通信方式的配置参数，例如设置对端行为的首选项和约束。

SETTINGS 帧还用于确认收到这些参数。单独地，SETTINGS 参数也可以称为"设置"。

```
+-------------------------------+
|       Identifier (16)         |
+-------------------------------+-------------------------------+
|                        Value (32)                             |
+---------------------------------------------------------------+
```

（6）PUSH_PROMISE 帧

flag 标识部分有效

PUSH_PROMISE帧(类型 = 0x5) 用于在发送方打算发起的流之前提前通知对端。PUSH_PROMISE 帧包括端点计划创建的流的无符号 31 位标识符以及为流提供附加上下文的一组头。

```
+---------------+
|Pad Length? (8)|
+-+-------------+-----------------------------------------------+
|R|                  Promised Stream ID (31)                    |
+-+-----------------------------+-------------------------------+
|                   Header Block Fragment (*)                 ...
+---------------------------------------------------------------+
|                           Padding (*)                       ...
+---------------------------------------------------------------+
```

（7）PING 帧

 flag 标识一个有效：ACK (0x1)

PING 帧(类型 = 0x6)是用于测量来自发送方的最小往返时间以及确定空闲连接是否仍然起作用的机制。 PING 帧可以从任何端点发送。可用作心跳检测，兼具计算 RTT 往返时间的功能。

```
+---------------------------------------------------------------+
|                                                               |
|                      Opaque Data (64)                         |
|                                                               |
+---------------------------------------------------------------+
```

（8） GOAWAY 帧

没有定义任何 flag 标识

GOAWAY 帧(类型 = 0x7) 用于启动连接关闭或发出严重错误信号。GOAWAY 允许端点优雅地停止接受新流，同时仍然完成先前建立的流的处理。这可以实现管理员的操作，例如服务器维护。GOAWAY 帧用来优雅的终止连接或者通知错误。

```
+-+-------------------------------------------------------------+
|R|                  Last-Stream-ID (31)                        |
+-+-------------------------------------------------------------+
|                      Error Code (32)                          |
+---------------------------------------------------------------+
|                  Additional Debug Data (*)                    |
+---------------------------------------------------------------+
```

（9）WINDOW_UPDATE 帧

WINDOW_UPDATE帧(类型 = 0x8) 用于实现流量控制；

流量控制在两个级别上运行：在每个单独的流上和整个连接上。

```
+-+-------------------------------------------------------------+
|R|              Window Size Increment (31)                     |
+-+-------------------------------------------------------------+
```

（10）CONTINUATION 帧

CONTINUATION 帧(类型 = 0x9) 用于继续一系列 header block fragments 头块片段。只要前一帧在同一个流上并且是没有设置 END_HEADERS 标志的 HEADERS，PUSH_PROMISE 或 CONTINUATION 帧，就可以发送任意数量的 CONTINUATION 帧。此帧专门用于传递较大 HTTP 头部时的持续帧。

```
+---------------------------------------------------------------+
|                   Header Block Fragment (*)                 ...
+---------------------------------------------------------------+
```



### 三、HTTP2头压缩机制

（1）整个头部键值对都在字典中

（2）头部名称在字典中，更新动态字典

（3）头部名称不在字典中，更新动态字典

（4）头部名称在字典中，不允许更新动态字典

（5）头部名称不在字典中，不允许更新动态字典

### 四、HTTP2帧详解

[参考](https://halfrost.com/http2-http-frames-definitions/#toc-1)

4.5 关于帧扩展

HTTP/2协议的扩展是允许存在的，在于提供额外服务。

扩展包括： 

- 新类型帧，需要遵守通用帧格式 
- 新的设置参数，用于设置新帧相关属性
- 新的错误代码，约定帧可能触发的错误

[关于帧扩展](http://www.blogjava.net/yongboy/archive/2015/03/20/423655.html)

### 五、小结



HTTP2 DATA 帧直接解压

HTTP2 SETTINGS，GOAWAY 帧没有key只有value，key值固定

HTTP2 HEADERS帧需要使用HPack解压

RST_STREAM只有一个WINDOW_SIZE值



dpkt.http2使用了两种设计模式

（1）工厂设计模式

（2）策略设计模式

本次实现的代码没有使用策略模式，因为Flag标记起作用的，没几个，虽然这样存在一定的代码冗余

动态表问题

hpack.exceptions.InvalidTableIndex: Invalid table index 67

Parser全局唯一

参考dpkt.http2.FrameFactory，其使用的是\_\_new\_\_ 方法实现实例化，关于该方法的介绍 

\_\_new\_\_ 方法用于实现Singleton与工厂设计模式

实际上，\_\_init\_\_函数并不是真正意义上的构造函数，\_\_init\_\_方法做的事情是在对象创建好之后初始化变量。真正创建实例的是\_\_new\_\_方法。定义python对象时的构造函数一般只定义\_\_init\_\_方法，在调用时会隐式调用\_\_new\_\_，创建对象





使用教程

```python
from h2p.parser import HTTP2Parser
rst_stream = "00000403000000000300000008"
parser = HTTP2Parser(bytes.fromhex(rst_stream), True)
parser.parse_data()

# 方法二
parser = HTTP2Parser(True)
parser.parse_data(bytes.fromhex(rst_stream))
```

