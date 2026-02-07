import os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import ipaddress

sslCert = "server.crt"
sslKey = "server.key"

# Generate cert only if it doesn't exist
if not os.path.exists(sslCert) or not os.path.exists(sslKey):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "purplescout.local")
    ])
    cert = (x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName("purplescout.local")]),
                critical=False
            )
            .sign(key, hashes.SHA256()))

    # Write to files
    with open(sslCert, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    with open(sslKey, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print(f"✓ Generated self-signed certificate {sslCert} and key {sslKey}")
