import requests
import time
from .logging import Log
import colorama

##  ##  ##
# Im revamping all this shitty old code soon no worries
##  ##  ## 

class Captcha:
    @staticmethod
    def solve(user_agent: str, api_key: str, proxy: str, service: str = 'razorcap', site_key: str = "4c672d35-0701-42b2-88c3-78380b0db560", rq_data: str = None, max_retries: int = 150) -> str | bool:
        custom = None
        headers = {
            'user-agent': "Mozilla"
        }
        if service == "razorcap":
            url = 'https://api.razorcap.xyz'
            payload = {
                "key": api_key,
                "type": "hcaptcha_basic",
                "data": {
                    "sitekey": site_key,
                    "siteurl": "discord.com",
                    "proxy": proxy,
                }
            }
            if rq_data:
                payload["data"]["rqdata"] = rq_data

        # Other service implementations omitted for brevity...

        try:
            if service == "razorcap":
                r = requests.post(f"{url}/create_task", json=payload)
            else:
                r = requests.post(f"{service}/createTask", json=payload)
        except:
            Log.bad(f"Error Creating {service} Task")
            return None

        try:
            if service == "razorcap":
                if r.json().get("task_id"):
                    taskid = r.json()["task_id"]
                else:
                    Log.bad("Error getting captcha task id")
                    return None
            else:
                # Handling for other services omitted for brevity...
                pass
        except:
            Log.bad("Error getting captcha task id")
            return None

        for i in range(max_retries):
            try:
                if service == "razorcap":
                    r = requests.get(f"{url}/get_result/{taskid}").json()
                    if r.get("status") == "solved":
                        cap_pri = r["response_key"][:35]
                        Log.good(f"Solved captcha ({colorama.Fore.LIGHTBLACK_EX}{cap_pri}..{colorama.Fore.RESET})")
                        return r["response_key"]
                else:
                    # Handling for other services omitted for brevity...
                    pass
                time.sleep(0.5)
            except Exception:
                Log.bad("Failed to solve captcha.", symbol="!")
                return None

        Log.bad("Failed to solve captcha.", symbol="!")
        return None
