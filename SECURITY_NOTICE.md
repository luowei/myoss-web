# 配置更新说明

## 环境变量配置

**更新时间**: 2026 年 3 月 20 日

### 变更内容

为了更好地管理项目配置，现将所有环境相关配置改为使用环境变量方式。

### 配置方式

#### 方式一：使用 .env 文件（推荐本地开发）

1. 复制配置模板
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的配置：
```bash
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your_bucket_name
```

#### 方式二：系统环境变量（推荐生产环境）

在 `~/.zshrc` 或 `~/.bash_profile` 中添加：
```bash
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export OSS_ENDPOINT="oss-cn-hangzhou.aliyuncs.com"
export OSS_BUCKET_NAME="your_bucket_name"
```

#### 方式三：Docker 环境变量

```bash
docker run -d \
  --name my-oss \
  -e OSS_ACCESS_KEY_ID=your_key_id \
  -e OSS_ACCESS_KEY_SECRET=your_key_secret \
  -e OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com \
  -e OSS_BUCKET_NAME=your_bucket \
  -p 5000:5000 \
  myoss:v1.0
```

### 获取阿里云 OSS 配置

1. 登录 [阿里云控制台](https://oss.console.aliyun.com/)
2. 进入 OSS 管理控制台
3. 在 Bucket 详情页面获取 Endpoint
4. 在 [RAM 访问控制](https://ram.console.aliyun.com/manage/ak) 获取 AccessKey

### 配置说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `OSS_ACCESS_KEY_ID` | 阿里云 AccessKey ID | LTAI5t... |
| `OSS_ACCESS_KEY_SECRET` | 阿里云 AccessKey Secret | xxxxxxxxxxxxxx |
| `OSS_ENDPOINT` | OSS 区域端点 | oss-cn-hangzhou.aliyuncs.com |
| `OSS_BUCKET_NAME` | Bucket 名称 | my-bucket |

### 常用 OSS 端点

| 区域 | Endpoint |
|------|----------|
| 华东 1（杭州） | oss-cn-hangzhou.aliyuncs.com |
| 华东 2（上海） | oss-cn-shanghai.aliyuncs.com |
| 华北 1（青岛） | oss-cn-qingdao.aliyuncs.com |
| 华北 2（北京） | oss-cn-beijing.aliyuncs.com |
| 华南 1（深圳） | oss-cn-shenzhen.aliyuncs.com |
| 香港 | oss-cn-hongkong.aliyuncs.com |

---

**更新**: 2026 年 3 月 20 日
