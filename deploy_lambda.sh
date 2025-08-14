#!/bin/bash

# 配置变量
FUNCTION_NAME="route53-resolver-rule-manager"
REGION="us-west-2"
ROLE_NAME="lambda-route53-resolver-role"
POLICY_NAME="Route53ResolverLambdaPolicy"

echo "=========================================="
echo "部署Route53 Resolver规则管理Lambda函数"
echo "=========================================="
echo "函数名称: $FUNCTION_NAME"
echo "区域: $REGION"
echo "=========================================="

# 获取账户ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "账户ID: $ACCOUNT_ID"

# 创建IAM策略
echo ""
echo "1. 创建IAM策略..."
cat > lambda-policy.json << EOF
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
EOF

aws iam create-policy \
    --policy-name $POLICY_NAME \
    --policy-document file://lambda-policy.json \
    --description "Policy for Route53 Resolver Lambda function" \
    2>/dev/null || echo "策略可能已存在，继续..."

# 创建IAM角色
echo ""
echo "2. 创建IAM角色..."
cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json \
    --description "Execution role for Route53 Resolver Lambda function" \
    2>/dev/null || echo "角色可能已存在，继续..."

# 附加策略到角色
echo ""
echo "3. 附加策略到角色..."
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn "arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME"

aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

# 等待角色创建完成
echo ""
echo "4. 等待IAM角色生效..."
sleep 10

# 创建部署包
echo ""
echo "5. 创建部署包..."
mkdir -p lambda-deployment
cp lambda_function.py lambda-deployment/
cd lambda-deployment
zip -r ../function.zip .
cd ..

# 创建或更新Lambda函数
echo ""
echo "6. 创建Lambda函数..."
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

# 尝试创建函数
aws lambda create-function \
    --region $REGION \
    --function-name $FUNCTION_NAME \
    --runtime python3.9 \
    --role $ROLE_ARN \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --description "管理Route53 Resolver规则与VPC的关联" \
    --timeout 30 \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo "Lambda函数创建成功!"
else
    echo "函数可能已存在，尝试更新..."
    aws lambda update-function-code \
        --region $REGION \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://function.zip
    
    if [ $? -eq 0 ]; then
        echo "Lambda函数更新成功!"
    else
        echo "Lambda函数创建/更新失败!"
        exit 1
    fi
fi

# 清理临时文件
echo ""
echo "7. 清理临时文件..."
rm -f lambda-policy.json
rm -f trust-policy.json
rm -f function.zip
rm -rf lambda-deployment

echo ""
echo "=========================================="
echo "部署完成!"
echo "=========================================="
echo "函数名称: $FUNCTION_NAME"
echo "区域: $REGION"
echo "角色ARN: $ROLE_ARN"
echo ""
echo "现在可以运行测试脚本:"
echo "  chmod +x aws_cli_test.sh"
echo "  ./aws_cli_test.sh"
echo ""
echo "或者运行Python测试:"
echo "  python test_specific_resources.py"
