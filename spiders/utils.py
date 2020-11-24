
def process_secucode(data: dict):
    secu_code = data.get("SecuCode")
    if secu_code.startswith("6"):
        data['SecuCode'] = "SH" + secu_code
    elif secu_code.startswith("3") or secu_code.startswith("0"):
        data['SecuCode'] = "SZ" + secu_code
    else:
        return None
    return data
