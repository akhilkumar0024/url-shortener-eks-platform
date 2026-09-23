# 1. Fetch the TLS certificate of the OIDC issuer to obtain its thumbprint
data "tls_certificate" "oidc_issuer" {
  url = var.cluster_oidc_issuer_url
}

# 2. Configure the AWS IAM OIDC Provider
resource "aws_iam_openid_connect_provider" "eks_cluster_oidc_provider" {
  url            = var.cluster_oidc_issuer_url
  client_id_list = ["sts.amazonaws.com"]

  # Root CA thumbprints for the OpenID Connect identity provider's server certificate
  thumbprint_list = [data.tls_certificate.oidc_issuer.certificates[0].sha1_fingerprint]
}
