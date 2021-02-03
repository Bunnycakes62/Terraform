#data "aws_secretsmanager_secret_version" "creds" {
#  # Fill in the name you gave to your secret
#  secret_id = "ces592-week11"
#}
#
#
#locals {
#  db_creds = jsondecode(
#    data.aws_secretsmanager_secret_version.creds.secret_string
#  )
#}
#
#
#output "db_creds" {
#        value = local.db_creds
#}


resource "aws_rds_cluster" "rds-ces592-a10" {
        cluster_identifier = "rds-ces592-a10"
        engine_mode = "serverless"
        engine = "aurora-mysql"
        engine_version = "5.7.mysql_aurora.2.07.1"
        master_username = "admin"
#       master_password = local.db_creds.password
        master_password = "password"
        storage_encrypted = true
        skip_final_snapshot = true

        db_subnet_group_name = aws_db_subnet_group.subg-ces592-a10.name

#       database_name = "a10db"

        scaling_configuration {
                auto_pause = true
                max_capacity = 2
                min_capacity = 1
                seconds_until_auto_pause = 300
        }
}