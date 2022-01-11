from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# uncomment the following to create your private and public key pair
# private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
# public_key = private_key.public_key()
# private_key_pem = private_key.private_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PrivateFormat.PKCS8, # TraditionalOpenSSL
#     encryption_algorithm=serialization.NoEncryption()
# )
# with open('priv.pem', 'wb') as f:
#     f.write(private_key_pem)
#
# public_key_pem = public_key.public_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PublicFormat.SubjectPublicKeyInfo # PKCS1
# )
# with open('pub.cer', 'wb') as f:
#     f.write(public_key_pem)
    
    

# ## read private and public key from file

with open('priv.pem', "rb") as key_file:
    private_key_from_file = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )
private_key_pem = private_key_from_file.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,  # TraditionalOpenSSL
    encryption_algorithm=serialization.NoEncryption()
)

with open('pub.cer', "rb") as key_file:
    public_key_from_file = serialization.load_pem_public_key(
        key_file.read()
    )
public_key_pem = public_key_from_file.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo  # PKCS1
)