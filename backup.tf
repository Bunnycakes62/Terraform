resource "aws_backup_plan" "tfs-ces592-backup" {
        name = "tfs-ces592-backup"

        rule {
                rule_name = "tfs-ces592-backup-rule"
                target_vault_name = "Default"
                schedule = "cron(0 12 * * ? *)"

        }
}

resource "aws_backup_selection" "tfs-ces592-selection" {
        iam_role_arn = "arn:aws:iam::647502022961:role/service-role/AWSBackupDefaultServiceRole"
        name = "tfs-ces592-selection"
        plan_id = aws_backup_plan.tfs-ces592-backup.id

        selection_tag {
                type = "STRINGEQUALS"
                key = "assignment"
                value = "13"
        }
}