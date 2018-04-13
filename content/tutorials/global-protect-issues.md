Title: Solving Connectivity Issues w/ Global Protect
Date: 2018-04-13
Modified: 2018-04-13
Tags: mac, vpn
Slug: global-protect-issues
Author: Miguel Lopez
Summary: Solving Connectivity Issues on Global Protect

## **Resend Credential Error**

I recently got a new Mac at work and spent the past 8 hours trying to solve connectivity issues with Global Protect.

My global protect would throw out this generic error that said:

```
Resend Credential

Cannot connect to service socket
```

I was able to poke around and find the logs for this issue at `~/Library/Logs/PaloAltoNetworks/GlobalProtect/PanGPA.log`.

I ran a `tail -f` on that log and found the following trace:

```
P 595-T771   Apr 10 20:40:42:225745 Info ( 291): InitConnection ...
P 595-T771   Apr 10 20:40:42:225785 Info (  59): fd still open before connect
P 595-T771   Apr 10 20:40:42:225988 Info (  80): Failed to connect to server at port:4767
P 595-T771   Apr 10 20:40:42:226004 Info ( 295): Cannot connect to service, error: 61
P 595-T771   Apr 10 20:40:42:226010 Debug( 474): Unable to connect to Pan Service
P 595-T771   Apr 10 20:40:47:225540 Info ( 291): InitConnection ...
P 595-T771   Apr 10 20:40:47:225581 Info (  59): fd still open before connect
P 595-T771   Apr 10 20:40:47:225782 Info (  80): Failed to connect to server at port:4767
P 595-T771   Apr 10 20:40:47:225799 Info ( 295): Cannot connect to service, error: 61
P 595-T771   Apr 10 20:40:47:225805 Debug( 474): Unable to connect to Pan Service
P 595-T771   Apr 10 20:40:52:226040 Info ( 291): InitConnection ...
P 595-T771   Apr 10 20:40:52:226069 Info (  59): fd still open before connect
P 595-T771   Apr 10 20:40:52:226206 Info (  80): Failed to connect to server at port:4767
P 595-T771   Apr 10 20:40:52:226218 Info ( 295): Cannot connect to service, error: 61
P 595-T771   Apr 10 20:40:52:226223 Debug( 474): Unable to connect to Pan Service
```

Over and over again.

As it turns out, this was because Global Protect could not connect to an agent called the pangps service. You can check if this service is loaded by running the following command in your terminal.

```
launchctl load /Library/LaunchAgents/com.paloaltonetworks.gp.pangpa.plist
launchctl load /Library/LaunchAgents/com.paloaltonetworks.gp.pangps.plist
```

If you're ~lucky~ like me, you'll see that the service is running. So what the hell right? Why isn't Pan Service working???

-----

As it turns out, I needed to **install Global Protect as the root admin** on my Mac. This is incredibly **frustrating** because my user already had the admin role associated with it. 

Before you reinstall, it's important that you allow your mac to allow 3rd party apps to run. 

You can find this under "Security and Privacy". You'll need to show Advanced settings and click Allow Apps Downloaded from "Anywhere"

1. Uninstall Global Protect
2. Log in as the admin user
3. Reinstall Global Protect

Once you reinstall, head back over to the "Security and Privacy" settings. You'll see a prompt that asks if Global Protect is allowed to run on this machine. Click yes. 

![Security and Privacy](http://cdn.osxdaily.com/wp-content/uploads/2016/09/gatekeeper-allow-apps-anywhere-macos-2.jpg "Security and Privacy")

By this point you should able to connect to Global Protect. If not, i'm sorry. Best of luck :(