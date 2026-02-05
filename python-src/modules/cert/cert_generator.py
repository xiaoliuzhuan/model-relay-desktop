"""
证书生成模块
将 generate_certs.py 的功能模块化，支持直接函数调用
"""

import atexit
import os
import tempfile

from modules.cert.ca_metadata import save_ca_info
from modules.cert.cert_utils import (
    parse_openssl_enddate_to_unix,
    parse_openssl_fingerprint,
)
from modules.runtime.process_utils import run_subprocess
from modules.runtime.resource_manager import ResourceManager


def create_temp_file(content, suffix=".cnf"):
    """创建临时文件并写入内容"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(content.encode("utf-8"))
        temp_path = temp_file.name
    # 注册脚本退出时删除临时文件
    atexit.register(lambda: os.remove(temp_path) if os.path.exists(temp_path) else None)
    return temp_path


def run_openssl_command(command, error_message, log_func=print):
    """运行 OpenSSL 命令并检查结果"""
    log_func(f"执行命令: {' '.join(command)}")
    result = run_subprocess(command, check=False, capture_output=True, text=True)

    # 特殊处理证书签署的情况 - 如果stderr包含"Signature ok"，则认为成功
    if result.returncode != 0:
        if "Signature ok" in result.stderr and "subject=" in result.stderr:
            # 证书签署成功，只是序列号文件权限问题，不影响实际功能
            log_func("证书签署成功（忽略序列号文件权限警告）")
            return True, result.stderr
        else:
            error_msg = f"{error_message}\n错误输出: {result.stderr}"
            log_func(error_msg)
            return False, error_msg

    if result.stdout:
        log_func(result.stdout.strip())
    return True, result.stdout


def _record_ca_cert_metadata(
    resource_manager: ResourceManager,
    ca_cert_path: str,
    log_func=print,
) -> bool:
    """读取 CA 证书指纹/到期时间并写入元数据文件。"""
    success, output = run_openssl_command(
        [
            resource_manager.openssl_path,
            "x509",
            "-noout",
            "-fingerprint",
            "-sha1",
            "-enddate",
            "-in",
            ca_cert_path,
        ],
        "读取 CA 证书信息失败",
        log_func,
    )
    if not success:
        return False

    fingerprint = parse_openssl_fingerprint(output)
    not_after_unix = parse_openssl_enddate_to_unix(output)
    if not fingerprint or not_after_unix is None:
        log_func("无法解析 CA 证书指纹或到期时间")
        return False

    return save_ca_info(
        resource_manager,
        fingerprint_sha1=fingerprint,
        not_after_unix=not_after_unix,
        log_func=log_func,
    )


def create_default_config_files(resource_manager, log_func=print):
    """创建默认配置文件（如果不存在）"""
    ca_dir = resource_manager.ca_path

    # 确保 ca 目录存在
    if not os.path.exists(ca_dir):
        try:
            os.makedirs(ca_dir)
            log_func(f"创建目录: {ca_dir}")
        except Exception as e:
            log_func(f"无法创建ca目录: {e}")
            return False

    # 配置文件内容定义
    config_files = {
        "openssl.cnf": """[ req ]
default_bits		= 2048
default_md		= sha256
distinguished_name	= req_distinguished_name
attributes		= req_attributes

[ req_distinguished_name ]
countryName			= Country Name (2 letter code)
countryName_min			= 2
countryName_max			= 2
stateOrProvinceName		= State or Province Name (full name)
localityName			= Locality Name (eg, city)
0.organizationName		= Organization Name (eg, company)
organizationalUnitName		= Organizational Unit Name (eg, section)
commonName			= Common Name (eg, fully qualified host name)
commonName_max			= 64
emailAddress			= Email Address
emailAddress_max		= 64

[ req_attributes ]
challengePassword		= A challenge password
challengePassword_min		= 4
challengePassword_max		= 20
""",
        "v3_ca.cnf": """[ v3_ca ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
basicConstraints = critical, CA:TRUE, pathlen:3
keyUsage = critical, cRLSign, keyCertSign
nsCertType = sslCA, emailCA
""",
        "v3_req.cnf": """[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names
""",
        "api.openai.com.cnf": """
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = api.openai.com
""",
        "api.openai.com.subj": "/C=CN/ST=State/L=City/O=Organization/OU=Unit/CN=api.openai.com",
    }

    # 创建配置文件
    for filename, content in config_files.items():
        file_path = resource_manager.get_config_file(filename)
        if not os.path.exists(file_path):
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                log_func(f"创建配置文件: {file_path}")
            except Exception as e:
                log_func(f"无法创建文件 {file_path}: {e}")
                return False
        else:
            log_func(f"配置文件已存在: {file_path}")

    return True


def generate_ca_cert(resource_manager, log_func=print, *, ca_common_name="MTGA_CA"):
    """生成 CA 证书和私钥"""
    log_func("开始生成CA证书和私钥...")

    # 读取并合并配置文件
    openssl_cnf_path = resource_manager.get_config_file("openssl.cnf")
    v3_ca_cnf_path = resource_manager.get_config_file("v3_ca.cnf")

    if not os.path.exists(openssl_cnf_path):
        log_func(f"配置文件不存在: {openssl_cnf_path}")
        return False
    if not os.path.exists(v3_ca_cnf_path):
        log_func(f"配置文件不存在: {v3_ca_cnf_path}")
        return False

    with open(openssl_cnf_path, encoding="utf-8") as f:
        openssl_cnf = f.read()
    with open(v3_ca_cnf_path, encoding="utf-8") as f:
        v3_ca_cnf = f.read()

    # 合并配置文件
    combined_config = openssl_cnf + "\n" + v3_ca_cnf
    temp_config_file = create_temp_file(combined_config)
    log_func(f"临时配置文件已创建: {temp_config_file}")

    # 生成 CA 私钥
    ca_key_path = resource_manager.get_ca_key_file()
    log_func("正在生成CA私钥 (ca.key)...")

    # 设置环境变量确保使用正确的 OpenSSL
    env = os.environ.copy()
    if os.name == "nt":
        env["PATH"] = resource_manager.openssl_dir + os.pathsep + env["PATH"]

    success, _ = run_openssl_command(
        [resource_manager.openssl_path, "genrsa", "-out", ca_key_path, "2048"],
        "生成CA私钥失败",
        log_func,
    )
    if not success:
        return False

    log_func("CA私钥已生成: ca.key")

    # 生成 CA 证书
    ca_crt_path = resource_manager.get_ca_cert_file()
    log_func("正在生成CA证书 (ca.crt)...")

    # 使用默认值构建主题字符串
    subject = f"/C=CN/ST=X/L=X/O=X/OU=X/CN={ca_common_name}"
    log_func(f"使用默认证书信息: {subject}")

    success, _ = run_openssl_command(
        [
            resource_manager.openssl_path,
            "req",
            "-new",
            "-x509",
            "-extensions",
            "v3_ca",
            "-days",
            "36500",
            "-key",
            ca_key_path,
            "-out",
            ca_crt_path,
            "-config",
            temp_config_file,
            "-subj",
            subject,
        ],
        "生成CA证书失败",
        log_func,
    )
    if not success:
        return False

    log_func("CA证书已生成: ca.crt")
    if not _record_ca_cert_metadata(resource_manager, ca_crt_path, log_func):
        log_func("CA 证书元数据写入失败")
        return False
    return True


def generate_server_cert(resource_manager, domain="api.openai.com", log_func=print):  # noqa: PLR0911, PLR0915
    """生成服务器证书"""
    log_func(f"开始为 {domain} 生成服务器证书...")

    ca_key_path = resource_manager.get_ca_key_file()
    ca_crt_path = resource_manager.get_ca_cert_file()

    # 检查必要文件是否存在
    required_files = [
        resource_manager.get_config_file("openssl.cnf"),
        resource_manager.get_config_file("v3_req.cnf"),
        resource_manager.get_config_file(f"{domain}.cnf"),
        resource_manager.get_config_file(f"{domain}.subj"),
        ca_crt_path,
        ca_key_path,
    ]

    for file_path in required_files:
        if not os.path.exists(file_path):
            log_func(f"必需文件不存在: {file_path}")
            return False

    # 读取配置文件
    with open(resource_manager.get_config_file("openssl.cnf"), encoding="utf-8") as f:
        openssl_cnf = f.read()
    with open(resource_manager.get_config_file("v3_req.cnf"), encoding="utf-8") as f:
        v3_req_cnf = f.read()
    with open(resource_manager.get_config_file(f"{domain}.cnf"), encoding="utf-8") as f:
        domain_cnf = f.read()

    # 合并配置文件
    combined_config = openssl_cnf + "\n" + v3_req_cnf + "\n" + domain_cnf
    temp_config_file = create_temp_file(combined_config)
    log_func(f"临时配置文件已创建: {temp_config_file}")

    # 读取主题信息
    with open(resource_manager.get_config_file(f"{domain}.subj"), encoding="utf-8") as f:
        subject_info = f.read().strip()

    if not subject_info:
        log_func(f"主题文件 {domain}.subj 为空或无法读取")
        return False

    log_func(f"从 {domain}.subj 读取的主题信息: {subject_info}")

    # 设置环境变量
    env = os.environ.copy()
    if os.name == "nt":
        env["PATH"] = resource_manager.openssl_dir + os.pathsep + env["PATH"]

    # 生成服务器私钥
    server_key_path = resource_manager.get_key_file(domain)
    log_func(f"正在生成私钥 {domain}.key (2048位 RSA)...")

    success, _ = run_openssl_command(
        [resource_manager.openssl_path, "genrsa", "-out", server_key_path, "2048"],
        f"生成私钥 {domain}.key 失败",
        log_func,
    )
    if not success:
        return False

    # 将私钥转换为 PKCS#8 格式
    log_func(f"正在将私钥 {domain}.key 转换为 PKCS#8 格式...")
    server_key_pk8_path = server_key_path + ".pk8"

    success, _ = run_openssl_command(
        [
            resource_manager.openssl_path,
            "pkcs8",
            "-topk8",
            "-nocrypt",
            "-in",
            server_key_path,
            "-out",
            server_key_pk8_path,
        ],
        f"将私钥 {domain}.key 转换为 PKCS#8 格式失败",
        log_func,
    )
    if not success:
        return False

    # 删除原始私钥并重命名 PKCS#8 格式的私钥
    os.remove(server_key_path)
    os.rename(server_key_pk8_path, server_key_path)
    log_func(f"私钥 {domain}.key 处理完成")

    # 生成 CSR
    server_csr_path = os.path.join(resource_manager.ca_path, f"{domain}.csr")
    log_func(f"正在生成证书签名请求 (CSR) {domain}.csr...")

    success, _ = run_openssl_command(
        [
            resource_manager.openssl_path,
            "req",
            "-reqexts",
            "v3_req",
            "-sha256",
            "-new",
            "-key",
            server_key_path,
            "-out",
            server_csr_path,
            "-config",
            temp_config_file,
            "-subj",
            subject_info,
        ],
        f"生成 CSR {domain}.csr 失败",
        log_func,
    )
    if not success:
        return False

    log_func(f"CSR {domain}.csr 生成成功")

    # 使用 CA 签署证书
    server_crt_path = resource_manager.get_cert_file(domain)
    log_func(f"正在使用 CA 签署证书 {domain}.crt...")

    # 为LibreSSL准备序列号文件路径（避免权限问题）
    ca_serial_path = os.path.join(resource_manager.ca_path, "ca.srl")

    # 确保序列号文件存在且可写
    try:
        if not os.path.exists(ca_serial_path):
            with open(ca_serial_path, "w") as f:
                f.write("01")
    except Exception as e:
        log_func(f"警告: 无法创建序列号文件: {e}")
        # 如果无法创建序列号文件，仍继续尝试，让OpenSSL自己处理

    success, output = run_openssl_command(
        [
            resource_manager.openssl_path,
            "x509",
            "-req",
            "-extensions",
            "v3_req",
            "-days",
            "365",
            "-sha256",
            "-in",
            server_csr_path,
            "-CA",
            ca_crt_path,
            "-CAkey",
            ca_key_path,
            "-CAserial",
            ca_serial_path,
            "-out",
            server_crt_path,
            "-extfile",
            temp_config_file,
        ],
        f"签署证书 {domain}.crt 失败",
        log_func,
    )
    if not success:
        log_func(f"签署证书失败，输出: {output}")
        return False

    # 验证证书文件是否实际生成且不为空
    if not os.path.exists(server_crt_path):
        log_func(f"错误: 证书文件 {server_crt_path} 未生成")
        return False

    file_size = os.path.getsize(server_crt_path)
    if file_size == 0:
        log_func(f"错误: 证书文件 {server_crt_path} 为空文件")
        return False

    log_func(f"证书 {domain}.crt 生成成功 (大小: {file_size} bytes)")
    log_func(f"私钥 {domain}.key 生成成功")
    log_func("")
    log_func("=== 服务器证书生成完成 ===")
    return True


def generate_certificates(domain="api.openai.com", *, ca_common_name="MTGA_CA", log_func=print):
    """
    一键生成 CA 证书和服务器证书

    参数:
        domain: 服务器证书的域名
        log_func: 日志输出函数

    返回:
        成功返回 True，失败返回 False
    """
    log_func("=" * 60)
    log_func("证书生成工具 - 一键生成CA证书和服务器证书")
    log_func("=" * 60)

    # 初始化资源管理器
    resource_manager = ResourceManager()

    # 检查 OpenSSL 是否可用
    try:
        result = run_subprocess(
            [resource_manager.openssl_path, "version"], check=False, capture_output=True, text=True
        )
        if result.returncode == 0:
            log_func(f"检测到OpenSSL: {result.stdout.strip()}")
        else:
            log_func("OpenSSL命令执行失败。请确保OpenSSL已安装并添加到PATH中。")
            return False
    except FileNotFoundError:
        log_func("未找到OpenSSL。请安装OpenSSL并确保它在系统PATH中。")
        return False

    # 创建默认配置文件
    if not create_default_config_files(resource_manager, log_func):
        return False

    # 生成 CA 证书
    if not generate_ca_cert(resource_manager, log_func, ca_common_name=ca_common_name):
        return False

    # 生成服务器证书
    if not generate_server_cert(resource_manager, domain, log_func):
        return False

    # 输出结果摘要
    log_func("=" * 60)
    log_func("证书生成完成！")
    log_func("=" * 60)
    log_func(f"CA 证书: {resource_manager.get_ca_cert_file()}")
    log_func(f"CA 私钥: {resource_manager.get_ca_key_file()} (请妥善保管，勿泄露)")
    log_func(f"服务器证书: {resource_manager.get_cert_file(domain)}")
    log_func(f"服务器私钥: {resource_manager.get_key_file(domain)} (请妥善保管，勿泄露)")
    log_func("")
    log_func("后续步骤:")
    log_func("1. 将CA证书 (ca.crt) 导入到Windows的受信任的根证书颁发机构存储中")
    log_func("2. 修改hosts文件，将api.openai.com指向127.0.0.1")
    log_func("3. 配置并运行代理服务器")
    log_func("=" * 60)

    return True
