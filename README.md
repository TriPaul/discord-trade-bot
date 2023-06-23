# Discord Trade Bot

<img src="bot.png" alt="Bot Logo" width="300" height="200" />

Welcome to the Discord Trade Bot repository ! This bot is designed to provide users with real-time stock market data directly within their Discord server. It allows users to fetch information about various stocks, including current prices, historical data, and more. This README will guide you through the setup and usage of the Discord Stock Bot.

## Installation

To get started with the Discord Trade Bot, follow these steps:

1. Clone the repository to your local machine using the following command:
```git clone https://github.com/TriPaul/discord-trade-bot.git```

2. Navigate to the project directory:
```cd discord-trade-bot```

3. Install the required dependencies:
```pip install -r requirements.txt```

4. Create a new Discord application, retrieve the bot token and add it onto your own Discord server. You can follow the official Discord Developer Portal guide on how to create a new bot and obtain the token.
```https://discord.com/developers/docs/getting-started```

5. Create an account on Page2Images to get an free API key:
```https://www.page2images.com/home```

6. Generate an API key on Alpha Vantage : 
```https://www.alphavantage.co/support/#api-key```

7. Modify the JSON configuration file by adding API keys and companies informations :
```
{
    "config": {
        "alphavantage_api_key": "YOUR_API_KEY",
        "page2images_api_key": "YOUR_API_KEY",
        "discord_token": "YOUR_API_KEY",
        "discord_channel_id": YOUR_DISCORD_CHANNEL_ID,
        "google_api_key": "YOUR_API_KEY",
        "google_cx": "YOUR_CX"
    },
    "companies":[
        {
            "name": "Vinci",
            "infos": {
                "boursier.com": "vinci-FR0000125486,FR.html",
                "alpha_vantage_api": "DG.PAR"
            }
        },
        {
            "name": "Wallix",
            "infos": {
                "boursier.com": "wallix-FR0010131409,FR.html",
                "alpha_vantage_api": "ALLIX.PAR"
            }
        },
        {
            "name": "BNP Paribas",
            "infos": {
                "boursier.com": "bnp-paribas-FR0000131104,FR.html",
                "alpha_vantage_api": "BNP.PAR"
            }
        }
    ]
}
```

8. Start the bot by running the following command:
``` python discord_bourse_bot.py```


