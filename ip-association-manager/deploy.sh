#!/bin/bash

# Route53 Resolver Rule更新Lambda函数部署脚本

set -e

# 配置变量
FUNCTION_NAME="update-resolver-rule"
RUNTIME="python3.9"
TIMEOUT=60
MEMORY_SIZE=128
DEPLOYMENT_DIR="lambda-deployment"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始部署Route53 Resolver Rule更新Lambda函数...${NC}"

# 检查必需的文件
if [ ! -f "update_resolver_rule.py" ]; then
    echo -e "${RED}错误: update_resolver_rule.py 文件不存在${NC}"
    exit 1
fi

# 检查AWS CLI是否已安装
if ! command -v aws &> /dev/null; then
    echo -e "${RED}错误: AWS CLI 未安装${NC}"
    exit 1
fi

# 检查AWS凭证
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}错误: AWS凭证未配置或无效${NC}"
    exit 1
fi

# 获取账户ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${YELLOW}当前AWS账户ID: ${ACCOUNT_ID}${NC}"

# 创建部署目录
echo -e "${YELLOW}创建部署目录...${NC}"
rm -rf $DEPLOYMENT_DIR
mkdir $DEPLOYMENT_DIR
cd $DEPLOYMENT_DIR

# 复制函数文件
cp ../update_resolver_rule.py .

# 安装依赖（如果requirements.txt存在）
if [ -f "../requirements.txt" ]; then
    echo -e "${YELLOW}安装Python依赖...${NC}"
    pip install -r ../requirements.txt -t . --quiet
fi

# 创建部署包
echo -e "${YELLOW}创建部署包...${NC}"
zip -r resolver-rule-updater.zip . > /dev/null

# 检查Lambda函数是否已存在
if aws lambda get-function --function-name $FUNCTION_NAME &> /dev/null; then
    echo -e "${YELLOW}更新现有Lambda函数...${NC}"
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://resolver-rule-updater.zip
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout $TIMEOUT \
        --memory-size $MEMORY_SIZE
else
    echo -e "${YELLOW}创建新的Lambda函数...${NC}"
    
    # 检查执行角色是否存在
    ROLE_NAME="lambda-resolver-rule-execution-role"
    ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
    
    if ! aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
        echo -e "${YELLOW}创建Lambda执行角色...${NC}"
        
        # 创建信任策略
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
        
        # 创建角色
        aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document file://trust-policy.json
        
        # 附加基本执行策略
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        # 创建并附加自定义策略
        aws iam put-role-policy \
            --role-name $ROLE_NAME \
            --policy-name ResolverRuleUpdatePolicy \
            --policy-document file://../iam-policy.json
        
        echo -e "${YELLOW}等待角色创建完成...${NC}"
        sleep 10
    fi
    
    # 创建Lambda函数
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler update_resolver_rule.lambda_handler \
        --zip-file fileb://resolver-rule-updater.zip \
        --timeout $TIMEOUT \
        --memory-size $MEMORY_SIZE \
        --description "Update Route53 Resolver Rule target IPs"
fi

# 清理临时文件
cd ..
rm -rf $DEPLOYMENT_DIR

echo -e "${GREEN}部署完成！${NC}"
echo -e "${YELLOW}函数名称: ${FUNCTION_NAME}${NC}"
echo -e "${YELLOW}测试命令:${NC}"
echo "aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"resolver_rule_id\":\"rslvr-rr-xxxxxxxxx\",\"target_ips\":[\"8.8.8.8\",\"8.8.4.4\"],\"region\":\"us-east-1\"}' response.json"
