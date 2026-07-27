# MT5700 WebUI OpenWrt Server

这是一个面向 OpenWrt 的 MT5700 WebUI 和 LuCI 管理插件，包含独立的 AT WebServer 服务，以及 LuCI 中的配置、日志和 WebUI 首页。

## 本次版本功能

- LuCI 菜单 `服务 → AT WebServer` 新增“首页”。
- 首页直接在 LuCI 页面内嵌 `/5700/` WebUI，不再自动打开新页面。
- Tab 顺序为：首页、配置、日志查看。
- iframe 使用同源相对路径，自动继承当前 LuCI 的协议、主机地址和端口；用户修改 IPv4 管理地址后无需修改插件配置。
- 配置页面的 Web 管理界面入口改为返回 LuCI 内嵌首页。

## 页面入口

安装并启用服务后，在 LuCI 中打开：

```
服务 → AT WebServer → 首页
```

独立 WebUI 仍可通过以下路径访问：

```
http://路由器IP/5700/
```

## 安装与开发

本仓库包含两个 OpenWrt 软件包：

- `at-webserver`：AT WebSocket 服务、CGI 接口和 `/www/5700/` WebUI。
- `luci-app-at-webserver`：LuCI 菜单、首页 iframe、配置和日志页面。

请在 OpenWrt SDK 或完整 buildroot 中编译对应软件包。LuCI 首页相关源码位于：

```
luci-app-at-webserver/htdocs/luci-static/resources/view/at-webserver/home.js
luci-app-at-webserver/root/usr/share/luci/menu.d/luci-app-at-webserver.json
```

---

## 预编译版本

已经编译好的版本可直接下载，安装前请确认依赖包已经存在：

链接：https://www.123865.com/s/BwcjVv-PexFd?pwd=GweY#
提取码：GweY

<img width="2104" height="1326" alt="HT495J9_)2B7_F2{{PNV9R2" src="https://github.com/user-attachments/assets/229ee8de-6309-43c0-99a3-14cb36b770a2" />
<img width="2455" height="1322" alt="D%P)4D)A($VUZOIYHT4Y1LB" src="https://github.com/user-attachments/assets/cff3c45c-7d5c-4c77-af75-8e16fe94a25b" />
<img width="2443" height="1328" alt="APUCD096I V))XV@Y6QUB~E" src="https://github.com/user-attachments/assets/64d9ee66-6d4d-4005-b7de-93cdd3652162" />
<img width="2457" height="1326" alt="9(TM7)SQA1G0Q}6V9Y3JO)Y" src="https://github.com/user-attachments/assets/a002f79c-335a-4dfd-9a5d-8df1a1dac736" />
<img width="2443" height="1335" alt="`SQWWP VX7%L~B8J%3C(X8" src="https://github.com/user-attachments/assets/a9a0a84c-5ea5-4c4f-96b9-35f2d53f269d" />
<img width="2452" height="1318" alt="`RR6H0LRW9L5{M5{L82NX_2" src="https://github.com/user-attachments/assets/d4290143-69fc-4211-8d97-b1527f77d7ff" />



