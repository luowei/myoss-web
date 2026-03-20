# GitHub Actions CI/CD 使用指南

## 概述

本项目使用 GitHub Actions 实现自动化的 Docker 镜像构建和发布。当推送版本标签（如 `v1.0`, `v2.1.0`）时，会自动：

1. 构建多平台 Docker 镜像（amd64, arm64）
2. 推送到 GitHub Container Registry (GHCR)
3. 创建 GitHub Release
4. 发送部署通知

## 工作流程

### 触发条件

#### 1. 推送标签（主要方式）
```bash
# 打标签
git tag v1.0.0
git push origin v1.0.0
```

#### 2. 手动触发
在 GitHub Actions 页面手动触发，可指定 tag 名称。

### 构建流程

```
推送 Tag → 触发 Workflow → 构建镜像 → 推送 GHCR → 创建 Release
```

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `REGISTRY` | 镜像仓库 | ghcr.io |
| `IMAGE_NAME` | 镜像名称 | 仓库全名 |

### Docker 镜像标签

自动生成的标签：
- `v1.0.0` - 版本标签
- `latest` - 最新稳定版

### 构建参数

| 参数 | 说明 |
|------|------|
| `BUILD_DATE` | 构建时间 |
| `VCS_REF` | 提交哈希 |
| `VERSION` | 版本号 |

## 使用步骤

### 1. 发布新版本

```bash
# 1. 更新版本号（如果需要）
# 编辑相关版本文件

# 2. 提交更改
git add .
git commit -m "release: v1.0.0"

# 3. 打标签
git tag v1.0.0

# 4. 推送标签
git push origin v1.0.0
```

### 2. 查看构建进度

访问：https://github.com/luowei/myoss-web/actions

### 3. 拉取镜像

```bash
# 拉取特定版本
docker pull ghcr.io/luowei/myoss.wodedata.com:v1.0.0

# 拉取最新版
docker pull ghcr.io/luowei/myoss.wodedata.com:latest
```

### 4. 运行容器

```bash
docker run -d \
  --name myoss \
  -p 5000:5000 \
  -e OSS_ACCESS_KEY_ID=your_key \
  -e OSS_ACCESS_KEY_SECRET=your_secret \
  -e OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com \
  -e OSS_BUCKET_NAME=your_bucket \
  ghcr.io/luowei/myoss.wodedata.com:v1.0.0
```

## 权限配置

### 自动配置

GitHub Actions 会自动使用 `GITHUB_TOKEN`，无需手动配置。

### 手动配置（可选）

如需使用 Personal Access Token：

1. 创建 Token：
   - 访问：https://github.com/settings/tokens
   - 权限：`read:packages`, `write:packages`

2. 添加 Secret：
   - 仓库 → Settings → Secrets and variables → Actions
   - 添加 `GHCR_TOKEN`

## 自定义配置

### 修改镜像名称

编辑 `.github/workflows/docker-publish.yml`：

```yaml
env:
  IMAGE_NAME: your-image-name
```

### 添加其他平台

```yaml
platforms: linux/amd64,linux/arm64,linux/arm/v7
```

### 添加其他标签

```yaml
tags: |
  type=ref,event=tag
  type=raw,value=stable
  type=semver,pattern={{version}}
```

## 故障排查

### 问题 1: 推送失败

**原因**: 权限不足

**解决**:
1. 检查仓库权限
2. 确认 GITHUB_TOKEN 权限
3. 查看 Actions 日志

### 问题 2: 构建失败

**原因**: Dockerfile 错误

**解决**:
```bash
# 本地测试构建
docker build -t myoss:test .

# 查看详细日志
docker build --progress=plain -t myoss:test .
```

### 问题 3: 镜像拉取失败

**原因**: 认证问题

**解决**:
```bash
# 登录 GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# 拉取镜像
docker pull ghcr.io/luowei/myoss.wodedata.com:v1.0.0
```

## 最佳实践

### 1. 版本命名

遵循语义化版本规范：
- `v1.0.0` - 主版本
- `v1.1.0` - 次版本
- `v1.1.1` - 补丁版本

### 2. Release Notes

在打标签时提供详细的更新说明：
```bash
git tag -a v1.0.0 -m "
版本 1.0.0

新功能:
- 用户认证系统
- 批量文件操作
- Redis 缓存支持

修复:
- 修复 OSS 连接问题
- 优化前端性能
"
```

### 3. 镜像清理

定期清理旧镜像：
```bash
# 查看镜像
docker images

# 删除旧镜像
docker rmi ghcr.io/luowei/myoss.wodedata.com:old-version
```

## 镜像信息

### 查看镜像详情

```bash
# 查看镜像信息
docker inspect ghcr.io/luowei/myoss.wodedata.com:v1.0.0

# 查看构建标签
docker inspect --format='{{index .Config.Labels "org.label-schema.version"}}' ghcr.io/luowei/myoss.wodedata.com:v1.0.0
```

### 镜像大小

- **基础镜像**: Python 3.11-slim (~120MB)
- **应用层**: ~30MB
- **总大小**: ~150MB

### 支持平台

- `linux/amd64` - Intel/AMD 64 位
- `linux/arm64` - ARM 64 位（树莓派、M1/M2 Mac）

## 安全建议

### 1. 密钥管理

- ✅ 使用 GitHub Secrets 存储敏感信息
- ✅ 不在镜像中硬编码密钥
- ✅ 定期轮换 AccessKey

### 2. 镜像扫描

使用 GitHub 自带的漏洞扫描：
```yaml
- name: Scan image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'ghcr.io/luowei/myoss.wodedata.com:v1.0.0'
```

### 3. 最小权限

- 使用非 root 用户运行
- 限制容器资源
- 只暴露必要端口

## 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Buildx 文档](https://docs.docker.com/buildx/working-with-buildx/)
- [GHCR 文档](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

**更新时间**: 2026-03-20  
**版本**: v3.0
