#!/bin/bash

# 设置变量
FUNCTION_NAME="route53-resolver-rule-manager"
REGION="us-west-2"
FORWARD_RULE_ID="rslvr-rr-4434e3b2252648c2a"
SYSTEM_RULE_ID="rslvr-rr-997b5cb773fa4a39b"
VPC_ID="vpc-0c443442382a4d7ca"

echo "=========================================="
echo "Route53 Resolver规则管理测试"
echo "=========================================="
echo "区域: $REGION"
echo "Forward Rule ID: $FORWARD_RULE_ID"
echo "System Rule ID: $SYSTEM_RULE_ID"
echo "VPC ID: $VPC_ID"
echo "=========================================="

# 测试Forward Rule关联
echo ""
echo "1. 测试Forward Rule关联操作..."
aws lambda invoke \
    --region $REGION \
    --function-name $FUNCTION_NAME \
    --payload '{
        "action": "associate",
        "resolver_rule_id": "'$FORWARD_RULE_ID'",
        "vpc_id": "'$VPC_ID'"
    }' \
    forward_associate_response.json

echo "响应内容:"
cat forward_associate_response.json | jq '.'
echo ""

# 测试System Rule关联
echo "2. 测试System Rule关联操作..."
aws lambda invoke \
    --region $REGION \
    --function-name $FUNCTION_NAME \
    --payload '{
        "action": "associate",
        "resolver_rule_id": "'$SYSTEM_RULE_ID'",
        "vpc_id": "'$VPC_ID'"
    }' \
    system_associate_response.json

echo "响应内容:"
cat system_associate_response.json | jq '.'
echo ""

# 检查当前关联状态
echo "3. 检查当前关联状态..."
echo "Forward Rule关联:"
aws route53resolver list-resolver-rule-associations \
    --region $REGION \
    --filters Name=ResolverRuleId,Values=$FORWARD_RULE_ID \
    --query 'ResolverRuleAssociations[*].{AssociationId:Id,VPCId:VPCId,Status:Status}' \
    --output table

echo ""
echo "System Rule关联:"
aws route53resolver list-resolver-rule-associations \
    --region $REGION \
    --filters Name=ResolverRuleId,Values=$SYSTEM_RULE_ID \
    --query 'ResolverRuleAssociations[*].{AssociationId:Id,VPCId:VPCId,Status:Status}' \
    --output table

echo ""

# 测试Forward Rule解除关联
echo "4. 测试Forward Rule解除关联操作..."
aws lambda invoke \
    --region $REGION \
    --function-name $FUNCTION_NAME \
    --payload '{
        "action": "disassociate",
        "resolver_rule_id": "'$FORWARD_RULE_ID'",
        "vpc_id": "'$VPC_ID'"
    }' \
    forward_disassociate_response.json

echo "响应内容:"
cat forward_disassociate_response.json | jq '.'
echo ""

# 测试System Rule解除关联
echo "5. 测试System Rule解除关联操作..."
aws lambda invoke \
    --region $REGION \
    --function-name $FUNCTION_NAME \
    --payload '{
        "action": "disassociate",
        "resolver_rule_id": "'$SYSTEM_RULE_ID'",
        "vpc_id": "'$VPC_ID'"
    }' \
    system_disassociate_response.json

echo "响应内容:"
cat system_disassociate_response.json | jq '.'
echo ""

# 最终检查关联状态
echo "6. 最终检查关联状态..."
echo "Forward Rule关联:"
aws route53resolver list-resolver-rule-associations \
    --region $REGION \
    --filters Name=ResolverRuleId,Values=$FORWARD_RULE_ID \
    --query 'ResolverRuleAssociations[*].{AssociationId:Id,VPCId:VPCId,Status:Status}' \
    --output table

echo ""
echo "System Rule关联:"
aws route53resolver list-resolver-rule-associations \
    --region $REGION \
    --filters Name=ResolverRuleId,Values=$SYSTEM_RULE_ID \
    --query 'ResolverRuleAssociations[*].{AssociationId:Id,VPCId:VPCId,Status:Status}' \
    --output table

echo ""
echo "测试完成!"

# 清理响应文件
echo "清理临时文件..."
rm -f forward_associate_response.json
rm -f system_associate_response.json
rm -f forward_disassociate_response.json
rm -f system_disassociate_response.json
