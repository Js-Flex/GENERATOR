import requests
import time
import colorama
from .logging import Log  # Replace with your logging import path

class Captcha:
    @staticmethod
    def solve_razorcap(api_key: str = "9836c167-2f59-4a9f-b256-6f21d82b5b76", 
                       proxy: str = "geo.iproyal.com:12321@prismboosts:SantaProxy_streaming-1", 
                       site_key: str = "4c672d35-0701-42b2-88c3-78380b0db560", 
                       site_url: str = "https://discord.com", rq_data: str = None, max_retries: int = 150) -> str | bool:
        """
        Solves a captcha using RazorCap.

        Args:
            api_key (str): RazorCap API key.
            proxy (str): Proxy to use in the format "http://user:pass@ip:port" or "ip:port".
            site_key (str): hCaptcha site key.
            site_url (str): URL where the captcha is hosted.
            rq_data (str, optional): Optional rqdata parameter for hCaptcha enterprise.
            max_retries (int): Maximum number of retries for task completion.

        Returns:
            str | bool: Captcha solution string if successful, False otherwise.
        """
        # RazorCap Task Creation
        url = 'https://api.razorcap.xyz/create_task'
        payload = {
            "key": api_key,
            "type": "hcaptcha_basic",  # Can be "enterprise" for enterprise captchas
            "data": {
                "sitekey": site_key,
                "siteurl": site_url,
                "proxy": proxy,
                "rqdata": rq_data if rq_data else ""
            }
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            Log.bad(f"Error creating RazorCap task: {str(e)}")
            return False

        # Parse task ID
        task_id = response.json().get("task_id")
        if not task_id:
            Log.bad(f"Error retrieving task ID: {response.text}")
            return False

        Log.good(f"RazorCap task created successfully. Task ID: {task_id}")

        # Poll for task result
        for _ in range(max_retries):
            try:
                result_response = requests.post(
                    "https://api.razorcap.xyz/get_task_data",
                    json={"key": api_key, "task_id": task_id}
                )
                result_response.raise_for_status()
                result_data = result_response.json()

                if result_data.get("status") == "completed":
                    solution = result_data.get("solution")
                    if solution:
                        cap_pri = solution[:35]  # Display the first 35 characters of the solution
                        Log.good(f"Solved captcha ({colorama.Fore.LIGHTBLACK_EX}{cap_pri}..{colorama.Fore.RESET})")
                        return solution

            except Exception as e:
                Log.bad(f"Error retrieving RazorCap task result: {str(e)}")
                return False

            time.sleep(0.5)  # Delay between retries

        Log.bad("Failed to solve captcha within retry limit.")
        return False


# Example usage:
if __name__ == "__main__":
    solved_captcha = Captcha.solve_razorcap()
    print(f"Captcha Solved: {solved_captcha}")
