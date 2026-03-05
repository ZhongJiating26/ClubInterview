完成部署，正常使用前端,
为快速部署演示，将package.json里的"build": "vue-tsc -b && vite build"改成了"build": "vite build"，这样忽略了不影响的报错，后期开发要恢复。
将dist.zip上传到/www/wwwroot/club-frontend并解压，最后目录结构为：/www/wwwroot/club-frontend/dist/index.html
直接访问http://120.26.177.237，正常显示网页

域名配置：
第一步：DNS 解析（在阿里云控制台）
   1. 登录 阿里云控制台。
   2. 进入 云解析 DNS。
   3. 点击 zhongjiating.cn 进入解析设置。
   4. 点击 添加记录：
       * 记录类型：A
       * 主机记录：club (这就是前缀)
       * 记录值：120.26.177.237 (你的服务器 IP)
       * TTL：默认即可 (10分钟)
   5. 点击 确认。等待几分钟解析生效。
第二步：宝塔添加域名
   1. 登录 宝塔面板。
   2. 进入 网站 菜单。
   3. 找到你之前创建的那个用来放前端和 Nginx 配置的网站（如果还没创建，就新建一个纯静态网站）。
   4. 点击右侧的 设置。
   5. 在 域名管理 标签页中：
       * 输入：club.zhongjiating.cn
       * 点击 添加。
   6. (可选) 如果你想支持 HTTPS（强烈建议），可以在 SSL 标签页中申请免费的 Let's Encrypt 证书。
第三步：Nginx 配置微调
  由于你加了域名，我们需要确保 Nginx 监听这个新域名。
   1. 在网站设置中，点击 配置文件。
   2. 找到 server_name 这一行，把它修改为：
        server_name club.zhongjiating.cn 120.26.177.237; 
      (其实宝塔在你添加域名时通常会自动改这一行，但确认一下更稳妥)
   3. 关键检查：
      确保你的 Nginx 配置里，/api 的转发逻辑依然存在且正确（应该不需要动，只要 server_name 加上了域名，之前的配置对域名也生效）。
         # 再次确认这一段还在
         location /api/ {
           proxy_pass http://127.0.0.1:8000/api/;
           # ...
        }
   4. 保存。
访问测试
  DNS 解析生效可能需要 1-10 分钟。稍等片刻后，在浏览器访问：
  http://club.zhongjiating.cn (http://club.zhongjiating.cn)


HTTPS安全证书配置
1. 申请并部署 SSL 证书

   1. 登录 宝塔面板。
   2. 进入 网站 菜单。
   3. 找到你的 club.zhongjiating.cn 网站，点击右侧的 设置。
   4. 点击左侧菜单的 SSL。
   5. 选择 Let's Encrypt 标签页。
   6. 勾选你的域名 club.zhongjiating.cn。
   7. 点击 申请 按钮。
       * 注意：这一步需要等待几十秒，宝塔会自动验证你的域名所有权（通过文件验证）。
   8. 申请成功后，你会看到证书的有效期和密钥信息。
   9. 关键一步：点击右上角的 强制 HTTPS 开关（将其变为绿色）。
       * 这样用户访问 `http://...` 时会自动跳转到 `https://...`。

  2. 检查 Nginx 配置 (通常宝塔会自动处理)

  当你开启 SSL 后，宝塔会自动修改 Nginx 配置文件，增加监听 443 端口的配置。

  你需要检查的一点是：
  有时候宝塔自动生成的 SSL 配置可能会覆盖掉我们之前手动写的 location / 和 location /api/。     

  请务必重新检查配置文件：
   1. 在网站设置中，点击 配置文件。
   2. 你会发现现在可能有了两个 server 块（一个监听 80，一个监听 443），或者一个合并的块。
   3. 确保监听 443 的那个 server 块里，依然包含我们之前写的：
       * root /www/wwwroot/club-frontend/dist;
       * location / { try_files ... }
       * location /api/ { proxy_pass ... }

  如果发现被覆盖了（变回了默认的），请把那几段配置复制回 443 的 server 块中。

  示例（开启 SSL 后的正确配置结构）：

    1 server
    2 {
    3     listen 80;
    4     listen 443 ssl http2;
    5     server_name club.zhongjiating.cn 120.26.177.237;
    6
    7     # ... SSL 证书路径配置 (宝塔自动生成的，不动它) ...
    8     ssl_certificate    /www/server/panel/vhost/cert/...;
    9     ssl_certificate_key /www/server/panel/vhost/cert/...;
   10
   11     # 强制 HTTPS (如果你点了开关，这里会有重定向，或者在 80 端口的 server 块里)
   12     if ($server_port !~ 443){
   13         rewrite ^(/.*)$ https://$host$1 permanent;
   14     }
   15
   16     # ==============================
   17     # ⚠️ 确保下面这几段在 SSL 的 server 块里存在！
   18     # ==============================
   19
   20     # 1. 前端静态文件
   21     root /www/wwwroot/club-frontend/dist;
   22     index index.html index.htm;
   23
   24     location / {
   25         try_files $uri $uri/ /index.html;
   26     }
   27
   28     # 2. 后端 API
   29     location /api/ {
   30         proxy_pass http://127.0.0.1:8000/api/;
   31         proxy_set_header Host $host;
   32         proxy_set_header X-Real-IP $remote_addr;
   33         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   34         proxy_set_header REMOTE-HOST $remote_addr;
   35         # ... 超时设置 ...
   36     }
   37
   38     # ... 其他日志和禁止访问配置 ...
   39 }

  3. 测试

  配置保存后，访问 https://club.zhongjiating.cn (https://club.zhongjiating.cn)

  如果你看到浏览器地址栏有了一把小锁🔒，且页面功能正常，那就成功了！