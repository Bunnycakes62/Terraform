resource "aws_lambda_function" "ces592-lgm" {
        s3_bucket = "ces592-lgm-lambda"
        s3_key = "lgm.zip"
        function_name = "Ces592LgmLambda"
        role = aws_iam_role.iam_for_lgm.arn
        handler = "lgm.lambda_handler"

        runtime = "python3.8"
}
