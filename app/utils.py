import re
import logging
from ipaddress import ip_address, ip_network
logging.info("Logging configuration is active in utils.py")

def is_valid_ip(ip):
    """
    Kiểm tra xem chuỗi có phải là địa chỉ IP hợp lệ hay không.
    Hỗ trợ cả IPv4 và IPv6.
    """
    try:
        ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_cidr(cidr):
    """
    Kiểm tra xem chuỗi có phải là IP Range dạng CIDR hợp lệ hay không.
    """
    try:
        ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False

def is_valid_ip_or_cidr(value):
    """
    Kiểm tra xem chuỗi có phải là địa chỉ IP hoặc IP Range dạng CIDR hợp lệ hay không.
    """
    return is_valid_ip(value) or is_valid_cidr(value)



def validate_domain_entry(domain):
    """
    Validate a single domain string.
    Returns True if valid, False otherwise.
    Does NOT raise generic exceptions, just returns boolean for simple checks.
    """
    # Regex patterns
    domain_pattern = r'^(\.[a-zA-Z0-9-]+)+\.[a-zA-Z]{2,}$'  # Domain must start with '.'
    simple_domain_pattern = r'^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$' # Standard domain (e.g., sub.example.com)
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'  # IPv4
    hostname_pattern = r'^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)$'  # Hostname (simple)

    domain = domain.strip()
    if not domain:
        return False
    
    # Check patterns
    if re.match(domain_pattern, domain):
         return True
    elif not domain.startswith('.') and re.match(simple_domain_pattern, domain):
         # Valid domain but missing dot - Accept it (Whitelist Service handles leading dot logic if needed, or treats as exact match)
         return True
    elif re.match(ip_pattern, domain):
        return True
    elif re.match(hostname_pattern, domain):
        return True
    
    return False

def validate_allowed_domains(domains):
    """
    CHECK list of domains, IPs, or hostnames.
    Ensures domains start with '.' if they are domains (for Squid partial matching).
    Removes subdomains if parent exists.
    """
    logging.info(f"Validating domains: {domains}") 

    # Regex patterns
    # Regex patterns - Updated to support complex subdomains
    domain_pattern = r'^(\.[a-zA-Z0-9-]+)+\.[a-zA-Z]{2,}$'
    simple_domain_pattern = r'^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$'
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$' 
    hostname_pattern = r'^(?!-)[a-zA-Z0-9-]{1,63}(?<!-)$'

    unique_domains = []
    for domain in domains.splitlines():
        domain = domain.strip()
        logging.info(f"Checking domain: {domain}") 

        if domain: 
            if re.match(domain_pattern, domain):
                if not any(domain.endswith(existing) for existing in unique_domains):
                    unique_domains.append(domain)
            elif re.match(simple_domain_pattern, domain) and not domain.startswith('.'):
                # Domain is valid but missing dot -> Automatically add it
                logging.info(f"Auto-adding leading dot to: {domain}")
                domain = '.' + domain
                unique_domains.append(domain)
            elif re.match(ip_pattern, domain):
                unique_domains.append(domain)
            elif re.match(hostname_pattern, domain):
                unique_domains.append(domain)
            else:
                logging.error(f"Invalid domain: {domain}")
                raise ValueError(f'Invalid domain: {domain}')

    # Remove subdomains if parent exists
    unique_domains = sorted(unique_domains, key=len)
    filtered_domains = []
    for domain in unique_domains:
        if not any(domain.endswith(existing) and domain != existing for existing in filtered_domains):
            filtered_domains.append(domain)
        else:
            # Just log, don't flash
            logging.warning(f"Duplicated domain found: {domain}")

    return filtered_domains