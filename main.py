import requests
import time
from .logging import Log
import colorama

class Captcha:
    @staticmethod
    def solve(user_agent: str, api_key: str, proxy: str, service: str = 'razorcap', 
              site_key: str = "4c672d35-0701-42b2-88c3-78380b0db560", rq_data: str = None, 
              max_retries: int = 150) -> str | bool:
        """
        Solves a captcha using a specified service.

        Args:
            user_agent (str): User-Agent for the request.
            api_key (str): API key for the chosen captcha service.
            proxy (str): Proxy to use, in the format "http://user:pass@ip:port" or "ip:port".
            service (str): Captcha solving service (default: 'razorcap').
            site_key (str): hCaptcha site key (default: RazorCap example key).
            rq_data (str, optional): Optional rqdata parameter for hCaptcha Enterprise.
            max_retries (int): Maximum retries to retrieve the captcha solution.

        Returns:
            str | bool: The solved captcha response key if successful, False otherwise.
        """
        headers = {'user-agent': user_agent}
        custom = False

        if service == "razorcap":
            url = "https://api.razorcap.xyz/create_task"
            payload = {
                "key": api_key,
                "type": "hcaptcha_basic",  # Use "enterprise" for hCaptcha Enterprise
                "data": {
                    "sitekey": site_key,
                    "siteurl": "discord.com",
                    "proxy": proxy,
                    "rqdata": rq_data or ""
                }
            }
        else:
            Log.bad(f"Service {service} is not supported in this implementation.")
            return None

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except Exception as e:
            Log.bad(f"Error creating {service} task: {str(e)}")
            return None

        # Parse task ID
        try:
            response_data = response.json()
            if response_data.get("task_id"):
                task_id = response_data["task_id"]
                Log.good(f"Task created successfully. Task ID: {task_id}")
            else:
                Log.bad(f"Failed to retrieve task ID: {response_data}")
                return None
        except Exception as e:
            Log.bad(f"Error parsing task ID: {str(e)}")
            return None

        # Poll for result
        for _ in range(max_retries):
            try:
                result_url = f"https://api.razorcap.xyz/get_result/{task_id}"
                result_response = requests.get(result_url, headers=headers)
                result_response.raise_for_status()
                result_data = result_response.json()

                if result_data.get("status") == "solved":
                    solution = result_data.get("response_key")
                    if solution:
                        cap_pri = solution[:35]  # Display the first 35 characters of the solution
                        Log.good(f"Solved captcha ({colorama.Fore.LIGHTBLACK_EX}{cap_pri}..{colorama.Fore.RESET})")
                        return solution

                elif result_data.get("status") == "error":
                    Log.bad("Captcha task returned an error.")
                    return None

            except Exception as e:
                Log.bad(f"Error retrieving task result: {str(e)}")
                return None

            time.sleep(0.5)  # Wait before retrying

        Log.bad("Failed to solve captcha within the retry limit.")
        return None


# Example usage
if __name__ == "__main__":
    solved_captcha = Captcha.solve(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        api_key="9836c167-2f59-4a9f-b256-6f21d82b5b76",
        proxy="prismboosts:SantaProxy_streaming-1@geo.iproyal.com:12321",
    )
    print(f"Captcha Solved: {solved_captcha}")
