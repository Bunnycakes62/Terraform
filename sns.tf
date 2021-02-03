# Create the SNS topic
resource "aws_sns_topic" "sns-ces592-a9-lgm" {
        name = "sns-ces592-a9-lgm"
        kms_master_key_id = "alias/aws/sns"
}

# Create the SNS topic subscription
resource "aws_sns_topic_subscription" "sub-ces592-a9-lgm-cell" {
        topic_arn = aws_sns_topic.sns-ces592-a9-lgm.arn
        protocol = "sms"
        endpoint = "+17073044472"

        filter_policy = jsonencode(map("lgm",list("true")))
}


resource "aws_sns_topic_subscription" "sub-ces592-a9-lgm-lambda" {
        topic_arn = aws_sns_topic.sns-ces592-a9-lgm.arn
        protocol = "lambda"
        endpoint = aws_lambda_function.ces592-lgm.arn
}