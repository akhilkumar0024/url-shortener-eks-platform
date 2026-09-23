# 1.Queue to catch the Click Analytics 
resource "aws_sqs_queue" "click_analytics_q" {
  name                      = "click_analytics_q"
  delay_seconds             = 5     #when a message is pushed to Q is becomes available for consumption only after 5 secs
  max_message_size          = 2048  #max size of a message in bytes
  message_retention_seconds = 86400 #default is 4 days, max is 14 days
  receive_wait_time_seconds = 10    #long polling waits for 10 secs to respond if the queue contains no messages 
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.click_analytics_dq.arn
    maxReceiveCount     = 4
  })

  tags = {
    Environment = "production"
  }
}

# 2.DQ to catch the mesages that dont get processed even after 4 attempts
resource "aws_sqs_queue" "click_analytics_dq" {
  name = "click_analytics_dq"
}

# 3. Redrive Policy to allow only the main queue to push messages to DQ
resource "aws_sqs_queue_redrive_allow_policy" "click_analytics_dq_policy" {
  queue_url = aws_sqs_queue.click_analytics_dq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.click_analytics_q.arn]
  })
}


