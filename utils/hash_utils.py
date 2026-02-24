import hashlib
import os
import binascii

# 固定盐值（32位十六进制字符串，相当于16字节）
FIXED_SALT = "5a1e1234567890abcdef1234567890ab"

def hash_password(password):
    """
    使用 SHA-256 和固定盐值对密码进行哈希加密
    
    Args:
        password: 需要加密的明文密码
        
    Returns:
        str: 哈希后的密码
    """
    # 使用固定盐值
    salt = binascii.unhexlify(FIXED_SALT)
    
    # 将盐值和密码结合，并进行哈希
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'), 
        salt, 
        100000  # 迭代次数
    )
    
    # 将哈希值转换为十六进制
    hash_hex = binascii.hexlify(pw_hash).decode('utf-8')
    return hash_hex