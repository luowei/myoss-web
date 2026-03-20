# ⚠️ 安全通告

## 配置更新说明

**发现时间**: 2026 年 3 月 20 日  
**严重程度**: 🔴 高危

### 问题描述

在 Git 历史提交中发现硬编码的阿里云 OSS 凭证：

- **AccessKey ID**: `YOUR_ACCESS_KEY_ID`
- **AccessKey Secret**: `YOUR_ACCESS_KEY_SECRET`

### 影响范围

- 提交历史：`b844f0a` 至 `50baf22` 之间的所有提交
- GitHub 仓库：https://github.com/luowei/myoss-web

### 已采取的修复措施

✅ 已移除当前代码中的硬编码凭证  
✅ 已改用环境变量管理敏感配置  
✅ 已添加 `.gitignore` 排除 `.env` 文件  
✅ 已创建 `.env.example` 配置模板  
✅ 已强制重写 Git 历史并推送到 GitHub

### ⚠️ 必须立即执行的操作

**请立即轮换（撤销并重新生成）阿里云 AccessKey！**

#### 操作步骤：

1. **登录阿里云 RAM 控制台**
   - 访问：https://ram.console.aliyun.com/manage/ak

2. **禁用泄露的 AccessKey**
   - 找到 AccessKey ID: `YOUR_ACCESS_KEY_ID`
   - 点击"禁用"

3. **删除旧密钥**
   - 禁用后点击"删除"

4. **创建新的 AccessKey**
   - 点击"创建 AccessKey"
   - 保存新的 AccessKey ID 和 Secret

5. **更新项目配置**
   ```bash
   cp .env.example .env
   # 编辑 .env 填入新的密钥
   ```

6. **更新部署环境**
   - 更新服务器上的环境变量
   - 更新 Docker 容器的环境变量
   - 重新构建和部署

### 为什么必须轮换密钥？

即使我们重写了 Git 历史，以下风险仍然存在：

1. **克隆过旧版本的人**：任何人在之前克隆过仓库的人都持有敏感信息
2. **GitHub 快照**：GitHub 可能保留了历史快照
3. **第三方工具**：CI/CD 工具、镜像服务可能已缓存旧代码
4. **本地仓库**：所有已克隆的本地仓库仍有完整历史

### 最佳实践建议

1. **永远不要**将密钥硬编码到代码中
2. **使用**环境变量或配置管理工具
3. **启用**阿里云 RAM 角色（如果在 ECS 上部署）
4. **定期轮换**访问密钥（建议每 90 天）
5. **监控** AccessKey 使用情况
6. **启用**最小权限原则

### 参考资源

- [阿里云 AccessKey 管理最佳实践](https://help.aliyun.com/document_detail/102600.html)
- [Git 历史中删除敏感信息](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

---

**发布**: 2026 年 3 月 20 日  
**更新**: 2026 年 3 月 20 日
