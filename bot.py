from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import json
import os
import getpass
import openai
import configparser
import argparse

class DiscordAutomationBot:
    def __init__(self, headless=False, openai_api_key=None):
        """Initialize the Discord automation bot with browser options and OpenAI API key"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        self.actions = ActionChains(self.driver)
        
        # Set up OpenAI API for AI assistance
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            print("OpenAI API key set successfully")
        else:
            print("Warning: No OpenAI API key provided. AI assistance will not work.")
        
        # Command history
        self.command_history = []
        
        # Available commands
        self.commands = {
            "help": self.show_help,
            "login": self.login,
            "send": self.send_message,
            "join": self.join_server,
            "channel": self.switch_channel,
            "dm": self.open_dm,
            "react": self.add_reaction,
            "reply": self.reply_to_message,
            "search": self.search_messages,
            "ai_chat": self.generate_ai_response,
            "exit": self.close
        }
        
    def show_help(self, *args):
        """Display available commands and their usage"""
        help_text = """
Available Commands:
------------------
help                       - Show this help message
login <email> <password>   - Login to Discord
send <message>             - Send message in current channel
join <invite_code>         - Join a Discord server with invite code
channel <channel_name>     - Switch to a specific channel
dm <username>              - Open DM with specific user
react <emoji> <msg_index>  - React to a message with emoji (index counts from bottom)
reply <msg_index> <text>   - Reply to a message (index counts from bottom)
search <query>             - Search for messages containing the query
ai_chat <prompt>           - Generate a response using AI
exit                       - Close the bot

Example: send Hello everyone!
        """
        print(help_text)
        return True
        
    def login(self, email=None, password=None):
        """Log in to Discord"""
        self.driver.get("https://discord.com/login")
        print("Loading Discord login page...")
        
        # Wait for login page to be fully loaded
        time.sleep(3)
        
        if not email or not password:
            if len(email) > 0:  # Only email was provided as argument
                password = getpass.getpass("Enter your Discord password: ")
            else:
                email = input("Enter your Discord email: ")
                password = getpass.getpass("Enter your Discord password: ")
            
        try:
            # Find and fill email field
            email_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.send_keys(email)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            print("Login credentials submitted...")
            
            # Wait for successful login (Discord main page)
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Servers']"))
            )
            print("Successfully logged in to Discord!")
            
            # Wait for everything to load
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def send_message(self, *message_parts):
        """Send a message in the current channel"""
        if not message_parts:
            print("Error: No message content provided")
            return False
            
        message = " ".join(message_parts)
        
        try:
            # Find the message input field
            message_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
            )
            
            # Clear any existing text and type the message
            message_input.clear()
            message_input.send_keys(message)
            
            # Send the message with Enter key
            message_input.send_keys(Keys.RETURN)
            print(f"Message sent: {message}")
            
            # Add a small delay to ensure message is sent
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def join_server(self, invite_code=None):
        """Join a Discord server with an invite code"""
        if not invite_code:
            invite_code = input("Enter the server invite code: ")
            
        # Clean the invite code (sometimes users paste the full URL)
        if "discord.gg/" in invite_code:
            invite_code = invite_code.split("discord.gg/")[1]
        if "invite/" in invite_code:
            invite_code = invite_code.split("invite/")[1]
            
        try:
            # Navigate to invite URL
            self.driver.get(f"https://discord.com/invite/{invite_code}")
            print(f"Opening invite link for code: {invite_code}...")
            
            # Wait for the accept button and click it
            accept_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Join')]"))
            )
            accept_button.click()
            
            # Wait for the server to load
            time.sleep(5)
            print("Successfully joined the server!")
            return True
            
        except Exception as e:
            print(f"Error joining server: {e}")
            return False
    
    def switch_channel(self, *channel_name_parts):
        """Switch to a specific channel"""
        if not channel_name_parts:
            print("Error: No channel name provided")
            return False
            
        channel_name = " ".join(channel_name_parts)
        
        try:
            # Look for the channel in the sidebar
            channel_elements = self.driver.find_elements(By.XPATH, 
                f"//div[contains(@class, 'channelName') and contains(text(), '{channel_name}')]")
            
            if not channel_elements:
                print(f"Channel '{channel_name}' not found")
                return False
                
            # Click on the first matching channel
            channel_elements[0].click()
            print(f"Switched to channel: {channel_name}")
            
            # Wait for channel to load
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Error switching channel: {e}")
            return False
    
    def open_dm(self, username=None):
        """Open a direct message with a specific user"""
        if not username:
            username = input("Enter the username to DM: ")
            
        try:
            # Click on DMs button first
            dm_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Direct Messages']"))
            )
            dm_button.click()
            time.sleep(1)
            
            # Click on the search/find DM button
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Find or start a conversation')]"))
            )
            search_button.click()
            
            # Enter the username in the search field
            search_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Where would you like to go?']"))
            )
            search_field.clear()
            search_field.send_keys(username)
            time.sleep(2)
            
            # Find and click on the username in the results
            user_result = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{username}')]"))
            )
            user_result.click()
            
            print(f"Opened DM with: {username}")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Error opening DM: {e}")
            return False
    
    def add_reaction(self, emoji=None, message_index=1):
        """Add a reaction to a message"""
        if not emoji:
            emoji = input("Enter the emoji to react with: ")
            
        try:
            # Convert message_index to integer if it's a string
            if isinstance(message_index, str):
                message_index = int(message_index)
                
            # Find all messages in the current channel
            messages = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
            
            if not messages or len(messages) < message_index:
                print(f"Message at index {message_index} not found")
                return False
                
            # Get the message to react to (counting from bottom)
            target_message = messages[-message_index]
            
            # Hover over the message to show action buttons
            self.actions.move_to_element(target_message).perform()
            
            # Click the add reaction button
            reaction_button = target_message.find_element(By.XPATH, ".//div[@aria-label='Add Reaction']")
            reaction_button.click()
            
            # Wait for emoji picker
            time.sleep(1)
            
            # Enter the emoji in the search field
            emoji_search = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Find the perfect emoji']"))
            )
            emoji_search.send_keys(emoji)
            
            # Wait for search results
            time.sleep(1)
            
            # Click the first emoji result
            emoji_result = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@role='menuitem'][1]"))
            )
            emoji_result.click()
            
            print(f"Added {emoji} reaction to message #{message_index}")
            return True
            
        except Exception as e:
            print(f"Error adding reaction: {e}")
            return False
    
    def reply_to_message(self, message_index=None, *reply_text_parts):
        """Reply to a specific message"""
        if not message_index or not reply_text_parts:
            message_index = input("Enter message index to reply to: ")
            reply_text = input("Enter your reply: ")
        else:
            reply_text = " ".join(reply_text_parts)
            
        try:
            # Convert message_index to integer
            message_index = int(message_index)
            
            # Find all messages in the current channel
            messages = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
            
            if not messages or len(messages) < message_index:
                print(f"Message at index {message_index} not found")
                return False
                
            # Get the message to reply to (counting from bottom)
            target_message = messages[-message_index]
            
            # Hover over the message to show action buttons
            self.actions.move_to_element(target_message).perform()
            
            # Click the reply button
            reply_button = target_message.find_element(By.XPATH, ".//div[@aria-label='Reply']")
            reply_button.click()
            
            # Wait for reply box to appear
            time.sleep(1)
            
            # Enter the reply text
            reply_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
            )
            reply_input.clear()
            reply_input.send_keys(reply_text)
            reply_input.send_keys(Keys.RETURN)
            
            print(f"Replied to message #{message_index}")
            return True
            
        except Exception as e:
            print(f"Error replying to message: {e}")
            return False
    
    def search_messages(self, *query_parts):
        """Search for messages containing specific text"""
        if not query_parts:
            query = input("Enter search query: ")
        else:
            query = " ".join(query_parts)
            
        try:
            # Click the search button
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Search']"))
            )
            search_button.click()
            
            # Enter the search query
            search_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
            )
            search_field.clear()
            search_field.send_keys(query)
            search_field.send_keys(Keys.RETURN)
            
            print(f"Searching for: {query}")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Error performing search: {e}")
            return False
    
    def generate_ai_response(self, *prompt_parts):
        """Generate a response using OpenAI API and send it"""
        if not self.openai_api_key:
            print("Error: OpenAI API key not configured")
            return False
            
        if not prompt_parts:
            prompt = input("Enter prompt for AI response: ")
        else:
            prompt = " ".join(prompt_parts)
            
        try:
            print(f"Generating AI response for: {prompt[:50]}...")
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # or whichever model you prefer
                messages=[
                    {"role": "system", "content": "You are a helpful assistant in a Discord conversation. Keep your responses concise and conversational."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            
            # Extract the response text
            ai_response = response.choices[0].message.content.strip()
            print(f"AI generated response: {ai_response[:50]}...")
            
            # Send the response in the current channel
            return self.send_message(ai_response)
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return False
    
    def process_command(self, command_line):
        """Process a user command"""
        if not command_line:
            return False
            
        # Add command to history
        self.command_history.append(command_line)
        
        # Parse command and arguments
        parts = command_line.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Execute command if it exists
        if command in self.commands:
            return self.commands[command](*args)
        else:
            print(f"Unknown command: {command}. Type 'help' for available commands.")
            return False
    
    def save_config(self, config):
        """Save current configuration to config file"""
        try:
            with open('discord_bot_config.ini', 'w') as f:
                config.write(f)
            print("Configuration saved")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def close(self, *args):
        """Close the browser and clean up"""
        try:
            self.driver.quit()
            print("Browser closed.")
            return True
        except:
            pass
        return False

def load_config():
    """Load configuration from config.ini file"""
    config = configparser.ConfigParser()
    
    # Define default configuration
    default_config = {
        'Discord': {
            'email': '',
            'password': ''
        },
        'OpenAI': {
            'api_key': ''
        }
    }
    
    # Check if config file exists
    if os.path.exists('discord_bot_config.ini'):
        config.read('discord_bot_config.ini')
    else:
        # Create config file with default values
        for section, keys in default_config.items():
            if not config.has_section(section):
                config.add_section(section)
            for key, value in keys.items():
                config.set(section, key, value)
        
        with open('discord_bot_config.ini', 'w') as f:
            config.write(f)
        
        print("Created discord_bot_config.ini file. Please edit it to include your credentials.")
        
    return config

def main():
    print("Discord Automation Bot with AI Support")
    print("=====================================")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Discord Automation Bot')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--login', action='store_true', help='Login automatically using config')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Get OpenAI API key
    openai_api_key = config.get('OpenAI', 'api_key', fallback='')
    if not openai_api_key:
        openai_api_key = input("Enter your OpenAI API key (press Enter to skip): ")
        if openai_api_key:
            # Save to config
            if not config.has_section('OpenAI'):
                config.add_section('OpenAI')
            config.set('OpenAI', 'api_key', openai_api_key)
            with open('discord_bot_config.ini', 'w') as f:
                config.write(f)
    
    # Initialize bot
    bot = DiscordAutomationBot(headless=args.headless, openai_api_key=openai_api_key)
    
    # Show help
    bot.show_help()
    
    # Auto-login if requested
    if args.login:
        email = config.get('Discord', 'email', fallback='')
        password = config.get('Discord', 'password', fallback='')
        if email and password:
            bot.login(email, password)
    
    try:
        print("\nEnter commands (type 'help' for available commands, 'exit' to quit):")
        
        # Command loop
        running = True
        while running:
            command = input("\n> ")
            if command.lower() == 'exit':
                running = False
            else:
                bot.process_command(command)
                
    except KeyboardInterrupt:
        print("\nBot terminated by user.")
    finally:
        bot.close()

if __name__ == "__main__":
    main()