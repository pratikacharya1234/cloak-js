import pywhatkit as pwk

# Define conditions
entry_conditions = (":begin", "start")
exit_conditions = ( "quit", "exit")

#services list to use bot
services_list = {
   '1': "Auto WhatsApp Message",
}
def main():

    # Print welcome message and available services
    print("Welcome to bot!")
    print("""Available Services:
    1. Auto WhatsApp Message"
    """) 

    # Loop to keep the bot running until exit conditions are met
    while True:

        # Prompt user for input
        chat = input('Hey, How can I assist you today? (Type "service" to view services list) ')

        # Check for entry conditions
        if chat == "service":
            print("Here are the available commands:")
            print(services_list)
        
        # Check for exit conditions
        chat = input('Please enter the number of the service you want to use: ')

        # Check if the user wants to exit
        if chat in services_list:

            # Print the selected service
            print(f"{chat}: {services_list[chat]}")

            # Check if the user wants to exit
            if chat == '1':
                phone_number = input("Enter the phone number (with country code): ")
                message = input("Enter the message you want to send: ")
                hour = int(input("Enter the hour (24-hour format): "))
                minute = int(input("Enter the minute: "))

                # Send the WhatsApp message using pywhatkit
                print(f"Sending message to {phone_number}...")
                pwk.sendwhatmsg(phone_number, message, hour, minute)
                print("Message sent successfully!")
        else:
            print("Your input did not match any predefined commands. Please try again.")

# Check if the script is being run directly
# and call the main function
if __name__ == "__main__":
    main()