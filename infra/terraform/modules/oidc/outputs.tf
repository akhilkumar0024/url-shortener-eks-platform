output "oidc_provider_arn" {
  description = "ARN of the IAM OIDC Provider"
  value       = aws_iam_openid_connect_provider.eks_cluster_oidc_provider.arn
}

output "oidc_provider_url" {
  description = "URL of the IAM OIDC Provider"
  value       = aws_iam_openid_connect_provider.eks_cluster_oidc_provider.url
}

# Helper: extracts the domain without "https://" (e.g. oidc.eks.ap-south-1.amazonaws.com/id/...)
# In AWS IAM trust policies, condition keys MUST omit "https://" (e.g. "${oidc_issuer}:sub")
output "oidc_issuer" {
  description = "OIDC issuer URL without protocol scheme"
  value       = replace(aws_iam_openid_connect_provider.eks_cluster_oidc_provider.url, "https://", "")
}
