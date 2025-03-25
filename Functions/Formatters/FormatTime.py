def Format_Time(seconds):
    if not seconds:
        seconds = 0 
    days, remainder = divmod(seconds, 86400)  
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    uptime_parts = []
    if days > 0:
        uptime_parts.append(f"{days}d")
    if hours > 0:
        uptime_parts.append(f"{hours}h")
    if minutes > 0:
        uptime_parts.append(f"{minutes}m")
    if seconds > 0 or not uptime_parts: 
        uptime_parts.append(f"{seconds}s")

    if seconds == 0:
        return "ERROR"
    return " ".join(uptime_parts)

