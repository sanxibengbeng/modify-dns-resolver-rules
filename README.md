# Route53 Resolver规则管理Lambda函数

这个Lambda函数用于管理Route53 Resolver规则与VPC的绑定和解绑操作。

## 功能特性

- 支持将Resolver规则与VPC关联
- 支持解除Resolver规则与VPC的关联
- 自动检查现有关联状态
- 完整的错误处理和日志记录
- 支持中文错误消息

## 输入格式

函数期望接收以下格式的event：

```json
{
    "action": "associate" | "disassociate",
    "resolver_rule_id": "rslvr-rr-xxxxxxxxx",
    "vpc_id": "vpc-xxxxxxxxx",
    "region": "us-west-2"
}
```

### 参数说明

- `action`: 操作类型
  - `associate`: 关联Resolver规则与VPC
  - `disassociate`: 解除关联
- `resolver_rule_id`: Route53 Resolver规则ID
- `vpc_id`: VPC ID
- `region`: AWS区域（可选，默认为us-west-2）

## 输出格式

### 成功响应 (200)
```json
{
    "statusCode": 200,
    "body": {
        "message": "操作 associate 成功完成",
        "result": {
            "association_id": "rslvr-rrassoc-xxxxxxxxx",
            "status": "associated"
        }
    }
}
```

### 错误响应 (400/500)
```json
{
    "statusCode": 400,
    "body": {
        "error": "参数错误",
        "message": "缺少必需参数: action, resolver_rule_id, vpc_id"
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
cp ../lambda_function.py .

# 如果需要额外的依赖包（Lambda运行时已包含boto3）
pip install -r ../requirements.txt -t .
```

### 2. 创建Lambda函数

使用AWS CLI创建函数：

```bash
# 打包代码
zip -r function.zip .

# 创建Lambda函数
aws lambda create-function \
    --function-name route53-resolver-rule-manager \
    --runtime python3.9 \
    --role arn:aws:iam::<account-id>:role/lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --description "管理Route53 Resolver规则与VPC的关联"
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
                "route53resolver:AssociateResolverRule",
                "route53resolver:DisassociateResolverRule",
                "route53resolver:ListResolverRuleAssociations",
                "route53resolver:GetResolverRule"
            ],
            "Resource": "*"
        }
    ]
}
```

## 使用示例

### 通过AWS CLI调用

```bash
# 关联Resolver规则与VPC
aws lambda invoke \
    --function-name route53-resolver-rule-manager \
    --payload '{
        "action": "associate",
        "resolver_rule_id": "rslvr-rr-example123456",
        "vpc_id": "vpc-example123456"
    }' \
    response.json

# 解除关联
aws lambda invoke \
    --function-name route53-resolver-rule-manager \
    --payload '{
        "action": "disassociate",
        "resolver_rule_id": "rslvr-rr-example123456",
        "vpc_id": "vpc-example123456"
    }' \
    response.json
```

### 通过Python SDK调用

```python
import boto3
import json

lambda_client = boto3.client('lambda')

# 关联操作
response = lambda_client.invoke(
    FunctionName='route53-resolver-rule-manager',
    Payload=json.dumps({
        'action': 'associate',
        'resolver_rule_id': 'rslvr-rr-example123456',
        'vpc_id': 'vpc-example123456'
    })
)

result = json.loads(response['Payload'].read())
print(result)
```

## 本地测试

运行测试脚本：

```bash
python test_lambda.py
```

注意：本地测试需要配置AWS凭证。

## 错误处理

函数包含完整的错误处理：

- 参数验证错误 (400)
- AWS API错误 (500)
- 未预期错误 (500)

所有错误都会记录到CloudWatch日志中。

## 监控和日志

- 函数执行日志会自动发送到CloudWatch
- 可以通过CloudWatch监控函数的执行情况
- 建议设置CloudWatch告警监控函数错误率

## 注意事项

1. 确保Lambda函数有足够的权限访问Route53 Resolver
2. 检查VPC和Resolver规则是否在同一区域
3. 关联操作是幂等的，重复关联不会报错
4. 解除不存在的关联也不会报错
