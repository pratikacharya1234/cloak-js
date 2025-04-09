from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re
import json
import os
import getpass
import openai
import configparser

class SmartBookAutomation:
    def __init__(self, headless=False, openai_api_key=None):
        """Initialize the SmartBook automation tool with browser options and OpenAI API key"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        
        # Set up OpenAI API
        self.openai_api_key = openai_api_key or os.environ.get('')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            print("OpenAI API key set successfully")
        else:
            print("Warning: No OpenAI API key provided. AI answer selection will not work.")
        
    def login(self, username=None, password=None):
        """Log in to the SmartBook platform"""
        self.driver.get("")
        print("Loading login page...")
        
        # Wait for login page to be fully loaded
        time.sleep(3)
        
        if not username:
            username = input("Enter your SmartBook username/email: ")
        if not password:
            password = getpass.getpass("Enter your SmartBook password: ")
            
        try:
            # Find and fill username field
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            print("Login credentials submitted...")
            
            # Wait for successful login and redirect
            self.wait.until(
                EC.url_contains("learning.mheducation.com")
            )
            print("Successfully logged in!")
            
        except Exception as e:
            print(f"Login failed: {e}")
            self.close()
            return False
            
        return True
    
    def navigate_to_assignment(self):
        """Navigate to the current assignment page"""
        try:
            print("Looking for available assignments...")
            
            # Wait for the assignments page to load
            assignments = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'assignment-card')]"))
            )
            
            if not assignments:
                print("No assignments found.")
                return False
                
            # Click on the first available assignment
            assignments[0].click()
            print("Navigating to assignment...")
            
            # Wait for assignment to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'question-container')]"))
            )
            print("Assignment loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error navigating to assignment: {e}")
            return False
    
    def get_question_details(self):
        """Extract the current question text and options"""
        try:
            # Find the current question container
            question_container = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'question-container')]"))
            )
            
            # Extract question text
            question_text = question_container.find_element(By.XPATH, ".//*[contains(@class, 'question-text') or contains(@class, 'question-stem')]").text
            print(f"Current question: {question_text[:100]}...")
            
            options = []
            
            # Check for radio buttons (multiple choice)
            radio_options = question_container.find_elements(By.XPATH, ".//input[@type='radio']")
            if radio_options:
                for option in radio_options:
                    option_id = option.get_attribute("id")
                    if option_id:
                        try:
                            label = question_container.find_element(By.XPATH, f"//label[@for='{option_id}']")
                            options.append({
                                "id": option_id,
                                "text": label.text.strip(),
                                "element": option
                            })
                        except:
                            pass
            
            # Check for checkboxes (multiple select)
            if not options:
                checkbox_options = question_container.find_elements(By.XPATH, ".//input[@type='checkbox']")
                if checkbox_options:
                    for option in checkbox_options:
                        option_id = option.get_attribute("id")
                        if option_id:
                            try:
                                label = question_container.find_element(By.XPATH, f"//label[@for='{option_id}']")
                                options.append({
                                    "id": option_id,
                                    "text": label.text.strip(),
                                    "element": option
                                })
                            except:
                                pass
            
            return {
                "question_text": question_text,
                "options": options
            }
                
        except Exception as e:
            print(f"Error getting question details: {e}")
            return {"question_text": "", "options": []}
    
    def use_openai_for_answer(self, question_text, options):
        """Use OpenAI API to determine the best answer"""
        if not self.openai_api_key:
            print("No OpenAI API key available. Selecting first option by default.")
            return 0
        
        try:
            # Format options for prompt
            options_text = "\n".join([f"{i+1}. {opt['text']}" for i, opt in enumerate(options)])
            
            prompt = f"""As an AI tutor, answer the following multiple-choice question:

Question: {question_text}

Options:
{options_text}

Please select the correct answer by number and provide a brief explanation of why it's correct.
Just provide the number of the correct answer first, followed by your explanation.
"""
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # or whichever model you prefer
                messages=[
                    {"role": "system", "content": "You are a helpful AI tutor that helps answer academic questions accurately."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            
            answer_text = response.choices[0].message.content.strip()
            print(f"AI response: {answer_text}")
            
            # Extract the answer number from the response
            # Look for a number at the beginning of the response
            match = re.search(r"^(\d+)", answer_text)
            if match:
                answer_num = int(match.group(1)) - 1  # Convert to 0-based index
                if 0 <= answer_num < len(options):
                    print(f"AI selected option {answer_num + 1}")
                    return answer_num
            
            # Fallback: look for any number in the response
            match = re.search(r"(\d+)", answer_text)
            if match:
                answer_num = int(match.group(1)) - 1
                if 0 <= answer_num < len(options):
                    print(f"AI selected option {answer_num + 1} (fallback)")
                    return answer_num
            
            print("Could not determine answer from AI response. Selecting first option.")
            return 0
            
        except Exception as e:
            print(f"Error using OpenAI API: {e}")
            return 0  # Default to first option
    
    def select_high_confidence(self):
        """Select 'High' confidence level after answering a question"""
        try:
            # Wait for confidence level selector to appear
            confidence_container = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'confidence-container') or contains(text(), 'confidence') or contains(text(), 'Confidence')]"))
            )
            
            # Look for the "High" confidence button
            high_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'High') or contains(@class, 'high-confidence')]")
            high_button.click()
            print("Selected 'High' confidence level")
            
            # Sometimes there's a confirmation or continue button after selecting confidence
            try:
                continue_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue') or contains(text(), 'Next') or contains(@class, 'continue-button')]"))
                )
                continue_button.click()
                print("Clicked continue button after confidence selection")
            except:
                print("No continue button found after confidence selection")
                
            return True
        except Exception as e:
            print(f"Error selecting confidence level: {e}")
            return False
    
    def answer_question(self):
        """Answer the current question using OpenAI API"""
        try:
            # Get question details
            question_data = self.get_question_details()
            
            if not question_data["options"]:
                print("No answer options found. Skipping question.")
                
                # Try to find a "Skip" or "Next" button
                try:
                    skip_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Skip') or contains(text(), 'Next')]")
                    skip_button.click()
                    print("Skipped question")
                    time.sleep(2)
                    return True
                except:
                    print("Could not skip question")
                    return False
            
            # Use OpenAI to select the best answer
            best_answer_idx = self.use_openai_for_answer(
                question_data["question_text"], 
                question_data["options"]
            )
            
            # Click the selected option
            best_option = question_data["options"][best_answer_idx]["element"]
            best_option.click()
            print(f"Selected answer: {question_data['options'][best_answer_idx]['text'][:50]}...")
            
            # Submit the answer
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit') or contains(@class, 'submit-button')]"))
            )
            submit_button.click()
            print("Answer submitted!")
            
            # Wait for feedback
            time.sleep(3)
            
            # Select high confidence
            self.select_high_confidence()
            
            # Check for the next button and click it if available
            try:
                next_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next') or contains(@class, 'next-button')]"))
                )
                next_button.click()
                print("Moving to next question...")
                time.sleep(2)
                return True
            except:
                print("No next button found. Assignment may be complete.")
                return False
                
        except Exception as e:
            print(f"Error answering question: {e}")
            return False
            
    def save_progress(self, filename="smartbook_progress.json"):
        """Save current progress to a file"""
        try:
            progress_data = {
                "timestamp": time.time(),
                "current_url": self.driver.current_url,
                "completed_questions": 0  # You would track this in a real implementation
            }
            
            with open(filename, 'w') as f:
                json.dump(progress_data, f)
                
            print(f"Progress saved to {filename}")
            
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def complete_assignment(self, max_questions=50):
        """Complete the entire assignment"""
        question_count = 0
        
        while question_count < max_questions:
            print(f"\nQuestion {question_count + 1}:")
            if not self.answer_question():
                break
            question_count += 1
            
            # Add a small delay between questions
            time.sleep(2)
            
        print(f"Assignment completed! Answered {question_count} questions.")
        self.save_progress()
    
    def close(self):
        """Close the browser and clean up"""
        try:
            self.driver.quit()
            print("Browser closed.")
        except:
            pass

def load_config():
    """Load configuration from config.ini file"""
    config = configparser.ConfigParser()
    
    # Define default configuration
    default_config = {
        'SmartBook': {
            'username': '',
            'password': ''
        },
        'OpenAI': {
            'api_key': ''
        }
    }
    
    # Check if config file exists
    if os.path.exists('config.ini'):
        config.read('config.ini')
    else:
        # Create config file with default values
        for section, keys in default_config.items():
            if not config.has_section(section):
                config.add_section(section)
            for key, value in keys.items():
                config.set(section, key, value)
        
        with open('config.ini', 'w') as f:
            config.write(f)
        
        print("Created config.ini file. Please edit it to include your credentials.")
        
    return config

def main():
    print("SmartBook Assignment Automation Tool with OpenAI")
    print("============================================")
    
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
            with open('config.ini', 'w') as f:
                config.write(f)
    
    # Get SmartBook credentials
    username = config.get('SmartBook', 'username', fallback='')
    password = config.get('SmartBook', 'password', fallback='')
    
    if not username:
        username = input("Enter your SmartBook username/email: ")
        if username and not password:
            password = getpass.getpass("Enter your SmartBook password: ")
            
        # Save to config if provided
        if username:
            if not config.has_section('SmartBook'):
                config.add_section('SmartBook')
            config.set('SmartBook', 'username', username)
            if password:
                config.set('SmartBook', 'password', password)
            with open('config.ini', 'w') as f:
                config.write(f)
    
    # Initialize automation
    headless_mode = input("Run in headless mode? (y/n): ").lower() == 'y'
    bot = SmartBookAutomation(headless=headless_mode, openai_api_key=openai_api_key)
    
    try:
        # Login
        if not bot.login(username, password):
            return
        
        # Navigate to assignment
        if not bot.navigate_to_assignment():
            print("Could not find an assignment to complete.")
            bot.close()
            return
        
        # Ask how many questions to answer
        try:
            max_questions = int(input("Maximum number of questions to answer (default 50): ") or "50")
        except ValueError:
            max_questions = 50
        
        # Complete the assignment
        bot.complete_assignment(max_questions)
        
        # Pause before closing
        input("Press Enter to close the browser...")
        
    finally:
        bot.close()

if __name__ == "__main__":
    main()
