import pywhatkit as pwk

# Define conditions
entry_conditions = (":begin", "start")
exit_conditions = ( "quit", "exit")

#services list to use bot
services_list = {
   '1': "Auto WhatsApp Message",
}
def main():

    print("Welcome to bot!")
    print("""Available Services:
    1. Auto WhatsApp Message"
    """) 
    while True:
        chat = input('Hey, How can I assist you today? (Type "service" to view services list) ')

        if chat == "service":
            print("Here are the available commands:")
            print(services_list)
            
        chat = input('Please enter the number of the service you want to use: ')
        if chat in services_list:
            print(f"{chat}: {services_list[chat]}")
            if chat == '1':
                phone_number = input("Enter the phone number (with country code): ")
                message = input("Enter the message you want to send: ")
                hour = int(input("Enter the hour (24-hour format): "))
                minute = int(input("Enter the minute: "))
                pwk.sendwhatmsg(phone_number, message, hour, minute)
                print("Message sent successfully!")
        else:
            print("Your input did not match any predefined commands. Please try again.")

if __name__ == "__main__":
    main()