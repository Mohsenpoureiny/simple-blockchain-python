import rsa

(publickey, privatekey) = rsa.newkeys(1024)
print(publickey,privatekey)
sig = rsa.sign("Hi".encode(), privatekey, 'SHA-256')

rsa.verify("Hi".encode(),sig,publickey)