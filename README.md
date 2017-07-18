![alt text][aws]
# MotherBot - AWS Chatbot submission

**MotherBot** helps by Sharing Calendars, Approved Contacts and provides a self-service administration platform for the C.E.O. of the Home to effectively schedule and organize.  The AWS Chat Bot allows various processes to be made available to these household with the primary purpose of verifying the identity of the individual connections, formalizing an approval process and managing the ‘feasibility’ on the calendar.  

![alt text][serverless]

## **Uniqueness**

Households are like mini-organizations, except their members or ‘little users’ often find themselves in a place of constant challenge and response.  Seeking approval and then finding out how to facilitate getting it done is the world that ‘Tweens’ live in.  The coordination required among Parents often requires effective communication practices regardless of your Work-life or Marital status.  Technology can enable Parents or Parental guardians to manage the household workloads while providing an appropriate level of privacy and respect.

## Design Components
![alt text][motherbot]  

There are 3 main functional aspects to MotherBot.  

1.	Identity and Access Management (Contact Management)
2.	Activity Approval
3.	Calendar Feasibility

## Contact Management
 
Managing the contacts that are made are very important in a digital age.  This is for protection, but also as a measure of maintaining contact information.  There is often a need to share contact information within the private networks that Households create.  

**MotherBot** can be introduced to a friend which begins this Functional workflow.  It is similar to performing a 2 form factor of authorization, by authenticating the new contact by gaining a phone number as a by-product.  This allows for a contact number for each of the ‘friends’ that are included in the direct calls or attended events.  

![alt text][friend] 

**Phone Verification**, using Twillio, is used to make sure people are who they say they are when signing up as a ‘Friend’. It reduces risk and prevents fraudulent signups and increases trust. Phone verification events are best implemented when the user is giving you their number for the first time.  When a user triggers that event, generate a One Time Passcode (OTP) and send it via SMS to the user Present the user with a UI to enter the code and verify the code against the one you generated to see if they match.   

![alt text][twilio1]

## Models
Intents  
* MeetAFriend  
 Slots: FriendInfo  
 Utterances:  
 Prompts:  
* CanICall  
 Slots: WhoCall  
 Utterances:  
 Prompts:  
* CanIGoTo:   
 Slots: ApprovedFriendsHome - Available approved Friend's House  
 Slots: ApprovedPublicPlaces – Pool Club, Library, Bowling, Mall  
 Utterances:  
 Prompts:  
* CanISee:  
 Slots: Events –   
 Slots: Approved Movie   
 Slots: Approved Concert  
 Utterances:  
 Prompts:  

[aws]: https://bentowner.blob.core.windows.net/images/EPS.png?raw=true "AWS Chatbot Challenge"
[friend]: https://bentowner.blob.core.windows.net/images/meetafriend.png?raw=true "Meet a friend Intent"
[serverless]: https://bentowner.blob.core.windows.net/images/serverlessarch.png?raw=true "AWS serverless arch"
[motherbot]: https://bentowner.blob.core.windows.net/images/MotherBot2.png?raw=true "MotherBot"
[twilio1]: https://bentowner.blob.core.windows.net/images/twilio.png?raw=true "twilio Api"
[twilio2]: https://bentowner.blob.core.windows.net/images/twilio2.png?raw=true "twilio"
