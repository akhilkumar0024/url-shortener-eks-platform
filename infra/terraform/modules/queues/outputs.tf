output "queue_url" {
  description = "URL of the click analytics SQS queue"
  value       = aws_sqs_queue.click_analytics_q.url
}

output "queue_arn" {
  description = "ARN of the click analytics SQS queue"
  value       = aws_sqs_queue.click_analytics_q.arn
}

output "dlq_url" {
  description = "URL of the Dead Letter Queue"
  value       = aws_sqs_queue.click_analytics_dq.url
}

output "dlq_arn" {
  description = "ARN of the Dead Letter Queue"
  value       = aws_sqs_queue.click_analytics_dq.arn
}
