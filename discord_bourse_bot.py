from alphaVantageAPI import AlphaVantage
from google_images_search import GoogleImagesSearch
import plotly.graph_objects as go
import io, discord, schedule, time, requests, json
from PIL import Image

def get_company_logo(company_name):

    # Load Google API key and CX from json configuration file
    with open('bourse.json', 'r') as config_file:
        data = json.load(config_file)
    google_api_key = data["config"]["google_api_key"]
    google_cx = data["config"]["google_cx"]
 
    # Configure Google Images Search API with your API key and CX
    gis = GoogleImagesSearch(google_api_key, google_cx)

    # Perform image search with the company name and keyword "logo"
    search_params = {
        'q': f'{company_name} logo site:wikipedia.org',
        'num': 1, 
        'safe': 'high',
        'fileType': 'jpg|png'
    }
    
    # Perform the image search
    gis.search(search_params=search_params)

    # Retrieve the URL of the logo image
    image_url = gis.results()[0].url

    # Return the URL
    return image_url

def collect_and_send_trade_data(company_name, company_boursier_url, company_symbol):

    # Enable/Disable debug mode
    debug_mode = False
    if debug_mode:
        print("Debug mode is enabled.")

    # Load configuration such as API keys from json file
    with open('bourse.json', 'r') as config_file:
        data = json.load(config_file)
    alphavantage_api_key = data["config"]["alphavantage_api_key"]
    page2images_api_key = data["config"]["page2images_api_key"]
    discord_token = data["config"]["discord_token"]
    discord_channel_id = data["config"]["discord_channel_id"]

    # Initialize the AlphaVantage Class
    av = AlphaVantage(
        api_key=alphavantage_api_key,
        premium=False,
        output_size="compact",
        datatype='json',
        export=False,
        clean=True,
    )

    # Get symbol currency and name 
    company_symbol_currency = av.search(company_symbol)['currency'].values[0]
    company_symbol_name = av.search(company_symbol)['name'].values[0]

    # Company trade data
    quote = av.quote(company_symbol)
    data = av.data(symbol=company_symbol, function="DA") # Daily Adjusted
    price_change_day_pct = float(data['close'].pct_change(periods=1).iloc[-1] * 100)
    price_change_week_pct = float(((data['close'].tail(5).iloc[-1] - data['close'].tail(5).iloc[0]) / data['close'].tail(5).iloc[0]) * 100)
    price_change_month_pct = float(((data['close'].tail(20).iloc[-1] - data['close'].tail(20).iloc[0]) / data['close'].tail(20).iloc[0]) * 100)

    # Generate the graph using Plotly
    fig = go.Figure(data=go.Scatter(x=data.index, y=data['close'], mode='lines', name='Données'))

    # Customization
    fig.update_layout(
        title=f"Evolution de l'action {company_symbol_name}",
        xaxis_title="Date",
        yaxis_title="Prix",
        template="plotly_dark",
        xaxis=dict(showgrid=False), 
        yaxis=dict(showgrid=False) 
    )

    # Convert the graph to an image
    graph_to_image = fig.to_image(format='png')

    url = "http://api.page2images.com/restfullink?p2i_url=http://www.boursier.com/actions/consensus/" + company_boursier_url + "&p2i_key=" + page2images_api_key + "&p2i_size=1280x0&p2i_screen=1280x750&p2i_fullpage=1&p2i_wait=0&p2i_quality=100&p2i_imageformat=jpg&p2i_refresh=1"
    reponse = requests.post(url)
    reponse_json = json.loads(reponse.text)
    if debug_mode:
        print(reponse_json)

    while reponse_json['status'] == 'processing':
        time.sleep(5)
        reponse = requests.post(url)
        reponse_json = json.loads(reponse.text)
        if debug_mode:
            print(reponse_json)

    if reponse_json['status'] == 'error':
        print("An issue occured with the Page2Images API.")
        exit(1)

    if reponse_json['status'] == 'finished':
        url_image = reponse_json['image_url']
        if debug_mode:
            print(url_image)
        reponse_image = requests.get(url_image)
        img = Image.open(io.BytesIO(reponse_image.content))
        box = (160, 765, 800, 1028)
        image_stream_consensus = io.BytesIO()
        img.crop(box).save(image_stream_consensus, format='JPEG')
        image_stream_consensus.seek(0)

    # Connect to the Discord bot
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    async def send_trading_info():
        embed = discord.Embed(color=0x044fc8)
        embed.set_author(name=company_name, icon_url=get_company_logo(company_name))
        embed.set_thumbnail(url=get_company_logo(company_name))
        embed.add_field(name="Action", value=f"{company_symbol_name} ({company_symbol})", inline=False)
        embed.add_field(name="Prix", value=f"{float(quote['price'].values[0]):.2f} {company_symbol_currency}", inline=False)
        embed.add_field(name="Tendance journalière", value=f"{price_change_day_pct:.2f}%", inline=True)
        embed.add_field(name="Tendance hebdomadaire", value=f"{price_change_week_pct:.2f}%", inline=True)
        embed.add_field(name="Tendance mensuelle", value=f"{price_change_month_pct:.2f}%", inline=True)
        embed.add_field(name="Graphique d'évolution du cours de l'action", value='', inline=False)
        embed.set_image(url="attachment://" + company_name + "_graph.png")
        embed2 = discord.Embed(color=0x044fc8)
        embed2.set_author(name=company_name, icon_url=get_company_logo(company_name))
        embed2.set_thumbnail(url=get_company_logo(company_name))
        embed2.add_field(name="Détail du consensus des analystes", value='', inline=False)
        embed2.set_image(url="attachment://" + company_name + "_consensus.jpg")

        # Create a Discord file object with the image stream
        graph = discord.File(io.BytesIO(graph_to_image), filename=company_name + "_graph.png")
        consensus = discord.File(image_stream_consensus, filename=company_name + "_consensus.jpg")  
        
        # Send the message to the Discord channel
        channel = client.get_channel(discord_channel_id)
        await channel.send(file=graph, embed=embed)
        await channel.send(file=consensus, embed=embed2)

    @client.event
    async def on_ready():
        print('Bot connected to Discord.')
        await send_trading_info()
        # Exit the event loop
        print('Message sent.')
        await client.close()

    # Run the Discord Bot
    client.run(discord_token)

# Function to be executed ("main")
def run_daily_task():

    # Load companies information from json file
    f = open("bourse.json", "r")
    data = json.load(f)
    for data in data["companies"]:
        company_name = data["name"]
        company_boursier_url = data["infos"]["boursier.com"]
        company_symbol = data["infos"]["alpha_vantage_api"]
        # Call the function with appropriate parameters
        collect_and_send_trade_data(company_name, company_boursier_url, company_symbol)

# Schedule the daily execution at 6:00 PM
schedule.every().day.at("18:00").do(run_daily_task)

# Execution loop
while True:
    schedule.run_pending()
    time.sleep(1)