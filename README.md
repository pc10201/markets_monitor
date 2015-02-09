#部署手册

```
pip install flask MySQL-python gevent
```

直接运行python gevent_web.py即可

将settings.py.sample重命名为settings.py
此文件保存了数据库和账号密码等配置信息

运行python gevent_web.py即可

所有监控在周末和每天凌晨0点到8点总是输出正常的状态，即此时的监控是停止的

**markets_monitor_time**

此文件夹是基于时间维度的监控程序

http://monitor.wallstreetcn.com/forex
此URL反映的是货币对的状态，默认是如果80%以上的资产更新时间在5分钟内则认为是正常的

http://monitor.wallstreetcn.com/index
此URL反映的是指数的状态，默认是如果20%以上的资产更新时间在30分钟内则认为是正常的
因为各国指数开收盘时间不一致，另外部分国家数据有延迟，所以此值设置得宽松一些

**markets_monitor_data**
先将ax_config.sql导入数据库中
此文件夹是基于数据维度的监控程序
建议部署到海外服务器

将第三方数据源与本站最新价进行对比，并设置允许的误差范围，超过范围则报警
参照来源及允许误差范围在ax_config表中

##linux下的连接数优化

关于系统连接数的优化
linux 默认值 open files 和 max user processes 为 1024
```
#ulimit -n
```
1024
```
#ulimit –u
```
1024

问题描述： 说明 server 只允许同时打开 1024 个文件，处理 1024 个用户进程

使用ulimit -a 可以查看当前系统的所有限制值，使用ulimit -n 可以查看当前的最大打开文件数。

新装的linux 默认只有1024 ，当作负载较大的服务器时，很容易遇到error: too many open files 。因此，需要将其改大。
 

解决方法：

使用 ulimit –n 65535 可即时修改，但重启后就无效了。（注ulimit -SHn 65535 等效 ulimit -n 65535 ，-S 指soft ，-H 指hard)

有如下三种修改方式：

1. 在/etc/rc.local 中增加一行 ulimit -SHn 65535
2. 在/etc/profile 中增加一行 ulimit -SHn 65535
3. 在/etc/security/limits.conf 最后增加：

```
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
```

具体使用哪种，在 CentOS 中使用第1 种方式无效果，使用第3 种方式有效果，而在Debian 中使用第2 种有效果

```
# ulimit -n
```

65535
```
# ulimit -u
```
65535

备注：ulimit 命令本身就有分软硬设置，加-H 就是硬，加-S 就是软默认显示的是软限制

soft 限制指的是当前系统生效的设置值。 hard 限制值可以被普通用户降低。但是不能增加。 soft 限制不能设置的比 hard 限制更高。 只有 root 用户才能够增加 hard 限制值。

参考来源
[http://blog.csdn.net/zqtsx/article/details/24111319][1]


  [1]: http://blog.csdn.net/zqtsx/article/details/24111319