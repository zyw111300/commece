# Django 电商系统 - 项目运行指南

## 项目概述

这是一个基于Django的电商系统，实现了批量订单处理和商品搜索功能，包含：

- 商品管理和搜索
- 批量订单处理
- 库存管理和并发控制
- 缓存优化
- 简单的前端界面

## 环境要求

### Python 包依赖

请安装以下包（使用pip安装）：

```bash
pip install django==5.2
pip install mysqlclient
pip install django-redis
```

如果在Windows上安装mysqlclient遇到问题，可以：

1. 下载对应版本的whl文件：https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
2. 使用pip install 下载的whl文件名

### 数据库配置

1. **MySQL数据库**
    - 确保MySQL服务正在运行
    - 创建数据库：
   ```sql
   CREATE DATABASE commerce DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
    - 更新settings.py中的数据库配置（用户名、密码等）

2. **Redis缓存（可选）**
    - 如果要使用Redis缓存，请确保Redis服务正在运行
    - 如果没有Redis，系统会使用Django默认的内存缓存

## 项目启动步骤

### 1. 数据库迁移

```bash
python manage.py makemigrations
 
```

### 2. 创建超级用户（用于管理后台）

```bash
python manage.py createsuperuser
```

### 3. 初始化示例数据

```bash
python manage.py shell < init_data.py
```

### 4. 启动开发服务器

```bash
python manage.py runserver
```

## 访问地址

- **前端首页**: http://127.0.0.1:8000/
- **管理后台**: http://127.0.0.1:8000/admin/
- **API文档**: 见下方API接口说明

## API接口说明

### 商品相关接口

1. **获取商品列表**
    - URL: `GET /api/products/`
    - 参数: `page`, `size`
    - 示例: `/api/products/?page=1&size=20`

2. **商品搜索**
    - URL: `GET /api/products/search/`
    - 参数: `keyword`, `page`, `size`
    - 示例: `/api/products/search/?keyword=手机&page=1&size=10`

3. **获取商品详情**
    - URL: `GET /api/products/{product_id}/`
    - 示例: `/api/products/1/`

### 订单相关接口

1. **批量创建订单**
    - URL: `POST /api/orders/batch/`
    - 请求体:
   ```json
   {
     "user_id": 1001,
     "order_items": [
       {
         "product_id": 1,
         "quantity": 2
       },
       {
         "product_id": 2,
         "quantity": 1
       }
     ]
   }
   ```

2. **获取订单详情**
    - URL: `GET /api/orders/{order_no}/`
    - 示例: `/api/orders/ORD202412271234567890ABCD/`

## 功能测试

### 1. 商品搜索测试

1. 访问首页，在搜索框中输入关键词（如"手机"、"苹果"）
2. 查看搜索结果是否正确显示
3. 测试分页功能

### 2. 批量订单测试

1. 访问批量下单页面：http://127.0.0.1:8000/order/
2. 选择多个商品添加到购物车
3. 提交批量订单
4. 查看订单结果，验证库存扣减是否正确
5. 测试库存不足的情况

### 3. 并发测试

可以使用以下方式测试并发处理：

1. 同时打开多个浏览器标签
2. 对同一商品进行下单操作
3. 验证库存不会超卖

### 4. 管理后台测试

1. 访问管理后台
2. 查看和编辑商品信息
3. 查看订单和库存日志

## 项目结构说明

```
Electronic_Commerce/
├── comerge/                    # 主应用
│   ├── models.py              # 数据模型
│   ├── views.py               # 视图函数
│   ├── urls.py                # URL配置
│   ├── admin.py               # 管理后台配置
│   └── services/              # 服务层
│       ├── cache_service.py   # 缓存服务
│       ├── product_service.py # 商品服务
│       └── order_service.py   # 订单服务
├── templates/comerge/         # 前端模板
│   ├── base.html             # 基础模板
│   ├── index.html            # 首页
│   ├── product_detail.html   # 商品详情
│   └── order.html            # 批量下单
├── Electronic_Commerce/       # 项目配置
│   ├── settings.py           # 设置文件
│   └── urls.py               # 主URL配置
└── init_data.py              # 初始化数据脚本
```

## 技术特点

1. **数据库设计**
    - 使用索引优化查询性能
    - 实现乐观锁防止并发问题
    - 记录详细的库存变更日志

2. **缓存策略**
    - 商品信息缓存
    - 搜索结果缓存
    - 自动缓存失效机制

3. **并发控制**
    - 使用select_for_update实现悲观锁
    - 防止库存超卖问题
    - 事务保证数据一致性

4. **前端体验**
    - 响应式设计，支持移动端
    - 异步加载，提升用户体验
    - 友好的错误提示和状态反馈

## 扩展功能建议

1. **Redis分布式锁**: 如果需要多服务器部署，可以使用Redis实现分布式锁
2. **消息队列**: 使用Celery处理大批量订单的异步处理
3. **搜索引擎**: 集成Elasticsearch提供更强大的搜索功能
4. **API限流**: 添加接口访问频率限制
5. **日志监控**: 集成ELK Stack进行日志分析

## 故障排除

### 常见问题

1. **数据库连接失败**
    - 检查MySQL服务是否启动
    - 确认数据库配置信息是否正确

2. **缓存相关错误**
    - 如果Redis未安装，系统会使用默认缓存，不影响基本功能

3. **静态文件问题**
    - 开发环境下Django会自动处理静态文件
    - 生产环境需要配置STATIC_ROOT和collectstatic

4. **端口占用**
    - 如果8000端口被占用，可以使用其他端口：
   ```bash
   python manage.py runserver 0.0.0.0:8080
   ```

## 联系方式

如有问题或建议，请联系开发团队。
