import random
DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"
class UserAgent:
    def __init__(self, userAgentFile="useragents.txt"):
        self.useragents = []
        try:
            with open(userAgentFile) as f:
                self.useragents = [line.strip() for line in f.readlines()]
        except Exception:
            pass
        if not self.useragents:
            self.useragents.append(DEFAULT_USER_AGENT)
    
    def generate_random_user_agent(self):
        return random.choice(self.useragents)

if __name__ == "__main__":
    useragent = UserAgent()
