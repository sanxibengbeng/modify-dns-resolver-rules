# Route53 Resolver Rule IP更新Lambda函数

这个Lambda函数用于更新Route53 Resolver Rule的目标IP地址。

## 功能特性

- 支持输入Resolver Rule ID和IP列表
- 自动验证IP地址格式
- 完整的错误处理和日志记录
- 返回详细的操作结果

## 输入参数

Lambda函数接受以下JSON格式的事件：

```json
{
  "resolver_rule_id": "rslvr-rr-xxxxxxxxx",
  "target_ips": ["8.8.8.8", "8.8.4.4", "1.1.1.1"],
  "region": "us-east-1"
}
```

### 参数说明

- `resolver_rule_id` (必需): Route53 Resolver Rule的ID
- `target_ips` (必需): 新的目标IP地址列表
- `region` (可选): VPC所在的AWS区域，如果未指定则使用默认区域

## 输出格式

成功时返回：
```json
{
  "statusCode": 200,
  "body": {
    "message": "Resolver rule updated successfully",
    "resolver_rule_id": "rslvr-rr-xxxxxxxxx",
    "region": "us-east-1",
    "updated_target_ips": ["8.8.8.8", "8.8.4.4"],
    "result": {
      "resolver_rule_id": "rslvr-rr-xxxxxxxxx",
      "region": "us-east-1",
      "status": "UPDATING",
      "modification_time": "2025-08-14T14:38:43.501000",
      "new_target_ips": ["8.8.8.8", "8.8.4.4"]
    }
  }
}
```

错误时返回：
```json
{
  "statusCode": 400,
  "body": {
    "error": "resolver_rule_id is required"
  }
}
```

## 部署步骤

### 1. 准备部署包

```bash
# 创建部署目录
mkdir lambda-deployment
cd lambda-deployment

# 复制函数文件
cp ../update_resolver_rule.py .

# 安装依赖（如果需要）
pip install -r ../requirements.txt -t .

# 创建部署包
zip -r resolver-rule-updater.zip .
```

### 2. 创建Lambda函数

使用AWS CLI创建Lambda函数：

```bash
aws lambda create-function \
  --function-name update-resolver-rule \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --handler update_resolver_rule.lambda_handler \
  --zip-file fileb://resolver-rule-updater.zip \
  --timeout 60 \
  --memory-size 128
```

### 3. 配置IAM权限

Lambda执行角色需要以下权限：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "route53resolver:GetResolverRule",
        "route53resolver:UpdateResolverRule"
      ],
      "Resource": "*"
    }
  ]
}
```

## 使用示例

### 通过AWS CLI调用

```bash
aws lambda invoke \
  --function-name update-resolver-rule \
  --payload '{"resolver_rule_id":"rslvr-rr-xxxxxxxxx","target_ips":["8.8.8.8","8.8.4.4"],"region":"us-east-1"}' \
  response.json
```

### 通过Python SDK调用

```python
import boto3
import json

lambda_client = boto3.client('lambda')

payload = {
    'resolver_rule_id': 'rslvr-rr-xxxxxxxxx',
    'target_ips': ['8.8.8.8', '8.8.4.4'],
    'region': 'us-east-1'  # 可选参数
}

response = lambda_client.invoke(
    FunctionName='update-resolver-rule',
    Payload=json.dumps(payload)
)

result = json.loads(response['Payload'].read())
print(json.dumps(result, indent=2))
```

## 注意事项

1. **权限要求**: 确保Lambda执行角色有足够的权限访问Route53 Resolver
2. **IP格式验证**: 函数会自动验证IP地址格式
3. **异步操作**: Resolver Rule更新是异步操作，函数返回后更新可能仍在进行中
4. **端口设置**: 默认使用53端口（DNS标准端口）
5. **错误处理**: 包含完整的错误处理和日志记录

## 故障排除

- 检查CloudWatch日志获取详细错误信息
- 确认Resolver Rule ID是否正确
- 验证IP地址格式是否有效
- 检查IAM权限配置
