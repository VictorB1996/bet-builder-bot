def get_headers() -> dict[str, str]:
    """Generate headers. Might need to randomize user-agent in the future."""
    headers = {
        "authority": "api.casapariurilor.ro",
        "method": "GET",
        "path": "",  # This should be set dynamically based on the request path
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-language": "ro-RO",
        "accept_encoding": "gzip, deflate, br, zstd",
        "origin": "https://www.casapariurilor.ro",
        "priority": "u=1, i",
        "referer": "https://www.casapariurilor.ro/",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    }

    return headers
