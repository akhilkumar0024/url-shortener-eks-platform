
output "cluster_name" {
  description = "name of the Cluster"
  value       = aws_eks_cluster.url_shortner_cluster.name
}

output "cluster_id" {
  description = "value of the cluster id"
  value       = aws_eks_cluster.url_shortner_cluster.id
}

output "cluster_endpoint" {
  description = "value of the cluster endpoint"
  value       = aws_eks_cluster.url_shortner_cluster.endpoint
}

output "cluster_certificate_authority_data" {
  description = "value of the cluster certificate authority data"
  value       = aws_eks_cluster.url_shortner_cluster.certificate_authority[0].data
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster for the OpenID Connect identity provider"
  value       = aws_eks_cluster.url_shortner_cluster.identity[0].oidc[0].issuer
}
